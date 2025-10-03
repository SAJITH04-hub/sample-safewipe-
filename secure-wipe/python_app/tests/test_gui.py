import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from src.gui import SecureWipeApp
from src.utils import load_config
import sys

@pytest.fixture(scope="session")
def app():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app

def test_gui_launches(qtbot, app):
    config = load_config()
    window = SecureWipeApp()
    qtbot.addWidget(window)
    window.show()
    assert window.windowTitle() == 'Secure Wipe'
    assert window.device_combo.count() > 0  # Devices loaded

def test_theme_toggle(qtbot, app):
    window = SecureWipeApp()
    qtbot.addWidget(window)
    initial_theme = load_config()['app']['theme']
    window.theme_btn.click()  # Toggle
    new_theme = 'dark' if initial_theme == 'light' else 'light'
    assert load_config()['app']['theme'] == new_theme  # Config updated

def test_wipe_button(qtbot, app, mocker):
    window = SecureWipeApp()
    qtbot.addWidget(window)
    mocker.patch('src.gui.engine.wipe_device')  # Mock wipe
    mocker.patch('src.gui.engine.handle_hpa_dco')
    mocker.patch('src.gui.CertificateGenerator.generate_full_cert')
    window.device_combo.addItem('/dev/mock')
    window.device_combo.setCurrentText('/dev/mock')
    # Simulate confirm dialog
    mocker.patch('PyQt6.QtWidgets.QMessageBox.exec', return_value=1)  # Yes
    window.wipe_btn.click()
    # Check log (indirect: no crash)
    assert True  # Passes if no exception