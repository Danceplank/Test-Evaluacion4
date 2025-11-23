from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class Endpoint(Base):
    __tablename__ = "endpoints"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False)
    ip_address = Column(String(45))
    mac_address = Column(String(17))
    hostname = Column(String(255))
    os = Column(String(100))
    os_version = Column(String(50))
    endpoint_type = Column(String(50))  # SERVER, WORKSTATION, LAPTOP, VM
    status = Column(String(20), default="PROTECTED")
    last_seen = Column(DateTime, default=datetime.utcnow)
    protection_status = Column(String(20), default="PROTECTED")
    risk_score = Column(Float, default=0.0)

class Threat(Base):
    __tablename__ = "threats"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False)
    type = Column(String(50))  # RANSOMWARE, MALWARE, PHISHING, ZERO_DAY
    severity = Column(String(20))  # CRITICAL, HIGH, MEDIUM, LOW
    status = Column(String(20), default="BLOCKED")
    endpoint_id = Column(String(36))
    detection_time = Column(DateTime, default=datetime.utcnow)
    description = Column(Text)
    action_taken = Column(String(100))

class RansomwareIncident(Base):
    __tablename__ = "ransomware_incidents"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    endpoint_id = Column(String(36))
    detection_time = Column(DateTime, default=datetime.utcnow)
    files_targeted = Column(Integer)
    files_protected = Column(Integer)
    encryption_attempts = Column(Integer)
    backup_created = Column(Boolean, default=True)
    status = Column(String(20), default="BLOCKED")

class SecurityPolicy(Base):
    __tablename__ = "security_policies"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False)
    policy_type = Column(String(50))  # RANSOMWARE, NETWORK, WEB, BEHAVIORAL
    settings = Column(JSON)
    is_active = Column(Boolean, default=True)