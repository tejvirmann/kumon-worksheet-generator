# How to Install LaTeX for 2-Up Print Layout

## Quick Fix

You need to install LaTeX to make the 2-up print layout work. Here's how:

### Option 1: Full LaTeX Installation (Recommended)

```bash
brew install --cask mactex
```

**Pros:**
- Complete LaTeX installation
- Everything you need included
- Best quality PDFs with perfect fonts

**Cons:**
- Large download (~4GB)
- Takes 10-15 minutes to install

### Option 2: Basic LaTeX (Lighter)

```bash
brew install basictex
```

**Pros:**
- Smaller download (~100MB)
- Faster installation

**Cons:**
- May need to install additional packages later
- Less complete than MacTeX

## After Installation

1. **Restart your terminal** (or run `source ~/.zshrc`)
2. **Verify installation:**
   ```bash
   which pdflatex
   which xelatex
   ```
3. **Restart the Flask app:**
   ```bash
   make run
   ```

## What This Fixes

- ✅ Normal PDF will use LaTeX (better fonts, perfect formatting)
- ✅ 2-up print layout will work
- ✅ All fonts will match Kumon worksheets exactly

## Alternative: Use ReportLab Fallback

If you don't want to install LaTeX, you can install pdf2image instead:

```bash
pip install pdf2image
brew install poppler
```

But LaTeX gives better quality and is recommended! 🎯

