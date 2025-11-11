"""
Test suite and examples for Armenian Rhyme Finder

Run this file to test the rhyme detection algorithm without needing the Flask server.
"""

import json
from typing import List, Dict
from app import (
    load_dictionary, extract_rhyme_tail, phone_distance,
    levenshtein_similarity, get_rhyme_label, find_rhymes
)


def test_rhyme_tail_extraction():
    """Test rhyme tail extraction"""
    print("\n" + "="*60)
    print("TEST: Rhyme Tail Extraction")
    print("="*60)
    
    test_cases = [
        (['b', 'i', 'kʰ', 'ə', 'v', 'a', 'r', 'k'], ['a', 'r', 'k']),
        (['g', 'ə', 'l', 'u', 'x'], ['u', 'x']),
        (['s', 'e', 'r'], ['e', 'r']),
        (['p', 'ə'], ['ə']),
    ]
    
    for phones, expected_tail in test_cases:
        result = extract_rhyme_tail(phones)
        status = "✓" if result == expected_tail else "✗"
        print(f"{status} Input: {' '.join(phones)}")
        print(f"  Expected tail: {' '.join(expected_tail)}")
        print(f"  Got tail:      {' '.join(result)}")


def test_phone_distance():
    """Test phone distance calculation"""
    print("\n" + "="*60)
    print("TEST: Phone Distance Calculation")
    print("="*60)
    
    test_cases = [
        ('a', 'a', 0.0, "Identical vowel"),
        ('a', 'e', 0.3, "Different vowels, similar height/backness"),
        ('p', 'p', 0.0, "Identical consonant"),
        ('p', 'b', 0.1, "Consonants: same place and manner"),
        ('p', 's', 0.4, "Consonants: different place and manner"),
        ('a', 'p', 1.0, "Vowel vs consonant"),
    ]
    
    for phone1, phone2, expected, description in test_cases:
        result = phone_distance(phone1, phone2)
        status = "✓" if abs(result - expected) < 0.05 else "✗"
        print(f"{status} {phone1} → {phone2}: {result:.2f} (expected {expected:.2f})")
        print(f"   {description}")


def test_similarity():
    """Test Levenshtein similarity"""
    print("\n" + "="*60)
    print("TEST: Levenshtein Similarity")
    print("="*60)
    
    test_cases = [
        (['a', 'r', 'k'], ['a', 'r', 'k'], 1.0, "Identical"),
        (['a', 'r', 'k'], ['a', 'r', 'k', 'i'], 0.75, "One insertion"),
        (['o', 'v'], ['o', 'v'], 1.0, "Identical"),
        (['u', 'x'], ['o', 'x'], 0.5, "Different vowel, same coda"),
    ]
    
    for tail1, tail2, expected, description in test_cases:
        result = levenshtein_similarity(tail1, tail2)
        status = "✓" if abs(result - expected) < 0.15 else "?"
        print(f"{status} {' '.join(tail1)} ↔ {' '.join(tail2)}: {result:.2f} (expected ≈{expected:.2f})")
        print(f"   {description}")


def test_rhyme_labels():
    """Test rhyme classification"""
    print("\n" + "="*60)
    print("TEST: Rhyme Classification")
    print("="*60)
    
    test_cases = [
        (['a', 'r', 'k'], ['a', 'r', 'k'], 1.0, "perfect"),
        (['e', 'r'], ['e', 'l'], 0.9, "near-perfect"),
        (['a', 'k'], ['a', 't'], 0.7, "assonance"),
        (['a', 'r', 'k'], ['o', 'r', 'k'], 0.67, "slant"),
    ]
    
    for tail1, tail2, sim, expected_label in test_cases:
        result = get_rhyme_label(tail1, tail2, sim)
        status = "✓" if result == expected_label else "✗"
        print(f"{status} {' '.join(tail1)} ↔ {' '.join(tail2)} (sim: {sim:.2f})")
        print(f"   Expected: {expected_label}, Got: {result}")


def demo_word_search():
    """Demonstrate searching for rhymes"""
    print("\n" + "="*60)
    print("DEMO: Word Search")
    print("="*60)
    
    # Example words to search for (if they exist in dictionary)
    test_words = ['գլուխ', 'լույս', 'սեր', 'բառ']
    
    for word in test_words:
        print(f"\nSearching rhymes for: {word}")
        rhymes = find_rhymes(word, limit=5)
        
        if rhymes:
            for i, rhyme in enumerate(rhymes, 1):
                print(f"  {i}. {rhyme['word']:<20} | {rhyme['label']:<12} | "
                      f"Similarity: {rhyme['similarity']} | {rhyme['definition']}")
        else:
            print(f"  No rhymes found (word may not exist in dictionary)")


def print_statistics():
    """Print dictionary statistics"""
    print("\n" + "="*60)
    print("DICTIONARY STATISTICS")
    print("="*60)
    print(f"Total words loaded: {len(dictionary)}")
    
    if dictionary:
        # Count words by part of speech
        pos_count = {}
        for entry in dictionary.values():
            pos = entry.get('p', ['unknown'])[0]
            pos_count[pos] = pos_count.get(pos, 0) + 1
        
        print("\nWords by part of speech:")
        for pos, count in sorted(pos_count.items(), key=lambda x: -x[1])[:10]:
            print(f"  {pos:<20} {count:>5}")


def example_api_usage():
    """Show how to use the API programmatically"""
    print("\n" + "="*60)
    print("EXAMPLE: Programmatic Usage")
    print("="*60)
    
    print("""
# Example 1: Find rhymes for a word
rhymes = find_rhymes('սեր', limit=10)
for rhyme in rhymes:
    print(f"{rhyme['word']}: {rhyme['label']} ({rhyme['similarity']})")

# Example 2: Analyze phonetic similarity
from app import extract_rhyme_tail, levenshtein_similarity

word1_ipa = 'g ə l u x'.split()
word2_ipa = 'k ə l u x'.split()

tail1 = extract_rhyme_tail(word1_ipa)
tail2 = extract_rhyme_tail(word2_ipa)

similarity = levenshtein_similarity(tail1, tail2)
print(f"Similarity: {similarity}")

# Example 3: Using with Flask API
import requests

response = requests.get('http://localhost:5000/api/rhymes', 
                       params={'word': 'սեր', 'limit': 25})
data = response.json()

for rhyme in data['rhymes']:
    print(f"{rhyme['word']}: {rhyme['label']}")
    """)


if __name__ == '__main__':
    print("\n" + "█"*60)
    print("█ Armenian Rhyme Finder - Test Suite")
    print("█"*60)
    
    # Load dictionary
    print("\nLoading dictionary...")
    try:
        load_dictionary('dictionary-hy.cleaned.jsonl')
        print(f"✓ Successfully loaded {len(dictionary)} words")
    except Exception as e:
        print(f"✗ Failed to load dictionary: {e}")
        exit(1)
    
    # Run tests
    test_rhyme_tail_extraction()
    test_phone_distance()
    test_similarity()
    test_rhyme_labels()
    
    # Print statistics
    print_statistics()
    
    # Demonstrate search
    demo_word_search()
    
    # Show example usage
    example_api_usage()
    
    print("\n" + "█"*60)
    print("█ Tests Complete!")
    print("█"*60)
    print("\nNext steps:")
    print("1. Run 'python app.py' to start the Flask backend")
    print("2. Open 'index.html' in your browser")
    print("3. Search for Armenian words to find rhymes!")
    print("\n")
