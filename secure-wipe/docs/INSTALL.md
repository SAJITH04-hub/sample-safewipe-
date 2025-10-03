# Installation Guide for Secure Wipe

## Prerequisites
- **Git**: Download from [git-scm.com](https://git-scm.com). Verify: `git --version`.
- **Rust**: Install via [rustup.rs](https://rustup.rs) (includes Cargo). Update: `rustup update`.
- **Python 3.10+**: Download from [python.org](https://python.org). Verify: `python --version`.
- **Platform-Specific Dependencies**:
  - **Linux (Ubuntu/Debian)**:
    ```
    sudo apt update
    sudo apt install build-essential clang libssl-dev pkg-config grub-pc-bin xorriso syslinux-utils hdparm python3-venv python3-pip
    ```
    - For Rust: `rustup target add x86_64-unknown-linux-gnu`.
  - **Windows**:
    - Install Visual Studio Build Tools (free from [visualstudio.microsoft.com](https://visualstudio.microsoft.com/downloads); select "C++ build tools").
    - Python: From Microsoft Store or python.org (add to PATH).
    - For ISO: Use WSL (Windows Subsystem for Linux) with Ubuntu, or Docker Desktop.
    - hdparm equivalent: Not native; use placeholders or third-party tools.
  - **macOS**:
    ```
    xcode-select --install  # Command Line Tools
    brew install rust python@3.11 qt@6 grub hdparm
    ```
    - Link Python: `brew link --force python@3.11`.
    - For Rust: `rustup target add x86_64-apple-darwin`.
- **Optional Tools**:
  - Docker: For reproducible ISO builds ([docker.com](https://docker.com)).
  - PyInstaller: For standalone executables (`pip install pyinstaller`).
  - QEMU/VirtualBox: For testing ISO boots (free VMs).
  - maturin: For Rust-Python bindings (`pip install maturin`).

## Setup Steps
1. **Clone the Repository**: