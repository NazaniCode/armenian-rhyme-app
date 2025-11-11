# Armenian Rhyme Finder - Architecture & Design

This document explains the system architecture, data flow, and design decisions.

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER BROWSER                                │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  index.html (Web Interface)                              │   │
│  │  ├─ Search Input with Autocomplete                       │   │
│  │  ├─ Results Display with Filtering                       │   │
│  │  └─ Modern Responsive UI                                 │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           ↕ HTTP/CORS                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  FLASK BACKEND (app.py)                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  REST API Layer                                          │   │
│  │  ├─ GET /api/rhymes (main endpoint)                     │   │
│  │  ├─ GET /api/search (autocomplete)                      │   │
│  │  ├─ GET /api/word/<word> (info)                         │   │
│  │  ├─ GET /api/stats (statistics)                         │   │
│  │  └─ GET /api/health (health check)                      │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           ↓                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Business Logic Layer                                    │   │
│  │  ├─ find_rhymes() - Main rhyme finder                   │   │
│  │  ├─ extract_rhyme_tail() - Phoneme extraction           │   │
│  │  ├─ levenshtein_similarity() - Similarity scoring       │   │
│  │  ├─ phone_distance() - Feature-aware distance           │   │
│  │  └─ get_rhyme_label() - Classification                  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           ↓                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Data Layer                                              │   │
│  │  └─ dictionary (in-memory cache of 18,831 words)         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           ↓                                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              PERSISTENT DATA STORAGE                            │
│  dictionary-hy.cleaned.jsonl (18,831 Armenian words)            │
│  ├─ Word: Armenian text                                         │
│  ├─ Definition: English meaning                                 │
│  ├─ POS: Part of speech                                         │
│  ├─ Forms: All grammatical forms                                │
│  └─ Forms_IPA: Phonetic transcriptions                           │
└─────────────────────────────────────────────────────────────────┘

Configuration & Utilities:
├─ config.py (Settings and thresholds)
├─ test_rhymes.py (Testing and examples)
└─ start.bat/start.ps1 (Launch scripts)
```

---

## Data Flow Diagram

### Rhyme Search Flow

```
USER INPUT
  │ "սեր" (love)
  ↓
┌─────────────────────────────┐
│ Frontend: index.html        │
│ 1. User types word          │
│ 2. Autocomplete fetches     │
│ 3. User clicks result       │
└────────────┬────────────────┘
             │ AJAX Request
             ↓
┌─────────────────────────────┐
│ Backend: app.py             │
│ GET /api/rhymes             │
│ word="սեր", limit=25        │
└────────────┬────────────────┘
             │
             ↓
┌─────────────────────────────┐
│ Step 1: Load Dictionary     │
│ - Check if word exists      │
│ - Get IPA forms             │
│ - Extract IPA phones        │
└────────────┬────────────────┘
             │
             ↓
┌─────────────────────────────┐
│ Step 2: Extract Rhyme Tail  │
│ - Find last vowel in IPA    │
│ - Extract from vowel to end │
│ - Result: ['e', 'r']        │
└────────────┬────────────────┘
             │
             ↓
┌─────────────────────────────┐
│ Step 3: Compare All Words   │
│ For each word in dictionary:│
│ - Extract its rhyme tail    │
│ - Calculate similarity      │
│ - Classify rhyme type       │
│ - If > min_threshold, save  │
└────────────┬────────────────┘
             │
             ↓
┌─────────────────────────────┐
│ Step 4: Sort Results        │
│ - Perfect (1.0)             │
│ - Near-perfect (0.85+)      │
│ - Assonance (0.6+)          │
│ - Slant (0.5+)              │
│ - By similarity descending  │
└────────────┬────────────────┘
             │
             ↓
┌─────────────────────────────┐
│ Step 5: Format Response     │
│ - JSON with rhyme data      │
│ - Include definitions       │
│ - Include similarity scores │
└────────────┬────────────────┘
             │ JSON Response
             ↓
┌─────────────────────────────┐
│ Frontend: index.html        │
│ 1. Parse JSON               │
│ 2. Color-code by type       │
│ 3. Display with formatting  │
│ 4. Show definitions         │
└────────────┬────────────────┘
             │
             ↓
        USER SEES RESULTS
