# Contributing to Armenian Rhyme Finder

**Note:** This is a **private repository**. Only authorized contributors with direct access can contribute.

Thank you for your interest in contributing to the Armenian Rhyme Finder project! We welcome contributions from team members, whether they're bug fixes, new features, documentation improvements, or other enhancements.

## How to Contribute

### 1. Clone the Repository
```powershell
git clone https://github.com/YOUR_USERNAME/armenian-rhyme-app.git
cd armenian-rhyme-app
```

### 2. Create a Branch
```powershell
git checkout -b feature/your-feature-name
# or for bug fixes:
git checkout -b fix/bug-description
```

Use descriptive branch names like:
- `feature/add-export-results`
- `fix/rhyme-score-calculation`
- `docs/improve-api-documentation`

### 3. Make Your Changes
- Write clear, readable code
- Follow the existing code style and patterns
- Add comments for complex logic
- Test your changes thoroughly

### 4. Commit Your Changes
```powershell
git add .
git commit -m "Clear, descriptive commit message"
```

**Commit message tips:**
- Start with a verb: "Add", "Fix", "Update", "Refactor"
- Be specific: "Fix IndexError in rhyme search" not "fix bug"
- Keep it under 72 characters for the main line

Examples:
```
Add toggle for including word tenses in search results
Fix empty list handling in definition field
Update backend documentation
Refactor rhyme similarity calculation for clarity
```

### 6. Push to Your Fork
```powershell
git push origin feature/your-feature-name
```

### 7. Create a Pull Request
1. Go to your forked repository on GitHub
2. Click "Compare & pull request"
3. Fill in the PR description:
   - **Title**: Clear summary of changes
   - **Description**: What changes did you make and why?
   - **Related issues**: Link to any related issues

### 8. Address Feedback
- Respond to comments and feedback
- Make requested changes and commit them
- Push updates to your branch

Once approved, your PR will be merged! 🎉

## Development Setup

### Prerequisites
- Python 3.7+
- pip (Python package manager)
- Git

### Installation
```powershell
# Clone the repository
git clone https://github.com/YOUR_USERNAME/armenian-rhyme-app.git
cd armenian-rhyme-app

# Install dependencies
pip install -r requirements.txt

# Run the application
python backend.py
```

## Code Style Guidelines

### Python
- Follow PEP 8 style guide
- Use meaningful variable names
- Add docstrings to functions
- Use type hints where possible

Example:
```python
def calculate_rhyme_score(word1_ipa: str, word2_ipa: str) -> float:
    """Calculate rhyme similarity score between two IPA transcriptions."""
    # Implementation
    pass
```

### JavaScript
- Use clear, descriptive variable names
- Add comments for complex logic
- Use const/let instead of var
- Follow consistent indentation (2 spaces)

### HTML/CSS
- Use semantic HTML
- Follow BEM naming convention for CSS classes
- Keep stylesheets organized
- Ensure responsive design

## Testing

Before submitting a PR, please test:
- The application runs without errors
- New features work as intended
- Existing features still work
- Edge cases are handled

For the rhyme finder, test with:
- Different Armenian words
- Words with various forms/tenses
- Including/excluding tenses toggle
- Different limit values

## Bug Reports

Found a bug? Please create an issue:

1. Go to the Issues tab
2. Click "New issue"
3. Provide:
   - **Title**: Clear bug description
   - **Description**: Steps to reproduce, expected behavior, actual behavior
   - **Screenshots**: If applicable
   - **Environment**: OS, Python version, browser

## Feature Requests

Have an idea? Create a feature request:

1. Go to the Issues tab
2. Click "New issue"
3. Use the feature request template
4. Clearly describe the feature and why it's useful

## Documentation

Improvements to documentation are always welcome!

- README.md: Project overview and setup
- API_DOCS.md: API endpoints and parameters
- ARCHITECTURE.md: System design and structure
- Code comments: Inline documentation

## Areas for Contribution

We'd especially appreciate contributions in:

1. **Performance Optimization**
   - Speed up rhyme searches
   - Optimize memory usage
   - Cache frequently used results

2. **Features**
   - Export results to different formats (CSV, JSON, PDF)
   - Advanced filtering options
   - Phoneme-by-phoneme similarity visualization
   - Batch rhyme search

3. **Testing**
   - Comprehensive unit tests
   - Integration tests
   - Performance benchmarks

4. **Documentation**
   - Better code examples
   - Video tutorials
   - FAQs and troubleshooting guides

5. **UI/UX**
   - Improved interface design
   - Better mobile responsiveness
   - Accessibility improvements
   - Dark mode support

6. **Localization**
   - Support for other languages
   - Internationalization (i18n)

## Project Structure

```
armenian-rhyme-app/
├── backend.py              # Flask API server
├── index.html              # Frontend interface
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── dictionary-hy.reordered.jsonl  # Armenian dictionary
├── README.md               # Project overview
├── API_DOCS.md            # API documentation
├── ARCHITECTURE.md        # System architecture
└── LICENSE                # MIT License
```

## Getting Help

- **Questions?** Create an issue with the "question" label
- **Need clarification?** Comment on relevant PRs or issues
- **Want to discuss?** Start a discussion in GitHub Discussions

## Recognition

Contributors will be:
- Added to the project's CONTRIBUTORS file
- Mentioned in release notes for significant contributions
- Given credit in relevant documentation

## Licensing

By contributing to this project, you agree that your contributions will be licensed under its MIT License.

---

Thank you for contributing! Your efforts help make the Armenian Rhyme Finder better for everyone. 💜
