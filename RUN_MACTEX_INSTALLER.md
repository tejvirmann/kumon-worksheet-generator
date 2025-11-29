# Run MacTeX Installer

## What Just Happened

I found the MacTeX installer package and opened it for you. You should see a MacTeX installer window.

## What to Do Next

1. **Follow the installer prompts**:
   - Click "Continue" through the installation
   - Enter your password when prompted
   - Wait for installation to complete (~10-15 minutes, ~4GB)

2. **After installation completes**:
   - Close the installer
   - **Restart your terminal completely** (quit and reopen it)

3. **Verify LaTeX is installed**:
   ```bash
   which pdflatex
   which xelatex
   ```
   Both should show paths like `/Library/TeX/texbin/pdflatex`

4. **Restart your Flask app**:
   ```bash
   make run
   ```

5. **Try 2-up print layout again** - it should work now! ✅

## Note

I've already added the LaTeX path to your `.zshrc` file, so after you restart your terminal, everything should work automatically.

---

**The installer is now opening. Just follow the prompts!** 🚀