```

---

## Component Architecture

### Frontend Components

```
index.html
├─ Header Section
│  └─ Title & subtitle
├─ Search Section
│  ├─ Search Input
│  │  ├─ Event: oninput → autocomplete
│  │  └─ Event: onkeypress → search
│  ├─ Results Limit Selector
│  │  └─ Options: 10, 25, 50, 100
│  └─ Search Button
│     └─ Event: onclick → search()
├─ Loading Indicator
│  └─ Spinner animation
├─ Results Section
│  ├─ Results Header
│  │  └─ Result count display
│  └─ Results Container
│     ├─ Rhyme Item (repeated)
│     │  ├─ Word name
│     │  ├─ Rhyme type badge
│     │  │  ├─ perfect (green)
│     │  │  ├─ near-perfect (yellow)
│     │  │  ├─ assonance (blue)
│     │  │  └─ slant (orange)
│     │  ├─ Similarity score
│     │  ├─ Part of speech
│     │  └─ Definition
│     └─ Empty state (if no results)
└─ Statistics Footer
   └─ Dictionary size
```

### Backend Components

```
app.py
├─ Configuration Loading
│  └─ import config.*
├─ Dictionary Loading
│  └─ load_dictionary()
├─ Logging Setup
│  └─ Logger initialization
├─ REST API Endpoints
│  ├─ @app.route('/api/rhymes')
│  ├─ @app.route('/api/search')
│  ├─ @app.route('/api/word/<word>')
│  ├─ @app.route('/api/stats')
│  ├─ @app.route('/api/health')
│  └─ Error handlers
└─ Core Algorithm Functions
   ├─ extract_rhyme_tail()
   ├─ phone_distance()
   ├─ levenshtein_similarity()
   ├─ get_rhyme_label()
   └─ find_rhymes()
```

---

## Algorithm Architecture

### Rhyme Detection Pipeline

```
Input Word "սեր"
    ↓
Extract IPA Phones
    "s e r" → ['s', 'e', 'r']
    ↓
Find Last Vowel
    Last vowel at index 1 → 'e'
    ↓
Extract Rhyme Tail
    From index 1 to end → ['e', 'r']
    ↓
────────────────────────────────────────────
For Each Word in Dictionary:
    ↓
    Extract its rhyme tail
        e.g., ["ե", "ր"] → ['e', 'r']
        e.g., ["ո", "վ"] → ['o', 'v']
    ↓
    Calculate Similarity (Levenshtein)
    ┌─────────────────────────────────┐
    │ Build DP table:                 │
    │  ['e','r'] ↔ ['e','r'] = 1.0   │
    │  ['e','r'] ↔ ['o','v'] = 0.33  │
    │  ['e','r'] ↔ ['e','l'] = 0.67  │
    └─────────────────────────────────┘
    ↓
    Classify Rhyme Type
    ┌─────────────────────────────────┐
    │ IF identical                    │
    │   → "perfect"                   │
    │ ELSE IF sim≥0.85 & same nucleus │
    │   → "near-perfect"              │
    │ ELSE IF same nucleus & sim≥0.6 │
    │   → "assonance"                 │
    │ ELSE IF sim≥0.5                 │
    │   → "slant"                     │
    │ ELSE                            │
    │   → "none" (skip)               │
    └─────────────────────────────────┘
    ↓
    IF similarity ≥ threshold
        → Add to results
────────────────────────────────────────────
Sort Results
    By rhyme type, then by similarity
    ↓
Return Top N Results
    ["հեր", "շերտ", "սուր", ...]
```

### Levenshtein Distance with Features

```
Comparing tails: ['e','r'] vs ['o','v']

Build DP table (3×3):
        ""  'o'  'v'
    ""   0   1    2
    'e'  1   ?    ?
    'r'  2   ?    ?

For each cell [i,j]:
    If tails[i-1] == tails[j-1]:
        cost = 0
    Else:
        cost = phone_distance(tails[i-1], tails[j-1])
        
    dp[i][j] = min(
        dp[i-1][j] + 1,      (deletion)
        dp[i][j-1] + 1,      (insertion)
        dp[i-1][j-1] + cost  (substitution)
    )

