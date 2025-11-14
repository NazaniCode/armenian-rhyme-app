"""
Armenian Rhyme Finder - Backend
Implements phoneme-based rhyme detection with similarity scoring
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import re
from typing import List, Tuple, Dict
from collections import defaultdict

app = Flask(__name__)
CORS(app)

# Phoneme feature definitions
VOWELS = {'a', 'e', 'i', 'o', 'u', 'ə', 'ɑ', 'ɔ', 'ʌ', 'æ', 'iː', 'uː', 'oː', 'ɛ'}

# Consonant features: (place, manner)
CONSONANTS = {
    'p': ('labial', 'stop'), 'b': ('labial', 'stop'),
    't': ('alveolar', 'stop'), 'd': ('alveolar', 'stop'),
    'k': ('velar', 'stop'), 'g': ('velar', 'stop'), 'kʰ': ('velar', 'stop'),
    'f': ('labial', 'fricative'), 'v': ('labial', 'fricative'),
    's': ('alveolar', 'fricative'), 'z': ('alveolar', 'fricative'),
    'ʃ': ('palatal', 'fricative'), 'ʒ': ('palatal', 'fricative'),
    'x': ('velar', 'fricative'), 'ɣ': ('velar', 'fricative'),
    'θ': ('dental', 'fricative'), 'ð': ('dental', 'fricative'),
    'h': ('glottal', 'fricative'),
    'm': ('labial', 'nasal'), 'n': ('alveolar', 'nasal'), 'ŋ': ('velar', 'nasal'),
    'l': ('alveolar', 'approximant'), 'ɹ': ('alveolar', 'approximant'), 'r': ('alveolar', 'approximant'),
    'j': ('palatal', 'approximant'), 'w': ('labial', 'approximant'),
    'tsʰ': ('alveolar', 'stop'), 'tʃ': ('palatal', 'stop'),
}

# Vowel features: (height, backness)
VOWEL_FEATURES = {
    'i': ('close', 'front'), 'iː': ('close', 'front'),
    'e': ('close-mid', 'front'), 'ɛ': ('open-mid', 'front'),
    'æ': ('near-open', 'front'),
    'a': ('open', 'front'),
    'ə': ('open-mid', 'central'),
    'ʌ': ('open-mid', 'back'),
    'o': ('close-mid', 'back'), 'oː': ('close-mid', 'back'),
    'ɔ': ('open-mid', 'back'),
    'u': ('close', 'back'), 'uː': ('close', 'back'),
    'ɑ': ('open', 'back'),
}

# Global dictionaries
dictionary = {}  # Main dictionary: base_word -> entry
form_to_entries = {}  # Maps any form to list of (base_word, form_index)


def load_dictionary(filepath: str):
    """Load JSONL dictionary into memory"""
    global dictionary, form_to_entries
    dictionary = {}
    form_to_entries = {}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            entry = json.loads(line.strip())
            word = entry.get('', '')
            if word:
                dictionary[word] = entry
                
                # Map all forms to this entry
                forms = entry.get('f', [])
                forms_ipa = entry.get('f_ipa', [])
                
                if forms and isinstance(forms, list):
                    for idx, form in enumerate(forms):
                        if form not in form_to_entries:
                            form_to_entries[form] = []
                        form_to_entries[form].append((word, idx))


def split_into_syllables(ipa_phones: List[str]) -> List[List[str]]:
    """
    Split IPA phones into syllables.
    Each syllable has: (optional onset consonants) + vowel + (optional coda consonants)
    """
    if not ipa_phones:
        return []
    
    syllables = []
    current_syllable = []
    
    for phone in ipa_phones:
        current_syllable.append(phone)
        
        # If we hit a vowel, we might be in the middle of a syllable
        # Continue until we hit another vowel or run out of phones
        if phone in VOWELS:
            # Collect consonants after this vowel (coda)
            continue
    
    # Group phones into syllables by finding vowels
    syllables = []
    i = 0
    while i < len(ipa_phones):
        syllable = []
        
        # Collect onset consonants
        while i < len(ipa_phones) and ipa_phones[i] not in VOWELS:
            syllable.append(ipa_phones[i])
            i += 1
        
        # Collect vowel (nucleus)
        if i < len(ipa_phones) and ipa_phones[i] in VOWELS:
            syllable.append(ipa_phones[i])
            i += 1
        
        # Collect coda consonants (until next vowel or end)
        while i < len(ipa_phones) and ipa_phones[i] not in VOWELS:
            # Check if this consonant should start the next syllable
            # If there are multiple consonants, split them between syllables
            if i + 1 < len(ipa_phones) and ipa_phones[i + 1] in VOWELS:
                # Next is a vowel, so this consonant starts the next syllable
                break
            syllable.append(ipa_phones[i])
            i += 1
        
        if syllable:
            syllables.append(syllable)
    
    return syllables


def extract_rhyme_tail(ipa_phones: List[str]) -> List[str]:
    """
    Extract rhyme tail: the last syllable (onset + nucleus + coda).
    """
    syllables = split_into_syllables(ipa_phones)
    if syllables:
        return syllables[-1]
    return ipa_phones


def phone_distance(phone1: str, phone2: str) -> float:
    """
    Calculate distance between two phones.
    Returns 0 for identical, < 1 for similar, 1 for different.
    """
    if phone1 == phone2:
        return 0.0
    
    # Check if both are vowels
    if phone1 in VOWELS and phone2 in VOWELS:
        f1 = VOWEL_FEATURES.get(phone1)
        f2 = VOWEL_FEATURES.get(phone2)
        if f1 and f2:
            # Check height and backness similarity
            height_match = f1[0] == f2[0]
            backness_match = f1[1] == f2[1]
            if height_match or backness_match:
                return 0.3
        return 0.7
    
    # Check if both are consonants
    if phone1 in CONSONANTS and phone2 in CONSONANTS:
        c1 = CONSONANTS[phone1]
        c2 = CONSONANTS[phone2]
        place_match = c1[0] == c2[0]
        manner_match = c1[1] == c2[1]
        if place_match and manner_match:
            return 0.1
        elif place_match or manner_match:
            return 0.4
        return 0.8
    
    # Different types (vowel vs consonant)
    return 1.0


def levenshtein_similarity(tail1: List[str], tail2: List[str], is_last_syllable: bool = False) -> float:
    """
    Vowel-weighted Levenshtein distance with similarity scoring.
    Vowels are weighted more heavily than consonants for rhyme matching.
    Returns score from 0 to 1, where 1 is identical.
    
    Args:
        tail1: First phoneme sequence
        tail2: Second phoneme sequence
        is_last_syllable: If True, gives extra weight to vowels (nucleus)
    """
    m, n = len(tail1), len(tail2)
    
    if m == 0 and n == 0:
        return 1.0
    if m == 0 or n == 0:
        return 0.0
    
    # Find the vowel (nucleus) positions - most important for rhyming
    vowel_pos1 = -1
    vowel_pos2 = -1
    for i, phone in enumerate(tail1):
        if phone in VOWELS:
            vowel_pos1 = i
            break  # Take first vowel (nucleus)
    for i, phone in enumerate(tail2):
        if phone in VOWELS:
            vowel_pos2 = i
            break
    
    # DP table with weighted costs
    dp = [[0.0] * (n + 1) for _ in range(m + 1)]
    
    # Initialize base cases with weighted costs
    for i in range(1, m + 1):
        weight = 1.5 if tail1[i-1] in VOWELS else 1.0
        dp[i][0] = dp[i-1][0] + weight
    for j in range(1, n + 1):
        weight = 1.5 if tail2[j-1] in VOWELS else 1.0
        dp[0][j] = dp[0][j-1] + weight
    
    # Fill DP table with vowel-weighted costs
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            phone1 = tail1[i-1]
            phone2 = tail2[j-1]
            
            # Weight calculation: vowels are more important than consonants
            is_vowel1 = phone1 in VOWELS
            is_vowel2 = phone2 in VOWELS
            
            # Base weight: 1.5 for vowels, 1.0 for consonants
            base_weight = 1.5 if (is_vowel1 or is_vowel2) else 1.0
            
            # Extra weight if this is the nucleus (primary vowel) of last syllable
            if is_last_syllable and ((i-1 == vowel_pos1) or (j-1 == vowel_pos2)):
                base_weight *= 1.3  # 30% more weight for nucleus vowel
            
            if phone1 == phone2:
                cost = 0
            else:
                # Use phone_distance but weight vowel mismatches more heavily
                base_distance = phone_distance(phone1, phone2)
                cost = base_distance * base_weight
            
            dp[i][j] = min(
                dp[i-1][j] + base_weight,      # deletion
                dp[i][j-1] + base_weight,      # insertion
                dp[i-1][j-1] + cost             # substitution
            )
    
    distance = dp[m][n]
    
    # Calculate max possible distance with weights
    max_distance = 0.0
    for i in range(max(m, n)):
        if i < m:
            weight = 1.5 if tail1[i] in VOWELS else 1.0
            if is_last_syllable and i == vowel_pos1:
                weight *= 1.3
            max_distance += weight
        if i < n:
            weight = 1.5 if tail2[i] in VOWELS else 1.0
            if is_last_syllable and i == vowel_pos2:
                weight *= 1.3
            max_distance += weight
    max_distance /= 2.0  # Average of the two
    
    if max_distance == 0:
        return 1.0
    
    similarity = 1.0 - (distance / max_distance)
    return max(0.0, min(1.0, similarity))


def calculate_multi_syllable_rhyme_score(ipa1: List[str], ipa2: List[str]) -> Dict:
    """
    Calculate comprehensive rhyme score considering all syllables.
    Returns a dict with:
    - final_score: overall rhyme quality (0-1)
    - label: rhyme classification
    - syllables_matched: number of syllables that rhyme
    - last_syllable_similarity: similarity of the last syllable specifically
    """
    syllables1 = split_into_syllables(ipa1)
    syllables2 = split_into_syllables(ipa2)
    
    if not syllables1 or not syllables2:
        return {
            'final_score': 0.0,
            'label': 'none',
            'syllables_matched': 0,
            'last_syllable_similarity': 0.0
        }
    
    # Calculate last syllable similarity (most important)
    # Use vowel weighting for last syllable - vowels matter more for rhyming!
    last_syl1 = syllables1[-1]
    last_syl2 = syllables2[-1]
    last_syllable_sim = levenshtein_similarity(last_syl1, last_syl2, is_last_syllable=True)
    
    # Check if last syllables are identical
    last_syllables_identical = last_syl1 == last_syl2
    
    # Count consecutive matching syllables from the end
    # The last syllable always "participates" if there's any rhyme at all
    syllables_matched = 0
    min_syllables = min(len(syllables1), len(syllables2))
    
    # First, count the last syllable if it has decent similarity
    if last_syllable_sim >= 0.5:
        syllables_matched = 1
    
    # Then check previous syllables (only if last syllable is near-perfect)
    # IMPORTANT: Only give multi-syllable bonus if the last syllable is very high quality
    # This prevents inflating mediocre rhymes to perfect scores
    if syllables_matched > 0 and last_syllable_sim >= 0.90:
        for i in range(2, min_syllables + 1):
            syl1 = syllables1[-i]
            syl2 = syllables2[-i]
            
            if syl1 == syl2:
                # Identical syllables count
                syllables_matched += 1
            else:
                sim = levenshtein_similarity(syl1, syl2, is_last_syllable=False)
                # For additional syllables, require very high similarity (90%+)
                # This ensures we only give bonus for true multi-syllable rhymes
                if sim >= 0.90:
                    syllables_matched += 1
                else:
                    # Stop - this syllable doesn't match well enough
                    break
    
    # Calculate bonus for multi-syllable rhymes
    # Only give bonus if we have MORE than just the last syllable matching
    # AND the last syllable itself is very high quality (checked above)
    multi_syllable_bonus = 0.0
    if syllables_matched > 1:
        # Bonus: 0.08 for each additional matching syllable beyond the first
        # Conservative bonus to prevent over-inflation
        multi_syllable_bonus = 0.08 * (syllables_matched - 1)
    
    # Base score on last syllable similarity
    base_score = last_syllable_sim
    
    # Add multi-syllable bonus (but cap at 1.0)
    final_score = min(1.0, base_score + multi_syllable_bonus)
    
    # Determine label based on last syllable matching
    label = get_rhyme_label_from_score(
        last_syl1, last_syl2, last_syllable_sim, 
        last_syllables_identical, syllables_matched
    )
    
    return {
        'final_score': final_score,
        'label': label,
        'syllables_matched': syllables_matched,
        'last_syllable_similarity': last_syllable_sim
    }


def get_rhyme_label_from_score(tail1: List[str], tail2: List[str], 
                                 similarity: float, identical: bool,
                                 syllables_matched: int) -> str:
    """
    Classify rhyme type based on criteria.
    Perfect: Only for truly exceptional rhymes (99%+ or identical)
    Near-perfect: 90%+ similarity
    Assonance: Same vowel sound, 70%+
    Slant: 50%+
    """
    if identical:
        return "perfect"
    
    # Extract nucleus (vowel) from each tail
    nucleus1 = None
    nucleus2 = None
    for phone in tail1:
        if phone in VOWELS:
            nucleus1 = phone
            break
    for phone in tail2:
        if phone in VOWELS:
            nucleus2 = phone
            break
    
    same_nucleus = nucleus1 == nucleus2
    
    # Perfect: Only for truly exceptional rhymes
    # Multi-syllable rhymes with very high similarity (99%+)
    if syllables_matched >= 2 and similarity >= 0.99:
        return "perfect"
    
    # Near-perfect: High quality rhymes
    if syllables_matched >= 2 and similarity >= 0.90:
        return "near-perfect"
    elif similarity >= 0.93 and same_nucleus:
        return "near-perfect"
    
    # Assonance: Same vowel, decent similarity
    if same_nucleus and similarity >= 0.70:
        return "assonance"
    
    # Slant: Moderate similarity
    if similarity >= 0.50:
        return "slant"
    
    return "none"


def find_rhymes(input_word: str, limit: int = 50, include_tenses: bool = False) -> List[Dict]:
    """
    Find rhyming words for the given Armenian word or form.
    - If include_tenses=False: return only base words (first form of each entry)
    - If include_tenses=True: return all forms/tenses of all matching entries
    
    Returns sorted list of rhymes with scores and labels.
    """
    input_word = input_word.strip()
    
    # Find which dictionary entries match the input (could be base word or a form)
    query_entries = []
    
    if input_word in dictionary:
        # Direct match - it's a base word
        query_entries = [(input_word, 0)]  # (base_word, form_index)
    elif input_word in form_to_entries:
        # It's a form of some word(s)
        query_entries = form_to_entries[input_word]
    else:
        # No match
        return []
    
    # Get IPA for the query word (use first form if it's a base word, or the matched form)
    query_ipa = None
    for base_word, form_idx in query_entries:
        entry = dictionary[base_word]
        forms_ipa = entry.get('f_ipa', [])
        if forms_ipa and form_idx < len(forms_ipa):
            query_ipa = forms_ipa[form_idx].split()
            break
    
    if not query_ipa:
        return []
    
    rhymes = []
    seen = set()  # Track (base_word, display_word) to avoid duplicates
    
    # Search through all words
    for dict_word, entry in dictionary.items():
        # Skip the query word itself
        if dict_word == input_word:
            continue
        
        forms = entry.get('f', [])
        forms_ipa = entry.get('f_ipa', [])
        
        if not forms or not forms_ipa or len(forms) != len(forms_ipa):
            continue
        
        if include_tenses:
            # Check all forms/tenses
            for idx in range(len(forms)):
                display_word = forms[idx]
                ipa_str = forms_ipa[idx]
                
                candidate_ipa = ipa_str.split()
                
                # Use multi-syllable scoring
                rhyme_result = calculate_multi_syllable_rhyme_score(query_ipa, candidate_ipa)
                
                # Only include if there's some similarity
                if rhyme_result['final_score'] < 0.3:
                    continue
                
                # Skip "none" category
                if rhyme_result['label'] == "none":
                    continue
                
                # Avoid duplicates
                key = (dict_word, display_word)
                if key in seen:
                    continue
                seen.add(key)
                
                rhyme_entry = {
                    'word': display_word,
                    'base_word': dict_word,
                    'similarity': round(rhyme_result['final_score'], 3),
                    'label': rhyme_result['label'],
                    'syllables_matched': rhyme_result['syllables_matched'],
                    'definition': (entry.get('d') or [''])[0] if entry.get('d') else '',
                    'part_of_speech': (entry.get('p') or [''])[0] if entry.get('p') else '',
                    'is_base_form': (idx == 0),
                }
                rhymes.append(rhyme_entry)
        else:
            # Check only first form (base word)
            if forms and forms_ipa:
                display_word = forms[0]
                ipa_str = forms_ipa[0]
                
                candidate_ipa = ipa_str.split()
                
                # Use multi-syllable scoring
                rhyme_result = calculate_multi_syllable_rhyme_score(query_ipa, candidate_ipa)
                
                # Only include if there's some similarity
                if rhyme_result['final_score'] < 0.3:
                    continue
                
                # Skip "none" category
                if rhyme_result['label'] == "none":
                    continue
                
                key = (dict_word, display_word)
                if key in seen:
                    continue
                seen.add(key)
                
                rhyme_entry = {
                    'word': display_word,
                    'base_word': dict_word,
                    'similarity': round(rhyme_result['final_score'], 3),
                    'label': rhyme_result['label'],
                    'syllables_matched': rhyme_result['syllables_matched'],
                    'definition': (entry.get('d') or [''])[0] if entry.get('d') else '',
                    'part_of_speech': (entry.get('p') or [''])[0] if entry.get('p') else '',
                    'is_base_form': True,
                }
                rhymes.append(rhyme_entry)
    
    # Sort primarily by similarity score, then by label as tiebreaker
    # This ensures that a 95% match ranks higher than an 80% match,
    # regardless of their label categories
    label_priority = {"perfect": 0, "near-perfect": 1, "assonance": 2, "slant": 3}
    rhymes.sort(key=lambda x: (-x['similarity'], label_priority.get(x['label'], 4)))
    
    return rhymes[:limit]


@app.route('/api/rhymes', methods=['GET'])
def get_rhymes():
    """API endpoint to get rhymes for a word"""
    word = request.args.get('word', '').strip()
    limit = request.args.get('limit', 50, type=int)
    include_tenses = request.args.get('include_tenses', 'false').lower() == 'true'
    
    if not word:
        return jsonify({'error': 'Word parameter required'}), 400
    
    rhymes = find_rhymes(word, limit, include_tenses)
    return jsonify({'word': word, 'rhymes': rhymes, 'include_tenses': include_tenses})


@app.route('/api/search', methods=['GET'])
def search():
    """API endpoint to search for words"""
    query = request.args.get('q', '').strip().lower()
    
    if not query:
        return jsonify({'results': []})
    
    results = []
    for word in dictionary.keys():
        if query in word.lower():
            results.append({
                'word': word,
                'definition': dictionary[word].get('d', [''])[0],
                'pos': dictionary[word].get('p', [''])[0],
            })
            if len(results) >= 20:
                break
    
    return jsonify({'results': results})


@app.route('/api/word/<word>', methods=['GET'])
def get_word_info(word):
    """Get detailed info about a word"""
    if word not in dictionary:
        return jsonify({'error': 'Word not found'}), 404
    
    entry = dictionary[word]
    return jsonify({
        'word': word,
        'definition': entry.get('d', [''])[0],
        'pos': entry.get('p', [''])[0],
        'forms_count': len(entry.get('f', [])),
    })


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get dictionary statistics"""
    return jsonify({
        'total_words': len(dictionary),
    })


if __name__ == '__main__':
    # Load dictionary
    try:
        load_dictionary('dictionary-hy-improved.jsonl')
        print(f"Loaded {len(dictionary)} words from dictionary")
        print(f"Indexed {len(form_to_entries)} total forms/tenses")
    except Exception as e:
        print(f"Error loading dictionary: {e}")
    
    app.run(debug=True, port=5000)
