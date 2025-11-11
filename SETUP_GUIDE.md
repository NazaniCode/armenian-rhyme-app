# Armenian Rhyme Finder - Complete Setup Guide

A complete guide to setting up and running the Armenian Rhyme Finder web application.

## Table of Contents
1. [Quick Start (5 minutes)](#quick-start)
2. [Detailed Setup](#detailed-setup)
3. [Running the Application](#running-the-application)
4. [Troubleshooting](#troubleshooting)
5. [Advanced Configuration](#advanced-configuration)

---

## Quick Start

### Windows (Easiest Method)

1. **Double-click `start.bat`** in the project folder
2. Wait for the server to start (you'll see "Running on http://127.0.0.1:5000")
3. Open your browser to: `file:///c:/Users/Nazani/Desktop/armenian-rhyme-app/index.html`
4. Start searching for rhymes!

### Windows with PowerShell

```powershell
# Navigate to the project folder
cd c:\Users\Nazani\Desktop\armenian-rhyme-app

# Run the PowerShell start script
.\start.ps1
```

### macOS/Linux

```bash
cd ~/Desktop/armenian-rhyme-app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open `index.html` in your browser.

---

## Detailed Setup

### Prerequisites

- **Python 3.7+** ([Download here](https://www.python.org/downloads/))
- **Modern web browser** (Chrome, Firefox, Safari, Edge)
- The `dictionary-hy.cleaned.jsonl` file (should already be in the folder)

### Step 1: Verify Python Installation

**Windows:**
```powershell
python --version
```

**macOS/Linux:**
```bash
python3 --version
```

You should see: `Python 3.x.x` (x.x = any version ≥ 3.7)

If not installed, download from [python.org](https://python.org)

### Step 2: Install Dependencies

**Windows:**
```powershell
cd c:\Users\Nazani\Desktop\armenian-rhyme-app
pip install -r requirements.txt
```

**macOS/Linux:**
```bash
cd ~/Desktop/armenian-rhyme-app
pip3 install -r requirements.txt
```

You should see:
```
Successfully installed Flask-2.3.0 Flask-CORS-4.0.0 Werkzeug-2.3.0
```

### Step 3: Verify Dictionary File

Check that `dictionary-hy.cleaned.jsonl` is in the project folder:
- File size: ~30-50 MB
- Contains 18,831 Armenian words with IPA phonetic transcriptions

**Windows:**
```powershell
ls dictionary-hy.cleaned.jsonl
```

**macOS/Linux:**
```bash
ls -lh dictionary-hy.cleaned.jsonl
```

---

## Running the Application

### Method 1: Batch File (Windows - Easiest)

Simply double-click: **`start.bat`**

The batch file will:
- Check Python installation
- Install dependencies if needed
- Start the backend server
- Tell you how to open the frontend

### Method 2: Command Line

**Windows:**
```powershell
python app.py
```

**macOS/Linux:**
```bash
python3 app.py
```

You should see:
```
Loading dictionary from dictionary-hy.cleaned.jsonl
Successfully loaded 18831 words
Starting Flask app on 127.0.0.1:5000
 * Running on http://127.0.0.1:5000
```

### Method 3: Using the Simpler Backend (Original)

If you want to use the simpler `backend.py` instead of `app.py`:

```powershell
python backend.py
```

---

## Opening the Frontend

### Option A: File URL (No Server Needed)

Open your browser and navigate to:
```
file:///c:/Users/Nazani/Desktop/armenian-rhyme-app/index.html
```

Or simply drag-and-drop `index.html` into your browser.

### Option B: Local HTTP Server (Better for Testing)

While the backend server is running, open a **new terminal** and run:

**Windows:**
```powershell
cd c:\Users\Nazani\Desktop\armenian-rhyme-app
python -m http.server 8000
```

**macOS/Linux:**
```bash
cd ~/Desktop/armenian-rhyme-app
python3 -m http.server 8000
```

Then visit: `http://localhost:8000`

---

## Testing the Setup

### Quick Test Without Browser

```powershell
python test_rhymes.py
```

This will:
- Load the dictionary
- Run algorithm tests
- Show example searches
- Print statistics

**Expected output:**
```
█ Armenian Rhyme Finder - Test Suite
Loaded 18831 words from dictionary

TEST: Rhyme Tail Extraction
✓ Input: b i kʰ ə v a r k
  Expected tail: ['a', 'r', 'k']
  Got tail: ['a', 'r', 'k']
...
```

### Search for Specific Word

Create a test script `test_search.py`:

```python
from app import load_dictionary, find_rhymes

load_dictionary('dictionary-hy.cleaned.jsonl')

# Search for rhymes
word = 'գլուխ'  # Change this to any Armenian word
rhymes = find_rhymes(word, limit=10)

print(f"Rhymes for '{word}':")
for rhyme in rhymes:
    print(f"  {rhyme['word']:<20} {rhyme['label']:<12} {rhyme['similarity']}")
```

Run it:
```powershell
python test_search.py
```

---

## Using the Web Application

### 1. Enter a Word
- Type an Armenian word in the search box
- Autocomplete suggestions will appear
- Select one or press Enter

### 2. View Results
Results are sorted by rhyme quality:
- **Perfect** 🎯 - Identical sound
- **Near-Perfect** ⭐ - Very similar + same vowel
- **Assonance** 💫 - Same vowel + good similarity
- **Slant** 📍 - Consonant-driven similarity

### 3. Adjust Settings
- **Results**: Choose 10, 25, 50, or 100 rhymes
- Each result shows:
  - Word in Armenian
  - Rhyme type (badge)
  - Similarity score (0-100%)
  - Part of speech
  - Definition

---

## Troubleshooting

### Problem: "Python not found"

**Solution:**
- Install Python from [python.org](https://www.python.org/downloads)
- **Important**: Check "Add Python to PATH" during installation
- Restart your terminal after installing

### Problem: "ModuleNotFoundError: No module named 'flask'"

**Solution:**
```powershell
pip install -r requirements.txt
```

Or install manually:
```powershell
pip install Flask==2.3.0
pip install Flask-CORS==4.0.0
```

### Problem: "dictionary-hy.cleaned.jsonl not found"

**Solution:**
- Verify the file is in the project directory:
  ```powershell
  ls dictionary-hy.cleaned.jsonl
  ```
- Check the filename spelling matches exactly
- File should be ~30-50 MB

### Problem: "Port 5000 already in use"

**Solution:**

Find and stop the process:

**Windows:**
```powershell
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

Replace `<PID>` with the number shown.

Or change the port in `config.py`:
```python
FLASK_PORT = 5001  # Use different port
```

### Problem: Backend starts but frontend shows "Cannot connect"

**Solutions:**
1. Ensure backend is running (should see "Running on http://127.0.0.1:5000")
2. Check CORS is enabled (should be in `app.py`)
3. Try using `http://localhost:5000` instead of `127.0.0.1`
4. Disable browser cache (Ctrl+Shift+Delete)

### Problem: Slow search or high memory usage

**Solutions:**
- Dictionary loads once (~3 seconds)
- Subsequent searches are fast
- If very slow, check system resources
- Reduce `MAX_RESULT_LIMIT` in `config.py`

### Problem: Search returns no results

**Possible causes:**
- Word not in dictionary (try autocomplete)
- Word has no similar-sounding forms
- Try different rhyme types (click badges to filter)

**Solution:**
- Use autocomplete to find words that exist
- Try common words first: գլուխ, սեր, լույս
- Check definition to verify it's the right word

---

## Advanced Configuration

### Customizing Thresholds

Edit `config.py`:

```python
RHYME_THRESHOLDS = {
    'near_perfect': 0.85,  # Increase for stricter near-perfect
    'assonance': 0.6,      # Increase for stricter assonance
    'slant': 0.5,          # Increase for stricter slant
    'minimum': 0.3,        # Minimum to include results
}
```

Lower values = more (but weaker) matches
Higher values = fewer but stronger matches

### Changing Server Port

Edit `config.py`:

```python
FLASK_PORT = 8000  # Change from 5000 to 8000
```

Then restart the server.

### Disabling Debug Mode

In production, disable debug mode in `config.py`:

```python
FLASK_DEBUG = False  # Security: disable in production
```

### Adding Custom Phoneme Features

Edit `config.py` to add new consonants or vowels:

```python
CONSONANTS = {
    # ... existing entries ...
    'nʰ': ('alveolar', 'nasal'),  # New entry
}

VOWEL_FEATURES = {
    # ... existing entries ...
    'ɪ': ('near-close', 'front'),  # New entry
}
```

---

## File Structure Explained

```
armenian-rhyme-app/
├── app.py                      # Main Flask backend (with config)
├── backend.py                  # Simpler Flask backend (alternative)
├── index.html                  # Web interface
├── config.py                   # Configuration file
├── test_rhymes.py              # Test suite
├── requirements.txt            # Python dependencies
├── start.bat                   # Quick start for Windows
├── start.ps1                   # PowerShell start script
├── README.md                   # Project documentation
├── SETUP_GUIDE.md             # This file
├── dictionary-hy.cleaned.jsonl # Armenian dictionary (18,831 words)
└── (other files)               # Data processing scripts
```

### Key Files

| File | Purpose |
|------|---------|
| `app.py` | Main backend (recommended) |
| `backend.py` | Simpler backend alternative |
| `index.html` | Web interface (open in browser) |
| `config.py` | Settings and thresholds |
| `dictionary-hy.cleaned.jsonl` | Word database |
| `test_rhymes.py` | Test and demo script |

---

## Performance Tips

### Speed Up Dictionary Loading
- First run loads dictionary (~3 seconds)
- Subsequent searches are cached (~50-200ms)
- Keep backend running while testing

### Reduce Memory Usage
- Backend uses ~200-300 MB RAM for dictionary
- Browser cache uses minimal space
- Close other applications if low on RAM

### Improve Web Performance
1. **Clear browser cache** - sometimes stale results
2. **Use modern browser** - Chrome/Firefox fastest
3. **Disable extensions** - can interfere with requests
4. **Use local HTTP server** - slightly faster than file://

---

## Getting Help

### Check the Logs

**Backend logs:**
```
rhyme_finder.log  # Created by app.py
```

**Browser console:**
- Press F12
- Click "Console" tab
- Look for error messages

### Debug Search Issues

Test directly with Python:

```python
from app import load_dictionary, find_rhymes

load_dictionary('dictionary-hy.cleaned.jsonl')
rhymes = find_rhymes('test_word', limit=5)
print(rhymes)
```

### API Testing

Test API directly:
```
http://localhost:5000/api/stats
http://localhost:5000/api/search?q=բա
http://localhost:5000/api/rhymes?word=սեր&limit=10
```

---

## Next Steps

1. ✅ Complete the setup above
2. 🔍 Try the web interface
3. 📚 Explore different Armenian words
4. ⚙️ Customize settings in `config.py`
5. 🛠️ Check `test_rhymes.py` for advanced usage

---

## Support

For issues or questions:
1. Check this setup guide
2. Run `test_rhymes.py` to verify setup
3. Check `rhyme_finder.log` for backend errors
4. Review `app.py` comments for implementation details

Good luck! 🎵
