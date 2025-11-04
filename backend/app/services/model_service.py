"""
Model Service - New Clean Architecture
Handles all model-related business logic using SQLAlchemy with PostgreSQL

This is the new pipeline alongside existing code.
Original api_server.py remains untouched for backward compatibility.
"""

import subprocess
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

# Import from database package (SQLAlchemy) - using PostgreSQL
from database.postgres_connection import create_spirit_engine
from sqlalchemy.orm import sessionmaker

# Import SQLAlchemy models from PostgreSQL schema
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from model.minion import ExternalAPIModel
from model.user import User


class ModelService:
    """
    Service class for model operations using SQLAlchemy
    Handles both local (Ollama) and external API models
    """
    
    def __init__(self):
        """Initialize the service with database connection"""
        # Using PostgreSQL with SQLAlchemy
        self.engine = create_spirit_engine()
        self.Session = sessionmaker(bind=self.engine)
        self.session = None
    
    def get_session(self):
        """Get SQLAlchemy session"""
        if not self.session:
            self.session = self.Session()
        return self.session
    
    def close_session(self):
        """Close SQLAlchemy session"""
        if self.session:
            self.session.close()
            self.session = None
    
    def get_all_models(self) -> Dict[str, Any]:
        """
        Get all models (Ollama + External) with detailed capabilities
        Returns the same format as the original endpoint
        """
        try:
            all_models = []
            
            # Get Ollama models
            ollama_models = self._get_ollama_models()
            all_models.extend(ollama_models)
            
            # Get external API models using SQLAlchemy
            external_models = self._get_external_models()
            all_models.extend(external_models)
            
            return {
                'success': True,
                'models': all_models,
                'total': len(all_models)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'models': [],
                'total': 0
            }
        finally:
            self.close_session()
    
    def _get_ollama_models(self) -> List[Dict[str, Any]]:
        """
        Get Ollama models using subprocess (same as original)
        """
        models = []
        
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                # Parse Ollama list output
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                
                # Get training jobs to map Ollama names to proper version names
                training_jobs = []  # TODO: Implement with SQLAlchemy
                ollama_to_proper_name = {}
                for job in training_jobs:
                    if job.get('status') == 'COMPLETED' and job.get('model_name'):
                        proper_name = job['model_name']  # e.g., "kalsada:v1.0"
                        # Create mapping from Ollama name (with :latest) to proper version name
                        base_name = proper_name.split(':')[0]  # e.g., "kalsada"
                        ollama_name = f"{base_name}:latest"  # e.g., "kalsada:latest"
                        ollama_to_proper_name[ollama_name] = proper_name
                
                for line in lines:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            ollama_model_name = parts[0]
                            size = parts[1] if parts[1] != 'latest' else parts[2] if len(parts) > 2 else 'Unknown'
                            modified = ' '.join(parts[2:]) if len(parts) > 2 else 'Unknown'
                            
                            # Use proper version name if available, otherwise use Ollama name
                            display_name = ollama_to_proper_name.get(ollama_model_name, ollama_model_name)
                            
                            # Get detailed model information from ollama show
                            model_details = self._get_model_details_from_ollama(ollama_model_name)
                            
                            # Get avatar information from model profile using the display name
                            profile = None  # TODO: Implement with SQLAlchemy
                            avatar_url = profile['avatar_url'] if profile else None
                            
                            models.append({
                                'name': display_name,
                                'size': size,
                                'modified': modified,
                                'capabilities': model_details['capabilities'],
                                'architecture': model_details['architecture'],
                                'parameters': model_details['parameters'],
                                'context_length': model_details['context_length'],
                                'quantization': model_details['quantization'],
                                'temperature': model_details['temperature'],
                                'top_p': model_details['top_p'],
                                'system_prompt': model_details['system_prompt'],
                                'license': model_details['license'],
                                'avatar_url': avatar_url,
                                'type': 'ollama',
                                'ollama_name': ollama_model_name  # Keep original Ollama name for API calls
                            })
                            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Ollama not available, continue with external models
            pass
        
        return models
    
    def _get_external_models(self) -> List[Dict[str, Any]]:
        """
        Get external API models using SQLAlchemy
        """
        models = []
        
        try:
            session = self.get_session()
            
            # Query external API models using SQLAlchemy
            external_models = session.query(ExternalAPIModel).all()
            
            for model in external_models:
                # Use avatar from external_api_models table first, fallback to model profile
                avatar_url = model.avatar_url
                if not avatar_url and model.avatar_path:
                    # Construct avatar URL from avatar_path
                    filename = os.path.basename(model.avatar_path)
                    avatar_url = f"http://localhost:5001/api/avatars/{filename}"
                if not avatar_url:
                    profile = None  # TODO: Implement with SQLAlchemy
                    avatar_url = profile['avatar_url'] if profile else None
                
                # Parse capabilities from JSON string to array
                capabilities = []
                if model.capabilities:
                    try:
                        import json
                        if isinstance(model.capabilities, str):
                            capabilities = json.loads(model.capabilities) if model.capabilities.strip() else []
                        elif isinstance(model.capabilities, list):
                            capabilities = model.capabilities
                    except (json.JSONDecodeError, AttributeError):
                        capabilities = []
                
                models.append({
                    'id': model.id,
                    'name': model.name,
                    'display_name': model.display_name,
                    'description': model.description,
                    'provider': model.provider,
                    'model_id': model.model_id,
                    'base_url': model.base_url,
                    'capabilities': capabilities,
                    'parameters': model.parameters,
                    'context_length': model.context_length,
                    'max_tokens': model.max_tokens,
                    'quantization': getattr(model, 'quantization', None),  # Optional attribute
                    'architecture': getattr(model, 'architecture', None),  # Optional attribute
                    'license': getattr(model, 'license', None),  # Optional attribute
                    'embedding_length': getattr(model, 'embedding_length', None),  # Optional attribute
                    'temperature': model.temperature,
                    'top_p': model.top_p,
                    'system_prompt': model.system_prompt,
                    'experience': (model.total_training_xp or 0) + (model.total_usage_xp or 0),  # Computed from training + usage XP
                    'level': model.level,
                    'rank': model.rank,
                    'rank_level': model.rank_level,
                    'total_training_xp': model.total_training_xp or 0,
                    'total_usage_xp': model.total_usage_xp or 0,
                    'xp_to_next_level': model.xp_to_next_level or 0,
                    'is_active': model.is_active,
                    'is_favorite': getattr(model, 'is_favorite', False),  # Optional attribute
                    'tags': model.tags,
                    'avatar_url': avatar_url,
                    'type': 'external_api',
                    'created_at': model.created_at.isoformat() if model.created_at else None
                })
                
        except Exception as e:
            print(f"Error getting external models: {e}")
            # Fallback to original database service
            external_models = []  # TODO: Implement with SQLAlchemy
            for model in external_models:
                # Use avatar from external_api_models table first, fallback to model profile
                avatar_url = model.get('avatar_url')
                if not avatar_url and model.get('avatar_path'):
                    # Construct avatar URL from avatar_path
                    filename = os.path.basename(model['avatar_path'])
                    avatar_url = f"http://localhost:5001/api/avatars/{filename}"
                if not avatar_url:
                    profile = None  # TODO: Implement with SQLAlchemy
                    avatar_url = profile['avatar_url'] if profile else None
                
                models.append({
                    'id': model['id'],
                    'name': model['name'],
                    'display_name': model['display_name'],
                    'description': model['description'],
                    'provider': model['provider'],
                    'model_id': model['model_id'],
                    'base_url': model['base_url'],
                    'capabilities': model['capabilities'],
                    'parameters': model['parameters'],
                    'context_length': model['context_length'],
                    'max_tokens': model['max_tokens'],
                    'quantization': model['quantization'],
                    'architecture': model['architecture'],
                    'license': model['license'],
                    'embedding_length': model['embedding_length'],
                    'temperature': model['temperature'],
                    'top_p': model['top_p'],
                    'system_prompt': model['system_prompt'],
                    'experience': model['experience'],
                    'level': model['level'],
                    'is_active': model['is_active'],
                    'is_favorite': model['is_favorite'],
                    'tags': model['tags'],
                    'avatar_url': avatar_url,
                    'type': 'external_api',
                    'created_at': model['created_at']
                })
        
        return models
    
    def _get_model_details_from_ollama(self, model_name: str) -> Dict[str, Any]:
        """
        Get detailed model information from Ollama (same as original)
        """
        try:
            result = subprocess.run(['ollama', 'show', model_name], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                # Parse the model details
                details = result.stdout
                
                # Extract information (this is a simplified parser)
                # In production, you'd want a more robust parser
                return {
                    'capabilities': ['text-generation'],  # Default capabilities
                    'architecture': 'unknown',
                    'parameters': 'unknown',
                    'context_length': 4096,  # Default
                    'quantization': 'unknown',
                    'temperature': 0.7,
                    'top_p': 0.9,
                    'system_prompt': '',
                    'license': 'unknown'
                }
            else:
                # Return default values if ollama show fails
                return {
                    'capabilities': ['text-generation'],
                    'architecture': 'unknown',
                    'parameters': 'unknown',
                    'context_length': 4096,
                    'quantization': 'unknown',
                    'temperature': 0.7,
                    'top_p': 0.9,
                    'system_prompt': '',
                    'license': 'unknown'
                }
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Return default values if ollama is not available
            return {
                'capabilities': ['text-generation'],
                'architecture': 'unknown',
                'parameters': 'unknown',
                'context_length': 4096,
                'quantization': 'unknown',
                'temperature': 0.7,
                'top_p': 0.9,
                'system_prompt': '',
                'license': 'unknown'
            }
    
    def get_model_by_name(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific model by name
        """
        try:
            # First check external models
            session = self.get_session()
            external_model = session.query(ExternalAPIModel).filter(
                ExternalAPIModel.name == model_name
            ).first()
            
            if external_model:
                return {
                    'id': external_model.id,
                    'name': external_model.name,
                    'display_name': external_model.display_name,
                    'type': 'external_api'
                }
            
            # If not found in external models, it might be an Ollama model
            # Check if it's available in Ollama
            try:
                result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0 and model_name in result.stdout:
                    return {
                        'name': model_name,
                        'type': 'ollama'
                    }
            except:
                pass
            
            return None
            
        except Exception as e:
            print(f"Error getting model by name: {e}")
            return None
        finally:
            self.close_session()
    
    def create_model(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new external API model (minion)
        """
        try:
            session = self.get_session()
            
            # Create new ExternalAPIModel instance
            external_model = ExternalAPIModel(
                user_id=model_data.get('userId'),  # Get from authenticated user
                name=model_data.get('name', ''),
                display_name=model_data.get('displayName', ''),
                description=model_data.get('description', ''),
                provider=model_data.get('provider', 'external'),
                model_id=model_data.get('modelId', model_data.get('model_name', '')),
                api_key=model_data.get('apiKey', ''),
                base_url=model_data.get('baseUrl', ''),
                model_type=model_data.get('model_type', 'external'),
                max_tokens=model_data.get('max_tokens', 4096),
                temperature=model_data.get('temperature', 0.7),
                top_p=model_data.get('top_p', 0.9),
                context_length=model_data.get('context_length'),
                capabilities=model_data.get('capabilities', ''),
                parameters=model_data.get('parameters', ''),
                model_metadata=model_data.get('metadata', ''),
                avatar_url=model_data.get('avatarUrl', ''),
                avatar_path=model_data.get('avatarPath', ''),
                title=model_data.get('title', ''),
                company=model_data.get('company', ''),
                theme_color=model_data.get('themeColor', model_data.get('theme_color', '#4f46e5')),
                system_prompt=model_data.get('systemPrompt', model_data.get('system_prompt', '')),
                tags=str(model_data.get('tags', [])),  # Convert list to string
                is_active=True
            )
            
            session.add(external_model)
            session.commit()
            
            return {
                'id': external_model.id,
                'name': external_model.name,
                'display_name': external_model.display_name,
                'success': True,
                'message': 'Model created successfully'
            }
            
        except Exception as e:
            session.rollback()
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to create model'
            }
        finally:
            self.close_session()