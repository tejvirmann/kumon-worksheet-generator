#!/bin/bash
# Install Tectonic for Vercel build
# This script downloads and installs Tectonic binary

set -e

echo "Installing Tectonic LaTeX engine..."

# Detect platform
ARCH=$(uname -m)
OS=$(uname -s)

if [ "$OS" = "Linux" ]; then
    # Vercel runs on Linux
    TECTONIC_URL="https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic@0.14.1/tectonic-x86_64-unknown-linux-musl.tar.gz"
    INSTALL_DIR="$HOME/.local/bin"
elif [ "$OS" = "Darwin" ]; then
    # macOS
    if [ "$ARCH" = "arm64" ]; then
        TECTONIC_URL="https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic@0.14.1/tectonic-aarch64-apple-darwin.tar.gz"
    else
        TECTONIC_URL="https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic@0.14.1/tectonic-x86_64-apple-darwin.tar.gz"
    fi
    INSTALL_DIR="/usr/local/bin"
fi

# Create install directory
mkdir -p "$INSTALL_DIR"

# Download and extract
echo "Downloading Tectonic..."
curl -L "$TECTONIC_URL" -o tectonic.tar.gz
tar xzf tectonic.tar.gz
chmod +x tectonic

# Move to install directory
if [ -w "$INSTALL_DIR" ]; then
    mv tectonic "$INSTALL_DIR/"
    echo "✅ Tectonic installed to $INSTALL_DIR"
else
    # Try user local bin if system bin is not writable
    USER_BIN="$HOME/.local/bin"
    mkdir -p "$USER_BIN"
    mv tectonic "$USER_BIN/"
    echo "✅ Tectonic installed to $USER_BIN"
    echo "Add to PATH: export PATH=\"\$HOME/.local/bin:\$PATH\""
fi

# Clean up
rm -f tectonic.tar.gz

# Verify installation
if command -v tectonic > /dev/null 2>&1 || [ -f "$INSTALL_DIR/tectonic" ] || [ -f "$HOME/.local/bin/tectonic" ]; then
    echo "✅ Tectonic installation successful!"
    tectonic --version 2>/dev/null || echo "Tectonic binary ready (add to PATH if needed)"
else
    echo "❌ Tectonic installation failed"
    exit 1
fi

