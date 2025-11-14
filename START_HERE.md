# 🎵 Armenian Rhyme Finder - START HERE

Welcome! This document will guide you through everything you need to know about the Armenian Rhyme Finder application.

---

## ⚡ Quick Start (5 Minutes)

### Windows Users (Easiest)
1. **Double-click**: `start.bat` in this folder
2. **Wait** for message "Running on http://127.0.0.1:5000"
3. **Open**: `index.html` in your browser
4. **Start searching** for Armenian words!

### Other Operating Systems
```bash
pip install -r requirements.txt
python app.py
```
Then open `index.html` in your browser.

---

## 📚 Documentation Guide

Read these in order based on your needs:

### 🆕 **I'm New - Where Do I Start?**
1. **QUICK_START.txt** ← Start here! (5 min read)
   - Fastest way to get running
   - Troubleshooting tips
   - Common questions

2. **SETUP_GUIDE.md** (30 min read)
   - Step-by-step installation
   - Multiple setup methods
   - Detailed troubleshooting
   - Advanced configuration

### 👨‍💻 **I Want to Understand the Code**
1. **README.md** (20 min read)
   - Full documentation
   - Feature overview
   - Algorithm explanation
   - File structure

2. **ARCHITECTURE.md** (30 min read)
   - System design
   - Data flow diagrams
   - Component architecture
   - Performance analysis

3. **app.py** (1 hour study)
   - Actual implementation
   - Well-commented code
   - Algorithm details

### 🔌 **I Want to Use the API**
1. **API_DOCS.md** (20 min read)
   - Complete API reference
   - All endpoints documented
   - Code examples (Python, JavaScript, cURL)
   - Error handling

2. **test_rhymes.py** (reference)
   - Example API usage
   - Test cases
   - Run with: `python test_rhymes.py`

### 📦 **I Want to Deploy or Modify**
1. **PROJECT_SUMMARY.md** (30 min read)
   - Complete project overview
   - Deployment guide
   - Configuration options
   - Performance tips

2. **config.py** (edit to customize)
   - All settings in one place
   - Adjust rhyme thresholds
   - Change port, debug mode, etc.

### 📋 **What Files Were Created?**
1. **FILES_CREATED.md** (reference)
   - Every file explained
   - File statistics
   - Quick lookup table

---

## 🎯 File Quick Reference

| File | Purpose | Time to Read |
|------|---------|--------------|
| **QUICK_START.txt** | Fastest setup guide | 5 min |
| **SETUP_GUIDE.md** | Detailed setup | 30 min |
| **README.md** | Complete documentation | 20 min |
| **ARCHITECTURE.md** | System design & flow | 30 min |
| **API_DOCS.md** | REST API reference | 20 min |
| **PROJECT_SUMMARY.md** | Project overview | 30 min |
| **FILES_CREATED.md** | File listing | 10 min |
| **START_HERE.md** | This file | 5 min |

---

## 💻 File Purposes

### Application Files
- **app.py** - Main Flask backend (330 lines) - **RUN THIS**
- **backend.py** - Alternative backend (280 lines)
- **index.html** - Web interface (450 lines) - **OPEN IN BROWSER**
- **config.py** - Configuration settings (180 lines) - **EDIT TO CUSTOMIZE**
- **requirements.txt** - Python packages - **pip install -r requirements.txt**

### Launch Scripts
- **start.bat** - Windows launcher - **DOUBLE-CLICK ON WINDOWS**
- **start.ps1** - PowerShell launcher
- **test_rhymes.py** - Test suite (300 lines) - **python test_rhymes.py**

### Data
- **dictionary-hy-improved.jsonl** - 18,831 Armenian words (required)

---

## 🚀 Getting Started Now

### Option 1: Windows (Fastest)
```
1. Double-click: start.bat
2. Open: index.html
3. Done! ✓
```

### Option 2: Command Line
```powershell
# Install dependencies
pip install -r requirements.txt

# Start backend
python app.py

# In browser, open:
# file:///c:/Users/Nazani/Desktop/armenian-rhyme-app/index.html
```

