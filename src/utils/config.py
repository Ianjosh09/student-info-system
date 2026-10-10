"""Load external configuration; relative paths are rooted at the project."""
import json
import os
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def load_config():
    path = Path(os.environ.get('SIS_CONFIG', ROOT / 'config/config.json'))
    with path.open(encoding='utf-8') as file:
        config = json.load(file)
    if not isinstance(config, dict):
        raise ValueError('Configuration must be a JSON object.')
    for key in ('data_file', 'log_file', 'export_file'):
        value = os.environ.get('SIS_' + key.upper(), config.get(key))
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f'Missing configuration: {key}')
        path = Path(value)
        config[key] = path if path.is_absolute() else ROOT / path
    return config
