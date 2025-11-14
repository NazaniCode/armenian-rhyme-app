# insert_schwa_rules.py — Armenian epenthetic /ə/ fixer (refined)
# Usage:
#   python insert_schwa_rules.py IN.jsonl OUT.jsonl
#
# Edits (when present):
#   - "ipa": a space-separated phone string
#   - "f_ipa": list of space-separated phone strings
#
# Rules (priority):
#  A) Word-initial CC → insert after C1 unless onset is allowed (ALLOWED_ONSETS).
#  B) After a vowel (V …):
#     B1) V C r AFFRICATE n V → insert between C and r
#     B1b) V [.] AFFRICATE r V → insert between AFFRICATE and r
#     B2) V C AFFRICATE n V   → insert between AFFRICATE and n
#     B3) V C C V             → insert between C1–C2 unless onset is allowed
#     B4) V C1 C2 C3 V (triple) → avoid a 3-consonant onset:
#         • if C2C3 is an allowed onset → break C1|C2
#         • elif C1C2 is an allowed onset → break C2|C3
#         • else → break C1|C2
#  C) FINAL -դ/-ս: if the word ends with C d / C s, insert ə before d/s.
#
# Notes: Extend symbol sets below if your pipeline emits more phones.

import sys, json

# --- IPA sets ---
VOWELS = {"a","ɑ","æ","e","ɛ","ə","i","ɪ","o","ɔ","u","ʊ","y","ʏ","ø","œ","ɨ","ɯ"}

# Liquids/glides that are onset-friendly — don't insert before these.
LIQUIDS_GLIDES = {"r","ɾ","ɹ","l","j","w"}

# Sonorants for the "sonorant + obstruent" legal split.
SONORANTS = {"m","n","ŋ","l","ɾ","r","ʀ","ɹ","j","w"}

# Obstruents (add as needed).
OBSTRUENTS = {
    "p","b","pʰ","pʼ","t","d","tʰ","tʼ","k","g","kʰ","kʼ","q","qʰ","qʼ",
    "s","z","ʃ","ʒ","x","χ","h","ɣ","ʁ","f","v",
    "ts","tsʰ","t͡s","t͡sʰ","dz","d͡z","tʃ","tʃʰ","t͡ʃ","dʒ","d͡ʒ"
}

# Affricates treated as single units in special patterns.
AFFRICATES = {"tsʰ","t͡sʰ","ts","t͡s","tʃ","tʃʰ","t͡ʃ","dz","d͡z","dʒ","d͡ʒ"}

# Onsets explicitly allowed (word-start or post-vowel).
# Added χ t / χ tʰ; kept earlier exceptions and stop+v clusters.
ALLOWED_ONSETS = {
    "s k","s p","s t","s tʰ","s pʰ","z b","z ɡ","ʃ t","ʃ χ",
    "p v","b v","t v","d v","tʰ v","k v","g v",
    "χ t","χ tʰ"
}

def is_vowel(ph): return ph in VOWELS
def is_cons(ph):  return not is_vowel(ph)

def insert_between(phones, idx):
    """Insert 'ə' between phones[idx] and phones[idx+1]."""
    return phones[:idx+1] + ["ə"] + phones[idx+1:]

def onset_allowed(c1, c2):
    """Is C1 C2 a permissible onset (so we avoid inserting before C2)?"""
    pair = f"{c1} {c2}"
    if pair in ALLOWED_ONSETS:
        return True
    if c2 in LIQUIDS_GLIDES:
        return True
    if c1 in SONORANTS and c2 in OBSTRUENTS:
        return True
    return False

def process_ipa(ipa_sp: str) -> str:
    p = [x for x in ipa_sp.split() if x]
    n = len(p)
    if n < 2:
        return ipa_sp

    # A) Word-initial CC
    if is_cons(p[0]) and is_cons(p[1]) and not onset_allowed(p[0], p[1]):
        p = insert_between(p, 0)
        n = len(p)

    # B) After a vowel
    i = 0
    while i < n - 1:
        if not is_vowel(p[i]):
            i += 1
            continue

        has1 = (i+1 < n)
        has2 = (i+2 < n)
        has3 = (i+3 < n)
        has4 = (i+4 < n)
        has5 = (i+5 < n)

        # B1) V C r AFFRICATE n V → C|r
        if has5:
            c1, c2, c3, c4, nxt = p[i+1], p[i+2], p[i+3], p[i+4], p[i+5]
            if is_cons(c1) and c2 in {"r","ɾ","ɹ","l"} and c3 in AFFRICATES and c4 == "n" and is_vowel(nxt):
                p = insert_between(p, i+1)
                n = len(p)
                i += 2
                continue

        # B1b) V . AFFRICATE r V → AFFRICATE|r
        if has3 and has4:
            prev, c2, c3, nxt = p[i+1], p[i+2], p[i+3], p[i+4]
            if (c2 in AFFRICATES) and (c3 in {"r","ɾ","ɹ","l"}) and is_vowel(nxt):
                p = insert_between(p, i+2)
                n = len(p)
                i += 3
                continue

        # B2) V C AFFRICATE n V → AFFRICATE|n
        if has4:
            c1, c2, c3, nxt = p[i+1], p[i+2], p[i+3], p[i+4]
            if is_cons(c1) and (c2 in AFFRICATES) and c3 == "n" and is_vowel(nxt):
                p = insert_between(p, i+2)
                n = len(p)
                i += 3
                continue

        # B4) V C1 C2 C3 V (triple) — avoid triple onset
        if has4:
            c1, c2, c3, nxt = p[i+1], p[i+2], p[i+3], p[i+4]
            if is_cons(c1) and is_cons(c2) and is_cons(c3) and is_vowel(nxt):
                if onset_allowed(c2, c3):
                    # keep C2C3 as onset → break C1|C2
                    p = insert_between(p, i+1)
                    n = len(p)
                    i += 2
                    continue
                elif onset_allowed(c1, c2):
                    # keep C1C2 as onset → break C2|C3
                    p = insert_between(p, i+2)
                    n = len(p)
                    i += 3
                    continue
                else:
                    # neither side is good → default to C1|C2
                    p = insert_between(p, i+1)
                    n = len(p)
                    i += 2
                    continue

        # B3) Generic V C C V
        if has3 and is_cons(p[i+1]) and is_cons(p[i+2]) and is_vowel(p[i+3]):
            c1, c2 = p[i+1], p[i+2]
            if not onset_allowed(c1, c2):
                p = insert_between(p, i+1)
                n = len(p)
                i += 2
                continue

        i += 1

    # C) FINAL -դ/-ս
    n = len(p)
    if n >= 2 and is_cons(p[-2]) and p[-1] in {"d","s"}:
        p = insert_between(p, n-2)

    return " ".join(p)

def fix_object(obj: dict) -> dict:
    if isinstance(obj.get("ipa"), str):
        obj["ipa"] = process_ipa(obj["ipa"])
    fipa = obj.get("f_ipa")
    if isinstance(fipa, list):
        obj["f_ipa"] = [process_ipa(s) if isinstance(s, str) else s for s in fipa]
    return obj

def main():
    if len(sys.argv) < 3:
        print("usage: python insert_schwa_rules.py IN.jsonl OUT.jsonl", file=sys.stderr)
        sys.exit(1)
    inf, outf = sys.argv[1], sys.argv[2]
    with open(inf, "r", encoding="utf-8") as fin, open(outf, "w", encoding="utf-8") as fout:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                fout.write(line + "\n")
                continue
            obj = fix_object(obj)
            fout.write(json.dumps(obj, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    main()