### Option 3: With Local HTTP Server
```powershell
# Terminal 1: Start backend
python app.py

# Terminal 2: Start HTTP server
python -m http.server 8000

# Browser: http://localhost:8000
```

---

## ❓ Common Questions

### "Where do I go first?"
→ Read **QUICK_START.txt** (5 minutes)

### "How do I set it up?"
→ Follow **SETUP_GUIDE.md** (step-by-step)

### "What does it do?"
→ Read **README.md** (complete overview)

### "How do I use the API?"
→ Check **API_DOCS.md** (with code examples)

### "How does it work internally?"
→ Study **ARCHITECTURE.md** (system design)

### "What was created?"
→ See **FILES_CREATED.md** (file inventory)

### "What's the project about?"
→ Read **PROJECT_SUMMARY.md** (project overview)

### "I have an error!"
→ Check **SETUP_GUIDE.md** → Troubleshooting section

---

## 🎯 Learning Path

### Path 1: Just Want to Use It
```
QUICK_START.txt
    ↓
Open index.html
    ↓
Start searching!
```
⏱️ **Time: 10 minutes**

### Path 2: Understand What's Inside
```
QUICK_START.txt
    ↓
README.md
    ↓
ARCHITECTURE.md
    ↓
Review app.py
```
⏱️ **Time: 2 hours**

### Path 3: Build With the API
```
QUICK_START.txt
    ↓
API_DOCS.md
    ↓
test_rhymes.py
    ↓
Write your code
```
⏱️ **Time: 1-2 hours**

### Path 4: Deploy to Production
```
README.md
    ↓
PROJECT_SUMMARY.md
    ↓
Edit config.py
    ↓
Deploy with Gunicorn
```
⏱️ **Time: 3-4 hours**

---

## 🔍 How the App Works

### Simple Explanation
1. **You search** for an Armenian word
2. **App extracts** its sound (IPA phonemes)
3. **App compares** to all dictionary words
4. **App finds** words that sound similar
5. **Results sorted** by how much they rhyme

### Rhyme Types
- **Perfect** 🎯 - Sounds identical
- **Near-Perfect** ⭐ - Very similar + same vowel
- **Assonance** 💫 - Same vowel sound
- **Slant** 📍 - Similar consonants/vowels

### Example
Search: "սեր" (love)
Results: "հեր" (master), "շերտ" (layer), "սուր" (sharp), etc.

---

## 🛠️ Main Features

✅ **Smart Rhyme Detection**
- Uses IPA phonetics
- Feature-aware comparison
- Multiple rhyme types

✅ **Fast Search**
- 50-200ms per search
- 18,831 Armenian words
- Real-time autocomplete

✅ **Beautiful Interface**
- Modern responsive design
- Color-coded results
- Mobile-friendly

✅ **REST API**
- 5 endpoints
- Autocomplete support
- Full documentation

✅ **Well Documented**
- 2,000+ lines of docs
- Code examples
- Architecture diagrams

---

## 📊 Project Stats

| Metric | Value |
|--------|-------|
| **Code Lines** | ~1,650 |
| **Documentation** | ~2,000 lines |
| **Dictionary Size** | 18,831 words |
| **API Endpoints** | 5 |
| **Supported Rhyme Types** | 4 |
| **Response Time** | 50-200ms |
| **Setup Time** | 5-30 minutes |

---

## 🎓 What You'll Learn

By exploring this project, you'll learn about:

- 🎵 **Phonetics**: How to analyze Armenian sounds
- 🔤 **IPA**: International Phonetic Alphabet
- 📏 **Algorithms**: Levenshtein distance, dynamic programming
- 🌐 **Web Development**: Flask backend + vanilla JS frontend
- 📱 **UI/UX**: Responsive design, autocomplete
- 🔌 **REST APIs**: Building and consuming APIs
- 🗂️ **System Design**: Architecture, data flow, performance

