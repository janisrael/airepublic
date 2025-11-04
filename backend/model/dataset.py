"""
Dataset management models for AI Refinement Dashboard
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime

class Dataset(Base):
    """Dataset model for training data management"""
    
    __tablename__ = "datasets"
    
    # Dataset information
    name = Column(String(255), nullable=False)
    description = Column(Text)
    dataset_type = Column(String(100), nullable=False)  # e.g., 'text', 'code', 'conversation'
    format = Column(String(50), nullable=False)  # e.g., 'json', 'csv', 'txt'
    
    # User association (USER SCOPED)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # File information
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, default=0, nullable=False)  # File size in bytes
    file_hash = Column(String(255))  # File hash for integrity checking
    
    # Dataset statistics
    total_items = Column(Integer, default=0, nullable=False)
    processed_items = Column(Integer, default=0, nullable=False)
    quality_score = Column(Float, default=0.0, nullable=False)  # Quality score (0.0 to 100.0)
    
    # Processing information
    processing_status = Column(String(50), default='pending', nullable=False)
    processing_started_at = Column(DateTime)
    processing_completed_at = Column(DateTime)
    processing_error = Column(Text)
    
    # Dataset configuration
    config = Column(JSON)  # Dataset-specific configuration
    preprocessing_config = Column(JSON)  # Preprocessing configuration
    validation_config = Column(JSON)  # Validation configuration
    
    # Dataset metadata
    tags = Column(JSON)  # Dataset tags for categorization
    dataset_metadata = Column(JSON)  # Additional dataset metadata
    version = Column(String(50), default="1.0")
    
    # Status and visibility
    is_active = Column(Boolean, default=True, nullable=False)
    is_public = Column(Boolean, default=False, nullable=False)  # Can be shared with other users
    is_verified = Column(Boolean, default=False, nullable=False)  # Quality verified
    
    # Usage tracking
    usage_count = Column(Integer, default=0, nullable=False)
    last_used = Column(DateTime)
    
    # Relationships
    evaluations = relationship("Evaluation", back_populates="dataset", cascade="all, delete-orphan")

class Evaluation(Base):
    """Dataset evaluation model for quality assessment"""
    
    __tablename__ = "evaluations"
    
    # Dataset association
    dataset_id = Column(Integer, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)
    
    # Evaluation information
    evaluation_type = Column(String(100), nullable=False)  # e.g., 'quality', 'completeness', 'accuracy'
    evaluation_name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Evaluation results
    score = Column(Float, nullable=False)  # Evaluation score (0.0 to 100.0)
    max_score = Column(Float, default=100.0, nullable=False)
    min_score = Column(Float, default=0.0, nullable=False)
    
    # Evaluation details
    criteria = Column(JSON)  # Evaluation criteria
    results = Column(JSON)  # Detailed evaluation results
    recommendations = Column(JSON)  # Improvement recommendations
    
    # Evaluation metadata
    evaluator = Column(String(255))  # Who/what performed the evaluation
    evaluation_method = Column(String(100))  # Evaluation method used
    evaluation_config = Column(JSON)  # Evaluation configuration
    
    # Status and timing
    status = Column(String(50), default='completed', nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime)
    
    # Relationships
    dataset = relationship("Dataset", back_populates="evaluations")
