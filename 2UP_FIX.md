# 2-Up Print Layout Fix

## What You Want

- **Print Page 1**: Two front pages side-by-side
- **Print Page 2**: Two back pages side-by-side

When printed double-sided and cut, you get two identical worksheets.

## Current Status

The code has been updated to:
1. ✅ Use simple PDF layout first (pdf2image + ReportLab) - **most reliable**
2. ✅ Fallback to LaTeX (for Vercel)  
3. ✅ Fallback to ReportLab (if pdf2image available)

## How It Works Now

The 2-up layout tries methods in this order:

1. **`pdf_2up_layout.py`** - Simple, reliable method using pdf2image + ReportLab
   - Converts PDF pages to images
   - Places them side-by-side using ReportLab
   - **Most reliable method**

2. **`latex_print_layout.py`** - LaTeX method (for Vercel)
   - Uses pdfpages package with `nup=2x1`
   - Arranges pages side-by-side
   - Works on Vercel with Tectonic

3. **`print_layout.py`** - ReportLab fallback
   - Same as method 1, different implementation

## To Make It Work

The simplest way to get 2-up working immediately:

```bash
pip install pdf2image
brew install poppler
```

Then restart your Flask app and try the 2-up print layout!

## Testing

1. Generate a worksheet normally
2. Click "Generate Print Layout (2-up)" button
3. Should see two fronts on page 1, two backs on page 2 ✅

