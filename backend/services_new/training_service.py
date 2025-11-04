"""
Training service using SQLAlchemy models and repository pattern
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from repositories.training_repository import TrainingRepository, DatasetRepository
from model.training import ExternalTrainingJob, UserTrainingDataset, TrainingStatus, TrainingType
from datetime import datetime

class TrainingService:
    """Service for training management operations"""
    
    def __init__(self, session: Session):
        self.session = session
        self.training_repo = TrainingRepository(session)
        self.dataset_repo = DatasetRepository(session)
    
    def create_training_job(self, user_id: int, minion_id: int, job_name: str, 
                           training_type: TrainingType, provider: str, model_name: str, **kwargs) -> ExternalTrainingJob:
        """Create a new training job"""
        training_data = {
            'user_id': user_id,
            'minion_id': minion_id,
            'job_name': job_name,
            'training_type': training_type,
            'provider': provider,
            'model_name': model_name,
            'status': TrainingStatus.PENDING,
            'progress': 0.0,
            **kwargs
        }
        
        return self.training_repo.create(**training_data)
    
    def get_training_job_by_id(self, job_id: int) -> Optional[ExternalTrainingJob]:
        """Get training job by ID"""
        return self.training_repo.get_by_id(job_id)
    
    def get_user_training_jobs(self, user_id: int) -> List[ExternalTrainingJob]:
        """Get all training jobs for a user"""
        return self.training_repo.get_by_user(user_id)
    
    def get_minion_training_jobs(self, minion_id: int) -> List[ExternalTrainingJob]:
        """Get all training jobs for a minion"""
        return self.training_repo.get_by_minion(minion_id)
    
    def get_pending_jobs(self) -> List[ExternalTrainingJob]:
        """Get all pending training jobs"""
        return self.training_repo.get_pending_jobs()
    
    def get_running_jobs(self) -> List[ExternalTrainingJob]:
        """Get all running training jobs"""
        return self.training_repo.get_running_jobs()
    
    def get_completed_jobs(self) -> List[ExternalTrainingJob]:
        """Get all completed training jobs"""
        return self.training_repo.get_completed_jobs()
    
    def get_failed_jobs(self) -> List[ExternalTrainingJob]:
        """Get all failed training jobs"""
        return self.training_repo.get_failed_jobs()
    
    def get_user_pending_jobs(self, user_id: int) -> List[ExternalTrainingJob]:
        """Get pending training jobs for a user"""
        return self.training_repo.get_user_pending_jobs(user_id)
    
    def get_user_running_jobs(self, user_id: int) -> List[ExternalTrainingJob]:
        """Get running training jobs for a user"""
        return self.training_repo.get_user_running_jobs(user_id)
    
    def get_latest_job_by_minion(self, minion_id: int) -> Optional[ExternalTrainingJob]:
        """Get latest training job for a minion"""
        return self.training_repo.get_latest_job_by_minion(minion_id)
    
    def get_latest_job_by_minion_and_user(self, minion_id: int, user_id: int) -> Optional[ExternalTrainingJob]:
        """Get latest training job for a minion and user"""
        return self.training_repo.get_latest_job_by_minion_and_user(minion_id, user_id)
    
    def start_training_job(self, job_id: int) -> bool:
        """Start a training job"""
        return self.training_repo.start_job(job_id)
    
    def complete_training_job(self, job_id: int, metrics: Dict[str, Any] = None, 
                             improvements: Dict[str, Any] = None) -> bool:
        """Complete a training job"""
        return self.training_repo.complete_job(job_id, metrics, improvements)
    
    def fail_training_job(self, job_id: int, error_message: str) -> bool:
        """Fail a training job"""
        return self.training_repo.fail_job(job_id, error_message)
    
    def update_job_status(self, job_id: int, status: TrainingStatus, progress: float = None, 
                         error_message: str = None) -> bool:
        """Update training job status"""
        return self.training_repo.update_job_status(job_id, status, progress, error_message)
    
    def get_training_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get training statistics for a user"""
        return self.training_repo.get_training_statistics(user_id)
    
    def get_minion_training_history(self, minion_id: int) -> List[ExternalTrainingJob]:
        """Get training history for a minion"""
        return self.training_repo.get_minion_training_history(minion_id)
    
    def get_minion_training_statistics(self, minion_id: int) -> Dict[str, Any]:
        """Get training statistics for a minion"""
        return self.training_repo.get_minion_training_statistics(minion_id)
    
    def get_jobs_by_date_range(self, start_date: datetime, end_date: datetime) -> List[ExternalTrainingJob]:
        """Get training jobs by date range"""
        return self.training_repo.get_jobs_by_date_range(start_date, end_date)
    
    def get_user_jobs_by_date_range(self, user_id: int, start_date: datetime, end_date: datetime) -> List[ExternalTrainingJob]:
        """Get user training jobs by date range"""
        return self.training_repo.get_user_jobs_by_date_range(user_id, start_date, end_date)
    
    def create_training_dataset(self, user_id: int, name: str, dataset_type: str, 
                               file_path: str, **kwargs) -> UserTrainingDataset:
        """Create a new training dataset"""
        dataset_data = {
            'user_id': user_id,
            'name': name,
            'dataset_type': dataset_type,
            'file_path': file_path,
            'processing_status': 'pending',
            **kwargs
        }
        
        return self.dataset_repo.create(**dataset_data)
    
    def get_training_dataset_by_id(self, dataset_id: int) -> Optional[UserTrainingDataset]:
        """Get training dataset by ID"""
        return self.dataset_repo.get_by_id(dataset_id)
    
    def get_user_training_datasets(self, user_id: int) -> List[UserTrainingDataset]:
        """Get all training datasets for a user"""
        return self.dataset_repo.get_by_user(user_id)
    
    def get_processed_datasets(self) -> List[UserTrainingDataset]:
        """Get processed datasets"""
        return self.dataset_repo.get_processed_datasets()
    
    def get_user_processed_datasets(self, user_id: int) -> List[UserTrainingDataset]:
        """Get processed datasets for a user"""
        return self.dataset_repo.get_user_processed_datasets(user_id)
    
    def get_high_quality_datasets(self, min_quality_score: float = 80.0) -> List[UserTrainingDataset]:
        """Get high quality datasets"""
        return self.dataset_repo.get_high_quality_datasets(min_quality_score)
    
    def get_user_high_quality_datasets(self, user_id: int, min_quality_score: float = 80.0) -> List[UserTrainingDataset]:
        """Get high quality datasets for a user"""
        return self.dataset_repo.get_user_high_quality_datasets(user_id, min_quality_score)
    
    def update_dataset_processing_status(self, dataset_id: int, status: str, error_message: str = None) -> bool:
        """Update dataset processing status"""
        return self.dataset_repo.update_processing_status(dataset_id, status, error_message)
    
    def get_dataset_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get dataset statistics for a user"""
        return self.dataset_repo.get_dataset_statistics(user_id)
    
    def get_grouped_training_jobs(self, user_id: int) -> Dict[str, Any]:
        """Get grouped training jobs by minion for a user"""
        jobs = self.get_user_training_jobs(user_id)
        
        # Group by minion
        grouped_jobs = {}
        for job in jobs:
            minion_id = job.minion_id
            if minion_id not in grouped_jobs:
                grouped_jobs[minion_id] = []
            grouped_jobs[minion_id].append(job)
        
        # Get latest job per minion
        latest_jobs = {}
        for minion_id, minion_jobs in grouped_jobs.items():
            # Sort by created_at descending and get the first one
            latest_job = sorted(minion_jobs, key=lambda x: x.created_at, reverse=True)[0]
            latest_jobs[minion_id] = latest_job
        
        return {
            'grouped_jobs': grouped_jobs,
            'latest_jobs': latest_jobs,
            'total_minions': len(grouped_jobs),
            'total_jobs': len(jobs)
        }