Result DP table:
        ""  'o'  'v'
    ""   0   1    2
    'e'  1   0.7  1.4
    'r'  2   1.7  1.1

Final distance: dp[2][2] = 1.1
Similarity: 1 - (1.1 / max(2,2)) = 1 - 0.55 = 0.45
```

---

## Data Structure: Dictionary Entry

```json
{
  "": "բառ",
  "p": ["noun"],
  "d": ["word"],
  "f": [
    "բառ",
    "բառդ", 
    "բառը",
    "բառի",
    "բառիդ",
    ...
  ],
  "f_ipa": [
    "b a r",
    "b a r d",
    "b a r ə",
    "b a r i",
    "b a r i d",
    ...
  ]
}
```

### Dictionary Field Meanings

| Field | Description | Type | Example |
|-------|-------------|------|---------|
| `""` | Base word | string | "բառ" |
| `p` | Part of speech | array | ["noun"] |
| `d` | Definition(s) | array | ["word"] |
| `f` | All word forms | array | ["բառ", "բառի", ...] |
| `f_ipa` | IPA phonetic forms | array | ["b a r", "b a r i", ...] |

---

## Performance Characteristics

### Time Complexity

```
Dictionary Loading:
  O(n) where n = 18,831 words
  Typical: 2-3 seconds (one-time)

Rhyme Search:
  O(n × m²) where:
    n = number of words (18,831)
    m = average rhyme tail length (3-5)
  
  Analysis:
    For each word (n times):
      - Extract tail: O(m)
      - Compare tails: O(m²) using Levenshtein
    Total: n × (m + m²) ≈ n × m²
  
  Typical: 50-200ms per query

Word Search:
  O(n × q) where:
    n = number of words
    q = query length
  Typical: 100-300ms per query
  Optimized with early termination (first 20 matches)
```

### Space Complexity

```
Dictionary Storage:
  ~18,831 entries × (word + forms + IPA)
  Typical: 200-300 MB in memory

Per-Query:
  - Temporary DP table: O(m²) where m ≈ 5
  - Results list: O(k) where k = limit
  Total per query: Minimal overhead
```

---

## Configuration Architecture

```
config.py
├─ Flask Configuration
│  ├─ FLASK_HOST
│  ├─ FLASK_PORT
│  └─ FLASK_DEBUG
├─ Dictionary Configuration
│  └─ DICTIONARY_FILE
├─ Rhyme Thresholds
│  ├─ RHYME_THRESHOLDS.perfect
│  ├─ RHYME_THRESHOLDS.near_perfect
│  ├─ RHYME_THRESHOLDS.assonance
│  ├─ RHYME_THRESHOLDS.slant
│  └─ RHYME_THRESHOLDS.minimum
├─ Search Configuration
│  ├─ AUTOCOMPLETE_LIMIT
│  ├─ DEFAULT_RESULT_LIMIT
│  └─ MAX_RESULT_LIMIT
├─ Phoneme Features
│  ├─ CONSONANTS (33 defined)
│  ├─ VOWELS (16 defined)
│  └─ VOWEL_FEATURES
├─ UI Configuration
│  └─ UI_CONFIG.theme
└─ Logging
   ├─ LOG_LEVEL
   └─ LOG_FILE
```

---

## Communication Protocol

### HTTP Request/Response

**Request:**
```
GET /api/rhymes?word=սեր&limit=10 HTTP/1.1
Host: localhost:5000
Accept: application/json
Access-Control-Request-Method: GET
```

**Response:**
```
HTTP/1.1 200 OK
Content-Type: application/json
Access-Control-Allow-Origin: *

{
  "word": "սեր",
  "rhymes": [
    {
      "word": "հեր",
      "similarity": 0.857,
      "label": "near-perfect",
      "definition": "master",
      "part_of_speech": "noun"
    }
  ]
}
```

---

## Error Handling Flow

```
User Request
    ↓
Validate Input
    ├─ Check required parameters
    ├─ Validate word exists
    └─ Validate limit range
    ↓
If Error:
    ├─ Generate error JSON
    ├─ Set HTTP status code
    ├─ Log error details
    └─ Return to client
    ↓
