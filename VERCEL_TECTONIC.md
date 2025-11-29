# Vercel Deployment with Tectonic ✅

## Overview

The app now uses **Tectonic** as the primary LaTeX compiler, perfect for Vercel/serverless deployment!

## What Changed

1. ✅ **LaTeX compilation** now tries Tectonic first
2. ✅ **Build script** (`install_tectonic.sh`) installs Tectonic during Vercel build
3. ✅ **Fallback** to XeLaTeX/pdflatex for local development

## How It Works

### Compiler Priority:
1. **Tectonic** (best for Vercel) ⭐
2. XeLaTeX (local dev, custom fonts)
3. pdflatex (local dev fallback)

### Build Process:
1. Vercel runs `install_tectonic.sh` to download Tectonic binary
2. Installs Python dependencies
3. Deploys with Tectonic available

## Local Development

Install Tectonic locally:

```bash
# macOS
brew install tectonic

# Or use the install script
bash install_tectonic.sh
```

Then test:
```bash
tectonic --version
make run
```

## Vercel Deployment

1. **Push to GitHub** (or your Git provider)

2. **Deploy on Vercel**:
   ```bash
   vercel
   ```

3. **Set Environment Variables** in Vercel dashboard:
   - `OPENROUTER_API_KEY` = your API key
   - `AI_PROVIDER` = `openrouter`
   - `OPENAI_MODEL` = `openai/gpt-4`
   - `FLASK_ENV` = `production`

4. **Build will automatically**:
   - Download Tectonic binary
   - Install Python dependencies
   - Deploy with LaTeX support!

## Benefits

✅ **Serverless-friendly**: Tectonic is small and fast  
✅ **On-demand packages**: Downloads only what's needed  
✅ **Vercel-compatible**: Works perfectly on serverless functions  
✅ **Local fallback**: Still works with MacTeX locally  

## Troubleshooting

**Build fails on Vercel:**
- Check build logs for Tectonic installation
- Verify `install_tectonic.sh` is executable: `chmod +x install_tectonic.sh`

**Tectonic not found at runtime:**
- Tectonic should be in `~/.local/bin` or `/usr/local/bin`
- PATH should include these directories (handled automatically)

**Local development:**
- Install Tectonic: `brew install tectonic`
- Or use MacTeX: `brew install --cask mactex`

## Files Modified

- ✅ `latex_generator.py` - Tries Tectonic first
- ✅ `latex_print_layout.py` - Tries Tectonic first  
- ✅ `vercel.json` - Includes Tectonic installation in build
- ✅ `install_tectonic.sh` - Downloads and installs Tectonic

Ready to deploy! 🚀

