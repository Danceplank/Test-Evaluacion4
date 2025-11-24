from sqlalchemy.orm import Session
from . import models, schemas
import uuid
from datetime import datetime

# 1. CREATE
def create_endpoint(db: Session, endpoint: schemas.EndpointCreate):
    db_endpoint = models.Endpoint(
        id=str(uuid.uuid4()), # Generamos ID único
        last_seen=datetime.now(),
        **endpoint.dict()
    )
    db.add(db_endpoint)
    db.commit()
    db.refresh(db_endpoint)
    return db_endpoint

# 2. READ (Todos)
def get_endpoints(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Endpoint).offset(skip).limit(limit).all()

# 3. READ (Uno solo)
def get_endpoint(db: Session, endpoint_id: str):
    return db.query(models.Endpoint).filter(models.Endpoint.id == endpoint_id).first()

# 4. UPDATE (No solicitado explícitamente pero necesario para CRUD completo)
def update_endpoint(db: Session, endpoint_id: str, endpoint_data: schemas.EndpointCreate):
    db_endpoint = get_endpoint(db, endpoint_id)
    if db_endpoint:
        for key, value in endpoint_data.dict().items():
            setattr(db_endpoint, key, value)
        db.commit()
        db.refresh(db_endpoint)
    return db_endpoint

# 5. DELETE
def delete_endpoint(db: Session, endpoint_id: str):
    db_endpoint = get_endpoint(db, endpoint_id)
    if db_endpoint:
        db.delete(db_endpoint)
        db.commit()
    return db_endpoint