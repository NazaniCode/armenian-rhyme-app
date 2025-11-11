# Armenian Rhyme Finder - API Documentation

Complete REST API reference for the Armenian Rhyme Finder backend.

## Base URL

```
http://localhost:5000/api
```

## Authentication

No authentication required. All endpoints are public.

## Response Format

All endpoints return JSON with the following structure:

### Success Response (2xx)
```json
{
  "data": { },
  "status": "success",
  "message": "Optional message"
}
```

### Error Response (4xx, 5xx)
```json
{
  "error": "Error description",
  "status": "error",
  "code": 400
}
```

---

## Endpoints

### 1. Find Rhymes

**Endpoint:** `GET /rhymes`

**Description:** Find rhyming words for a given Armenian word.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| word | string | Yes | - | Armenian word to find rhymes for |
| limit | integer | No | 25 | Max number of results (1-200) |

**Example Request:**

```
GET /api/rhymes?word=սեր&limit=10
```

**Example Response:**

```json
{
  "word": "սեր",
  "rhymes": [
    {
      "word": "հեր",
      "similarity": 0.857,
      "label": "near-perfect",
      "definition": "master, expert",
      "part_of_speech": "noun"
    },
    {
      "word": "սուր",
      "similarity": 0.714,
      "label": "assonance",
      "definition": "sharp, pointed",
      "part_of_speech": "adjective"
    }
  ]
}
```

**Response Fields:**

- `word` (string) - The search word
- `rhymes` (array) - Array of matching rhymes
  - `word` (string) - Armenian word
  - `similarity` (float) - Similarity score (0-1)
  - `label` (string) - Rhyme type: perfect, near-perfect, assonance, slant
  - `definition` (string) - English definition
  - `part_of_speech` (string) - Part of speech (noun, verb, adj, etc.)

**HTTP Status Codes:**

- `200` - Success
- `400` - Missing required parameter
- `404` - Word not found
- `500` - Server error

**cURL Example:**

```bash
curl "http://localhost:5000/api/rhymes?word=սեր&limit=10"
```

**Python Example:**

```python
import requests

response = requests.get('http://localhost:5000/api/rhymes', params={
    'word': 'սեր',
    'limit': 10
})
data = response.json()

for rhyme in data['rhymes']:
    print(f"{rhyme['word']:<20} {rhyme['label']:<15} {rhyme['similarity']}")
```

**JavaScript Example:**

```javascript
fetch('http://localhost:5000/api/rhymes?word=սեր&limit=10')
  .then(response => response.json())
  .then(data => {
    data.rhymes.forEach(rhyme => {
      console.log(`${rhyme.word}: ${rhyme.label} (${rhyme.similarity})`);
    });
  });
```

---

### 2. Search Words

**Endpoint:** `GET /search`

**Description:** Search for words by prefix/substring. Used for autocomplete.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| q | string | Yes | Search query (Armenian text) |

**Example Request:**

```
GET /api/search?q=բա
```

**Example Response:**

```json
{
  "results": [
    {
      "word": "բառ",
      "definition": "word",
      "pos": "noun"
    },
    {
      "word": "բաց",
      "definition": "open",
      "pos": "adjective"
    },
    {
      "word": "բազ",
      "definition": "base",
      "pos": "noun"
    }
  ]
}
```

**Response Fields:**

- `results` (array) - Matching words
  - `word` (string) - Armenian word
  - `definition` (string) - Definition
  - `pos` (string) - Part of speech

**HTTP Status Codes:**

- `200` - Success (empty results if no match)
- `400` - Missing query parameter

**Notes:**

- Case-insensitive search
- Returns first 20 matches
- Empty query returns empty results (no error)

**cURL Example:**

```bash
curl "http://localhost:5000/api/search?q=բա"
```

**JavaScript Example:**

```javascript
async function searchWords(query) {
  const response = await fetch(`http://localhost:5000/api/search?q=${query}`);
  const data = await response.json();
  return data.results;
}
```

---

### 3. Get Word Information

**Endpoint:** `GET /word/<word>`

**Description:** Get detailed information about a specific word.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| word | string (URL) | Armenian word |

**Example Request:**

```
GET /api/word/սեր
```

**Example Response:**

```json
{
  "word": "սեր",
  "definition": "love",
  "pos": "noun",
  "forms_count": 15
}
```

**Response Fields:**

- `word` (string) - The word
- `definition` (string) - Definition
- `pos` (string) - Part of speech
- `forms_count` (integer) - Number of word forms

**HTTP Status Codes:**

- `200` - Success
- `404` - Word not found

**cURL Example:**

```bash
curl "http://localhost:5000/api/word/սեր"
```

---

### 4. Dictionary Statistics

**Endpoint:** `GET /stats`

**Description:** Get general statistics about the dictionary.

**Example Request:**

```
GET /api/stats
```

**Example Response:**

```json
{
  "total_words": 18831
}
```

**Response Fields:**

- `total_words` (integer) - Total words in dictionary

**HTTP Status Codes:**

- `200` - Success

**cURL Example:**

```bash
curl "http://localhost:5000/api/stats"
```

**Python Example:**

```python
import requests

