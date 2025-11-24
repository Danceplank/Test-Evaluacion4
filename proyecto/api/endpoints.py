from typing import Any, Dict, List
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, Path
from sqlalchemy.orm import Session

from proyecto.app.database.database import get_db
from proyecto.app.features import get_all_features, set_feature

# Import Device model
from proyecto.modelo.device import Device

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


# Devices CRUD

@router.get("/devices", tags=["devices"])
def list_devices(db: Session = Depends(get_db)) -> Dict[str, Any]:
    devices = db.query(Device).order_by(Device.id.desc()).all()
    return {"devices": [d.to_dict() for d in devices]}


@router.post("/devices", tags=["devices"])
def create_device(payload: Dict[str, Any], db: Session = Depends(get_db)):
    hostname = payload.get("hostname")
    if not hostname:
        raise HTTPException(status_code=400, detail="hostname is required")
    d = Device(
        hostname=hostname,
        ip_address=payload.get("ip_address"),
        os=payload.get("os"),
        active=bool(payload.get("active", True)),
    )
    db.add(d)
    db.commit()
    db.refresh(d)
    return d.to_dict()


@router.get("/devices/{device_id}", tags=["devices"])
def get_device(device_id: int = Path(..., ge=1), db: Session = Depends(get_db)):
    d = db.query(Device).filter(Device.id == device_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Device not found")
    return d.to_dict()


@router.put("/devices/{device_id}", tags=["devices"])
def update_device(device_id: int, payload: Dict[str, Any], db: Session = Depends(get_db)):
    d = db.query(Device).filter(Device.id == device_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Device not found")
    if "hostname" in payload:
        d.hostname = payload["hostname"]
    if "ip_address" in payload:
        d.ip_address = payload["ip_address"]
    if "os" in payload:
        d.os = payload["os"]
    if "active" in payload:
        d.active = bool(payload["active"])
    db.add(d)
    db.commit()
    db.refresh(d)
    return d.to_dict()


@router.delete("/devices/{device_id}", tags=["devices"])
def delete_device(device_id: int, db: Session = Depends(get_db)):
    d = db.query(Device).filter(Device.id == device_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Device not found")
    db.delete(d)
    db.commit()
    return {"deleted": True, "id": device_id}