# Armenian Rhyme Finder 🎵

A sophisticated web application for discovering Armenian rhymes based on IPA (International Phonetic Alphabet) phoneme similarity analysis. The app uses intelligent feature-aware algorithms to identify different types of rhymes.

## Features

- **Multiple Rhyme Categories**:
  - **Perfect Rhymes**: Identical phonetic tails
  - **Near-Perfect Rhymes**: High similarity (≥85%) with same vowel nucleus
  - **Assonance/Near Rhymes**: Same vowel nucleus with decent similarity (≥60%)
  - **Slant Rhymes**: Consonant-driven similarity (≥50%)

- **Smart Phoneme Analysis**:
  - Extracts rhyme tails (nucleus + coda of the last syllable)
  - Feature-aware Levenshtein distance for phoneme similarity
  - Considers consonant place/manner and vowel height/backness

- **Modern Web Interface**:
  - Beautiful, responsive design
  - Real-time autocomplete search
  - Detailed word definitions and part-of-speech tags
  - Similarity scores for each match
  - Mobile-friendly layout

## Requirements

- Python 3.7+
- Modern web browser (Chrome, Firefox, Safari, Edge)

## Installation & Setup

### 1. Install Python Dependencies

```powershell
pip install -r requirements.txt
```

Or manually:

```powershell
pip install Flask==2.3.0 Flask-CORS==4.0.0 Werkzeug==2.3.0
```

### 2. Prepare Dictionary

Ensure `dictionary-hy.cleaned.jsonl` is in the project directory. Each line should be a JSON object with:

```json
{
  "": "word",
  "p": ["part_of_speech"],
  "d": ["definition"],
  "f": ["word_form_1", "word_form_2", ...],
  "f_ipa": ["phonetic_form_1", "phonetic_form_2", ...]
}
```

### 3. Start the Backend Server

```powershell
python backend.py
```

You should see:
```
Loaded [count] words from dictionary
 * Running on http://127.0.0.1:5000
```

### 4. Open the Web Interface

Open your browser and navigate to:
```
file:///c:/Users/Nazani/Desktop/armenian-rhyme-app/index.html
```

Or serve it with a local HTTP server:

```powershell
# Using Python's built-in server
python -m http.server 8000
```

Then visit: `http://localhost:8000`

## How It Works

### Rhyme Detection Algorithm

1. **Rhyme Tail Extraction**: 
   - Identifies the last vowel in a word's phonetic representation
   - Extracts all phones from that vowel to the end (nucleus + coda)

2. **Similarity Scoring**:
   - Uses feature-aware Levenshtein distance
   - Identical phones: cost 0
   - Similar phones (same place/manner for consonants, similar height/backness for vowels): cost < 1
   - Unrelated phones: cost 1
   - Insertions/deletions: cost 1

3. **Classification**:
   - Perfect: Identical tails
   - Near-perfect: ≥85% similarity + same nucleus
   - Assonance: Same nucleus + ≥60% similarity
   - Slant: ≥50% similarity
   - None: Everything else (filtered out)

### Phoneme Features

**Consonants** are classified by:
- Place: labial, alveolar, dental, palatal, velar, glottal
- Manner: stop, fricative, nasal, approximant

**Vowels** are classified by:
- Height: close, close-mid, open-mid, open, near-open
- Backness: front, central, back

## API Endpoints

### GET /api/rhymes
Find rhymes for a word.

**Parameters:**
- `word` (required): Armenian word to find rhymes for
- `limit` (optional): Maximum results (default: 50)

**Response:**
```json
{
  "word": "գլուխ",
  "rhymes": [
    {
      "word": "լուծ",
      "similarity": 0.857,
      "label": "near-perfect",
      "definition": "solution",
      "part_of_speech": "noun"
    }
  ]
}
```

### GET /api/search
Search for words by prefix.

**Parameters:**
- `q` (required): Search query

**Response:**
```json
{
  "results": [
    {
      "word": "word",
      "definition": "meaning",
      "pos": "noun"
    }
  ]
}
```

### GET /api/word/<word>
Get detailed info about a word.

**Response:**
```json
{
  "word": "բառ",
  "definition": "word",
  "pos": "noun",
  "forms_count": 25
}
```

### GET /api/stats
Get dictionary statistics.

**Response:**
```json
{
  "total_words": 18831
}
```

## Usage Examples

### Finding Rhymes via Web Interface

1. Click in the search field
2. Type an Armenian word (autocomplete suggestions will appear)
3. Press Enter or click "Search"
4. Results are sorted by rhyme quality (perfect → near-perfect → assonance → slant)

### Using the API

```python
import requests

response = requests.get(
    'http://localhost:5000/api/rhymes',
    params={'word': 'գլուխ', 'limit': 25}
)
rhymes = response.json()
for rhyme in rhymes['rhymes']:
    print(f"{rhyme['word']} ({rhyme['label']}): {rhyme['similarity']}")
```

## File Structure

```
armenian-rhyme-app/
├── backend.py                       # Flask backend with rhyme algorithm
├── index.html                       # Web interface (frontend)
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
├── dictionary-hy.cleaned.jsonl      # Armenian word dictionary
└── add_ipa.py                       # (Existing) IPA phonetization script
```

## Performance Notes

- Dictionary loading: ~2-3 seconds (18,000+ words)
- Per-search latency: 50-200ms depending on result count
- Autocomplete search: 100-300ms
- Browser queries are cached by the frontend

## Future Enhancements

- [ ] Multi-language support (transliteration)
- [ ] Advanced filters (filter by part of speech, definition)
- [ ] Export results (CSV, JSON)
- [ ] Offline mode with service workers
- [ ] Word frequency ranking
- [ ] Rhyme suggestions for poetry composition
- [ ] Audio pronunciation playback

## Troubleshooting

**"Word not found" error:**
- Check spelling and diacritics
- Use autocomplete to verify correct spelling

**CORS errors:**
- Ensure backend is running on port 5000
- Check that Flask-CORS is installed

**Slow performance:**
- First search loads dictionary (~3 seconds)
- Subsequent searches are much faster
- Try limiting results to 25-50

**Port already in use:**
```powershell
# Find and kill process on port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

## Technical Details

### Backend Stack
- **Framework**: Flask 2.3.0
- **CORS**: Flask-CORS 4.0.0
- **Algorithm**: Feature-aware Levenshtein distance
- **Data Format**: JSONL (JSON Lines)

### Frontend Stack
- **HTML5** with semantic markup
- **CSS3** with gradients and animations
- **Vanilla JavaScript** (ES6+)
- **No external dependencies** (except for API calls)

### Algorithm Complexity
- Dictionary loading: O(n) where n = number of words
- Per-search: O(n × m²) where m = average rhyme tail length
- Typical: ~0.1-0.2 seconds for 18,000 words

## License

This project is provided as-is for educational and personal use.

## Contributing

Feel free to:
- Report bugs and issues
- Suggest improvements
- Add new rhyme categories
- Enhance the phoneme feature system

## Questions?

Check the API documentation above or examine the code comments in `backend.py` for implementation details.
