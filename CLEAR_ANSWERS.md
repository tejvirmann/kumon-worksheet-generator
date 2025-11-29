# Clear Answers ✅

## Question 1: Does normal PDF use LaTeX compiler?

**Answer: NO**

- Normal PDF tries LaTeX first
- But since LaTeX isn't installed, it **automatically falls back to ReportLab**
- ReportLab doesn't need a compiler - it's pure Python
- **So in your setup, normal PDF uses ReportLab, not LaTeX**

## Question 2: Why is 2-up failing?

**Answer: The ReportLab fallback needs pdf2image**

When you try 2-up:
1. ❌ Tries LaTeX first → fails (LaTeX not installed)
2. ❌ Tries ReportLab fallback → fails (pdf2image not installed)

**To fix 2-up, you need ONE of these:**

**Option 1: Install LaTeX (recommended)**
```bash
brew install --cask mactex
```
This gives you:
- Best quality PDFs
- Exact font matching
- Works for both normal PDF and 2-up

**Option 2: Install pdf2image for ReportLab fallback**
```bash
pip install pdf2image
brew install poppler
```
This lets 2-up use ReportLab instead of LaTeX.

## Summary

| Feature | What It Actually Uses | Needs |
|---------|----------------------|-------|
| Normal PDF | **ReportLab** (fallback from LaTeX) | Nothing - works! |
| 2-Up PDF | **Nothing** (both LaTeX and ReportLab fail) | Either LaTeX OR pdf2image |

## Recommendation

Install LaTeX once and everything works:
```bash
brew install --cask mactex
```

Then both normal PDF and 2-up will use LaTeX with perfect fonts! 🎯

