from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from app.db.database import Base

class Deployment(Base):
    __tablename__ = "deployments"

    id = Column(Integer, primary_key=True, index=True)
    deployment_id = Column(String, unique=True, index=True)
    commit_id = Column(String, index=True)
    service = Column(String, index=True)
    
    # Core Feature Columns
    files_changed = Column(Integer, default=0)
    lines_added = Column(Integer, default=0)
    lines_deleted = Column(Integer, default=0)
    functions_changed = Column(Integer, default=0)
    
    # Detailed Risk Flags
    api_changes = Column(Boolean, default=False)
    db_changes = Column(Boolean, default=False)
    config_changes = Column(Boolean, default=False)
    dependency_changes = Column(Boolean, default=False)
    
    # Metadata
    services_touched = Column(Integer, default=1)
    criticality = Column(String, default="low")
    
    # Label for ML
    incident_24h = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
