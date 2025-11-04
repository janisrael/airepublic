"""
Legacy models for AI Refinement Dashboard
These models are kept for compatibility with existing data
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime

class TrainingJob(Base):
    """Legacy training job model - kept for compatibility"""
    
    __tablename__ = "training_jobs"
    
    # Basic information
    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), default='pending', nullable=False)
    
    # Training configuration
    config = Column(JSON)
    model_config = Column(JSON)
    dataset_config = Column(JSON)
    
    # Progress and results
    progress = Column(Float, default=0.0, nullable=False)
    results = Column(JSON)
    metrics = Column(JSON)
    
    # Timing information
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Error handling
    error_message = Column(Text)
    
    # Relationships
    model_profiles = relationship("ModelProfile", back_populates="training_job", cascade="all, delete-orphan")

class ModelProfile(Base):
    """Legacy model profile model - kept for compatibility"""
    
    __tablename__ = "model_profiles"
    
    # Training job association
    training_job_id = Column(Integer, ForeignKey("training_jobs.id", ondelete="CASCADE"), nullable=False)
    
    # Profile information
    name = Column(String(255), nullable=False)
    description = Column(Text)
    avatar_url = Column(String(500))
    avatar_path = Column(String(500))
    
    # Profile configuration
    system_prompt = Column(Text)
    capabilities = Column(JSON)
    tags = Column(JSON)
    config = Column(JSON)
    
    # Profile metadata
    version = Column(String(50), default="1.0")
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    training_job = relationship("TrainingJob", back_populates="model_profiles")
    # reference_models relationship removed - ReferenceModel moved to separate file

# ReferenceModel moved to model/reference_models.py to avoid conflicts

class Model(Base):
    """Legacy model model - kept for compatibility"""
    
    __tablename__ = "models"
    
    # Model information
    name = Column(String(255), nullable=False)
    provider = Column(String(255), nullable=False)
    model_name = Column(String(255), nullable=False)
    
    # Model configuration
    api_key = Column(String(500))
    api_url = Column(String(500))
    config = Column(JSON)
    
    # Model metadata
    description = Column(Text)
    capabilities = Column(JSON)
    tags = Column(JSON)
    
    # Status and usage
    is_active = Column(Boolean, default=True, nullable=False)
    usage_count = Column(Integer, default=0, nullable=False)
    last_used = Column(DateTime)
    
    # Model statistics
    total_requests = Column(Integer, default=0, nullable=False)
    total_tokens_used = Column(Integer, default=0, nullable=False)
    average_response_time = Column(Float, default=0.0, nullable=False)
    
    # Model performance
    success_rate = Column(Float, default=100.0, nullable=False)
    error_rate = Column(Float, default=0.0, nullable=False)
    
    # Model metadata
    version = Column(String(50), default="1.0")
    created_by = Column(String(255))
    last_updated = Column(DateTime, default=datetime.utcnow, nullable=False)
