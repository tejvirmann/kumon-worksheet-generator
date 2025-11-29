# Tectonic Setup for Vercel Deployment

## What is Tectonic?

Tectonic is a modern LaTeX engine designed for serverless platforms like Vercel:
- ✅ 100% LaTeX compatible
- ✅ Small size (downloads packages on demand)
- ✅ Fast and deterministic
- ✅ Works perfectly on Vercel/serverless
- ✅ Cross-platform (Linux-friendly)

## How It Works

The code now tries compilers in this order:
1. **Tectonic** (best for Vercel/serverless) ⭐
2. XeLaTeX (local development, custom fonts)
3. pdflatex (local development fallback)

## Installing Tectonic

### For Vercel (Automatic)

Tectonic will be installed during Vercel build. We'll add it to the build process.

### For Local Development

**macOS:**
```bash
brew install tectonic
```

**Linux:**
```bash
# Download from releases
curl -L https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic@0.14.1/tectonic-x86_64-unknown-linux-musl.tar.gz | tar xz
sudo mv tectonic /usr/local/bin/
```

**Or use cargo:**
```bash
cargo install tectonic
```

## Vercel Deployment Setup

Add Tectonic installation to your Vercel build. Create a `build.sh` script or add to `vercel.json` build command.

### Option 1: Download Tectonic in Build Script

Create `build.sh`:
```bash
#!/bin/bash
# Download Tectonic for Linux (Vercel runs on Linux)
curl -L https://github.com/tectonic-typesetting/tectonic/releases/latest/download/tectonic-x86_64-unknown-linux-musl.tar.gz -o tectonic.tar.gz
tar xzf tectonic.tar.gz
chmod +x tectonic
mv tectonic /usr/local/bin/tectonic || mv tectonic ~/.local/bin/tectonic
```

Update `vercel.json` to run build script.

### Option 2: Use Vercel Build Command

Add to `vercel.json`:
```json
{
  "buildCommand": "curl -L https://github.com/tectonic-typesetting/tectonic/releases/latest/download/tectonic-x86_64-unknown-linux-musl.tar.gz | tar xz && chmod +x tectonic && mkdir -p ~/.local/bin && mv tectonic ~/.local/bin/ && export PATH=\"$HOME/.local/bin:$PATH\" && pip install -r requirements.txt"
}
```

## Benefits

1. **Vercel-Ready**: Works out of the box on serverless
2. **Small Size**: Downloads only needed packages
3. **Fast**: Optimized compilation
4. **Reliable**: Deterministic builds

## Testing Locally

1. Install Tectonic: `brew install tectonic`
2. Test compilation:
   ```bash
   tectonic --help
   ```
3. Generate a worksheet - it will use Tectonic automatically!

## Verification

After setup, verify Tectonic is found:
```bash
which tectonic
tectonic --version
```

## Notes

- Tectonic uses its own package cache (in `~/.cache/Tectonic/`)
- First compilation may be slower (downloads packages)
- Subsequent compilations are fast (uses cached packages)
- 100% compatible with standard LaTeX documents

