"""
Training system models for AI Refinement Dashboard
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, Float, Enum
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime
import enum

class TrainingStatus(enum.Enum):
    """Training job status enumeration"""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class TrainingType(enum.Enum):
    """Training type enumeration"""
    RAG = "RAG"
    LORA = "LORA"
    FINE_TUNING = "FINE_TUNING"
    HYBRID = "HYBRID"

class ExternalTrainingJob(Base):
    """External training job model for minion training"""
    
    __tablename__ = "external_training_jobs"
    
    # User and minion association
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    minion_id = Column(Integer, ForeignKey("external_api_models.id", ondelete="CASCADE"), nullable=False)
    
    # Job information
    job_name = Column(String(255), nullable=False)
    description = Column(Text)
    training_type = Column(Enum(TrainingType), nullable=False)
    
    # Provider and model information
    provider = Column(String(255), nullable=False)
    model_name = Column(String(255), nullable=False)
    api_key = Column(String(500))  # Encrypted API key
    
    # Training configuration
    config = Column(JSON)  # Training configuration parameters
    dataset_config = Column(JSON)  # Dataset-specific configuration
    rag_config = Column(JSON)  # RAG-specific configuration
    lora_config = Column(JSON)  # LoRA-specific configuration
    config_hash = Column(String(64))  # Hash for duplicate detection
    
    # Job status and progress
    status = Column(Enum(TrainingStatus), default=TrainingStatus.PENDING, nullable=False)
    progress = Column(Float, default=0.0, nullable=False)  # 0.0 to 100.0
    error_message = Column(Text)
    
    # Timing information
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    estimated_duration = Column(Integer)  # Estimated duration in seconds
    
    # Training results and metrics
    metrics = Column(JSON)  # Training metrics and statistics
    improvements = Column(JSON)  # Calculated improvements
    validation_results = Column(JSON)  # Validation test results
    
    # XP and ranking information
    xp_gained = Column(Integer, default=0, nullable=False)
    level_up_info = Column(JSON)  # Level up information
    
    # Resource usage
    memory_used = Column(Float)  # Memory usage in MB
    storage_used = Column(Float)  # Storage usage in MB
    processing_time = Column(Float)  # Processing time in seconds
    
    # Relationships
    user = relationship("User", back_populates="training_jobs")
    minion = relationship("ExternalAPIModel", back_populates="training_jobs")
    datasets = relationship("TrainingJobDataset", back_populates="training_job", cascade="all, delete-orphan")
    # History records created for this training job
    training_results = relationship("TrainingResult", back_populates="training_job", cascade="all, delete-orphan")

class UserTrainingDataset(Base):
    """User training dataset model"""
    
    __tablename__ = "user_training_datasets"
    
    # User ownership
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Dataset information
    name = Column(String(255), nullable=False)
    description = Column(Text)
    dataset_type = Column(String(100), nullable=False)  # e.g., 'rag', 'lora', 'fine_tuning'
    
    # Dataset configuration
    config = Column(JSON)  # Dataset-specific configuration
    file_path = Column(String(500))  # Path to dataset file
    file_size = Column(Integer)  # File size in bytes
    file_format = Column(String(50))  # e.g., 'json', 'csv', 'txt'
    
    # Dataset statistics
    total_items = Column(Integer, default=0, nullable=False)
    processed_items = Column(Integer, default=0, nullable=False)
    quality_score = Column(Float, default=0.0, nullable=False)  # 0.0 to 100.0
    
    # Processing information
    processing_status = Column(String(50), default='pending', nullable=False)
    processing_started_at = Column(DateTime)
    processing_completed_at = Column(DateTime)
    processing_error = Column(Text)
    
    # Dataset metadata
    tags = Column(JSON)  # Dataset tags for categorization
    dataset_metadata = Column(JSON)  # Additional dataset metadata
    
    # Relationships
    user = relationship("User", back_populates="training_datasets")
    training_jobs = relationship("TrainingJobDataset", back_populates="dataset", cascade="all, delete-orphan")

class TrainingJobDataset(Base):
    """Many-to-many relationship between training jobs and datasets"""
    
    __tablename__ = "training_job_datasets"
    
    training_job_id = Column(Integer, ForeignKey("external_training_jobs.id", ondelete="CASCADE"), nullable=False)
    dataset_id = Column(Integer, ForeignKey("user_training_datasets.id", ondelete="CASCADE"), nullable=False)
    
    # Dataset usage in this training job
    usage_percentage = Column(Float, default=100.0, nullable=False)  # Percentage of dataset used
    preprocessing_config = Column(JSON)  # Dataset-specific preprocessing configuration
    
    # Relationships
    training_job = relationship("ExternalTrainingJob", back_populates="datasets")
    dataset = relationship("UserTrainingDataset", back_populates="training_jobs")