If Valid:
    ├─ Process request
    ├─ Return results
    └─ Log success
```

---

## Deployment Architecture

### Development (Current)

```
User Machine
├─ Browser
│  └─ index.html (file://)
├─ Flask Server (localhost:5000)
│  └─ app.py
└─ Dictionary File
   └─ dictionary-hy.cleaned.jsonl
```

### Production (Recommended)

```
Internet
    ↓
┌─────────────────────┐
│ Nginx Reverse Proxy │
│ Port 80/443         │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Gunicorn Server     │
│ (Multiple workers)  │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Flask App (app.py)  │
│ × 4 workers         │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Shared Dictionary   │
│ (Cached in memory)  │
└─────────────────────┘
```

---

## Phoneme Feature Space

### Consonant Classification

```
Consonants (33 total)
├─ Place of Articulation
│  ├─ Labial: p, b, f, v, m, w
│  ├─ Alveolar: t, d, s, z, n, l, ɹ, r, tsʰ
│  ├─ Dental: θ, ð
│  ├─ Palatal: ʃ, ʒ, j, tʃ
│  ├─ Velar: k, g, kʰ, x, ɣ, ŋ
│  └─ Glottal: h
└─ Manner of Articulation
   ├─ Stop (plosive): p, b, t, d, k, g, kʰ, tsʰ, tʃ
   ├─ Fricative: f, v, s, z, ʃ, ʒ, x, ɣ, θ, ð, h
   ├─ Nasal: m, n, ŋ
   └─ Approximant: l, ɹ, r, j, w
```

### Vowel Classification

```
Vowels (16 total)
├─ Height (Vertical Position)
│  ├─ Close: i, iː, u, uː
│  ├─ Close-mid: e, o, oː
│  ├─ Open-mid: ɛ, ʌ, ɔ
│  ├─ Near-open: æ
│  └─ Open: a, ɑ
└─ Backness (Front-to-Back)
   ├─ Front: i, iː, e, ɛ, æ, a
   ├─ Central: ə
   └─ Back: u, uː, o, oː, ʌ, ɔ, ɑ
```

---

## Testing Architecture

```
test_rhymes.py
├─ Unit Tests
│  ├─ test_rhyme_tail_extraction()
│  ├─ test_phone_distance()
│  ├─ test_similarity()
│  └─ test_rhyme_labels()
├─ Integration Tests
│  ├─ demo_word_search()
│  └─ print_statistics()
└─ Examples
   └─ example_api_usage()
```

---

## Security Considerations

### CORS Policy
- Enabled for all origins (development)
- Should restrict in production

### Input Validation
- Validate word parameter (no injection)
- Validate limit parameter (range check)
- Sanitize error messages

### Error Exposure
- Don't expose file paths
- Don't expose full stack traces
- Log errors server-side only

### Recommendations
1. Add rate limiting in production
2. Implement API authentication if needed
3. Use HTTPS in production
4. Restrict CORS origins
5. Add input length limits

---

## Scalability Considerations

### Current Limitations
- Single-process Flask server
- All dictionary in-memory
- No horizontal scaling

### Improvements for Scale
1. Use Gunicorn with multiple workers
2. Implement caching (Redis)
3. Database for dictionary (PostgreSQL)
4. Load balancer (Nginx)
5. CDN for static assets
6. Consider microservices

### Estimated Scaling
- Current: ~50-100 concurrent users
- With Gunicorn (4 workers): ~200 users
- With load balancing: ~500+ users
- With caching: Much higher throughput

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024-11 | Initial release |
| | | Full rhyme detection |
| | | REST API |
| | | Web interface |
| | | Documentation |

---

## Future Architecture Improvements

1. **Machine Learning**: ML-based similarity scoring
2. **Streaming**: Server-Sent Events for live results
3. **GraphQL**: Alternative to REST API
4. **WebAssembly**: Move algorithm to WASM for speed
5. **Mobile App**: Native iOS/Android app
6. **Offline Mode**: Service workers for offline support
7. **Database**: Move from JSONL to PostgreSQL
8. **Clustering**: Add word embeddings and clustering

---

This architecture is designed to be simple, maintainable, and extensible while providing excellent performance for the current use case.
