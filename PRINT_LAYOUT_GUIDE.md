# 2-Up Print Layout Guide

## What is the Print Layout?

The print layout creates a special PDF format for efficient printing:
- **Print Page 1**: Two worksheet fronts side-by-side
- **Print Page 2**: Two worksheet backs side-by-side

When you print this double-sided and cut it in half, you get **two identical worksheets**.

## How to Use

1. **Generate a worksheet** normally
2. Click **"Generate Print Layout (2-up)"** button
3. Download the print layout PDF
4. Print double-sided
5. Cut down the middle vertically
6. You now have two complete worksheets!

## Layout Structure

```
Print Page 1 (Front):
┌─────────────────┬─────────────────┐
│  Worksheet 1    │  Worksheet 2    │
│  Front Page     │  Front Page     │
│                 │                 │
└─────────────────┴─────────────────┘

Print Page 2 (Back):
┌─────────────────┬─────────────────┐
│  Worksheet 1    │  Worksheet 2    │
│  Back Page      │  Back Page      │
│                 │                 │
└─────────────────┴─────────────────┘
```

After cutting:
- Left half = Worksheet 1 (front + back)
- Right half = Worksheet 2 (front + back)

## Installation Requirements

The print layout feature requires:
- `pdf2image` library
- `poppler` system library

### Install on macOS:
```bash
brew install poppler
pip install pdf2image
```

### Install on Linux:
```bash
sudo apt-get install poppler-utils
pip install pdf2image
```

### Install on Windows:
Download poppler from: https://github.com/oschwartz10612/poppler-windows/releases/
Then:
```bash
pip install pdf2image
```

## Troubleshooting

**Error: "pdf2image is required"**
- Install pdf2image: `pip install pdf2image`
- Install poppler (see above)

**Error: "poppler not found"**
- Install poppler system library (different from Python package)
- On macOS: `brew install poppler`
- On Linux: `sudo apt-get install poppler-utils`

**Print layout looks blurry**
- Increase DPI in `print_layout.py` (currently 300 DPI)
- Change: `convert_from_path(worksheet_pdf_path, dpi=300)` to higher value

## Notes

- The print layout duplicates the same worksheet twice (for identical copies)
- Scale is automatically adjusted to fit two pages side-by-side
- Small gap is left between pages for cutting margin
- Works with all Kumon worksheet styles (Level B through Level O)

