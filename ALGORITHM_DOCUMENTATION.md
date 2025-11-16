# Armenian Rhyme Finder - Algorithm Documentation

## Overview
This document explains the core logic and algorithms used in the Armenian Rhyme Finder application. This is intended for AI agents or developers who need to understand and maintain the rhyme detection system.

## System Architecture

### Main Components
1. **backend.py** - Flask backend with rhyme detection engine
2. **index.html** - Frontend web interface
3. **dictionary-hy.cleaned.jsonl** - Armenian dictionary with IPA transcriptions


The dictionary is stored in JSONL format where each line contains:

```json

{

  "": "base_word",           // Base form (lemma)

  "f": ["form1", "form2"],   // Inflected forms/tenses

  "f_ipa": ["ipa1", "ipa2"]  // IPA transcriptions for each form

}

```

### Deployment and Logging Notes
- The production environment runs on [Railway](https://railway.app) as a single Flask service behind Gunicorn. The service serves both the static `index.html` frontend and the `/api/*` routes, so the browser can rely on relative paths (for example, `/api/rhymes`).
- The backend loads `dictionary-hy-improved.jsonl` on startup. A startup log line reports the total number of entries loaded (e.g., `Loaded 18 830 dictionary entries`), and a warning is issued if the file cannot be found so operators can diagnose empty-result scenarios quickly.
- The dictionary path can be overridden with the `DICTIONARY_FILE` environment variable in Railway. This makes it easy to swap in alternative dictionaries or point to an object-storage URL without modifying code.


## Core Algorithm: Multi-Syllable Rhyme Detection

### 1. Syllabification
**Function:** `split_into_syllables(ipa_phones: List[str]) -> List[List[str]]`

Splits IPA phone sequences into syllables following the structure:
- **Onset** (optional): Initial consonants
- **Nucleus** (required): Vowel
- **Coda** (optional): Final consonants

**Algorithm:**
```
For each phone in IPA sequence:
  1. Collect onset consonants (until vowel)
  2. Collect nucleus vowel
  3. Collect coda consonants (until next vowel or end)
  4. If next phone is a vowel, start new syllable
```

**Example:**
- Input: `['a', 'r', 'a', 'v', 'o', 't']`
- Output: `[['a'], ['r', 'a'], ['v', 'o', 't']]`
- Syllables: a-ra-vot

### 2. Phoneme Distance Calculation
**Function:** `phone_distance(phone1: str, phone2: str) -> float`

Calculates phonetic similarity between two phones (0.0 = identical, 1.0 = completely different).

**Vowel Comparison:**
- Based on features: height (close/mid/open) and backness (front/central/back)
- Same height OR backness: distance = 0.3
- Different both: distance = 0.7

**Consonant Comparison:**
- Based on features: place of articulation and manner
- Same place AND manner: distance = 0.1
- Same place OR manner: distance = 0.4
- Different both: distance = 0.8

**Cross-category (vowel vs consonant):** distance = 1.0

### 3. Vowel-Weighted Levenshtein Similarity
**Function:** `levenshtein_similarity_weighted(tail1, tail2, is_last_syllable=False) -> float`

This is the core rhyme comparison function. It uses a modified Levenshtein distance that gives **extra weight to vowels**.

**Key Principles:**
1. **Vowels are more important than consonants for rhyming**
2. **The last syllable's vowel is the MOST important**
3. **Vowel mismatches should penalize more heavily**

**Weighting System:**
- **Vowel substitution cost:** `phone_distance * 1.5` (50% more penalty)
- **Last syllable vowel cost:** `phone_distance * 1.8` (80% more penalty)
- **Consonant substitution cost:** `phone_distance * 1.0` (normal)

**Algorithm:**
```python
For each position (i, j) in DP table:
  If phones match:
    cost = 0
  Else:
    base_cost = phone_distance(phone1, phone2)
    
    # Apply weighting
    If both are vowels:
      If is_last_syllable:
        cost = base_cost * 1.8  # Last syllable vowel - most important!
      Else:
        cost = base_cost * 1.5  # Other vowels - important
    Else:
      cost = base_cost * 1.0  # Consonants - normal weight
  
  dp[i][j] = min(
    dp[i-1][j] + 1.2,          # deletion (slight penalty)
    dp[i][j-1] + 1.2,          # insertion (slight penalty)  
    dp[i-1][j-1] + cost        # substitution (weighted)
  )
```

**Return value:** Similarity score from 0.0 to 1.0 (higher = more similar)

### 4. Multi-Syllable Rhyme Scoring
**Function:** `calculate_multi_syllable_rhyme_score(ipa1, ipa2) -> Dict`

Calculates comprehensive rhyme quality considering all syllables.

**Step 1: Calculate Last Syllable Similarity**
```python
last_syl1 = syllables1[-1]
last_syl2 = syllables2[-1]
last_syllable_sim = levenshtein_similarity_weighted(
    last_syl1, last_syl2, 
    is_last_syllable=True  # Apply vowel weighting!
)
```

**Step 2: Count Matching Syllables**
- Start with last syllable (if similarity ≥ 50%)
- **Only check previous syllables if last syllable is high quality (≥ 90%)**
- For previous syllables, require ≥ 90% similarity to count as matching

**Step 3: Multi-Syllable Bonus**
- Only applied if last syllable is excellent (≥ 90%)
- Bonus: `0.08 * (syllables_matched - 1)`
- Rewards words that rhyme across multiple syllables

**Step 4: Final Score Calculation**
```python
base_score = last_syllable_sim
multi_syllable_bonus = 0.08 * (syllables_matched - 1) if syllables_matched > 1 else 0
final_score = min(1.0, base_score + multi_syllable_bonus)
```

**Return Dictionary:**
```python
{
    'final_score': 0.0 to 1.0,
    'label': 'perfect' | 'near-perfect' | 'assonance' | 'slant' | 'none',
    'syllables_matched': int,
    'last_syllable_similarity': 0.0 to 1.0
}
```

### 5. Rhyme Classification Labels
**Function:** `get_rhyme_label_from_score(tail1, tail2, similarity, identical, syllables_matched)`

Classifies rhyme quality based on multiple criteria:

**Perfect Rhyme:**
- Syllables are identical, OR
- Multi-syllable match (≥2 syllables) with ≥99% similarity

**Near-Perfect Rhyme:**
- Multi-syllable match (≥2 syllables) with ≥85% similarity, OR
- Single syllable with ≥95% similarity and same nucleus vowel

**Assonance:**
- Same nucleus vowel with ≥70% similarity

**Slant Rhyme:**
- ≥50% similarity

**No Rhyme:**
- <50% similarity

### 6. Rhyme Search and Ranking
**Function:** `find_rhymes(input_word, limit=50, include_tenses=False)`

**Process:**
1. Look up input word in dictionary (could be base form or inflected form)
2. Get IPA transcription
3. Compare against all dictionary entries using `calculate_multi_syllable_rhyme_score`
4. Filter out the input word itself
5. Sort results by similarity (highest first)
6. Return top N results


**Sorting Priority:**

Results are sorted purely by `final_score` in descending order. This means:

- A 95% "near-perfect" rhyme ranks higher than an 85% "near-perfect" rhyme

- Labels are informational but don't affect ranking

**Frontend Filtering:**
The results UI provides pill-style toggle buttons (Noun, Verb, Adjective, Adverb, Name, Pronoun) that filter the currently loaded rhymes by part of speech without issuing new API calls. Each rhyme’s part-of-speech tag is normalized client-side to handle aliases (for example, `adj`, `proper noun`, or `common noun`), and infinite scrolling honors the active filter so newly appended results remain consistent with the user’s selection.


## Key Design Decisions

### Why Vowel Weighting?
In poetry and rhyming:
1. **Vowel sounds are the primary carriers of rhyme**
2. Words with matching vowels sound more similar even if consonants differ
3. The last syllable's vowel is what listeners focus on most

**Example:**
- "բանավոր" (ba-na-**vor**) vs "առավոտ" (a-ra-**vot**)
  - Same last vowel 'o' → Ranks higher
- "բուրավետ" (bu-ra-**vet**) vs "առավոտ" (a-ra-**vot**)
  - Different last vowel 'e' vs 'o' → Ranks lower

### Why Strict Multi-Syllable Bonus Threshold?
The 90% threshold prevents:
1. **Score inflation** - Mediocre rhymes getting boosted to "perfect"
2. **False positives** - Words with similar prefixes but different endings
3. **Ranking issues** - Poor rhymes sorting above good ones

**Example Prevention:**
- "առավոտ" (a-ra-vot) vs "առավել" (a-ra-vel)
  - Same prefix "a-ra" but different ending
  - Without threshold: Would get multi-syllable bonus → 100%
  - With threshold: Last syllable only 77% → No bonus → 77% ✓

### Why Small Bonus (0.08)?
- Large bonuses (0.15+) caused score inflation
- Small bonus (0.08) rewards genuine multi-syllable rhymes without distorting rankings
- Ensures last syllable quality remains the primary factor

## Phoneme Definitions

### Vowels
```python
VOWELS = {'a', 'e', 'i', 'o', 'u', 'ə', 'ɑ', 'ɔ', 'ʌ', 'æ', 'iː', 'uː', 'oː', 'ɛ'}
```

### Vowel Features
```python
VOWEL_FEATURES = {
    'i': ('close', 'front'),      # Like "ee" in "see"
    'e': ('close-mid', 'front'),  # Like "ay" in "day"
    'a': ('open', 'front'),       # Like "a" in "father"
    'o': ('close-mid', 'back'),   # Like "o" in "go"
    'u': ('close', 'back'),       # Like "oo" in "food"
    # ... etc
}
```

### Consonant Features
Place of articulation: labial, alveolar, palatal, velar, dental, glottal
Manner of articulation: stop, fricative, nasal, approximant

## Performance Considerations

### Dictionary Loading
- Dictionary is loaded once at startup into memory
- Two indexes maintained:
  - `dictionary`: base_word → entry
  - `form_to_entries`: any_form → list of (base_word, form_index)

### Search Complexity
- **Dictionary size:** ~18,830 entries
- **Search operation:** O(n) where n = dictionary size
- **Per-comparison:** O(m×n) where m, n = syllable lengths (typically 3-5 phones)
- **Total search time:** ~1-2 seconds for full dictionary scan

### Optimization Opportunities
1. **Pre-compute syllabifications** at load time
2. **Index by last syllable** for faster filtering
3. **Parallel processing** for large dictionary scans
4. **Caching** of frequently searched words

## Error Handling

### Missing IPA Transcriptions
- Words without IPA are skipped
- Logged as warnings in production

### Invalid Input
- Empty strings return empty results
- Non-existent words return empty results
- Malformed IPA is handled gracefully (worst-case: no match)

## Testing

### Unit Tests
Test files should cover:
1. Syllabification edge cases
2. Phone distance calculations
3. Vowel weighting effectiveness
4. Multi-syllable bonus thresholds
5. Known rhyme pairs (positive and negative examples)

### Key Test Cases
```python
# Perfect rhyme - identical last syllables
"տարեկան" vs "վարպետական" → ~100%

# Same vowel, different consonants  
"բանավոր" vs "առավոտ" → ~90%

# Different vowel, same consonants
"բուրավետ" vs "առավոտ" → ~85%

# Similar structure, different ending
"առավոտ" vs "առավել" → ~77%
```

## Future Enhancements

### Possible Improvements
1. **Stress patterns** - Armenian has stress that could affect rhyme quality
2. **Consonant clusters** - Better handling of complex onsets/codas
3. **Semantic similarity** - Bonus for thematically related words
4. **User feedback** - Learn from user preferences
5. **Phonetic rules** - Armenian-specific phonological rules

### API Extensions
- Batch rhyme search
- Rhyme scheme generation
- Phonetic similarity API
- Syllable count filtering

## Conclusion

The Armenian Rhyme Finder uses a sophisticated multi-syllable rhyme detection algorithm that:
1. **Prioritizes vowel matching** (especially in the last syllable)
2. **Considers full syllable structure** (onset, nucleus, coda)
3. **Rewards multi-syllable rhymes** (but only when deserved)
4. **Provides granular similarity scores** (not just binary match/no-match)

This approach produces rhyme rankings that align with human perception of rhyme quality in Armenian poetry and song.
