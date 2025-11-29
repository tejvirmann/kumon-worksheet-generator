"""
Tectonic LaTeX Engine Setup
Downloads and installs Tectonic if not found (for serverless/Vercel)
"""

import os
import subprocess
import shutil
import urllib.request
import tarfile
import stat
from pathlib import Path

def ensure_tectonic():
    """Ensure Tectonic is available, download if needed"""
    # Check if tectonic is already in PATH
    tectonic_path = shutil.which('tectonic')
    if tectonic_path:
        return tectonic_path
    
    # Check common installation locations
    possible_paths = [
        os.path.expanduser('~/.local/bin/tectonic'),
        '/usr/local/bin/tectonic',
        '/opt/homebrew/bin/tectonic',
        './tectonic',
        '/tmp/tectonic'
    ]
    
    for path in possible_paths:
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path
    
    # Tectonic not found - download it (for serverless/Vercel)
    print("Tectonic not found, downloading...")
    return download_tectonic()

def download_tectonic():
    """Download Tectonic binary for current platform"""
    import platform
    
    system = platform.system()
    machine = platform.machine()
    
    # Determine download URL
    if system == "Linux":
        url = "https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic@0.14.1/tectonic-x86_64-unknown-linux-musl.tar.gz"
        install_dir = os.path.expanduser('~/.local/bin')
    elif system == "Darwin":
        if machine == "arm64":
            url = "https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic@0.14.1/tectonic-aarch64-apple-darwin.tar.gz"
        else:
            url = "https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic@0.14.1/tectonic-x86_64-apple-darwin.tar.gz"
        install_dir = os.path.expanduser('~/.local/bin')
    else:
        raise RuntimeError(f"Unsupported platform: {system} {machine}")
    
    # Create install directory
    os.makedirs(install_dir, exist_ok=True)
    tectonic_path = os.path.join(install_dir, 'tectonic')
    
    # Download if not already downloaded
    if not os.path.isfile(tectonic_path):
        print(f"Downloading Tectonic from {url}...")
        tar_path = '/tmp/tectonic.tar.gz'
        
        try:
            urllib.request.urlretrieve(url, tar_path)
            
            # Extract
            with tarfile.open(tar_path, 'r:gz') as tar:
                tar.extractall('/tmp')
            
            # Move binary
            extracted_binary = '/tmp/tectonic'
            if os.path.isfile(extracted_binary):
                shutil.move(extracted_binary, tectonic_path)
                os.chmod(tectonic_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP)
            else:
                raise FileNotFoundError("Tectonic binary not found in archive")
            
            # Clean up
            os.remove(tar_path)
            print(f"✅ Tectonic installed to {tectonic_path}")
            
        except Exception as e:
            raise RuntimeError(f"Failed to download Tectonic: {e}")
    
    # Add to PATH
    os.environ['PATH'] = f"{install_dir}:{os.environ.get('PATH', '')}"
    
    return tectonic_path

