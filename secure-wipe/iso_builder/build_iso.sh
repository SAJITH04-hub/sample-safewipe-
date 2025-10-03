#!/bin/bash
set -e

echo "=== Building Bootable Secure Wipe ISO ==="

# Compile Rust CLI binary
cd ../rust_engine
cargo build --release --bin wipe_cli
cp target/release/wipe_cli ../iso_builder/boot/
cd ../iso_builder

# Use Docker for reproducible build (fallback to local if Docker available)
if command -v docker &> /dev/null; then
    echo "Using Docker to build ISO..."
    docker build -t secure-wipe-iso-builder .
    docker run --rm -v $(pwd)/output:/output secure-wipe-iso-builder
else
    echo "Docker not found. Building locally (requires GRUB tools)..."
    # Local build: Assume GRUB installed
    grub-mkrescue -o output/secure_wipe.iso boot/
fi

# Copy bootloader files if needed
if [ ! -f isolinux/isolinux.bin ]; then
    echo "Warning: isolinux.bin missing. Copy from GRUB install."
fi

echo "ISO built: output/secure_wipe.iso"
echo "Test: qemu-system-x86_64 -cdrom output/secure_wipe.iso -m 512"