"""
Dataset service using SQLAlchemy models and repository pattern
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from repositories.dataset_repository import DatasetRepository, EvaluationRepository
from model.dataset import Dataset, Evaluation

class DatasetService:
    """Service for dataset management operations"""
    
    def __init__(self, session: Session):
        self.session = session
        self.dataset_repo = DatasetRepository(session)
        self.evaluation_repo = EvaluationRepository(session)
    
    def create_dataset(self, **kwargs) -> Dataset:
        """Create a new dataset"""
        return self.dataset_repo.create(**kwargs)
    
    def get_dataset_by_id(self, dataset_id: int) -> Optional[Dataset]:
        """Get dataset by ID"""
        return self.dataset_repo.get_by_id(dataset_id)
    
    def get_processed_datasets(self) -> List[Dataset]:
        """Get processed datasets"""
        return self.dataset_repo.get_processed_datasets()
    
    def get_public_datasets(self) -> List[Dataset]:
        """Get public datasets"""
        return self.dataset_repo.get_public_datasets()
    
    def get_dataset_statistics(self) -> Dict[str, Any]:
        """Get dataset statistics"""
        return self.dataset_repo.get_dataset_statistics()
    
    def create_evaluation(self, **kwargs) -> Evaluation:
        """Create a new evaluation"""
        return self.evaluation_repo.create(**kwargs)
    
    def get_evaluations_by_dataset(self, dataset_id: int) -> List[Evaluation]:
        """Get evaluations for a dataset"""
        return self.evaluation_repo.get_by_dataset(dataset_id)
