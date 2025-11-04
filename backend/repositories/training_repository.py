"""
Training repository for training job operations
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from model.training import ExternalTrainingJob, UserTrainingDataset, TrainingJobDataset, TrainingStatus, TrainingType
from .base import BaseRepository

class TrainingRepository(BaseRepository[ExternalTrainingJob]):
    """Repository for training job operations"""
    
    def __init__(self, session: Session):
        super().__init__(ExternalTrainingJob, session)
    
    def get_by_user(self, user_id: int) -> List[ExternalTrainingJob]:
        """Get all training jobs for a user"""
        return self.filter_by(user_id=user_id)
    
    def get_by_minion(self, minion_id: int) -> List[ExternalTrainingJob]:
        """Get all training jobs for a minion"""
        return self.filter_by(minion_id=minion_id)
    
    def get_by_status(self, status: TrainingStatus) -> List[ExternalTrainingJob]:
        """Get training jobs by status"""
        return self.filter_by(status=status)
    
    def get_by_training_type(self, training_type: TrainingType) -> List[ExternalTrainingJob]:
        """Get training jobs by training type"""
        return self.filter_by(training_type=training_type)
    
    def get_by_provider(self, provider: str) -> List[ExternalTrainingJob]:
        """Get training jobs by provider"""
        return self.filter_by(provider=provider)
    
    def get_pending_jobs(self) -> List[ExternalTrainingJob]:
        """Get all pending training jobs"""
        return self.get_by_status(TrainingStatus.PENDING)
    
    def get_running_jobs(self) -> List[ExternalTrainingJob]:
        """Get all running training jobs"""
        return self.get_by_status(TrainingStatus.RUNNING)
    
    def get_completed_jobs(self) -> List[ExternalTrainingJob]:
        """Get all completed training jobs"""
        return self.get_by_status(TrainingStatus.COMPLETED)
    
    def get_failed_jobs(self) -> List[ExternalTrainingJob]:
        """Get all failed training jobs"""
        return self.get_by_status(TrainingStatus.FAILED)
    
    def get_user_pending_jobs(self, user_id: int) -> List[ExternalTrainingJob]:
        """Get pending training jobs for a user"""
        return self.session.query(ExternalTrainingJob).filter(
            ExternalTrainingJob.user_id == user_id,
            ExternalTrainingJob.status == TrainingStatus.PENDING
        ).all()
    
    def get_user_running_jobs(self, user_id: int) -> List[ExternalTrainingJob]:
        """Get running training jobs for a user"""
        return self.session.query(ExternalTrainingJob).filter(
            ExternalTrainingJob.user_id == user_id,
            ExternalTrainingJob.status == TrainingStatus.RUNNING
        ).all()
    
    def get_latest_job_by_minion(self, minion_id: int) -> Optional[ExternalTrainingJob]:
        """Get latest training job for a minion"""
        return self.session.query(ExternalTrainingJob).filter(
            ExternalTrainingJob.minion_id == minion_id
        ).order_by(desc(ExternalTrainingJob.created_at)).first()
    
    def get_latest_job_by_minion_and_user(self, minion_id: int, user_id: int) -> Optional[ExternalTrainingJob]:
        """Get latest training job for a minion and user"""
        return self.session.query(ExternalTrainingJob).filter(
            ExternalTrainingJob.minion_id == minion_id,
            ExternalTrainingJob.user_id == user_id
        ).order_by(desc(ExternalTrainingJob.created_at)).first()
    
    def get_jobs_by_date_range(self, start_date, end_date) -> List[ExternalTrainingJob]:
        """Get training jobs by date range"""
        return self.session.query(ExternalTrainingJob).filter(
            ExternalTrainingJob.created_at >= start_date,
            ExternalTrainingJob.created_at <= end_date
        ).all()
    
    def get_user_jobs_by_date_range(self, user_id: int, start_date, end_date) -> List[ExternalTrainingJob]:
        """Get user training jobs by date range"""
        return self.session.query(ExternalTrainingJob).filter(
            ExternalTrainingJob.user_id == user_id,
            ExternalTrainingJob.created_at >= start_date,
            ExternalTrainingJob.created_at <= end_date
        ).all()
    
    def update_job_status(self, job_id: int, status: TrainingStatus, progress: float = None, error_message: str = None) -> bool:
        """Update training job status"""
        job = self.get_by_id(job_id)
        if job:
            job.status = status
            if progress is not None:
                job.progress = progress
            if error_message is not None:
                job.error_message = error_message
            self.session.commit()
            return True
        return False
    
    def start_job(self, job_id: int) -> bool:
        """Start a training job"""
        job = self.get_by_id(job_id)
        if job and job.status == TrainingStatus.PENDING:
            job.status = TrainingStatus.RUNNING
            job.started_at = self.session.query(self.model).filter(self.model.id == job_id).first().created_at
            self.session.commit()
            return True
        return False
    
    def complete_job(self, job_id: int, metrics: Dict[str, Any] = None, improvements: Dict[str, Any] = None) -> bool:
        """Complete a training job"""
        job = self.get_by_id(job_id)
        if job and job.status == TrainingStatus.RUNNING:
            job.status = TrainingStatus.COMPLETED
            job.progress = 100.0
            job.completed_at = self.session.query(self.model).filter(self.model.id == job_id).first().created_at
            if metrics:
                job.metrics = metrics
            if improvements:
                job.improvements = improvements
            self.session.commit()
            return True
        return False
    
    def fail_job(self, job_id: int, error_message: str) -> bool:
        """Fail a training job"""
        job = self.get_by_id(job_id)
        if job:
            job.status = TrainingStatus.FAILED
            job.progress = 0.0
            job.error_message = error_message
            job.completed_at = self.session.query(self.model).filter(self.model.id == job_id).first().created_at
            self.session.commit()
            return True
        return False
    
    def get_training_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get training statistics for a user"""
        jobs = self.get_by_user(user_id)
        
        if not jobs:
            return {
                'total_jobs': 0,
                'completed_jobs': 0,
                'failed_jobs': 0,
                'pending_jobs': 0,
                'running_jobs': 0,
                'success_rate': 0,
                'total_xp_gained': 0
            }
        
        completed_jobs = [j for j in jobs if j.status == TrainingStatus.COMPLETED]
        failed_jobs = [j for j in jobs if j.status == TrainingStatus.FAILED]
        pending_jobs = [j for j in jobs if j.status == TrainingStatus.PENDING]
        running_jobs = [j for j in jobs if j.status == TrainingStatus.RUNNING]
        
        success_rate = (len(completed_jobs) / len(jobs)) * 100 if jobs else 0
        total_xp_gained = sum(j.xp_gained or 0 for j in completed_jobs)
        
        return {
            'total_jobs': len(jobs),
            'completed_jobs': len(completed_jobs),
            'failed_jobs': len(failed_jobs),
            'pending_jobs': len(pending_jobs),
            'running_jobs': len(running_jobs),
            'success_rate': round(success_rate, 2),
            'total_xp_gained': total_xp_gained
        }
    
    def get_minion_training_history(self, minion_id: int) -> List[ExternalTrainingJob]:
        """Get training history for a minion"""
        return self.session.query(ExternalTrainingJob).filter(
            ExternalTrainingJob.minion_id == minion_id
        ).order_by(desc(ExternalTrainingJob.created_at)).all()
    
    def get_minion_training_statistics(self, minion_id: int) -> Dict[str, Any]:
        """Get training statistics for a minion"""
        jobs = self.get_by_minion(minion_id)
        
        if not jobs:
            return {
                'total_trainings': 0,
                'successful_trainings': 0,
                'failed_trainings': 0,
                'total_xp_gained': 0,
                'average_improvement': 0,
                'last_training_date': None
            }
        
        successful_jobs = [j for j in jobs if j.status == TrainingStatus.COMPLETED]
        failed_jobs = [j for j in jobs if j.status == TrainingStatus.FAILED]
        
        total_xp_gained = sum(j.xp_gained or 0 for j in successful_jobs)
        
        # Calculate average improvement
        total_improvement = 0
        improvement_count = 0
        for job in successful_jobs:
            if job.improvements:
                improvements = job.improvements
                if isinstance(improvements, dict):
                    total_improvement += sum(improvements.values())
                    improvement_count += 1
        
        average_improvement = total_improvement / improvement_count if improvement_count > 0 else 0
        
        last_training_date = max(j.created_at for j in jobs) if jobs else None
        
        return {
            'total_trainings': len(jobs),
            'successful_trainings': len(successful_jobs),
            'failed_trainings': len(failed_jobs),
            'total_xp_gained': total_xp_gained,
            'average_improvement': round(average_improvement, 2),
            'last_training_date': last_training_date
        }

