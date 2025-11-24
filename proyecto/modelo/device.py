from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
# Reuse the Base declarative from seguridad.py
try:
    from proyecto.modelo.seguridad import Base
except Exception:
    from modelo.seguridad import Base


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    hostname = Column(String(128), nullable=False)
    ip_address = Column(String(64), nullable=True)
    os = Column(String(128), nullable=True)
    last_seen = Column(DateTime, default=datetime.utcnow)
    active = Column(Boolean, default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "hostname": self.hostname,
            "ip_address": self.ip_address,
            "os": self.os,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
            "active": bool(self.active),
        }