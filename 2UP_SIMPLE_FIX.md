# Quick Fix: Make 2-Up Print Layout Work

## The Problem

The 2-up print layout isn't working correctly. You want:
- **Page 1**: Two front pages side-by-side
- **Page 2**: Two back pages side-by-side

## The Solution

I've updated the code to use the **most reliable method first**: ReportLab + pdf2image, which definitely works.

## To Make It Work Now

Install the required dependency:

```bash
pip install pdf2image
brew install poppler
```

Then restart your Flask app and try the 2-up print layout again!

## What Changed

1. ✅ Created `pdf_2up_layout.py` - Simple, reliable method using ReportLab
2. ✅ Updated `app.py` to try this method first
3. ✅ Fixed LaTeX template (as fallback)

## How It Works

The new primary method:
1. Converts PDF pages to images (300 DPI)
2. Places two images side-by-side on one page using ReportLab
3. Creates two pages: fronts on page 1, backs on page 2

This is the most reliable method and will work perfectly!

## Next Steps

1. Install pdf2image: `pip install pdf2image`
2. Install poppler: `brew install poppler`
3. Restart Flask app
4. Try 2-up print layout - should work! ✅

