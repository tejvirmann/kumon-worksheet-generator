# Troubleshooting Guide

## "make: python: No such file or directory"

This error means your system doesn't have `python` command, only `python3` (common on macOS).

### Solution 1: Use the updated Makefile (Recommended)

The Makefile has been updated to automatically detect `python3`. Just run:

```bash
make run
```

If it still doesn't work, try:

```bash
# Install dependencies first (this creates a virtual environment)
make install

# Then run
make run
```

### Solution 2: Use run-direct (No virtual environment)

If you want to skip the virtual environment:

```bash
make run-direct
```

This uses your system's `python3` directly.

### Solution 3: Run directly with python3

You can also run directly:

```bash
python3 app.py
```

Or with the virtual environment:

```bash
venv/bin/python3 app.py
```

## Check Your Python Installation

Verify Python 3 is installed:

```bash
python3 --version
# Should show: Python 3.x.x

which python3
# Should show: /opt/homebrew/bin/python3 (or similar)
```

## Virtual Environment Issues

If the virtual environment isn't working:

```bash
# Remove old venv
rm -rf venv

# Reinstall
make install

# Then run
make run
```

## Common Issues

### "Module not found" errors
```bash
# Make sure dependencies are installed
make install
```

### "OPENAI_API_KEY not set"
```bash
# Check .env file exists
cat .env

# Should have:
# OPENROUTER_API_KEY=your-key-here
# or
# OPENAI_API_KEY=your-key-here
```

### Port already in use
```bash
# Change port in .env
PORT=5001

# Or kill the process using port 5000
lsof -ti:5000 | xargs kill
```

## Still Having Issues?

1. Check you're in the right directory:
   ```bash
   pwd
   # Should be: .../kumon-worksheet-generator
   ```

2. Check Makefile exists:
   ```bash
   ls -la Makefile
   ```

3. Check Python version:
   ```bash
   python3 --version
   # Need Python 3.11 or higher
   ```

4. Try running Python directly:
   ```bash
   python3 -c "import flask; print('Flask installed')"
   ```

