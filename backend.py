"""
Armenian Rhyme Finder - Backend
Provides rhyme search APIs backed by either a compressed SQLite dictionary
or a JSONL fallback.
"""

from __future__ import annotations

import json
import logging
import os
import re
import sqlite3
import zlib
from functools import lru_cache
from typing import Dict, Iterable, List, Optional, Tuple

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from config import AUTOCOMPLETE_LIMIT, DICTIONARY_FILE

# ---------------------------------------------------------------------------
# Flask application setup
# ---------------------------------------------------------------------------

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
CORS(app)

SQLITE_DB_FILE = os.environ.get("DICTIONARY_SQLITE_FILE", "dictionary-hy.db")

# Global state
db_connection: Optional[sqlite3.Connection] = None
USE_SQLITE = False

dictionary: Dict[str, dict] = {}
form_to_entries: Dict[str, List[Tuple[str, int]]] = {}
normalized_form_to_entries: Dict[str, List[Tuple[str, int]]] = {}

# ---------------------------------------------------------------------------
# Static file serving
# ---------------------------------------------------------------------------


@app.route("/")
def home():
    """Serve the single-page application."""
    return send_from_directory(".", "index.html")


# ---------------------------------------------------------------------------
# Phoneme feature definitions
# ---------------------------------------------------------------------------

VOWELS = {"a", "e", "i", "o", "u", "ə", "ɑ", "ɔ", "ʌ", "æ", "iː", "uː", "oː", "ɛ"}

CONSONANTS = {
    "p": ("labial", "stop"),
    "b": ("labial", "stop"),
    "t": ("alveolar", "stop"),
    "d": ("alveolar", "stop"),
    "k": ("velar", "stop"),
    "g": ("velar", "stop"),
    "kʰ": ("velar", "stop"),
    "f": ("labial", "fricative"),
    "v": ("labial", "fricative"),
    "s": ("alveolar", "fricative"),
    "z": ("alveolar", "fricative"),
    "ʃ": ("palatal", "fricative"),
    "ʒ": ("palatal", "fricative"),
    "x": ("velar", "fricative"),
    "ɣ": ("velar", "fricative"),
    "θ": ("dental", "fricative"),
    "ð": ("dental", "fricative"),
    "h": ("glottal", "fricative"),
    "m": ("labial", "nasal"),
    "n": ("alveolar", "nasal"),
    "ŋ": ("velar", "nasal"),
    "l": ("alveolar", "approximant"),
    "ɹ": ("alveolar", "approximant"),
    "r": ("alveolar", "approximant"),
    "j": ("palatal", "approximant"),
    "w": ("labial", "approximant"),
    "tsʰ": ("alveolar", "stop"),
    "tʃ": ("palatal", "stop"),
}

VOWEL_FEATURES = {
    "i": ("close", "front"),
    "iː": ("close", "front"),
    "e": ("close-mid", "front"),
    "ɛ": ("open-mid", "front"),
    "æ": ("near-open", "front"),
    "a": ("open", "front"),
    "ə": ("open-mid", "central"),
    "ʌ": ("open-mid", "back"),
    "o": ("close-mid", "back"),
    "oː": ("close-mid", "back"),
    "ɔ": ("open-mid", "back"),
    "u": ("close", "back"),
    "uː": ("close", "back"),
    "ɑ": ("open", "back"),
}


# ---------------------------------------------------------------------------
# Dictionary loading helpers
# ---------------------------------------------------------------------------