class DatasetRepository(BaseRepository[UserTrainingDataset]):
    """Repository for training dataset operations"""
    
    def __init__(self, session: Session):
        super().__init__(UserTrainingDataset, session)
    
    def get_by_user(self, user_id: int) -> List[UserTrainingDataset]:
        """Get all datasets for a user"""
        return self.filter_by(user_id=user_id)
    
    def get_by_type(self, dataset_type: str) -> List[UserTrainingDataset]:
        """Get datasets by type"""
        return self.filter_by(dataset_type=dataset_type)
    
    def get_processed_datasets(self) -> List[UserTrainingDataset]:
        """Get processed datasets"""
        return self.session.query(UserTrainingDataset).filter(
            UserTrainingDataset.processing_status == 'completed'
        ).all()
    
    def get_user_processed_datasets(self, user_id: int) -> List[UserTrainingDataset]:
        """Get processed datasets for a user"""
        return self.session.query(UserTrainingDataset).filter(
            UserTrainingDataset.user_id == user_id,
            UserTrainingDataset.processing_status == 'completed'
        ).all()
    
    def get_high_quality_datasets(self, min_quality_score: float = 80.0) -> List[UserTrainingDataset]:
        """Get high quality datasets"""
        return self.session.query(UserTrainingDataset).filter(
            UserTrainingDataset.quality_score >= min_quality_score
        ).all()
    
    def get_user_high_quality_datasets(self, user_id: int, min_quality_score: float = 80.0) -> List[UserTrainingDataset]:
        """Get high quality datasets for a user"""
        return self.session.query(UserTrainingDataset).filter(
            UserTrainingDataset.user_id == user_id,
            UserTrainingDataset.quality_score >= min_quality_score
        ).all()
    
    def update_processing_status(self, dataset_id: int, status: str, error_message: str = None) -> bool:
        """Update dataset processing status"""
        dataset = self.get_by_id(dataset_id)
        if dataset:
            dataset.processing_status = status
            if error_message:
                dataset.processing_error = error_message
            self.session.commit()
            return True
        return False
    
    def get_dataset_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get dataset statistics for a user"""
        datasets = self.get_by_user(user_id)
        
        if not datasets:
            return {
                'total_datasets': 0,
                'processed_datasets': 0,
                'total_items': 0,
                'average_quality': 0,
                'total_size': 0
            }
        
        processed_datasets = [d for d in datasets if d.processing_status == 'completed']
        total_items = sum(d.total_items for d in datasets)
        total_size = sum(d.file_size for d in datasets)
        average_quality = sum(d.quality_score for d in processed_datasets) / len(processed_datasets) if processed_datasets else 0
        
        return {
            'total_datasets': len(datasets),
            'processed_datasets': len(processed_datasets),
            'total_items': total_items,
            'average_quality': round(average_quality, 2),
            'total_size': total_size
        }
