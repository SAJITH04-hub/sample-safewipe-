import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, 
    QLabel, QTextEdit, QComboBox, QMessageBox, QWizard, QWizardPage
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor
import secure_wipe_engine as engine  # Rust module
from .cert_gen import CertificateGenerator
from .utils import load_config
from datetime import datetime
import psutil  # Fallback for device detection

class WipeWizard(QWizard):
    def __init__(self):
        super().__init__()
        self.addPage(DevicePage())
        self.addPage(MethodPage())
        self.addPage(ConfirmPage())

class DevicePage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Select Device")

class MethodPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Choose Wipe Method")

class ConfirmPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Confirm Wipe")

class SecureWipeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.setWindowTitle('Secure Wipe')
        self.setGeometry(100, 100, 800, 600)
        self.gen = CertificateGenerator()
        self.init_ui()
        self.set_theme(self.config['app']['theme'])

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()

        # Dashboard
        self.label = QLabel('Select Device to Wipe')
        layout.addWidget(self.label)

        self.device_combo = QComboBox()
        self.refresh_devices()
        layout.addWidget(self.device_combo)

        self.wipe_btn = QPushButton('One-Click Wipe (3-Pass)')
        self.wipe_btn.clicked.connect(self.wipe_device)
        layout.addWidget(self.wipe_btn)

        self.wizard_btn = QPushButton('Step-by-Step Wizard')
        self.wizard_btn.clicked.connect(self.start_wizard)
        layout.addWidget(self.wizard_btn)

        # Logs
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

        self.theme_btn = QPushButton('Toggle Dark/Light')
        self.theme_btn.clicked.connect(self.toggle_theme)
        layout.addWidget(self.theme_btn)

        central.setLayout(layout)

    def refresh_devices(self):
        try:
            devices = engine.detect_devices()
        except:
            devices = [p.device for p in psutil.disk_partitions()]
        self.device_combo.clear()
        self.device_combo.addItems(devices)
        self.log(f"Detected devices: {devices}")

    def log(self, msg):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.log_text.append(f"[{timestamp}] {msg}")

    def wipe_device(self):
        device = self.device_combo.currentText()
        if not device:
            self.log("No device selected.")
            return
        reply = QMessageBox.question(
            self, 'Confirm Wipe', f'Wipe {device}? This is IRREVERSIBLE!',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        try:
            passes = self.config['app']['wipe_passes']
            self.log(f"Starting {passes}-pass wipe on {device}...")
            engine.wipe_device(device, passes)
            engine.handle_hpa_dco(device)
            self.log("Wipe completed successfully.")
            self.generate_cert(device)
        except Exception as e:
            self.log(f"Error during wipe: {e}")
            QMessageBox.critical(self, 'Wipe Error', str(e))

    def generate_cert(self, device):
        method = self.config['app']['default_method']
        cert_files = self.gen.generate_full_cert(device, method)
        self.log(f"Certificates generated: {cert_files}")

    def start_wizard(self):
        wizard = WipeWizard()
        if wizard.exec() == QWizard.DialogCode.Accepted:
            self.log("Wizard completed.")
        else:
            self.log("Wizard cancelled.")

    def set_theme(self, mode):
        palette = QPalette()
        if mode == 'dark':
            palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
            palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        else:  # light
            palette.setColor(QPalette.ColorRole.Window, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.black)
            palette.setColor(QPalette.ColorRole.Base, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.AlternateBase, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.black)
            palette.setColor(QPalette.ColorRole.Button, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.black)
            palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
            palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        QApplication.setPalette(palette)

    def toggle_theme(self):
        current_mode = self.config['app']['theme']
        new_mode = 'dark' if current_mode == 'light' else 'light'
        self.config['app']['theme'] = new_mode
        self.set_theme(new_mode)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SecureWipeApp()
    ex.show()
    sys.exit(app.exec())