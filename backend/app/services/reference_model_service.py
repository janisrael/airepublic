"""
Reference Model Service - SQLAlchemy implementation
Handles all reference model-related business logic using SQLAlchemy ORM
"""

from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import json

from model.minion_models import ReferenceModel

class ReferenceModelService:
    """Service for managing reference model operations using SQLAlchemy"""
    
    def __init__(self):
        # Use the spirit system database connection (PostgreSQL ready)
        from database.postgres_connection import create_spirit_engine
        self.engine = create_spirit_engine()
        self.Session = sessionmaker(bind=self.engine)
    
    def get_all_reference_models(self) -> List[Dict[str, Any]]:
        """Get all reference models"""
        with self.Session() as session:
            try:
                reference_models = session.query(ReferenceModel).filter(
                    ReferenceModel.is_active == True
                ).order_by(ReferenceModel.provider, ReferenceModel.display_name).all()
                
                # Convert to list of dicts
                result = []
                for model in reference_models:
                    model_dict = {
                        'id': model.id,
                        'name': model.name,
                        'display_name': model.display_name,
                        'description': model.description,
                        'provider': model.provider,
                        'model_type': model.model_type,
                        'model_id': model.model_id,
                        'base_url': model.base_url,
                        'api_key_required': model.api_key_required,
                        'capabilities': model.capabilities or [],
                        'parameters': model.parameters or {},
                        'temperature': float(model.temperature) if model.temperature else 0.7,
                        'top_p': float(model.top_p) if model.top_p else 0.9,
                        'max_tokens': model.max_tokens,
                        'context_length': model.context_length,
                        'stream': model.stream,
                        'tags': model.tags or [],
                        'is_active': model.is_active,
                        'is_free': model.is_free,
                        'created_at': model.created_at.isoformat() if model.created_at else None,
                        'updated_at': model.updated_at.isoformat() if model.updated_at else None
                    }
                    result.append(model_dict)
                
                return result
                
            except Exception as e:
                print(f"Error getting reference models: {e}")
                return []
    
    def get_reference_model(self, model_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific reference model by ID"""
        with self.Session() as session:
            try:
                model = session.query(ReferenceModel).filter(
                    and_(
                        ReferenceModel.id == model_id,
                        ReferenceModel.is_active == True
                    )
                ).first()
                
                if not model:
                    return None
                
                return {
                    'id': model.id,
                    'name': model.name,
                    'display_name': model.display_name,
                    'description': model.description,
                    'provider': model.provider,
                    'model_type': model.model_type,
                    'model_id': model.model_id,
                    'base_url': model.base_url,
                    'api_key_required': model.api_key_required,
                    'capabilities': model.capabilities or [],
                    'parameters': model.parameters or {},
                    'temperature': float(model.temperature) if model.temperature else 0.7,
                    'top_p': float(model.top_p) if model.top_p else 0.9,
                    'max_tokens': model.max_tokens,
                    'context_length': model.context_length,
                    'stream': model.stream,
                    'tags': model.tags or [],
                    'is_active': model.is_active,
                    'is_free': model.is_free,
                    'created_at': model.created_at.isoformat() if model.created_at else None,
                    'updated_at': model.updated_at.isoformat() if model.updated_at else None
                }
                
            except Exception as e:
                print(f"Error getting reference model {model_id}: {e}")
                return None
    
    def create_reference_model(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new reference model"""
        with self.Session() as session:
            try:
                new_model = ReferenceModel(
                    name=model_data.get('name'),
                    display_name=model_data.get('display_name', model_data.get('name')),
                    description=model_data.get('description', ''),
                    provider=model_data.get('provider', 'custom'),
                    model_type=model_data.get('model_type', 'chat'),
                    model_id=model_data.get('model_id', model_data.get('name')),
                    base_url=model_data.get('base_url'),
                    api_key_required=model_data.get('api_key_required', True),
                    capabilities=model_data.get('capabilities', []),
                    parameters=model_data.get('parameters', {}),
                    temperature=model_data.get('temperature', 0.7),
                    top_p=model_data.get('top_p', 0.9),
                    max_tokens=model_data.get('max_tokens', 2048),
                    context_length=model_data.get('context_length', 4096),
                    stream=model_data.get('stream', True),
                    tags=model_data.get('tags', []),
                    is_active=model_data.get('is_active', True),
                    is_free=model_data.get('is_free', True)
                )
                
                session.add(new_model)
                session.commit()
                session.refresh(new_model)
                
                return {
                    'success': True,
                    'model': self.get_reference_model(new_model.id),
                    'message': 'Reference model created successfully',
                    'model_id': new_model.id
                }
                
            except Exception as e:
                session.rollback()
                print(f"Error creating reference model: {e}")
                return {'success': False, 'error': str(e)}
    
    def update_reference_model(self, model_id: int, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing reference model"""
        with self.Session() as session:
            try:
                model = session.query(ReferenceModel).filter(ReferenceModel.id == model_id).first()
                
                if not model:
                    return {'success': False, 'error': 'Reference model not found'}
                
                # Update fields
                for key, value in model_data.items():
                    if hasattr(model, key):
                        setattr(model, key, value)
                
                session.commit()
                
                return {
                    'success': True,
                    'model': self.get_reference_model(model_id),
                    'message': 'Reference model updated successfully'
                }
                
            except Exception as e:
                session.rollback()
                print(f"Error updating reference model: {e}")
                return {'success': False, 'error': str(e)}
    
    def delete_reference_model(self, model_id: int) -> Dict[str, Any]:
        """Delete a reference model (soft delete)"""
        with self.Session() as session:
            try:
                model = session.query(ReferenceModel).filter(ReferenceModel.id == model_id).first()
                
                if not model:
                    return {'success': False, 'error': 'Reference model not found'}
                
                model.is_active = False
                session.commit()
                
                return {
                    'success': True,
                    'message': 'Reference model deleted successfully'
                }
                
            except Exception as e:
                session.rollback()
                print(f"Error deleting reference model: {e}")
                return {'success': False, 'error': str(e)}
