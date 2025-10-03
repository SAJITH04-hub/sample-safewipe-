# Secure Wipe

A cross-platform application for secure data wiping and IT asset recycling. Features:
- Multi-pass wiping (HDD/SSD/removable drives, including HPA/DCO).
- Tamper-proof certificates (PDF/JSON/QR with ECDSA signatures).
- PyQt6 GUI: One-click wipe, wizard, logs, dark/light themes.
- Flask API for bulk/centralized management.
- OAuth 2.0/OpenID Connect authentication.
- GRUB2 bootable ISO for offline wiping.
- Compliant with NIST 800-88/DoD 5220.22-M.

## Quick Start
1. Clone: `git clone https://github.com/yourusername/secure-wipe.git && cd secure-wipe`
2. Install deps: See `docs/INSTALL.md`.
3. Build: `./build.sh`
4. Generate keys: `cd python_app/src && python gen_keys.py && mv *.pem ../../keys/`
5. Run GUI: `cd python_app && python main.py` (as admin/sudo for wipes).
6. Run API: `cd python_app && python -m api.app`
7. Build ISO: `./iso_builder/build_iso.sh` (test with QEMU/VM).

## Platforms
- Desktop: Windows/Linux/macOS.
- Offline: Bootable ISO (USB/VM).

## Testing
See `docs/TESTING.md` for safe mocks (e.g., wipe temp files).

## License
MIT (see LICENSE).