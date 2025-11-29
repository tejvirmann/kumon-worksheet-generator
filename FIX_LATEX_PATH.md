# Fixing LaTeX PATH Issue

## Problem
MacTeX is installed but `pdflatex` command is not found.

## Solution

I've added the LaTeX path to your `.zshrc` file. Now you need to:

### 1. Reload your shell configuration:
```bash
source ~/.zshrc
```

### 2. Verify LaTeX is found:
```bash
which pdflatex
```

### 3. If still not found:

MacTeX might need the installer to run. Check if you need to run the installer:

```bash
open /opt/homebrew/Caskroom/mactex/2025.0308/
```

Or manually add the path:

```bash
export PATH="/Library/TeX/texbin:$PATH"
```

### 4. Restart your Flask app:

After LaTeX is working:
```bash
make run
```

### Alternative: Reinstall MacTeX

If the above doesn't work:

```bash
brew uninstall --cask mactex
brew install --cask mactex
```

Then restart your terminal completely.

