"""
Test Syllabification Tool
Run this to see how words are split into syllables by the rhyme algorithm.
"""

import backend
from backend import split_into_syllables, load_dictionary
import sys

def syllabify_word(word):
    """Look up a word and show its syllabification"""
    # Try to find the word in the dictionary
    entry = backend.dictionary.get(word)
    
    if entry:
        # Found as base word
        forms = entry.get('f', [])
        forms_ipa = entry.get('f_ipa', [])
        
        if forms and forms_ipa:
            print(f"\n{'='*70}")
            print(f"Word: {word}")
            print(f"{'='*70}")
            
            # Show base form (first form)
            base_form = forms[0]
            base_ipa = forms_ipa[0]
            ipa_phones = base_ipa.split()
            syllables = split_into_syllables(ipa_phones)
            
            print(f"\nBase Form: {base_form}")
            print(f"IPA: {base_ipa}")
            print(f"IPA Phones: {ipa_phones}")
            print(f"Syllables: {syllables}")
            print(f"Syllables (formatted): {' - '.join([' '.join(syl) for syl in syllables])}")
            print(f"Syllable Count: {len(syllables)}")
            
            # Show last syllable details
            if syllables:
                last_syl = syllables[-1]
                print(f"\nLast Syllable: {' '.join(last_syl)}")
                
                # Identify nucleus (vowel) in last syllable
                vowels = {'a', 'e', 'i', 'o', 'u', 'ə', 'ɑ', 'ɔ', 'ʌ', 'æ', 'iː', 'uː', 'oː', 'ɛ'}
                nucleus = None
                for phone in last_syl:
                    if phone in vowels:
                        nucleus = phone
                        break
                
                if nucleus:
                    print(f"Last Syllable Nucleus (vowel): {nucleus}")
            
            # Show other forms if they exist
            if len(forms) > 1:
                print(f"\n{'─'*70}")
                print(f"Other Forms:")
                print(f"{'─'*70}")
                for i in range(1, min(len(forms), 5)):  # Show up to 5 forms
                    form = forms[i]
                    ipa = forms_ipa[i] if i < len(forms_ipa) else "N/A"
                    if ipa != "N/A":
                        ipa_phones = ipa.split()
                        syllables = split_into_syllables(ipa_phones)
                        print(f"\n  Form: {form}")
                        print(f"  IPA: {ipa}")
                        print(f"  Syllables: {' - '.join([' '.join(syl) for syl in syllables])}")
            
            print(f"\n{'='*70}\n")
            return True
    
    # Not found in dictionary
    print(f"\n❌ Word '{word}' not found in dictionary.")
    print("Make sure you're using Armenian script.")
    return False


def main():
    """Main function to run syllabification tests"""
    # Load dictionary
    print("Loading dictionary...")
    load_dictionary('dictionary-hy-improved.jsonl')
    print(f"✓ Loaded {len(backend.dictionary)} words\n")
    
    # Check if word provided as command line argument
    if len(sys.argv) > 1:
        word = sys.argv[1]
        syllabify_word(word)
    else:
        # Interactive mode
        print("="*70)
        print("ARMENIAN SYLLABIFICATION TESTER")
        print("="*70)
        print("\nType an Armenian word to see its syllabification.")
        print("Type 'quit' or 'exit' to stop.\n")
        
        # Example words
        print("Example words to try:")
        examples = ["առավոտ", "բանավոր", "բուրավետ", "գիրք", "սեր"]
        for ex in examples:
            print(f"  - {ex}")
        print()
        
        while True:
            try:
                word = input("Enter word (or 'quit'): ").strip()
                
                if word.lower() in ['quit', 'exit', 'q']:
                    print("\nGoodbye!")
                    break
                
                if not word:
                    continue
                
                syllabify_word(word)
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    main()