def get_db_connection() -> Optional[sqlite3.Connection]:
    """Initialise and cache a SQLite connection if the database exists."""
    global db_connection, USE_SQLITE

    if db_connection is not None:
        return db_connection

    db_path = SQLITE_DB_FILE
    if not db_path or not os.path.exists(db_path):
        logging.info(
            "SQLite dictionary '%s' not found; defaulting to JSONL dictionary.",
            db_path,
        )
        USE_SQLITE = False
        return None

    try:
        connection = sqlite3.connect(db_path, check_same_thread=False)
        connection.row_factory = sqlite3.Row

        # Ensure schema exists
        required_tables = {"entries", "forms"}
        existing = {
            row["name"]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        if not required_tables.issubset(existing):
            missing = ", ".join(sorted(required_tables - existing))
            raise RuntimeError(f"missing required tables: {missing}")

        connection.execute("SELECT 1 FROM entries LIMIT 1")

        db_connection = connection
        USE_SQLITE = True
        logging.info("Using SQLite dictionary at %s", os.path.abspath(db_path))
        return db_connection
    except Exception as exc:
        logging.warning(
            "Failed to initialise SQLite dictionary '%s': %s. Falling back to JSON.",
            db_path,
            exc,
        )
        if "connection" in locals():
            try:
                connection.close()
            except Exception:
                pass
        db_connection = None
        USE_SQLITE = False
        return None


@lru_cache(maxsize=4096)
def fetch_entry_from_sqlite(base_word: str) -> Optional[dict]:
    """Retrieve and decompress a dictionary entry from SQLite."""
    conn = get_db_connection()
    if not conn:
        return None

    row = conn.execute(
        "SELECT entry_blob FROM entries WHERE base_word = ?", (base_word,)
    ).fetchone()
    if not row:
        return None

    try:
        data = zlib.decompress(row["entry_blob"])
        return json.loads(data.decode("utf-8"))
    except Exception as exc:
        logging.error("Failed to decompress entry '%s': %s", base_word, exc)
        return None


def resolve_sqlite_forms(term: str) -> List[Tuple[str, int]]:
    """Fetch base-word mappings for a form using SQLite."""
    conn = get_db_connection()
    if not conn:
        return []

    cursor = conn.execute(
        "SELECT base_word, form_index FROM forms WHERE form = ? COLLATE NOCASE",
        (term,),
    )
    return [(row["base_word"], row["form_index"]) for row in cursor]


def iterate_dictionary_entries() -> Iterable[Tuple[str, dict]]:
    """Yield (base_word, entry) pairs from the active dictionary backend."""
    if USE_SQLITE:
        conn = get_db_connection()
        if not conn:
            return  # No SQLite connection available; yield nothing
        cursor = conn.execute("SELECT base_word, entry_blob FROM entries")
        for row in cursor:
            try:
                entry = json.loads(zlib.decompress(row["entry_blob"]).decode("utf-8"))
            except Exception:
                continue
            yield row["base_word"], entry
    else:
        for item in dictionary.items():
            yield item


def load_dictionary(filepath: str) -> None:
    """Load JSONL dictionary into memory as a fallback."""
    global dictionary, form_to_entries, normalized_form_to_entries

    dictionary = {}
    form_to_entries = {}
    normalized_form_to_entries = {}
    if "get_entry_data" in globals():
        get_entry_data.cache_clear()

    candidate_paths = [
        filepath,
        os.path.join(os.getcwd(), filepath),
        os.path.join(os.path.dirname(__file__), filepath),
    ]
    file_to_open = next((p for p in candidate_paths if os.path.exists(p)), None)

    if not file_to_open:
        logging.warning(
            "Dictionary file '%s' not found. Running with empty dictionary.", filepath
        )
        return

    def add_case_mapping(term: str, base_word: str, idx: int) -> None:
        if not term:
            return
        key = term.casefold()
        normalized_form_to_entries.setdefault(key, [])
        if (base_word, idx) not in normalized_form_to_entries[key]:
            normalized_form_to_entries[key].append((base_word, idx))

    try:
        with open(file_to_open, "r", encoding="utf-8") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if not line:
                    continue
                entry = json.loads(line)
                base_word = entry.get("", "")
                if not base_word:
                    continue

                dictionary[base_word] = entry
                add_case_mapping(base_word, base_word, 0)

                forms = entry.get("f", [])
                if isinstance(forms, list):
                    for idx, form in enumerate(forms):
                        form_to_entries.setdefault(form, []).append((base_word, idx))
                        add_case_mapping(form, base_word, idx)

        logging.info(
            "Loaded %d dictionary entries (%d forms indexed, %d case-insensitive mappings)",
            len(dictionary),
            sum(len(v) for v in form_to_entries.values()),
            sum(len(v) for v in normalized_form_to_entries.values()),
        )
    except Exception as exc:
        logging.error("Failed to load dictionary file '%s': %s", file_to_open, exc)
        dictionary = {}
        form_to_entries = {}
        normalized_form_to_entries = {}


def initialise_dictionary() -> None:
    """Prefer SQLite; fall back to JSON if unavailable."""
    conn = get_db_connection()
    if conn:
        logging.info("SQLite dictionary initialised successfully.")
    else:
        json_path = os.environ.get("DICTIONARY_FILE", DICTIONARY_FILE)
        load_dictionary(json_path)


initialise_dictionary()

# ---------------------------------------------------------------------------
# Phoneme utilities and rhyme scoring
# ---------------------------------------------------------------------------


def split_into_syllables(ipa_phones: List[str]) -> List[List[str]]:
    if not ipa_phones:
        return []

    syllables: List[List[str]] = []
    i = 0
    while i < len(ipa_phones):
        syllable: List[str] = []

        while i < len(ipa_phones) and ipa_phones[i] not in VOWELS:
            syllable.append(ipa_phones[i])
            i += 1

        if i < len(ipa_phones):
            syllable.append(ipa_phones[i])
            i += 1

        while i < len(ipa_phones) and ipa_phones[i] not in VOWELS:
            if i + 1 < len(ipa_phones) and ipa_phones[i + 1] in VOWELS:
                break
            syllable.append(ipa_phones[i])
            i += 1

        if syllable:
            syllables.append(syllable)

    return syllables


def phone_distance(phone1: str, phone2: str) -> float:
    if phone1 == phone2:
        return 0.0

    if phone1 in VOWELS and phone2 in VOWELS:
        f1 = VOWEL_FEATURES.get(phone1)
        f2 = VOWEL_FEATURES.get(phone2)
        if f1 and f2:
            if f1[0] == f2[0] or f1[1] == f2[1]:
                return 0.3
        return 0.7

    if phone1 in CONSONANTS and phone2 in CONSONANTS:
        c1 = CONSONANTS[phone1]
        c2 = CONSONANTS[phone2]
        if c1[0] == c2[0] and c1[1] == c2[1]:
            return 0.1
        if c1[0] == c2[0] or c1[1] == c2[1]:
            return 0.4
        return 0.8

    return 1.0


def levenshtein_similarity(
    tail1: List[str],
    tail2: List[str],
    is_last_syllable: bool = False,
) -> float:
    m, n = len(tail1), len(tail2)

    if m == 0 and n == 0:
        return 1.0
    if m == 0 or n == 0:
        return 0.0

    vowel_pos1 = next((i for i, p in enumerate(tail1) if p in VOWELS), -1)
    vowel_pos2 = next((i for i, p in enumerate(tail2) if p in VOWELS), -1)

    dp = [[0.0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        weight = 1.5 if tail1[i - 1] in VOWELS else 1.0
        dp[i][0] = dp[i - 1][0] + weight

    for j in range(1, n + 1):
        weight = 1.5 if tail2[j - 1] in VOWELS else 1.0
        dp[0][j] = dp[0][j - 1] + weight

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            phone1 = tail1[i - 1]
            phone2 = tail2[j - 1]
            is_vowel1 = phone1 in VOWELS
            is_vowel2 = phone2 in VOWELS
            base_weight = 1.5 if (is_vowel1 or is_vowel2) else 1.0

            if is_last_syllable and (i - 1 == vowel_pos1 or j - 1 == vowel_pos2):
                base_weight *= 1.3

            if phone1 == phone2:
                cost = 0
            else:
                cost = phone_distance(phone1, phone2) * base_weight

            dp[i][j] = min(
                dp[i - 1][j] + base_weight,
                dp[i][j - 1] + base_weight,
                dp[i - 1][j - 1] + cost,
            )

    distance = dp[m][n]

    max_distance = 0.0
    for idx in range(max(m, n)):
        if idx < m:
            weight = 1.5 if tail1[idx] in VOWELS else 1.0
            if is_last_syllable and idx == vowel_pos1:
                weight *= 1.3
            max_distance += weight
        if idx < n:
            weight = 1.5 if tail2[idx] in VOWELS else 1.0
            if is_last_syllable and idx == vowel_pos2:
                weight *= 1.3
            max_distance += weight

    max_distance /= 2.0
    if max_distance == 0:
        return 1.0

    similarity = 1.0 - (distance / max_distance)
    return max(0.0, min(1.0, similarity))


def extract_vowel_sequence(syllables: List[List[str]]) -> List[str]:
    vowels = []
    for syllable in syllables:
        for phone in syllable:
            if phone in VOWELS:
                vowels.append(phone)
                break
    return vowels


def calculate_vowel_sequence_similarity(
    vowels1: List[str], vowels2: List[str]
) -> float:
    if not vowels1 or not vowels2:
        return 0.0

    min_len = min(len(vowels1), len(vowels2))
    total_score = 0.0
    total_weight = 0.0

    for offset in range(1, min_len + 1):
        v1 = vowels1[-offset]
        v2 = vowels2[-offset]

        if offset == 1:
            weight = 3.0
        elif offset == 2:
            weight = 2.0
        elif offset == 3:
            weight = 1.5
        else:
            weight = 1.0

        score = 1.0 if v1 == v2 else 1.0 - phone_distance(v1, v2)
        total_score += score * weight
        total_weight += weight

    length_penalty = max(0.5, 1.0 - abs(len(vowels1) - len(vowels2)) * 0.1)

    if total_weight == 0:
        return 0.0

    return max(0.0, min(1.0, (total_score / total_weight) * length_penalty))


def calculate_multi_syllable_rhyme_score(ipa1: List[str], ipa2: List[str]) -> Dict:
    syllables1 = split_into_syllables(ipa1)
    syllables2 = split_into_syllables(ipa2)

    if not syllables1 or not syllables2:
        return {
            "final_score": 0.0,
            "label": "none",
            "syllables_matched": 0,
            "last_syllable_similarity": 0.0,
            "penultimate_similarity": 0.0,
            "vowel_sequence_similarity": 0.0,
            "length_diff": 0,
        }

    last_syl1 = syllables1[-1]
    last_syl2 = syllables2[-1]
    last_sim = levenshtein_similarity(last_syl1, last_syl2, is_last_syllable=True)

    penultimate_sim = 0.0
    if len(syllables1) >= 2 and len(syllables2) >= 2:
        penultimate_sim = levenshtein_similarity(
            syllables1[-2], syllables2[-2], is_last_syllable=False
        )

    vowels1 = extract_vowel_sequence(syllables1)
    vowels2 = extract_vowel_sequence(syllables2)
    vowel_seq_sim = calculate_vowel_sequence_similarity(vowels1, vowels2)

    length_diff = abs(len(syllables1) - len(syllables2))
    identical_last = last_syl1 == last_syl2

    syllables_matched = 1 if last_sim >= 0.5 else 0
    if syllables_matched and last_sim >= 0.90:
        min_syllables = min(len(syllables1), len(syllables2))
        for idx in range(2, min_syllables + 1):
            candidate1 = syllables1[-idx]
            candidate2 = syllables2[-idx]
            if candidate1 == candidate2:
                syllables_matched += 1
                continue
            sim = levenshtein_similarity(candidate1, candidate2)
            if sim >= 0.90:
                syllables_matched += 1
            else:
                break

    multi_bonus = 0.08 * (syllables_matched - 1) if syllables_matched > 1 else 0.0
    base_score = last_sim
    final_score = min(1.0, base_score + multi_bonus)

    if base_score >= 0.85:
        final_score = min(
            1.0,
            final_score * 0.85 + vowel_seq_sim * 0.15,  # 15% weight to vowels
        )

    label = get_rhyme_label_from_score(
        last_syl1, last_syl2, last_sim, identical_last, syllables_matched
    )

    return {
        "final_score": final_score,
        "label": label,
        "syllables_matched": syllables_matched,
        "last_syllable_similarity": last_sim,
        "penultimate_similarity": penultimate_sim,
        "vowel_sequence_similarity": vowel_seq_sim,
        "length_diff": length_diff,
    }


def get_rhyme_label_from_score(
    tail1: List[str],
    tail2: List[str],
    similarity: float,
    identical: bool,
    syllables_matched: int,
) -> str:
    if identical:
        return "perfect"

    nucleus1 = next((p for p in tail1 if p in VOWELS), None)
    nucleus2 = next((p for p in tail2 if p in VOWELS), None)
    same_nucleus = nucleus1 == nucleus2

    if syllables_matched >= 2 and similarity >= 0.99:
        return "perfect"
    if syllables_matched >= 2 and similarity >= 0.90:
        return "near-perfect"
    if similarity >= 0.93 and same_nucleus:
        return "near-perfect"
    if same_nucleus and similarity >= 0.70:
        return "assonance"
    if similarity >= 0.50:
        return "slant"
    return "none"


# ---------------------------------------------------------------------------
# Dictionary query helpers
# ---------------------------------------------------------------------------


def resolve_query_entries(input_word: str) -> List[Tuple[str, int]]:
    normalized = input_word.casefold()

    if USE_SQLITE:
        entries = resolve_sqlite_forms(input_word)
        if entries:
            return entries
        conn = get_db_connection()
        if conn:
            row = conn.execute(
                "SELECT base_word FROM entries "
                "WHERE base_word = ? COLLATE NOCASE LIMIT 1",
                (input_word,),
            ).fetchone()
            if row:
                return [(row["base_word"], 0)]
        return []

    if input_word in dictionary:
        return [(input_word, 0)]
    if input_word in form_to_entries:
        return form_to_entries[input_word]
    return normalized_form_to_entries.get(normalized, [])


@lru_cache(maxsize=8192)
def get_entry_data(base_word: str) -> Optional[dict]:
    if USE_SQLITE:
        return fetch_entry_from_sqlite(base_word)
    return dictionary.get(base_word)


# ---------------------------------------------------------------------------
# Rhyme search
# ---------------------------------------------------------------------------


def find_rhymes(
    input_word: str, limit: int = 50, offset: int = 0, include_tenses: bool = False
) -> Tuple[List[dict], int]:
    input_word = input_word.strip()
    if not input_word:
        return [], 0

    query_entries = resolve_query_entries(input_word)
    if not query_entries:
        return [], 0

    query_ipa = None
    matched_base_words = {base for base, _ in query_entries}

    for base_word, form_idx in query_entries:
        entry = get_entry_data(base_word)
        if not entry:
            continue
        forms_ipa = entry.get("f_ipa") or []
        if form_idx < len(forms_ipa):
            query_ipa = forms_ipa[form_idx].split()
            break

    if not query_ipa:
        return [], 0

    rhymes: List[dict] = []
    seen: set = set()

    for base_word, entry in iterate_dictionary_entries():
        if base_word in matched_base_words or not entry:
            continue

        forms = entry.get("f") or []
        forms_ipa = entry.get("f_ipa") or []
        if not forms or not forms_ipa or len(forms) != len(forms_ipa):
            continue

        indices = range(len(forms)) if include_tenses else range(1)
        for idx in indices:
            display = forms[idx]
            candidate_ipa = forms_ipa[idx].split()
            result = calculate_multi_syllable_rhyme_score(query_ipa, candidate_ipa)

            if result["final_score"] < 0.3 or result["label"] == "none":
                continue

            key = (base_word, display)
            if key in seen:
                continue
            seen.add(key)

            rhymes.append(
                {
                    "word": display,
                    "base_word": base_word,
                    "similarity": round(result["final_score"], 3),
                    "label": result["label"],
                    "syllables_matched": result["syllables_matched"],
                    "definition": (entry.get("d") or [""])[0] if entry.get("d") else "",
                    "part_of_speech": (entry.get("p") or [""])[0]
                    if entry.get("p")
                    else "",
                    "is_base_form": idx == 0,
                    "_penultimate_similarity": result["penultimate_similarity"],
                    "_vowel_sequence_similarity": result["vowel_sequence_similarity"],
                    "_length_diff": result["length_diff"],
                }
            )

    label_priority = {"perfect": 0, "near-perfect": 1, "assonance": 2, "slant": 3}
    rhymes.sort(
        key=lambda x: (
            -x["similarity"],
            -x.get("_vowel_sequence_similarity", 0),
            -x.get("_penultimate_similarity", 0),
            x.get("_length_diff", 999),
            label_priority.get(x["label"], 4),
        )
    )

    for rhyme in rhymes:
        rhyme.pop("_penultimate_similarity", None)
        rhyme.pop("_vowel_sequence_similarity", None)
        rhyme.pop("_length_diff", None)

    total = len(rhymes)
    return rhymes[offset : offset + limit], total


# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------


@app.route("/api/rhymes", methods=["GET"])
def get_rhymes():
    word = request.args.get("word", "").strip()
    limit = request.args.get("limit", 50, type=int)
    offset = request.args.get("offset", 0, type=int)
    include_tenses = request.args.get("include_tenses", "false").lower() == "true"

    if not word:
        return jsonify({"error": "Word parameter required"}), 400

    rhymes, total = find_rhymes(word, limit, offset, include_tenses)
    has_more = (offset + len(rhymes)) < total

    return jsonify(
        {
            "word": word,
            "rhymes": rhymes,
            "include_tenses": include_tenses,
            "limit": limit,
            "offset": offset,
            "total": total,
            "has_more": has_more,
        }
    )


@app.route("/api/search", methods=["GET"])
def search():
    query = request.args.get("q", "").strip().lower()
    if not query:
        return jsonify({"results": []})

    results: List[dict] = []
    seen: set = set()

    escaped = query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    like_pattern = f"%{escaped}%"

    if USE_SQLITE:
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.execute(
                    "SELECT base_word, entry_blob, definition, part_of_speech "
                    "FROM entries WHERE base_word LIKE ? ESCAPE '\\\\' "
                    "COLLATE NOCASE LIMIT ?",
                    (like_pattern, AUTOCOMPLETE_LIMIT),
                )
                for row in cursor:
                    base_word = row["base_word"]
                    if base_word in seen:
                        continue
                    definition = row["definition"] or ""
                    pos = row["part_of_speech"] or ""
                    supplemental_entry: dict = {}
                    if (not definition or not pos) and row["entry_blob"]:
                        try:
                            supplemental_entry = json.loads(
                                zlib.decompress(row["entry_blob"]).decode("utf-8")
                            )
                        except Exception as exc:
                            logging.warning(
                                "Failed to decompress autocomplete entry '%s': %s",
                                base_word,
                                exc,
                            )
                    if not definition and supplemental_entry:
                        definition = (
                            (supplemental_entry.get("d") or [""])[0]
                            if supplemental_entry.get("d")
                            else ""
                        )
                    if not pos and supplemental_entry:
                        pos = (
                            (supplemental_entry.get("p") or [""])[0]
                            if supplemental_entry.get("p")
                            else ""
                        )
                    results.append(
                        {
                            "word": base_word,
                            "definition": definition,
                            "pos": pos,
                        }
                    )
                    seen.add(base_word)
                    if len(results) >= AUTOCOMPLETE_LIMIT:
                        break
            except Exception as exc:
                logging.error(
                    "SQLite autocomplete query failed for '%s': %s",
                    query,
                    exc,
                )

    if not USE_SQLITE or len(results) < AUTOCOMPLETE_LIMIT:
        query_cf = query.casefold()
        for base_word, entry in iterate_dictionary_entries():
            if not entry or base_word in seen:
                continue
            if query_cf in base_word.casefold():
                results.append(
                    {
                        "word": base_word,
                        "definition": (entry.get("d") or [""])[0]
                        if entry.get("d")
                        else "",
                        "pos": (entry.get("p") or [""])[0] if entry.get("p") else "",
                    }
                )
                seen.add(base_word)
                if len(results) >= AUTOCOMPLETE_LIMIT:
                    break

    return jsonify({"results": results[:AUTOCOMPLETE_LIMIT]})


@app.route("/api/word/<word>", methods=["GET"])
def get_word_info(word: str):
    entry = get_entry_data(word)
    if not entry and USE_SQLITE:
        resolved = resolve_query_entries(word)
        if resolved:
            entry = get_entry_data(resolved[0][0])

    if not entry:
        return jsonify({"error": "Word not found"}), 404

    return jsonify(
        {
            "word": entry.get("", word),
            "definition": (entry.get("d") or [""])[0] if entry.get("d") else "",
            "pos": (entry.get("p") or [""])[0] if entry.get("p") else "",
            "forms_count": len(entry.get("f") or []),
            "syllable_count": len(entry.get("f_ipa") or []),
        }
    )


@app.route("/api/stats", methods=["GET"])
def get_stats():
    if USE_SQLITE:
        conn = get_db_connection()
        total = 0
        if conn:
            row = conn.execute("SELECT COUNT(*) AS count FROM entries").fetchone()
            if row:
                total = row["count"]
        return jsonify({"total_words": total})
    return jsonify({"total_words": len(dictionary)})


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        initialise_dictionary()
        print("Dictionary backend initialised.")
    except Exception as exc:
        print(f"Failed to initialise dictionary: {exc}")

    app.run(
        host=os.environ.get("FLASK_HOST", "127.0.0.1"),
        port=int(os.environ.get("FLASK_PORT", "5000")),
        debug=os.environ.get("FLASK_DEBUG", "False").lower() == "true",
    )
