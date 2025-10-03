#!/bin/bash
set -e  # Exit on error

echo "=== Building Secure Wipe ==="

# Build Rust Engine
echo "Building Rust Engine..."
cd rust_engine
cargo build --release
maturin develop  # Installs Python bindings (requires maturin: pip install maturin)
cd ..

# Python Setup
echo "Setting up Python..."
cd python_app
python -m venv env
# Activate (manual for cross-platform; adjust for Windows: env\Scripts\activate)
source env/bin/activate  # Linux/macOS
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
deactivate
cd ..

# Generate Keys (if not exist)
if [ ! -f "keys/private.pem" ]; then
    echo "Generating keys..."
    cd python_app/src
    python gen_keys.py
    cd ../..
    mkdir -p keys
    mv python_app/src/*.pem keys/
fi

# Build ISO
echo "Building Bootable ISO..."
cd iso_builder
./build_iso.sh
cd ..

# Optional: Build Distributables (requires pyinstaller: pip install pyinstaller)
echo "Building executables (optional)..."
cd python_app
pyinstaller --onefile --windowed --name SecureWipe main.py  # Outputs to dist/SecureWipe (adapt for platforms)
mkdir -p ../../dist/windows ../../dist/linux ../../dist/macos
mv dist/SecureWipe* ../../dist/windows/  # Example for Windows; adjust
cd ..

echo "Build complete! Run 'python python_app/main.py' for GUI or see docs/USAGE.md."