---

## 🆘 Troubleshooting Quick Links

### Issue: "Python not found"
→ Read **SETUP_GUIDE.md** → "Troubleshooting" → "Python not found"

### Issue: "Module not found: flask"
→ Run: `pip install -r requirements.txt`

### Issue: "Dictionary not found"
→ Verify `dictionary-hy-improved.jsonl` exists in folder

### Issue: "Port 5000 already in use"
→ Read **SETUP_GUIDE.md** → "Troubleshooting" → "Port already in use"

### Issue: "No results found"
→ Read **SETUP_GUIDE.md** → "Troubleshooting" → "Search returns no results"

### More issues?
→ Full troubleshooting in **SETUP_GUIDE.md**

---

## 🎯 Next Steps

### Right Now:
1. Read **QUICK_START.txt** (5 min)
2. Run **start.bat** (Windows) or `python app.py`
3. Open **index.html** in browser
4. Try a search!

### In the Next Hour:
1. Explore the web interface
2. Try different Armenian words
3. Read **README.md** for full understanding
4. Check **API_DOCS.md** if interested in API

### Later:
1. Read **ARCHITECTURE.md** for deep understanding
2. Study **app.py** for implementation details
3. Customize **config.py** for your needs
4. Deploy to production if desired

---

## 📞 Support Resources

**Documentation Files:**
- `QUICK_START.txt` - Fast reference
- `SETUP_GUIDE.md` - Detailed guide
- `README.md` - Full documentation
- `API_DOCS.md` - API reference
- `ARCHITECTURE.md` - System design
- `PROJECT_SUMMARY.md` - Project overview

**Code & Tests:**
- `app.py` - Main backend
- `test_rhymes.py` - Test suite + examples
- `config.py` - Configuration

**Error Messages:**
1. Check the error message
2. Search in **SETUP_GUIDE.md** → Troubleshooting
3. Check `rhyme_finder.log` for details
4. Review comments in `app.py`

---

## 🎉 Ready to Get Started?

### For Immediate Setup:
👉 **Go to: QUICK_START.txt**

### For Complete Guide:
👉 **Go to: SETUP_GUIDE.md**

### For Understanding the Code:
👉 **Go to: README.md**

### For Using the API:
👉 **Go to: API_DOCS.md**

---

## 📝 Document Index

```
START_HERE.md          ← You are here
├─ QUICK_START.txt     ← Go here first!
├─ SETUP_GUIDE.md      ← For detailed setup
├─ README.md           ← Full documentation
├─ API_DOCS.md         ← For developers
├─ ARCHITECTURE.md     ← System design
├─ PROJECT_SUMMARY.md  ← Project overview
└─ FILES_CREATED.md    ← File inventory
```

---

## ✨ Features at a Glance

### Search Capabilities
✅ Autocomplete suggestions  
✅ Fast rhyme detection  
✅ Multiple rhyme types  
✅ Similarity scores  
✅ Word definitions  

### Technical Features
✅ Feature-aware algorithm  
✅ REST API with 5 endpoints  
✅ Caching optimization  
✅ CORS enabled  
✅ Error handling  

### User Experience
✅ Beautiful responsive UI  
✅ Color-coded results  
✅ Mobile-friendly design  
✅ Real-time autocomplete  
✅ Loading indicators  

---

## 🚀 Your Journey Starts Now!

1. **Just opened this folder?** → Read **QUICK_START.txt**
2. **Want to set up?** → Follow **SETUP_GUIDE.md**
3. **Want full info?** → Read **README.md**
4. **Want to code?** → Check **API_DOCS.md**
5. **Want the details?** → Study **ARCHITECTURE.md**

---

**Happy Rhyming! 🎵**

Questions? Check the relevant documentation file above.

Still stuck? See the troubleshooting section in **SETUP_GUIDE.md**.

---

*Armenian Rhyme Finder - Making Armenian Poetry Search Easy*

Last Updated: 2024
