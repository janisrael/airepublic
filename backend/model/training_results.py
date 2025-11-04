"""
Training Results Model
Stores detailed before/after metrics and improvements for RAG training
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class TrainingResult(Base):
    """Detailed training results with before/after metrics"""
    
    __tablename__ = "training_results"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    job_id = Column(Integer, ForeignKey("external_training_jobs.id", ondelete="CASCADE"), nullable=False)
    minion_id = Column(Integer, ForeignKey("external_api_models.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Training configuration
    training_type = Column(String(50), nullable=False)  # RAG, LORA, HYBRID
    collection_name = Column(String(255))  # ChromaDB collection name
    
    # Before training metrics
    before_metrics = Column(JSON)  # Detailed before metrics
    
    # After training metrics  
    after_metrics = Column(JSON)  # Detailed after metrics
    
    # Calculated improvements
    improvements = Column(JSON)  # Accuracy, speed, knowledge improvements
    
    # Training statistics
    refinement_stats = Column(JSON)  # Dataset refinement statistics
    validation_results = Column(JSON)  # Training validation results
    test_results = Column(JSON)  # Performance test results
    
    # Configuration used
    rag_config = Column(JSON)  # RAG configuration used
    minion_config = Column(JSON)  # Minion configuration
    
    # Summary metrics (for quick access)
    accuracy_improvement = Column(Float, default=0.0)
    speed_improvement = Column(Float, default=0.0)
    knowledge_improvement = Column(Float, default=0.0)
    overall_improvement = Column(Float, default=0.0)
    
    # XP and progression
    xp_gained = Column(Integer, default=0)
    level_up = Column(Boolean, default=False)
    rank_up = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    training_job = relationship("ExternalTrainingJob", back_populates="training_results")
    minion = relationship("ExternalAPIModel", back_populates="training_results")
    user = relationship("User", back_populates="training_results")
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'job_id': self.job_id,
            'minion_id': self.minion_id,
            'user_id': self.user_id,
            'training_type': self.training_type,
            'collection_name': self.collection_name,
            'before_metrics': self.before_metrics,
            'after_metrics': self.after_metrics,
            'improvements': self.improvements,
            'refinement_stats': self.refinement_stats,
            'validation_results': self.validation_results,
            'test_results': self.test_results,
            'rag_config': self.rag_config,
            'minion_config': self.minion_config,
            'accuracy_improvement': self.accuracy_improvement,
            'speed_improvement': self.speed_improvement,
            'knowledge_improvement': self.knowledge_improvement,
            'overall_improvement': self.overall_improvement,
            'xp_gained': self.xp_gained,
            'level_up': self.level_up,
            'rank_up': self.rank_up,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_summary(self):
        """Get training summary for display"""
        return {
            'id': self.id,
            'training_type': self.training_type,
            'accuracy_improvement': f"{self.accuracy_improvement:+.1f}%",
            'speed_improvement': f"{self.speed_improvement:+.1f}%",
            'knowledge_improvement': f"+{self.knowledge_improvement:.1f}%",
            'overall_improvement': f"{self.overall_improvement:+.1f}%",
            'xp_gained': self.xp_gained,
            'level_up': self.level_up,
            'rank_up': self.rank_up,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def get_detailed_report(self):
        """Get detailed training report"""
        return {
            'summary': self.get_summary(),
            'before_metrics': self.before_metrics,
            'after_metrics': self.after_metrics,
            'improvements': self.improvements,
            'refinement_stats': self.refinement_stats,
            'validation_results': self.validation_results,
            'test_results': self.test_results,
            'configuration': {
                'rag_config': self.rag_config,
                'minion_config': self.minion_config
            }
        }
