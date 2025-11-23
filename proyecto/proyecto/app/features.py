from pathlib import Path
import json
import threading

BASE_DIR = Path(__file__).resolve().parents[1]  # proyecto/
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
FILE = DATA_DIR / "features.json"
_LOCK = threading.Lock()

DEFAULT_FEATURES = {
    "ransomware": {"name": "Protección multicapa contra ransomware", "enabled": True},
    "network_defense": {"name": "Network Attack Defense", "enabled": True},
    "endpoint_protection": {"name": "Protección de endpoints en tiempo real", "enabled": True},
    # removed "admin_console" (Consola de administración centralizada) because it must always be enabled
    "cloud_security": {"name": "Seguridad basada en la nube", "enabled": True},
}


def _load_raw():
    if not FILE.exists():
        _save_raw(DEFAULT_FEATURES)
        return DEFAULT_FEATURES.copy()
    try:
        with FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        # Remove deprecated/removed keys (e.g. admin_console) so existing files are cleaned up
        if "admin_console" in data:
            data.pop("admin_console", None)
            _save_raw(data)
        # Merge defaults to ensure keys exist and keep current states for known keys
        merged = DEFAULT_FEATURES.copy()
        for k, v in data.items():
            if k in merged:
                merged[k].update(v)
        return merged
    except Exception:
        return DEFAULT_FEATURES.copy()


def _save_raw(data: dict):
    with FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_all_features():
    """Return dict of feature_key -> {name, enabled}"""
    with _LOCK:
        return _load_raw()


def set_feature(feature_key: str, enabled: bool) -> bool:
    """Set feature enabled state. Returns True if updated, False if feature not found."""
    with _LOCK:
        data = _load_raw()
        if feature_key not in data:
            return False
        data[feature_key]["enabled"] = bool(enabled)
        _save_raw(data)
        return True