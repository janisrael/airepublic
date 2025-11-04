#!/usr/bin/env python3
"""
Optimized API Service with Redis Caching
High-performance API endpoints with intelligent caching for large volume
"""

import sys
import os
from typing import Dict, List, Optional, Any
import logging
from functools import wraps

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from cache.redis_config import redis_manager, cache_result, cache_user_data
from database.optimized_connection import DatabaseSession

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptimizedAPIService:
    """High-performance API service with Redis caching"""
    
    def __init__(self):
        self.redis = redis_manager
        logger.info("✅ Optimized API Service initialized")
    
    # === MODELS API (CACHED) ===
    
    @cache_result(ttl=600)  # Cache for 10 minutes
    def get_models_cached(self) -> Dict:
        """Get models with Redis caching"""
        try:
            with DatabaseSession() as session:
                # Import models here to avoid circular imports
                from model.minion import ExternalAPIModel
                from model.legacy import ModelProfile
                
                # Get external API models
                external_models = session.query(ExternalAPIModel).filter(
                    ExternalAPIModel.is_active == True
                ).all()
                
                # Get local models (Ollama)
                local_models = self._get_ollama_models()
                
                # Combine and format
                models = []
                
                # Add external API models
                for model in external_models:
                    models.append({
                        'id': model.id,
                        'name': model.name,
                        'display_name': model.display_name,
                        'provider': model.provider,
                        'type': 'external_api',
                        'model_id': model.model_id,
                        'capabilities': model.capabilities or [],
                        'context_length': model.context_length,
                        'max_tokens': model.max_tokens,
                        'temperature': model.temperature,
                        'top_p': model.top_p,
                        'is_active': model.is_active,
                        'is_favorite': model.is_favorite,
                        'avatar_url': model.avatar_url,
                        'description': model.description,
                        'created_at': model.created_at.isoformat() if model.created_at else None
                    })
                
                # Add local models
                for model in local_models:
                    models.append({
                        'id': f"ollama_{model['name']}",
                        'name': model['name'],
                        'display_name': model['name'].replace(':', ' ').title(),
                        'provider': 'ollama',
                        'type': 'ollama',
                        'model_id': model['name'],
                        'capabilities': model.get('capabilities', []),
                        'context_length': model.get('context_length'),
                        'max_tokens': model.get('max_tokens'),
                        'temperature': model.get('temperature', 0.7),
                        'top_p': model.get('top_p', 0.9),
                        'is_active': True,
                        'is_favorite': False,
                        'avatar_url': None,
                        'description': f"Local Ollama model: {model['name']}",
                        'created_at': None
                    })
                
                return {
                    'success': True,
                    'total': len(models),
                    'models': models
                }
                
        except Exception as e:
            logger.error(f"Error getting cached models: {e}")
            return {
                'success': False,
                'total': 0,
                'models': [],
                'error': str(e)
            }
    
    @cache_result(ttl=300)  # Cache for 5 minutes
    def get_training_jobs_cached(self) -> Dict:
        """Get training jobs with Redis caching"""
        try:
            with DatabaseSession() as session:
                from model.legacy import TrainingJob
                
                jobs = session.query(TrainingJob).order_by(
                    TrainingJob.created_at.desc()
                ).limit(100).all()
                
                jobs_data = []
                for job in jobs:
                    jobs_data.append({
                        'id': job.id,
                        'model_name': job.model_name,
                        'training_type': job.training_type,
                        'status': job.status,
                        'progress': job.progress,
                        'accuracy': job.accuracy,
                        'created_at': job.created_at.isoformat() if job.created_at else None,
                        'updated_at': job.updated_at.isoformat() if job.updated_at else None,
                        'dataset_name': job.dataset_name,
                        'epochs': job.epochs,
                        'learning_rate': job.learning_rate
                    })
                
                return {
                    'success': True,
                    'total': len(jobs_data),
                    'jobs': jobs_data
                }
                
        except Exception as e:
            logger.error(f"Error getting cached training jobs: {e}")
            return {
                'success': True,
                'total': 0,
                'jobs': []
            }
    
    @cache_result(ttl=900)  # Cache for 15 minutes
    def get_datasets_cached(self) -> Dict:
        """Get datasets with Redis caching"""
        try:
            with DatabaseSession() as session:
                from model.legacy import Dataset
                
                datasets = session.query(Dataset).filter(
                    Dataset.is_active == True
                ).order_by(Dataset.created_at.desc()).all()
                
                datasets_data = []
                for dataset in datasets:
                    datasets_data.append({
                        'id': dataset.id,
                        'name': dataset.name,
                        'description': dataset.description,
                        'type': dataset.type,
                        'format': dataset.format,
                        'sample_count': dataset.sample_count,
                        'size': dataset.size,
                        'source': dataset.source,
                        'license': dataset.license,
                        'is_public': dataset.is_public,
                        'is_favorite': dataset.is_favorite,
                        'tags': dataset.tags or [],
                        'created_at': dataset.created_at.isoformat() if dataset.created_at else None,
                        'last_modified': dataset.last_modified.isoformat() if dataset.last_modified else None,
                        'metadata': dataset.metadata or {}
                    })
                
                return {
                    'success': True,
                    'total': len(datasets_data),
                    'datasets': datasets_data
                }
                
        except Exception as e:
            logger.error(f"Error getting cached datasets: {e}")
            return {
                'success': True,
                'total': 0,
                'datasets': []
            }
    
    # === USER-SPECIFIC CACHED DATA ===
    
    @cache_user_data(ttl=1800)  # Cache for 30 minutes
    def get_user_minions_cached(self, user_id: int) -> Dict:
        """Get user minions with Redis caching"""
        try:
            with DatabaseSession() as session:
                from model.minion import ExternalAPIModel
                
                user_minions = session.query(ExternalAPIModel).filter(
                    ExternalAPIModel.user_id == user_id,
                    ExternalAPIModel.is_active == True
                ).order_by(ExternalAPIModel.created_at.desc()).all()
                
                minions_data = []
                for minion in user_minions:
                    minions_data.append({
                        'id': minion.id,
                        'name': minion.name,
                        'display_name': minion.display_name,
                        'provider': minion.provider,
                        'model_id': minion.model_id,
                        'capabilities': minion.capabilities or [],
                        'context_length': minion.context_length,
                        'max_tokens': minion.max_tokens,
                        'temperature': minion.temperature,
                        'top_p': minion.top_p,
                        'is_active': minion.is_active,
                        'is_favorite': minion.is_favorite,
                        'avatar_url': minion.avatar_url,
                        'description': minion.description,
                        'created_at': minion.created_at.isoformat() if minion.created_at else None
                    })
                
                return {
                    'success': True,
                    'total': len(minions_data),
                    'minions': minions_data
                }
                
        except Exception as e:
            logger.error(f"Error getting cached user minions: {e}")
            return {
                'success': False,
                'total': 0,
                'minions': [],
                'error': str(e)
            }
    
    # === CACHE MANAGEMENT ===
    
    def invalidate_user_cache(self, user_id: int):
        """Invalidate all cache for a specific user"""
        self.redis.invalidate_user_cache(user_id)
        logger.info(f"Invalidated cache for user {user_id}")
    
    def invalidate_models_cache(self):
        """Invalidate models cache"""
        self.redis.invalidate_pattern("api:get_models_cached:*")
        logger.info("Invalidated models cache")
    
    def invalidate_training_jobs_cache(self):
        """Invalidate training jobs cache"""
        self.redis.invalidate_pattern("api:get_training_jobs_cached:*")
        logger.info("Invalidated training jobs cache")
    
    def invalidate_datasets_cache(self):
        """Invalidate datasets cache"""
        self.redis.invalidate_pattern("api:get_datasets_cached:*")
        logger.info("Invalidated datasets cache")
    
    # === HELPER METHODS ===
    
    def _get_ollama_models(self) -> List[Dict]:
        """Get local Ollama models"""
        try:
            import subprocess
            result = subprocess.run(['ollama', 'list'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                models = []
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                
                for line in lines:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            model_name = parts[0]
                            model_id = parts[1]
                            models.append({
                                'name': model_name,
                                'ollama_name': model_name,
                                'model_id': model_id,
                                'capabilities': ['text-generation'],
                                'context_length': 4096,  # Default
                                'max_tokens': 2048,      # Default
                                'temperature': 0.7,
                                'top_p': 0.9
                            })
                
                return models
            else:
                logger.warning("Failed to get Ollama models")
                return []
                
        except Exception as e:
            logger.warning(f"Error getting Ollama models: {e}")
            return []
    
    def get_cache_stats(self) -> Dict:
        """Get Redis cache statistics"""
        return self.redis.get_cache_stats()
    
    def get_database_pool_status(self) -> Dict:
        """Get database connection pool status"""
        from database.optimized_connection import db_manager
        return db_manager.get_pool_status()

# Global optimized API service instance
optimized_api_service = OptimizedAPIService()

# Export
__all__ = ['optimized_api_service', 'OptimizedAPIService']
