from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, Body
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

@router.get("/health", tags=["system"])
def api_health() -> dict[str, Any]:
    return {"status": "ok"}

@router.get("/services/status", tags=["services"])
def services_status(db: Session = Depends(get_db)):
    try:
        rsp = {
            "ransomware": RansomwareProtectionService is not None,
            "endpoint_protection": EndpointProtectionService is not None,
            "network_defense": NetworkAttackDefenseService is not None,
        }
        return {"services": rsp}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/features", tags=["system"])
def features_list() -> Dict[str, Any]:
    """
    Return all feature flags and their display names.
    """
    try:
        data = get_all_features()
        return {"features": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/features/{feature_key}", tags=["system"])
def features_set(feature_key: str, payload: dict = Body(...)):
    """
    Set a feature's enabled state.
    Body: {"enabled": true}
    """
    if "enabled" not in payload:
        raise HTTPException(status_code=400, detail="Missing 'enabled' in request body")
    enabled = bool(payload["enabled"])
    ok = set_feature(feature_key, enabled)
    if not ok:
        raise HTTPException(status_code=404, detail="Feature not found")
    return {"feature": feature_key, "enabled": enabled}

# Example endpoint that starts a background task (safe no-op if service is placeholder)
@router.post("/ransomware/scan", tags=["ransomware"])
def start_ransomware_scan(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    def _scan():
        try:
            svc = RansomwareProtectionService(db)
            if hasattr(svc, "scan"):
                svc.scan()
        except Exception:
            pass

    background_tasks.add_task(_scan)
    return {"started": True}