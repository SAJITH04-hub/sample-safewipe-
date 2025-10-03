#!/usr/bin/env python3
"""
Main entry point for Secure Wipe Desktop App.
Flow: Auth → Launch GUI → Wipe/Cert Generation.
Run: python main.py
"""

import sys
from src.auth import authenticate, test_auth  # Use test_auth for dev
from src.gui import SecureWipeApp
from src.utils import log_message
from PyQt6.QtWidgets import QApplication

def main():
    log_message('INFO', 'Starting Secure Wipe Application')

    # Authentication (OAuth/OpenID)
    print("Authenticating user...")
    token = test_auth()  # Or authenticate() for real Auth0
    if not token:
        print("Authentication failed. Exiting.")
        sys.exit(1)
    log_message('INFO', f'Authenticated as: {token.get("user", "unknown")}')

    # Launch GUI
    app = QApplication(sys.argv)
    window = SecureWipeApp()
    window.show()
    log_message('INFO', 'GUI launched successfully')
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
