"""
Armenian Rhyme Finder - Enhanced Backend with Configuration
Implements phoneme-based rhyme detection with similarity scoring
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import logging
from typing import List, Tuple, Dict
from config import (
    FLASK_HOST, FLASK_PORT, FLASK_DEBUG, DICTIONARY_FILE,
    RHYME_THRESHOLDS, AUTOCOMPLETE_LIMIT, DEFAULT_RESULT_LIMIT, MAX_RESULT_LIMIT,
    CONSONANTS, VOWEL_FEATURES, VOWELS, PHONE_DISTANCE_COSTS,
    LOG_LEVEL, LOG_FILE
)

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global dictionary
dictionary = {}


def load_dictionary(filepath: str):
    """Load JSONL dictionary into memory"""
    global dictionary
    dictionary = {}
    logger.info(f"Loading dictionary from {filepath}")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line.strip())
                    word = entry.get('', '')
                    if word:
                        dictionary[word] = entry
        logger.info(f"Successfully loaded {len(dictionary)} words")
    except Exception as e:
        logger.error(f"Error loading dictionary: {e}")
        raise


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
        return PHONE_DISTANCE_COSTS['identical']
    
    # Check if both are vowels
    if phone1 in VOWELS and phone2 in VOWELS:
        f1 = VOWEL_FEATURES.get(phone1)
        f2 = VOWEL_FEATURES.get(phone2)
        if f1 and f2:
            # Check height and backness similarity
            height_match = f1[0] == f2[0]
            backness_match = f1[1] == f2[1]
            if height_match or backness_match:
                return PHONE_DISTANCE_COSTS['same_vowel_feature']
        return PHONE_DISTANCE_COSTS['substitution_unrelated']
    
    # Check if both are consonants
    if phone1 in CONSONANTS and phone2 in CONSONANTS:
        c1 = CONSONANTS[phone1]
        c2 = CONSONANTS[phone2]
        place_match = c1[0] == c2[0]
        manner_match = c1[1] == c2[1]
        if place_match and manner_match:
            return 0.1
        elif place_match or manner_match:
            return PHONE_DISTANCE_COSTS['same_consonant_feature']
        return PHONE_DISTANCE_COSTS['substitution_unrelated']
    
    # Different types (vowel vs consonant)
    return PHONE_DISTANCE_COSTS['substitution_unrelated']


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
                dp[i-1][j] + PHONE_DISTANCE_COSTS['insertion_deletion'],
                dp[i][j-1] + PHONE_DISTANCE_COSTS['insertion_deletion'],
                dp[i-1][j-1] + cost
            )
    
    distance = dp[m][n]
    max_len = max(m, n)
    if max_len == 0:
        return 1.0
    
    similarity = 1.0 - (distance / max_len)
    return max(0.0, min(1.0, similarity))


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
    
    if similarity >= RHYME_THRESHOLDS['near_perfect'] and same_nucleus:
        return "near-perfect"
    elif same_nucleus and similarity >= RHYME_THRESHOLDS['assonance']:
        return "assonance"
    elif similarity >= RHYME_THRESHOLDS['slant']:
        return "slant"
    else:
        return "none"


def find_rhymes(word: str, limit: int = DEFAULT_RESULT_LIMIT) -> List[Dict]:
    """
    Find rhyming words for the given Armenian word.
    Returns sorted list of rhymes with scores and labels.
    """
    word = word.strip()
    
    # Validate word
    if word not in dictionary:
        logger.warning(f"Word not found: {word}")
        return []
    
    # Get IPA forms of query word
    query_forms = dictionary[word].get('f_ipa', [])
    if not query_forms:
        logger.warning(f"No IPA forms found for: {word}")
        return []
    
    # Take first form as reference
    query_ipa = query_forms[0].split()
    query_tail = extract_rhyme_tail(query_ipa)
    
    rhymes = []
    
    # Search through all words
    for dict_word, entry in dictionary.items():
        if dict_word == word:
            continue
        
        forms_ipa = entry.get('f_ipa', [])
        if not forms_ipa:
            continue
        
        # Check first form
        candidate_ipa = forms_ipa[0].split()
        candidate_tail = extract_rhyme_tail(candidate_ipa)
        
        similarity = levenshtein_similarity(query_tail, candidate_tail)
        
        # Only include if there's some similarity
        if similarity < RHYME_THRESHOLDS['minimum']:
            continue
        
        label = get_rhyme_label(query_tail, candidate_tail, similarity)
        
        # Skip "none" category
        if label == "none":
            continue
        
        rhyme_entry = {
            'word': dict_word,
            'similarity': round(similarity, 3),
            'label': label,
            'definition': entry.get('d', [''])[0],
            'part_of_speech': entry.get('p', [''])[0],
        }
        rhymes.append(rhyme_entry)
    
    # Sort by label priority and similarity
    label_priority = {"perfect": 0, "near-perfect": 1, "assonance": 2, "slant": 3}
    rhymes.sort(key=lambda x: (label_priority.get(x['label'], 4), -x['similarity']))
    
    # Enforce result limit
    limit = min(limit, MAX_RESULT_LIMIT)
    logger.info(f"Found {len(rhymes)} rhymes for '{word}', returning {limit}")
    
    return rhymes[:limit]


# ==================== API ENDPOINTS ====================

@app.route('/api/rhymes', methods=['GET'])
def get_rhymes():
    """API endpoint to get rhymes for a word"""
    word = request.args.get('word', '').strip()
    limit = request.args.get('limit', DEFAULT_RESULT_LIMIT, type=int)
    
    if not word:
        return jsonify({'error': 'Word parameter required'}), 400
    
    try:
        rhymes = find_rhymes(word, limit)
        return jsonify({'word': word, 'rhymes': rhymes})
    except Exception as e:
        logger.error(f"Error in /api/rhymes: {e}")
        return jsonify({'error': str(e)}), 500


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
            if len(results) >= AUTOCOMPLETE_LIMIT:
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


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'words_loaded': len(dictionary),
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    try:
        load_dictionary(DICTIONARY_FILE)
        logger.info(f"Starting Flask app on {FLASK_HOST}:{FLASK_PORT}")
        app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
    except FileNotFoundError:
        logger.error(f"Dictionary file not found: {DICTIONARY_FILE}")
        exit(1)
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        exit(1)
