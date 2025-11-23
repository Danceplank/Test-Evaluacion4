from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from typing import Any, Dict

# Use the proyecto package imports so modules resolve when run from workspace root
from proyecto.app.database.database import get_db
from proyecto.app.features import get_all_features, set_feature

# Import services via proyecto.services (they live under proyecto/services/)
try:
    from proyecto.services.ransomware_protection import RansomwareProtectionService
    from proyecto.services.endpoint_protection import EndpointProtectionService
    from proyecto.services.network_defense import NetworkAttackDefenseService
except Exception:
    class RansomwareProtectionService:
        def __init__(self, db: Session | None = None): pass
    class EndpointProtectionService:
        def __init__(self, db: Session | None = None): pass
    class NetworkAttackDefenseService:
        def __init__(self, db: Session | None = None): pass

router = APIRouter()

# Try to detect if real service modules exist; fall back to flags (no heavy placeholders)
_services_available = {}
try:
    from proyecto.services.ransomware_protection import RansomwareProtectionService  # type: ignore
    _services_available["ransomware"] = True
except Exception:
    _services_available["ransomware"] = False

try:
    from proyecto.services.endpoint_protection import EndpointProtectionService  # type: ignore
    _services_available["endpoint_protection"] = True
except Exception:
    _services_available["endpoint_protection"] = False

try:
    from proyecto.services.network_defense import NetworkAttackDefenseService  # type: ignore
    _services_available["network_defense"] = True
except Exception:
    _services_available["network_defense"] = False


@router.get("/health", tags=["system"])
def api_health() -> Dict[str, Any]:
    return {"status": "ok"}


@router.get("/services/status", tags=["services"])
def services_status() -> Dict[str, Any]:
    """Return availability of internal service modules (for UI)."""
    return {"services": _services_available}


@router.get("/features", tags=["system"])
def features_list() -> Dict[str, Any]:
    try:
        data = get_all_features()
        return {"features": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/features/{feature_key}", tags=["system"])
def features_set(feature_key: str, payload: dict):
    if "enabled" not in payload:
        raise HTTPException(status_code=400, detail="Missing 'enabled' in request body")
    enabled = bool(payload["enabled"])
    ok = set_feature(feature_key, enabled)
    if not ok:
        raise HTTPException(status_code=404, detail="Feature not found")
    return {"feature": feature_key, "enabled": enabled}


@router.post("/ransomware/scan", tags=["ransomware"])
def start_ransomware_scan(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Trigger a background scan if service available (demo-safe)."""
    if not _services_available.get("ransomware"):
        return {"started": False, "reason": "ransomware service not available"}
    def _scan():
        try:
            svc = RansomwareProtectionService(db)  # type: ignore
            if hasattr(svc, "scan"):
                svc.scan()
        except Exception:
            pass
    background_tasks.add_task(_scan)
    return {"started": True}