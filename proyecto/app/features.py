from pathlib import Path
import json
import threading
from typing import Dict

BASE_DIR = Path(__file__).resolve().parents[1]  # proyecto/
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
FILE = DATA_DIR / "features.json"
_LOCK = threading.Lock()

DEFAULT_FEATURES: Dict[str, Dict] = {
    "ransomware": {"name": "Protección multicapa contra ransomware", "enabled": True},
    "network_defense": {"name": "Defensa ante ataques de red", "enabled": True},
    "endpoint_protection": {"name": "Protección de endpoints en tiempo real", "enabled": True},
    "cloud_security": {"name": "Seguridad basada en la nube", "enabled": True},
}


def _read() -> Dict[str, Dict]:
    if not FILE.exists():
        _write(DEFAULT_FEATURES)
        return DEFAULT_FEATURES.copy()
    try:
        with FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        # merge with defaults to ensure keys exist
        merged = {k: dict(DEFAULT_FEATURES[k]) for k in DEFAULT_FEATURES}
        for k, v in data.items():
            if k in merged:
                merged[k].update(v)
        return merged
    except Exception:
        return DEFAULT_FEATURES.copy()


def _write(data: Dict[str, Dict]):
    with FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_all_features() -> Dict[str, Dict]:
    with _LOCK:
        return _read()


def set_feature(feature_key: str, enabled: bool) -> bool:
    with _LOCK:
        data = _read()
        if feature_key not in data:
            return False
        data[feature_key]["enabled"] = bool(enabled)
        _write(data)
        return True