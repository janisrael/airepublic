"""
Dataset repository for dataset management operations
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from model.dataset import Dataset, Evaluation
from .base import BaseRepository

class DatasetRepository(BaseRepository[Dataset]):
    """Repository for dataset operations"""
    
    def __init__(self, session: Session):
        super().__init__(Dataset, session)
    
    def get_global_datasets(self) -> List[Dataset]:
        """Get global admin-provided datasets (free for all users)"""
        # Global datasets are those without a user_id (NULL) or with is_public=True
        return self.session.query(Dataset).filter(
            (Dataset.user_id.is_(None)) | (Dataset.is_public == True),
            Dataset.is_active == True
        ).all()
    
    def get_by_user_id(self, user_id: int) -> List[Dataset]:
        """Get datasets for a specific user - USER SCOPED"""
        return self.filter_by(user_id=user_id)
    
    def get_by_type(self, dataset_type: str) -> List[Dataset]:
        """Get datasets by type"""
        return self.filter_by(dataset_type=dataset_type)
    
    def get_by_format(self, format: str) -> List[Dataset]:
        """Get datasets by format"""
        return self.filter_by(format=format)
    
    def get_processed_datasets(self) -> List[Dataset]:
        """Get processed datasets"""
        return self.filter_by(processing_status='completed')
    
    def get_pending_datasets(self) -> List[Dataset]:
        """Get pending datasets"""
        return self.filter_by(processing_status='pending')
    
    def get_processing_datasets(self) -> List[Dataset]:
        """Get datasets currently being processed"""
        return self.filter_by(processing_status='processing')
    
    def get_failed_datasets(self) -> List[Dataset]:
        """Get failed datasets"""
        return self.filter_by(processing_status='failed')
    
    def get_public_datasets(self) -> List[Dataset]:
        """Get public datasets"""
        return self.filter_by(is_public=True, is_active=True)
    
    def get_verified_datasets(self) -> List[Dataset]:
        """Get verified datasets"""
        return self.filter_by(is_verified=True, is_active=True)
    
    def get_high_quality_datasets(self, min_quality_score: float = 80.0) -> List[Dataset]:
        """Get high quality datasets"""
        return self.session.query(Dataset).filter(
            Dataset.quality_score >= min_quality_score,
            Dataset.is_active == True
        ).all()
    
    def get_datasets_by_size_range(self, min_size: int = 0, max_size: int = None) -> List[Dataset]:
        """Get datasets by size range"""
        query = self.session.query(Dataset).filter(
            Dataset.file_size >= min_size
        )
        
        if max_size is not None:
            query = query.filter(Dataset.file_size <= max_size)
        
        return query.all()
    
    def get_datasets_by_item_count(self, min_items: int = 0, max_items: int = None) -> List[Dataset]:
        """Get datasets by item count range"""
        query = self.session.query(Dataset).filter(
            Dataset.total_items >= min_items
        )
        
        if max_items is not None:
            query = query.filter(Dataset.total_items <= max_items)
        
        return query.all()
    
    def get_recently_used_datasets(self, limit: int = 10) -> List[Dataset]:
        """Get recently used datasets"""
        return self.session.query(Dataset).filter(
            Dataset.last_used.isnot(None)
        ).order_by(desc(Dataset.last_used)).limit(limit).all()
    
    def get_most_used_datasets(self, limit: int = 10) -> List[Dataset]:
        """Get most used datasets"""
        return self.session.query(Dataset).order_by(desc(Dataset.usage_count)).limit(limit).all()
    
    def search_datasets(self, search_term: str) -> List[Dataset]:
        """Search datasets by name, description, or tags"""
        return self.search(search_term, ['name', 'description'])
    
    def get_datasets_by_tags(self, tags: List[str]) -> List[Dataset]:
        """Get datasets by tags (simplified implementation)"""
        # This would require JSON querying - simplified for now
        datasets = []
        for tag in tags:
            datasets.extend(self.session.query(Dataset).filter(
                Dataset.tags.contains(tag)
            ).all())
        return list(set(datasets))  # Remove duplicates
    
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
    
    def update_usage(self, dataset_id: int, usage_count: int = 1) -> bool:
        """Update dataset usage"""
        dataset = self.get_by_id(dataset_id)
        if dataset:
            dataset.usage_count += usage_count
            self.session.commit()
            return True
        return False
    
    def get_dataset_statistics(self) -> Dict[str, Any]:
        """Get dataset statistics"""
        total_datasets = self.count()
        processed_datasets = len(self.get_processed_datasets())
        pending_datasets = len(self.get_pending_datasets())
        failed_datasets = len(self.get_failed_datasets())
        public_datasets = len(self.get_public_datasets())
        verified_datasets = len(self.get_verified_datasets())
        
        # Calculate average quality score
        processed = self.get_processed_datasets()
        average_quality = sum(d.quality_score for d in processed) / len(processed) if processed else 0
        
        # Calculate total size
        total_size = sum(d.file_size for d in self.get_all())
        
        # Calculate total items
        total_items = sum(d.total_items for d in self.get_all())
        
        return {
            'total_datasets': total_datasets,
            'processed_datasets': processed_datasets,
            'pending_datasets': pending_datasets,
            'failed_datasets': failed_datasets,
            'public_datasets': public_datasets,
            'verified_datasets': verified_datasets,
            'average_quality': round(average_quality, 2),
            'total_size': total_size,
            'total_items': total_items
        }
    
    def get_dataset_types_distribution(self) -> Dict[str, int]:
        """Get distribution of dataset types"""
        datasets = self.get_all()
        type_distribution = {}
        
        for dataset in datasets:
            dataset_type = dataset.dataset_type
            type_distribution[dataset_type] = type_distribution.get(dataset_type, 0) + 1
        
        return type_distribution
    
    def get_dataset_formats_distribution(self) -> Dict[str, int]:
        """Get distribution of dataset formats"""
        datasets = self.get_all()
        format_distribution = {}
        
        for dataset in datasets:
            format_type = dataset.format
            format_distribution[format_type] = format_distribution.get(format_type, 0) + 1
        
        return format_distribution

class EvaluationRepository(BaseRepository[Evaluation]):
    """Repository for evaluation operations"""
    
    def __init__(self, session: Session):
        super().__init__(Evaluation, session)
    
    def get_by_dataset(self, dataset_id: int) -> List[Evaluation]:
        """Get evaluations for a dataset"""
        return self.filter_by(dataset_id=dataset_id)
    
    def get_by_evaluation_type(self, evaluation_type: str) -> List[Evaluation]:
        """Get evaluations by type"""
        return self.filter_by(evaluation_type=evaluation_type)
    
    def get_by_status(self, status: str) -> List[Evaluation]:
        """Get evaluations by status"""
        return self.filter_by(status=status)
    
    def get_completed_evaluations(self) -> List[Evaluation]:
        """Get completed evaluations"""
        return self.filter_by(status='completed')
    
    def get_pending_evaluations(self) -> List[Evaluation]:
        """Get pending evaluations"""
        return self.filter_by(status='pending')
    
    def get_failed_evaluations(self) -> List[Evaluation]:
        """Get failed evaluations"""
        return self.filter_by(status='failed')
    
    def get_high_score_evaluations(self, min_score: float = 80.0) -> List[Evaluation]:
        """Get high score evaluations"""
        return self.session.query(Evaluation).filter(
            Evaluation.score >= min_score
        ).all()
    
    def get_low_score_evaluations(self, max_score: float = 50.0) -> List[Evaluation]:
        """Get low score evaluations"""
        return self.session.query(Evaluation).filter(
            Evaluation.score <= max_score
        ).all()
    
    def get_evaluations_by_score_range(self, min_score: float = 0.0, max_score: float = 100.0) -> List[Evaluation]:
        """Get evaluations by score range"""
        return self.session.query(Evaluation).filter(
            Evaluation.score >= min_score,
            Evaluation.score <= max_score
        ).all()
    
    def get_latest_evaluations(self, limit: int = 10) -> List[Evaluation]:
        """Get latest evaluations"""
        return self.session.query(Evaluation).order_by(desc(Evaluation.created_at)).limit(limit).all()
    
    def get_evaluations_by_evaluator(self, evaluator: str) -> List[Evaluation]:
        """Get evaluations by evaluator"""
        return self.filter_by(evaluator=evaluator)
    
    def get_evaluations_by_method(self, evaluation_method: str) -> List[Evaluation]:
        """Get evaluations by method"""
        return self.filter_by(evaluation_method=evaluation_method)
    
    def get_evaluation_statistics(self) -> Dict[str, Any]:
        """Get evaluation statistics"""
        total_evaluations = self.count()
        completed_evaluations = len(self.get_completed_evaluations())
        pending_evaluations = len(self.get_pending_evaluations())
        failed_evaluations = len(self.get_failed_evaluations())
        
        # Calculate average score
        completed = self.get_completed_evaluations()
        average_score = sum(e.score for e in completed) / len(completed) if completed else 0
        
        # Calculate score distribution
        high_score = len(self.get_high_score_evaluations(80.0))
        low_score = len(self.get_low_score_evaluations(50.0))
        
        return {
            'total_evaluations': total_evaluations,
            'completed_evaluations': completed_evaluations,
            'pending_evaluations': pending_evaluations,
            'failed_evaluations': failed_evaluations,
            'average_score': round(average_score, 2),
            'high_score_evaluations': high_score,
            'low_score_evaluations': low_score
        }
    
    def get_evaluation_types_distribution(self) -> Dict[str, int]:
        """Get distribution of evaluation types"""
        evaluations = self.get_all()
        type_distribution = {}
        
        for evaluation in evaluations:
            eval_type = evaluation.evaluation_type
            type_distribution[eval_type] = type_distribution.get(eval_type, 0) + 1
        
        return type_distribution
    
    def get_evaluator_distribution(self) -> Dict[str, int]:
        """Get distribution of evaluators"""
        evaluations = self.get_all()
        evaluator_distribution = {}
        
        for evaluation in evaluations:
            evaluator = evaluation.evaluator or 'Unknown'
            evaluator_distribution[evaluator] = evaluator_distribution.get(evaluator, 0) + 1
        
        return evaluator_distribution
