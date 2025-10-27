import json
import os
from typing import Dict, Any


def _read_json(path: str) -> Dict[str, Any]:
    try:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f) or {}
                return data
    except Exception:
        pass
    return {}


def _write_json(path: str, data: Dict[str, Any]) -> None:
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f)


def _normalize_legacy_config(data: Dict[str, Any]) -> Dict[str, Any]:
    # Legacy flat structure to env names
    if 'api_key' in data or 'api_secret' in data:
        flat = {'api_key': data.get('api_key', ''), 'api_secret': data.get('api_secret', '')}
        return {'live': flat.copy(), 'test': flat.copy()}
    return data


def load_config_all(path: str = 'config.json') -> Dict[str, Any]:
    data = _read_json(path)
    return _normalize_legacy_config(data)


def save_config_env(env: str, api_key: str, api_secret: str, path: str = 'config.json') -> None:
    data = load_config_all(path)
    if env not in data:
        data[env] = {}
    data[env]['api_key'] = api_key
    data[env]['api_secret'] = api_secret
    _write_json(path, data)