response = requests.get('http://localhost:5000/api/stats')
stats = response.json()
print(f"Dictionary contains {stats['total_words']:,} words")
```

---

### 5. Health Check

**Endpoint:** `GET /health`

**Description:** Check if the API is running and dictionary is loaded.

**Example Request:**

```
GET /api/health
```

**Example Response:**

```json
{
  "status": "healthy",
  "words_loaded": 18831
}
```

**Response Fields:**

- `status` (string) - Health status ("healthy" or "unhealthy")
- `words_loaded` (integer) - Number of words currently in memory

**HTTP Status Codes:**

- `200` - Healthy
- `503` - Service unavailable

**cURL Example:**

```bash
curl "http://localhost:5000/api/health"
```

---

## Rhyme Classification Guide

### Label Definitions

| Label | Criteria | Example |
|-------|----------|---------|
| `perfect` | Identical rhyme tails | բառ ↔ տառ |
| `near-perfect` | Similarity ≥85% + same vowel nucleus | ե-sounds very similar to ե |
| `assonance` | Same vowel nucleus + similarity ≥60% | a-sounds ↔ a-sounds |
| `slant` | General similarity ≥50% | Consonant-driven matches |
| `none` | Everything else | Filtered out by default |

### Similarity Score

The similarity score is a float from 0 to 1:
- `1.0` = Identical
- `0.85` = Very similar (near-perfect threshold)
- `0.6` = Decent similarity (assonance threshold)
- `0.5` = Minimal similarity (slant threshold)
- `< 0.3` = Too different (filtered out)

---

## Error Handling

### Common Errors

**404 Not Found - Word**

```json
{
  "error": "Word not found",
  "status": "error"
}
```

Response when the word doesn't exist in dictionary.

**400 Bad Request - Missing Parameter**

```json
{
  "error": "Word parameter required",
  "status": "error"
}
```

Response when required parameter is missing.

**500 Internal Server Error**

```json
{
  "error": "Internal server error",
  "status": "error"
}
```

Response when server encounters an unexpected error. Check `rhyme_finder.log` for details.

---

## Rate Limiting

No rate limiting currently implemented. Use responsibly in production.

For high-volume usage, consider:
- Caching responses
- Implementing database indexing
- Using CDN for frontend assets

---

## CORS (Cross-Origin Resource Sharing)

CORS is enabled for all origins. The API accepts requests from:
- `file://` URLs (local HTML files)
- `http://localhost:*` (local development)
- Any other origin (production depends on configuration)

---

## Examples by Language

### Python

```python
import requests

# Find rhymes
response = requests.get('http://localhost:5000/api/rhymes', 
    params={'word': 'սեր', 'limit': 25})
rhymes = response.json()['rhymes']

# Search words
response = requests.get('http://localhost:5000/api/search', 
    params={'q': 'բա'})
words = response.json()['results']

# Get word info
response = requests.get('http://localhost:5000/api/word/սեր')
info = response.json()

# Get stats
response = requests.get('http://localhost:5000/api/stats')
total = response.json()['total_words']
```

### JavaScript

```javascript
// Find rhymes
async function findRhymes(word, limit = 25) {
  const response = await fetch(
    `http://localhost:5000/api/rhymes?word=${word}&limit=${limit}`
  );
  return response.json();
}

// Search words
async function searchWords(query) {
  const response = await fetch(
    `http://localhost:5000/api/search?q=${query}`
  );
  return response.json();
}

// Get word info
async function getWordInfo(word) {
  const response = await fetch(
    `http://localhost:5000/api/word/${word}`
  );
  return response.json();
}

// Usage
findRhymes('սեր', 10).then(data => {
  console.log(data.rhymes);
});
```

### cURL

```bash
# Find rhymes
curl "http://localhost:5000/api/rhymes?word=սեր&limit=10"

# Search words
curl "http://localhost:5000/api/search?q=բա"

# Get word info
curl "http://localhost:5000/api/word/սեր"

# Get stats
curl "http://localhost:5000/api/stats"

# Health check
curl "http://localhost:5000/api/health"
```

---

## Performance Notes

### Response Times

- Initial request: ~3 seconds (dictionary loading)
- Subsequent /rhymes: 50-200ms depending on results
- /search requests: 100-300ms
- /stats, /health: < 10ms

### Optimization Tips

1. **Cache dictionary**: Keep server running
2. **Batch requests**: Multiple queries in sequence (server-side cache)
3. **Limit results**: Use smaller `limit` values for faster responses
4. **Use search**: /search for autocomplete is indexed
5. **Filter threshold**: Can adjust in `config.py` for fewer results

---

## API Versioning

Current API version: **1.0**

No breaking changes planned. The API is stable.

---

## Support

For API issues:

1. Check error message and status code
2. Verify backend is running: `curl http://localhost:5000/api/health`
3. Check `rhyme_finder.log` for server errors
4. Review `app.py` implementation
5. Test with curl before client code

---

## Implementation Notes

The API uses:
- **Framework**: Flask 2.3.0
- **CORS**: Flask-CORS 4.0.0
- **Algorithm**: Feature-aware Levenshtein distance
- **Data**: JSONL format with 18,831 Armenian words

---

Last Updated: 2024
