import yaml
import os
from pathlib import Path

def load_config(config_file='app_config.yaml'):
    """Load YAML config from python_app/config/"""
    config_path = Path(__file__).parent / '..' / 'config' / config_file
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

def load_auth_config():
    """Load Auth0 config (separate for security)."""
    return load_config('auth0_config.json')

def parse_device_path(path):
    """Cross-platform device path parser."""
    if os.name == 'nt':  # Windows
        if not path.startswith('\\\\.\\'):
            path = f'\\\\.\\{path}'
    elif os.name == 'posix':  # Linux/macOS
        if not path.startswith('/dev/'):
            path = f'/dev/{path}'
    return path

def log_message(level, message):
    """Simple logging."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] [{level}] {message}")

if __name__ == "__main__":
    config = load_config()
    print("Loaded config:", config['app']['wipe_passes'])