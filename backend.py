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


def extract_rhyme_tail(ipa_phones: List[str]) -> List[str]:
    """
    Extract rhyme tail: from last vowel to end (nucleus + coda).
    Returns phones from the last vowel onward.
    """
    if not ipa_phones:
        return []
    
    # Find the last vowel
    last_vowel_idx = -1
    for i in range(len(ipa_phones) - 1, -1, -1):
        if ipa_phones[i] in VOWELS:
            last_vowel_idx = i
            break
    
    if last_vowel_idx == -1:
        return ipa_phones  # No vowel found, return all
    
    return ipa_phones[last_vowel_idx:]


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


def levenshtein_similarity(tail1: List[str], tail2: List[str]) -> float:
    """
    Feature-aware Levenshtein distance with similarity scoring.
    Returns score from 0 to 1, where 1 is identical.
    """
    m, n = len(tail1), len(tail2)
    
    # DP table
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Initialize base cases
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    
    # Fill DP table with feature-aware costs
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if tail1[i-1] == tail2[j-1]:
                cost = 0
            else:
                cost = phone_distance(tail1[i-1], tail2[j-1])
            
            dp[i][j] = min(
                dp[i-1][j] + 1,      # deletion
                dp[i][j-1] + 1,      # insertion
                dp[i-1][j-1] + cost  # substitution
            )
    
    distance = dp[m][n]
    max_len = max(m, n)
    if max_len == 0:
        return 1.0
    
    similarity = 1.0 - (distance / max_len)
    return max(0.0, similarity)


def get_rhyme_label(tail1: List[str], tail2: List[str], similarity: float) -> str:
    """
    Classify rhyme type based on criteria.
    """
    if tail1 == tail2:
        return "perfect"
    
    # Extract nucleus (first vowel) from each tail
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
    
    if similarity >= 0.85 and same_nucleus:
        return "near-perfect"
    elif same_nucleus and similarity >= 0.6:
        return "assonance"
    elif similarity >= 0.5:
        return "slant"
    else:
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
    
    query_tail = extract_rhyme_tail(query_ipa)
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
                candidate_tail = extract_rhyme_tail(candidate_ipa)
                
                similarity = levenshtein_similarity(query_tail, candidate_tail)
                
                # Only include if there's some similarity
                if similarity < 0.3:
                    continue
                
                label = get_rhyme_label(query_tail, candidate_tail, similarity)
                
                # Skip "none" category
                if label == "none":
                    continue
                
                # Avoid duplicates
                key = (dict_word, display_word)
                if key in seen:
                    continue
                seen.add(key)
                
                rhyme_entry = {
                    'word': display_word,
                    'base_word': dict_word,
                    'similarity': round(similarity, 3),
                    'label': label,
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
                candidate_tail = extract_rhyme_tail(candidate_ipa)
                
                similarity = levenshtein_similarity(query_tail, candidate_tail)
                
                # Only include if there's some similarity
                if similarity < 0.3:
                    continue
                
                label = get_rhyme_label(query_tail, candidate_tail, similarity)
                
                # Skip "none" category
                if label == "none":
                    continue
                
                key = (dict_word, display_word)
                if key in seen:
                    continue
                seen.add(key)
                
                rhyme_entry = {
                    'word': display_word,
                    'base_word': dict_word,
                    'similarity': round(similarity, 3),
                    'label': label,
                    'definition': (entry.get('d') or [''])[0] if entry.get('d') else '',
                    'part_of_speech': (entry.get('p') or [''])[0] if entry.get('p') else '',
                    'is_base_form': True,
                }
                rhymes.append(rhyme_entry)
    
    # Sort by label priority and similarity
    label_priority = {"perfect": 0, "near-perfect": 1, "assonance": 2, "slant": 3}
    rhymes.sort(key=lambda x: (label_priority.get(x['label'], 4), -x['similarity']))
    
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
        load_dictionary('dictionary-hy.reordered.jsonl')
        print(f"Loaded {len(dictionary)} words from dictionary")
        print(f"Indexed {len(form_to_entries)} total forms/tenses")
    except Exception as e:
        print(f"Error loading dictionary: {e}")
    
    app.run(debug=True, port=5000)
