"""
Configuration for Armenian Rhyme Finder Application

Adjust these settings to customize the behavior of the rhyme finder.
"""

# Flask Configuration
FLASK_HOST = '127.0.0.1'
FLASK_PORT = 5000
FLASK_DEBUG = True

# Dictionary Configuration
DICTIONARY_FILE = 'dictionary-hy-improved.jsonl'

# Rhyme Detection Thresholds
RHYME_THRESHOLDS = {
    'perfect': 1.0,           # Identical rhyme
    'near_perfect': 0.85,     # Very similar with same nucleus
    'assonance': 0.6,         # Same nucleus with good similarity
    'slant': 0.5,             # Consonant-driven similarity
    'minimum': 0.3,           # Minimum to include in results (filters out 'none')
}

# Search Configuration
AUTOCOMPLETE_LIMIT = 20       # Max autocomplete suggestions
DEFAULT_RESULT_LIMIT = 25     # Default number of results per search
MAX_RESULT_LIMIT = 200        # Maximum results per search

# Phoneme Feature Definitions
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

# All vowels
VOWELS = set(VOWEL_FEATURES.keys())

# Distance costs for phoneme similarity
PHONE_DISTANCE_COSTS = {
    'identical': 0.0,              # Same phone
    'same_vowel_feature': 0.3,    # Vowels with same height or backness
    'same_consonant_feature': 0.4, # Consonants with same place or manner
    'insertion_deletion': 1.0,     # Add or remove a phone
    'substitution_unrelated': 1.0, # Completely different phone
}

# UI Configuration (for future frontend customization)
UI_CONFIG = {
    'theme': 'dark',                # 'light' or 'dark'
    'results_per_page': 25,
    'show_definitions': True,
    'show_pos': True,
    'show_similarity_score': True,
}

# Logging
LOG_LEVEL = 'INFO'              # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = 'rhyme_finder.log'
