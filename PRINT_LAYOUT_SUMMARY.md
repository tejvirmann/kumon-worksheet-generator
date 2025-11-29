# 2-Up Print Layout Feature - Complete ✅

## What Was Implemented

Added a **2-up print layout** feature that creates a special PDF format for efficient double-sided printing and cutting.

## Layout Structure

```
Print Page 1:
┌─────────────────┬─────────────────┐
│  Worksheet 1    │  Worksheet 2    │
│  Front          │  Front          │
└─────────────────┴─────────────────┘

Print Page 2:
┌─────────────────┬─────────────────┐
│  Worksheet 1    │  Worksheet 2    │
│  Back           │  Back           │
└─────────────────┴─────────────────┘
```

**Result**: When printed double-sided and cut vertically, you get two identical complete worksheets!

## Files Created/Modified

### New Files
1. **`print_layout.py`** - Print layout generator module
   - Converts PDF pages to images using pdf2image
   - Places two pages side-by-side on each print page
   - Handles proper scaling and positioning

2. **`PRINT_LAYOUT_GUIDE.md`** - User guide with installation instructions

3. **`PRINT_LAYOUT_SUMMARY.md`** - This summary document

### Modified Files
1. **`app.py`**
   - Added `/api/generate-print-layout` endpoint
   - Handles print layout generation requests

2. **`templates/index.html`**
   - Added "Generate Print Layout (2-up)" button
   - Added print layout PDF viewer section
   - JavaScript to handle print layout generation

3. **`requirements.txt`**
   - Added `pdf2image==1.16.3`
   - Added `PyPDF2==3.0.1`

## How It Works

1. User generates a normal worksheet (front + back pages)
2. User clicks "Generate Print Layout (2-up)" button
3. System:
   - Converts worksheet PDF pages to images (300 DPI)
   - Creates new PDF with 2-up layout:
     - Page 1: Two front pages side-by-side
     - Page 2: Two back pages side-by-side
   - Scales pages to fit (each takes ~48% width)
4. User downloads and prints double-sided
5. User cuts vertically down the middle
6. Result: Two identical worksheets!

## Dependencies

### Required Python Package
- `pdf2image` - Converts PDF pages to images

### Required System Library
- `poppler` - PDF rendering library

**Installation:**
```bash
# macOS
brew install poppler
pip install pdf2image

# Linux
sudo apt-get install poppler-utils
pip install pdf2image

# Windows
# Download poppler from GitHub, then:
pip install pdf2image
```

## Usage

1. Generate a worksheet normally
2. After worksheet appears, click **"Generate Print Layout (2-up)"** button
3. Print layout PDF appears below with download link
4. Print double-sided, cut, and you're done!

## Technical Details

- **Scale Factor**: 0.48 (48% of page width per worksheet)
- **DPI**: 300 (high quality for printing)
- **Gap**: 0.1 inch margin between worksheets
- **Output Format**: Standard PDF (compatible with all printers)

## Benefits

✅ **Saves Paper**: Print two worksheets per sheet  
✅ **Time Efficient**: Print once, get two copies  
✅ **Professional**: Clean cut lines, proper alignment  
✅ **Versatile**: Works with all worksheet levels  

Perfect for teachers printing multiple worksheets for students!

