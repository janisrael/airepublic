"""
Training Service
Business logic for managing training jobs and datasets
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from repositories.training_repository import TrainingRepository
from database.postgres_connection import create_spirit_engine
from sqlalchemy.orm import sessionmaker
from model.training import ExternalTrainingJob, TrainingStatus, TrainingType
import json
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from utils.hash_utils import generate_training_hash, get_config_fingerprint


class TrainingService:
    """Service for training operations"""
    
    def __init__(self):
        engine = create_spirit_engine()
        Session = sessionmaker(bind=engine)
        self.session = Session()
        self.training_repo = TrainingRepository(self.session)
    
    def create_training_job(self, job_data: Dict[str, Any]) -> ExternalTrainingJob:
        """Create a new training job"""
        try:
            # Create training job object
            training_job = ExternalTrainingJob(
                job_name=job_data['job_name'],
                description=job_data.get('description', ''),
                minion_id=job_data['minion_id'],
                user_id=job_data['user_id'],
                provider=job_data['provider'],
                model_name=job_data['model'],
                training_type=TrainingType(job_data['training_type'].upper()),
                status=TrainingStatus(job_data['status'].upper()),
                config=json.dumps(job_data.get('config', {})),
                created_at=datetime.utcnow()
            )
            
            # Save to database
            self.session.add(training_job)
            self.session.commit()
            self.session.refresh(training_job)
            
            return training_job
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_training_job(self, job_id: int) -> Optional[ExternalTrainingJob]:
        """Get training job by ID"""
        return self.training_repo.get_by_id(job_id)
    
    def get_user_training_jobs(self, user_id: int) -> List[ExternalTrainingJob]:
        """Get all training jobs for a user"""
        return self.training_repo.get_by_user_id(user_id)
    
    def update_training_job_status(self, job_id: int, status: str) -> bool:
        """Update training job status"""
        try:
            job = self.get_training_job(job_id)
            if job:
                job.status = TrainingStatus(status)
                job.updated_at = datetime.utcnow()
                self.session.commit()
                return True
            return False
        except Exception as e:
            self.session.rollback()
            raise e
    
    def update_training_job_progress(self, job_id: int, progress: float, current_step: Optional[int] = None) -> bool:
        """
        Update training job progress (0.0 to 100.0)
        
        Args:
            job_id: Training job ID
            progress: Progress percentage (0.0 to 100.0)
            current_step: Optional step number for tracking
            
        Returns:
            True if updated successfully, False otherwise
        """
        try:
            job = self.get_training_job(job_id)
            if job:
                # Clamp progress to valid range
                job.progress = max(0.0, min(100.0, float(progress)))
                job.updated_at = datetime.utcnow()
                self.session.commit()
                print(f"📊 Updated training job {job_id} progress: {job.progress:.1f}%")
                return True
            return False
        except Exception as e:
            self.session.rollback()
            print(f"⚠️ Failed to update training job progress: {e}")
            return False
    
    def get_training_jobs_by_minion(self, minion_id: int) -> List[ExternalTrainingJob]:
        """Get training jobs for a specific minion"""
        return self.training_repo.get_by_minion_id(minion_id)
    
    def get_latest_training_jobs_by_minion(self, user_id: int) -> Dict[int, ExternalTrainingJob]:
        """Get latest training job for each minion"""
        jobs = self.training_repo.get_by_user_id(user_id)
        latest_by_minion = {}
        
        for job in jobs:
            if job.minion_id not in latest_by_minion or job.created_at > latest_by_minion[job.minion_id].created_at:
                latest_by_minion[job.minion_id] = job
        
        return latest_by_minion
    
    def exists_similar_job(self, user_id: int, minion_id: int, 
                          rag_config: Dict[str, Any], selected_datasets: List[str],
                          days_back: int = 3) -> Optional[ExternalTrainingJob]:
        """
        Check if a similar training job (same config + dataset) was recently created.
        
        Args:
            user_id: User ID
            minion_id: Minion ID
            rag_config: RAG configuration dictionary
            selected_datasets: List of dataset identifiers
            days_back: How many days back to check for duplicates (default: 3)
            
        Returns:
            Existing job if found, None otherwise
        """
        try:
            # Generate hash for the training configuration
            config_hash = generate_training_hash(rag_config, selected_datasets)
            
            # Calculate cutoff time
            cutoff_time = datetime.utcnow() - timedelta(days=days_back)
            
            # Query for similar jobs
            similar_jobs = self.session.query(ExternalTrainingJob).filter(
                ExternalTrainingJob.user_id == user_id,
                ExternalTrainingJob.minion_id == minion_id,
                ExternalTrainingJob.config_hash == config_hash,
                ExternalTrainingJob.created_at >= cutoff_time
            ).order_by(ExternalTrainingJob.created_at.desc()).all()
            
            return similar_jobs[0] if similar_jobs else None
            
        except Exception as e:
            # Log error but don't fail the request
            print(f"⚠️ Error checking for similar jobs: {e}")
            return None
    
    def create_training_job_with_hash(self, job_data: Dict[str, Any], 
                                    rag_config: Dict[str, Any], 
                                    selected_datasets: List[str]) -> ExternalTrainingJob:
        """
        Create a new training job with configuration hash for duplicate detection.
        
        Args:
            job_data: Basic job data
            rag_config: RAG configuration dictionary
            selected_datasets: List of dataset identifiers
            
        Returns:
            Created training job
        """
        try:
            # Generate configuration hash
            config_hash = generate_training_hash(rag_config, selected_datasets)
            
            # Create training job object
            training_job = ExternalTrainingJob(
                job_name=job_data['job_name'],
                description=job_data.get('description', ''),
                minion_id=job_data['minion_id'],
                user_id=job_data['user_id'],
                provider=job_data['provider'],
                model_name=job_data['model'],
                training_type=TrainingType(job_data['training_type'].upper()),
                status=TrainingStatus(job_data['status'].upper()),
                config=json.dumps(job_data.get('config', {})),
                rag_config=json.dumps(rag_config, sort_keys=True),
                config_hash=config_hash,  # Store the hash
                created_at=datetime.utcnow()
            )
            
            # Save to database
            self.session.add(training_job)
            self.session.commit()
            self.session.refresh(training_job)
            
            return training_job
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_job_config_info(self, job: ExternalTrainingJob) -> Dict[str, Any]:
        """
        Get configuration information for a training job.
        
        Args:
            job: Training job object
            
        Returns:
            Dictionary with configuration details
        """
        try:
            rag_config = json.loads(job.rag_config) if job.rag_config else {}
            
            return {
                'job_id': job.id,
                'job_name': job.job_name,
                'config_hash': job.config_hash,
                'config_fingerprint': get_config_fingerprint(job.config_hash) if job.config_hash else 'unknown',
                'rag_config': rag_config,
                'status': job.status.value if job.status else 'unknown',
                'created_at': job.created_at.isoformat() if job.created_at else None,
                'xp_gained': job.xp_gained or 0
            }
        except Exception as e:
            return {
                'job_id': job.id,
                'job_name': job.job_name,
                'config_hash': job.config_hash,
                'config_fingerprint': 'error',
                'rag_config': {},
                'status': 'unknown',
                'created_at': None,
                'xp_gained': 0
            }
