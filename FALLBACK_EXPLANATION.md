# PDF Generation: How It Works

## Normal Worksheet PDF Download

**Primary**: Tries LaTeX first
- Uses `LaTeXWorksheetGenerator` to create PDF with perfect typography
- Requires: LaTeX installed (XeLaTeX or pdflatex)

**Fallback**: If LaTeX fails, uses ReportLab
- Uses `WorksheetGenerator` (ReportLab-based)
- No external dependencies - works immediately!
- This is why your normal PDF downloads work ✅

## 2-Up Print Layout

**Primary**: Tries LaTeX first
- Uses `LaTeXPrintLayoutGenerator` with pdfpages package
- Requires: LaTeX installed

**Fallback**: If LaTeX fails, uses ReportLab + pdf2image
- Uses `PrintLayoutGenerator` (ReportLab-based)
- Requires: `pdf2image` Python package + `poppler` system library
- Requires: `pip install pdf2image` and `brew install poppler`

## Current Status

Since you don't have LaTeX installed:
- ✅ **Normal PDF**: Uses ReportLab (works!)
- ⚠️ **2-Up PDF**: Falls back to ReportLab, but needs pdf2image

To make 2-up work without LaTeX:
```bash
pip install pdf2image
brew install poppler
```

Or install LaTeX (better quality, matches fonts exactly):
```bash
brew install --cask mactex
```

## Summary

| Feature | Primary | Fallback | Status |
|---------|---------|----------|--------|
| Normal PDF | LaTeX | ReportLab | ✅ Works (uses ReportLab) |
| 2-Up PDF | LaTeX | ReportLab+pdf2image | ⚠️ Needs pdf2image or LaTeX |

