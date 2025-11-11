# GitHub Setup Guide

## Overview
Your Armenian Rhyme Finder project is now ready to be pushed to GitHub! Follow these steps to get your repository online.

## Prerequisites
- GitHub account (create one at https://github.com/signup if you don't have one)
- Git installed on your computer (you already have this!)

## Steps to Push to GitHub

### 1. Create a New Repository on GitHub
1. Go to [https://github.com/new](https://github.com/new)
2. Log in with your GitHub account
3. Fill in the repository details:
   - **Repository name**: `armenian-rhyme-app` (or your preferred name)
   - **Description**: "A web app for finding Armenian rhyming words using phoneme-based similarity"
   - **Visibility**: Choose "Public" (if you want others to see it) or "Private"
   - **Don't initialize** with README, .gitignore, or license (we already have these)
4. Click **Create repository**

### 2. Add Remote and Push to GitHub
GitHub will show you commands to push an existing repository. Use these exact commands:

```powershell
# Replace YOUR_USERNAME and YOUR_REPO_NAME with your actual values
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

**Example** (replace with your actual username):
```powershell
git remote add origin https://github.com/NazaniCode/armenian-rhyme-app.git
git branch -M main
git push -u origin main
```

### 3. Authenticate with GitHub
When prompted, choose one of these authentication methods:

#### Option A: Personal Access Token (Recommended)
1. Go to GitHub Settings → Developer settings → [Personal access tokens](https://github.com/settings/tokens)
2. Click **Generate new token**
3. Select scopes: `repo` (full control of private repositories)
4. Copy the token and paste it as your password when Git prompts

#### Option B: SSH Key (More Secure)
1. Follow GitHub's [SSH setup guide](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)
2. Then use SSH URL instead:
```powershell
git remote add origin git@github.com:YOUR_USERNAME/YOUR_REPO_NAME.git
```

### 4. Verify the Push
After pushing, verify your repository is on GitHub:
```powershell
git remote -v
```

You should see:
```
origin  https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git (fetch)
origin  https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git (push)
```

Visit your repository at: `https://github.com/YOUR_USERNAME/YOUR_REPO_NAME`

## Future Commits

Now that your repository is set up, future commits are easy:

```powershell
# Make changes to your files
# Stage changes
git add .

# Commit with a message
git commit -m "Your descriptive commit message"

# Push to GitHub
git push
```

## Example Workflow

```powershell
# Edit index.html
# Stage the change
git add index.html

# Commit
git commit -m "Update UI with better styling"

# Push to GitHub
git push
```

## Useful Git Commands

### View commit history
```powershell
git log --oneline
git log --graph --oneline --all
```

### Check status
```powershell
git status
```

### View remote configuration
```powershell
git remote -v
```

### Change remote URL (if needed)
```powershell
git remote set-url origin https://github.com/NEW_USERNAME/NEW_REPO.git
```

## Adding a License

Consider adding a license to your repository:

1. Create a file `LICENSE` in your project root
2. Popular options for open-source projects:
   - **MIT License** (permissive, most popular)
   - **Apache 2.0** (permissive with patent protection)
   - **GPL 3.0** (copyleft)

You can find license templates at [choosealicense.com](https://choosealicense.com/)

## Adding GitHub Topics

To help others find your project:
1. Go to your GitHub repository settings
2. Scroll to "Repository topics"
3. Add relevant topics like: `armenian`, `rhyme`, `phonetics`, `nlp`, `web-app`

## Enabling GitHub Pages (Optional)

To host your web app directly from GitHub:
1. Go to Settings → Pages
2. Select "master/main" branch as the source
3. Your site will be available at `https://YOUR_USERNAME.github.io/YOUR_REPO_NAME`

## Troubleshooting

### "remote origin already exists"
```powershell
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
```

### Authentication errors
- Update Git credentials in Windows Credential Manager
- Or use GitHub CLI: `gh auth login`

### Need to update files after push?
```powershell
# Make changes
git add .
git commit -m "Your message"
git push
```

## Next Steps

After pushing to GitHub, consider:
1. ✅ Add a CONTRIBUTING.md file for contributors
2. ✅ Set up GitHub Issues for bug tracking
3. ✅ Create GitHub Discussions for community questions
4. ✅ Add CI/CD with GitHub Actions
5. ✅ Create releases and tags for version control

## Questions?

Refer to:
- [GitHub Docs](https://docs.github.com)
- [Git Documentation](https://git-scm.com/doc)
- Your local Git help: `git help`
