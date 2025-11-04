"""
Dataset Service for AI Refinement Dashboard
Handles dataset operations and business logic
"""

from typing import List, Dict, Any, Optional
from repositories.dataset_repository import DatasetRepository
from database.postgres_connection import create_spirit_engine
from sqlalchemy.orm import sessionmaker
from model.dataset import Dataset
import json
import os

class DatasetService:
    """Service for dataset operations"""
    
    def __init__(self):
        engine = create_spirit_engine()
        Session = sessionmaker(bind=engine)
        self.session = Session()
        self.dataset_repo = DatasetRepository(self.session)
    
    def get_global_datasets(self) -> List[Dict[str, Any]]:
        """Get global admin-provided datasets (free for all users)"""
        try:
            # Global datasets are those without a user_id (NULL) or with is_public=True
            datasets = self.dataset_repo.get_global_datasets()
            
            # Transform to frontend format
            dataset_list = []
            for dataset in datasets:
                dataset_dict = {
                    'id': dataset.id,
                    'name': dataset.name,
                    'description': dataset.description or '',
                    'type': dataset.dataset_type,
                    'format': dataset.format,
                    'sample_count': dataset.total_items,
                    'sampleCount': dataset.total_items,  # Frontend expects this field
                    'file_size': dataset.file_size,
                    'quality_score': dataset.quality_score,
                    'processing_status': dataset.processing_status,
                    'is_active': dataset.is_active,
                    'is_public': dataset.is_public,
                    'is_verified': dataset.is_verified,
                    'usage_count': dataset.usage_count,
                    'tags': dataset.tags or [],
                    'created_at': dataset.created_at.isoformat() if dataset.created_at else None,
                    'updated_at': dataset.updated_at.isoformat() if dataset.updated_at else None,
                    'last_used': dataset.last_used.isoformat() if dataset.last_used else None,
                    'version': dataset.version or '1.0',
                    'file_path': dataset.file_path,
                    'file_hash': dataset.file_hash,
                    'processed_items': dataset.processed_items,
                    'is_global': True  # Mark as global dataset
                    # Removed large fields: config, preprocessing_config, validation_config, dataset_metadata
                }
                dataset_list.append(dataset_dict)
            
            return dataset_list
            
        except Exception as e:
            print(f"Error getting global datasets: {e}")
            return []

    def get_user_datasets(self, user_id: int) -> List[Dict[str, Any]]:
        """Get datasets for a specific user - USER SCOPED"""
        try:
            datasets = self.dataset_repo.get_by_user_id(user_id)
            
            # Transform to frontend format
            dataset_list = []
            for dataset in datasets:
                dataset_dict = {
                    'id': dataset.id,
                    'name': dataset.name,
                    'description': dataset.description or '',
                    'type': dataset.dataset_type,
                    'format': dataset.format,
                    'sample_count': dataset.total_items,
                    'sampleCount': dataset.total_items,  # Frontend expects this field
                    'file_size': dataset.file_size,
                    'quality_score': dataset.quality_score,
                    'processing_status': dataset.processing_status,
                    'is_active': dataset.is_active,
                    'is_public': dataset.is_public,
                    'is_verified': dataset.is_verified,
                    'usage_count': dataset.usage_count,
                    'tags': dataset.tags or [],
                    'created_at': dataset.created_at.isoformat() if dataset.created_at else None,
                    'updated_at': dataset.updated_at.isoformat() if dataset.updated_at else None,
                    'last_used': dataset.last_used.isoformat() if dataset.last_used else None,
                    'version': dataset.version or '1.0',
                    'file_path': dataset.file_path,
                    'file_hash': dataset.file_hash,
                    'processed_items': dataset.processed_items,
                    'is_global': False,  # Mark as user dataset
                    'user_id': user_id
                    # Removed large fields: config, preprocessing_config, validation_config, dataset_metadata
                }
                dataset_list.append(dataset_dict)
            
            return dataset_list
            
        except Exception as e:
            print(f"Error getting datasets for user {user_id}: {e}")
            return []

    def get_all_datasets(self) -> List[Dict[str, Any]]:
        """Get all available datasets (admin only)"""
        try:
            datasets = self.dataset_repo.get_all()
            
            # Transform to frontend format
            dataset_list = []
            for dataset in datasets:
                dataset_dict = {
                    'id': dataset.id,
                    'name': dataset.name,
                    'description': dataset.description or '',
                    'type': dataset.dataset_type,
                    'format': dataset.format,
                    'sample_count': dataset.total_items,
                    'sampleCount': dataset.total_items,  # Frontend expects this field
                    'file_size': dataset.file_size,
                    'quality_score': dataset.quality_score,
                    'processing_status': dataset.processing_status,
                    'is_active': dataset.is_active,
                    'is_public': dataset.is_public,
                    'is_verified': dataset.is_verified,
                    'usage_count': dataset.usage_count,
                    'tags': dataset.tags or [],
                    'created_at': dataset.created_at.isoformat() if dataset.created_at else None,
                    'updated_at': dataset.updated_at.isoformat() if dataset.updated_at else None,
                    'last_used': dataset.last_used.isoformat() if dataset.last_used else None,
                    'version': dataset.version or '1.0',
                    'file_path': dataset.file_path,
                    'file_hash': dataset.file_hash,
                    'processed_items': dataset.processed_items,
                    'config': dataset.config or {},
                    'preprocessing_config': dataset.preprocessing_config or {},
                    'validation_config': dataset.validation_config or {},
                    'dataset_metadata': dataset.dataset_metadata or {}
                }
                dataset_list.append(dataset_dict)
            
            return dataset_list
            
        except Exception as e:
            print(f"Error getting datasets: {e}")
            return []
    
    def get_dataset_by_id(self, dataset_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific dataset by ID"""
        try:
            dataset = self.dataset_repo.get_by_id(dataset_id)
            if not dataset:
                return None
            
            return {
                'id': dataset.id,
                'name': dataset.name,
                'description': dataset.description or '',
                'type': dataset.dataset_type,
                'format': dataset.format,
                'sample_count': dataset.total_items,
                'sampleCount': dataset.total_items,
                'file_size': dataset.file_size,
                'quality_score': dataset.quality_score,
                'processing_status': dataset.processing_status,
                'is_active': dataset.is_active,
                'is_public': dataset.is_public,
                'is_verified': dataset.is_verified,
                'usage_count': dataset.usage_count,
                'tags': dataset.tags or [],
                'created_at': dataset.created_at.isoformat() if dataset.created_at else None,
                'updated_at': dataset.updated_at.isoformat() if dataset.updated_at else None,
                'last_used': dataset.last_used.isoformat() if dataset.last_used else None,
                'version': dataset.version or '1.0',
                'file_path': dataset.file_path,
                'file_hash': dataset.file_hash,
                'processed_items': dataset.processed_items,
                'config': dataset.config or {},
                'preprocessing_config': dataset.preprocessing_config or {},
                'validation_config': dataset.validation_config or {},
                'dataset_metadata': dataset.dataset_metadata or {}
        }
        
        except Exception as e:
            print(f"Error getting dataset {dataset_id}: {e}")
            return None
    
    def get_dataset_data(self, dataset_id: int) -> Optional[Dict[str, Any]]:
        """Get dataset with actual data content loaded from file"""
        try:
            dataset = self.dataset_repo.get_by_id(dataset_id)
            if not dataset:
                return None
            
            # Try to load samples from metadata first (for Hugging Face datasets)
            dataset_data = []
            if dataset.dataset_metadata:
                try:
                    metadata = json.loads(dataset.dataset_metadata) if isinstance(dataset.dataset_metadata, str) else dataset.dataset_metadata
                    if 'all_samples' in metadata:
                        dataset_data = metadata['all_samples']
                        print(f"✅ Loaded {len(dataset_data)} samples from metadata")
                    else:
                        print(f"⚠️ No 'all_samples' found in metadata")
                except Exception as e:
                    print(f"⚠️ Failed to parse metadata: {e}")
            
            # If no samples from metadata, try to load from file
            if not dataset_data and dataset.file_path:
                try:
                    dataset_data = self._load_dataset_from_file(dataset.file_path, dataset.format)
                    print(f"✅ Loaded {len(dataset_data)} samples from file")
                except Exception as e:
                    print(f"⚠️ Failed to load from file: {e}")
            
            return {
                'id': dataset.id,
                'name': dataset.name,
                'description': dataset.description or '',
                'type': dataset.dataset_type,
                'format': dataset.format,
                'sample_count': dataset.total_items,
                'sampleCount': dataset.total_items,
                'file_size': dataset.file_size,
                'quality_score': dataset.quality_score,
                'processing_status': dataset.processing_status,
                'is_active': dataset.is_active,
                'is_public': dataset.is_public,
                'is_verified': dataset.is_verified,
                'usage_count': dataset.usage_count,
                'tags': dataset.tags or [],
                'created_at': dataset.created_at.isoformat() if dataset.created_at else None,
                'updated_at': dataset.updated_at.isoformat() if dataset.updated_at else None,
                'last_used': dataset.last_used.isoformat() if dataset.last_used else None,
                'version': dataset.version or '1.0',
                'file_path': dataset.file_path,
                'file_hash': dataset.file_hash,
                'processed_items': dataset.processed_items,
                'config': dataset.config or {},
                'preprocessing_config': dataset.preprocessing_config or {},
                'validation_config': dataset.validation_config or {},
                'dataset_metadata': dataset.dataset_metadata or {},
                'all_samples': dataset_data  # Include actual dataset content
            }
        
        except Exception as e:
            print(f"Error getting dataset data {dataset_id}: {e}")
            return None
    
    def _load_dataset_from_file(self, file_path: str, file_format: str) -> List[Dict[str, Any]]:
        """Load dataset content from file based on format"""
        try:
            if not os.path.exists(file_path):
                print(f"Dataset file not found: {file_path}")
                return []
            
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_format.lower() == 'json':
                    data = json.load(f)
                    # Handle different JSON structures
                    if isinstance(data, list):
                        return data
                    elif isinstance(data, dict) and 'data' in data:
                        return data['data']
                    elif isinstance(data, dict) and 'samples' in data:
                        return data['samples']
                    else:
                        # Convert single object to list
                        return [data]
                
                elif file_format.lower() == 'jsonl':
                    data = []
                    for line in f:
                        line = line.strip()
                        if line:
                            data.append(json.loads(line))
                    return data
                
                elif file_format.lower() == 'csv':
                    import csv
                    reader = csv.DictReader(f)
                    return list(reader)
                
                else:
                    # For text files, create simple structure
                    content = f.read()
                    return [{'text': content, 'source': file_path}]
        
        except Exception as e:
            print(f"Error loading dataset from file {file_path}: {e}")
            return []
    
    def get_datasets_by_type(self, dataset_type: str) -> List[Dict[str, Any]]:
        """Get datasets by type"""
        try:
            datasets = self.dataset_repo.get_by_type(dataset_type)
            return [self._dataset_to_dict(dataset) for dataset in datasets]
        except Exception as e:
            print(f"Error getting datasets by type {dataset_type}: {e}")
            return []
    
    def delete_dataset(self, dataset_id: int) -> bool:
        """Delete a dataset by ID"""
        try:
            # Check if dataset exists
            dataset = self.dataset_repo.get_by_id(dataset_id)
            if not dataset:
                return False
            
            # Delete the dataset
            success = self.dataset_repo.delete(dataset_id)
            if success:
                print(f"Dataset {dataset_id} deleted successfully")
            else:
                print(f"Failed to delete dataset {dataset_id}")
            
            return success
        except Exception as e:
            print(f"Error deleting dataset {dataset_id}: {e}")
            return False
    
    def get_processed_datasets(self) -> List[Dict[str, Any]]:
        """Get processed datasets"""
        try:
            datasets = self.dataset_repo.get_processed_datasets()
            return [self._dataset_to_dict(dataset) for dataset in datasets]
        except Exception as e:
            print(f"Error getting processed datasets: {e}")
            return []
    
    def get_public_datasets(self) -> List[Dict[str, Any]]:
        """Get public datasets"""
        try:
            datasets = self.dataset_repo.get_public_datasets()
            return [self._dataset_to_dict(dataset) for dataset in datasets]
        except Exception as e:
            print(f"Error getting public datasets: {e}")
            return []
    
    def get_verified_datasets(self) -> List[Dict[str, Any]]:
        """Get verified datasets"""
        try:
            datasets = self.dataset_repo.get_verified_datasets()
            return [self._dataset_to_dict(dataset) for dataset in datasets]
        except Exception as e:
            print(f"Error getting verified datasets: {e}")
            return []
    
    def get_dataset_statistics(self) -> Dict[str, Any]:
        """Get dataset statistics"""
        try:
            return self.dataset_repo.get_dataset_statistics()
        except Exception as e:
            print(f"Error getting dataset statistics: {e}")
            return {}
    
    def create_dataset(self, dataset_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new dataset in the database"""
        try:
            # Create new Dataset instance
            dataset = Dataset(
                name=dataset_data['name'],
                description=dataset_data.get('description', ''),
                dataset_type=dataset_data['dataset_type'],
                format=dataset_data['format'],
                file_path=dataset_data['file_path'],
                file_size=dataset_data.get('file_size', 0),
                file_hash=dataset_data.get('file_hash'),
                total_items=dataset_data.get('total_items', 0),
                processed_items=dataset_data.get('processed_items', 0),
                quality_score=dataset_data.get('quality_score', 0.0),
                processing_status=dataset_data.get('processing_status', 'completed'),
                is_active=dataset_data.get('is_active', True),
                is_public=dataset_data.get('is_public', False),
                is_verified=dataset_data.get('is_verified', False),
                usage_count=dataset_data.get('usage_count', 0),
                tags=json.dumps(dataset_data.get('tags', [])),
                version=dataset_data.get('version', '1.0'),
                user_id=dataset_data.get('user_id'),
                config=json.dumps(dataset_data.get('config', {})),
                preprocessing_config=json.dumps(dataset_data.get('preprocessing_config', {})),
                validation_config=json.dumps(dataset_data.get('validation_config', {})),
                dataset_metadata=json.dumps(dataset_data.get('dataset_metadata', {}))
            )
            
            # Save to database
            self.session.add(dataset)
            self.session.commit()
            self.session.refresh(dataset)
            
            # Return the created dataset as dictionary
            return self._dataset_to_dict(dataset)
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def _dataset_to_dict(self, dataset: Dataset) -> Dict[str, Any]:
        """Convert dataset model to dictionary"""
        return {
            'id': dataset.id,
            'name': dataset.name,
            'description': dataset.description or '',
            'type': dataset.dataset_type,
            'format': dataset.format,
            'sample_count': dataset.total_items,
            'sampleCount': dataset.total_items,
            'file_size': dataset.file_size,
            'quality_score': dataset.quality_score,
            'processing_status': dataset.processing_status,
            'is_active': dataset.is_active,
            'is_public': dataset.is_public,
            'is_verified': dataset.is_verified,
            'usage_count': dataset.usage_count,
            'tags': dataset.tags or [],
            'created_at': dataset.created_at.isoformat() if dataset.created_at else None,
            'updated_at': dataset.updated_at.isoformat() if dataset.updated_at else None,
            'last_used': dataset.last_used.isoformat() if dataset.last_used else None,
            'version': dataset.version or '1.0',
            'file_path': dataset.file_path,
            'file_hash': dataset.file_hash,
            'processed_items': dataset.processed_items,
            'config': json.loads(dataset.config) if dataset.config else {},
            'preprocessing_config': json.loads(dataset.preprocessing_config) if dataset.preprocessing_config else {},
            'validation_config': json.loads(dataset.validation_config) if dataset.validation_config else {},
            'dataset_metadata': json.loads(dataset.dataset_metadata) if dataset.dataset_metadata else {}
        }