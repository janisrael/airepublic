"""
Minion Service - SQLAlchemy implementation
Handles all minion-related business logic using SQLAlchemy ORM
"""

from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model.minion import ExternalAPIModel, TraitsLoadout
from .xp_calculator import XPCalculator
from model.provider import ProviderGroup
import os
import json
from datetime import datetime

class MinionService:
    """Service for managing minion operations using SQLAlchemy"""
    
    def __init__(self):
        # Use PostgreSQL database connection
        from database.postgres_connection import create_spirit_engine
        self.engine = create_spirit_engine()
        self.Session = sessionmaker(bind=self.engine)
        print("✅ Using PostgreSQL database connection")
    
    def _safe_json_parse(self, json_str, default_value):
        """Safely parse JSON string with fallback to default value"""
        if not json_str or not json_str.strip():
            return default_value
        try:
            return json.loads(json_str)
        except Exception:
            return default_value
    
    def get_user_minions(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all minions for a specific user"""
        with self.Session() as session:
            try:
                # Get minions with traits loadout data using LEFT JOIN
                if user_id == 1:  # Superuser can see all minions
                    minions = session.query(ExternalAPIModel, TraitsLoadout).outerjoin(
                        TraitsLoadout, ExternalAPIModel.id == TraitsLoadout.minion_id
                    ).filter(
                        ExternalAPIModel.is_active == True
                    ).order_by(
                        ExternalAPIModel.provider, ExternalAPIModel.display_name
                    ).all()
                else:
                    minions = session.query(ExternalAPIModel, TraitsLoadout).outerjoin(
                        TraitsLoadout, ExternalAPIModel.id == TraitsLoadout.minion_id
                    ).filter(
                        and_(
                            ExternalAPIModel.user_id == user_id,
                            ExternalAPIModel.is_active == True
                        )
                    ).order_by(ExternalAPIModel.provider, ExternalAPIModel.display_name).all()
                
                # Convert to list of dicts
                result = []
                for minion_data in minions:
                    minion, traits_loadout = minion_data
                    # Parse metadata and parameters safely
                    try:
                        metadata_obj = json.loads(minion.model_metadata) if minion.model_metadata and minion.model_metadata.strip() and minion.model_metadata.strip().startswith('{') else {}
                    except Exception:
                        metadata_obj = {}
                    try:
                        params_obj = json.loads(minion.parameters) if minion.parameters and minion.parameters.strip() and minion.parameters.strip().startswith('{') else {}
                    except Exception:
                        params_obj = {}

                    # Extract model_stats from metadata if present
                    model_stats = metadata_obj.get('model_stats') if isinstance(metadata_obj, dict) else None

                    # Prefer quantization from model_stats, then params, then model_type
                    inferred_quant = None
                    if model_stats and isinstance(model_stats, dict):
                        inferred_quant = model_stats.get('quantization')
                    if not inferred_quant and isinstance(params_obj, dict):
                        inferred_quant = params_obj.get('quantization') or params_obj.get('dtype') or params_obj.get('precision')

                    # Infer architecture
                    inferred_architecture = None
                    if model_stats and isinstance(model_stats, dict):
                        inferred_architecture = model_stats.get('architecture')
                    if not inferred_architecture and isinstance(params_obj, dict):
                        inferred_architecture = params_obj.get('type') or params_obj.get('architecture')

                    # Derive avatar url if missing but avatar_path exists
                    avatar_url = minion.avatar_url
                    if (not avatar_url or avatar_url.strip() == '') and getattr(minion, 'avatar_path', None):
                        filename = os.path.basename(minion.avatar_path)
                        avatar_url = f"/api/avatars/{filename}"

                    # Calculate proper XP and level progression
                    total_xp = (minion.total_usage_xp or 0) + (minion.total_training_xp or 0)
                    xp_progress = XPCalculator.get_xp_progress(total_xp)
                    
                    minion_dict = {
                        'id': minion.id,
                        'name': minion.name,
                        'display_name': minion.display_name,
                        'description': minion.description,
                        'provider': minion.provider,
                        'model_id': minion.model_id,
                        'capabilities': self._safe_json_parse(minion.capabilities, []),
                        'parameters': params_obj if params_obj else {},
                        'context_length': minion.context_length,
                        'max_tokens': minion.max_tokens,
                        'temperature': float(minion.temperature) if minion.temperature else 0.7,
                        'top_p': float(minion.top_p) if minion.top_p else 0.9,
                        'system_prompt': minion.system_prompt,
                        'experience': xp_progress['total_xp'],
                        'level': xp_progress['current_level'],
                        'total_usage_xp': minion.total_usage_xp or 0,
                        'total_training_xp': minion.total_training_xp or 0,
                        'xp_to_next_level': xp_progress['xp_to_next_level'],
                        'xp_progress_percentage': xp_progress['progress_percentage'],
                        'rank': xp_progress['rank_name'].lower(),
                        'rank_level': xp_progress['rank_level'],
                        'rank_display_name': xp_progress['rank_name'],
                        'score': minion.score or 0,
                        'score_breakdown': json.loads(minion.score_breakdown) if minion.score_breakdown and minion.score_breakdown.strip() and minion.score_breakdown.strip().startswith('{') else {},
                        'traits_slots': traits_loadout.slots if traits_loadout else 0,
                        'traits_points_available': traits_loadout.points_available if traits_loadout else 10,
                        'traits_points_spent': traits_loadout.points_spent if traits_loadout else 0,
                        'traits_intensities': traits_loadout.trait_intensities if traits_loadout else {},
                        'traits_compatibility_score': float(traits_loadout.compatibility_score) if traits_loadout and traits_loadout.compatibility_score else 0.0,
                        'traits_effectiveness_bonus': float(traits_loadout.effectiveness_bonus) if traits_loadout and traits_loadout.effectiveness_bonus else 0.0,
                        'avatar_url': avatar_url,
                        'quantization': inferred_quant or None,
                        'architecture': inferred_architecture or minion.model_type or 'unknown',
                        'license': 'AI Republic',
                        'tags': self._safe_json_parse(minion.tags, []),
                        'is_active': minion.is_active,
                        'is_favorite': False,  # Default to False since field doesn't exist
                        'minion_token': minion.minion_token,
                        'title': minion.title or 'AI Assistant',  # Minion title/role
                        'company': minion.company or 'AI Republic',  # Company affiliation
                        'theme_color': minion.theme_color or '#4f46e5',  # Theme color
                        'class_name': minion.class_name,  # Minion class
                        'created_at': minion.created_at.isoformat() if minion.created_at else None,
                        'updated_at': minion.updated_at.isoformat() if minion.updated_at else None,
                        'provider_display_name': minion.provider.title() if minion.provider else 'Unknown',
                        'provider_icon': 'settings_ethernet',  # Default icon
                        'provider_color': '#4f46e5',  # Default color
                        'model_stats': model_stats or None
                    }
                    result.append(minion_dict)
                
                return result
                
            except Exception as e:
                print(f"Error getting user minions: {e}")
                return []
    
    def get_all_minions(self) -> List[Dict[str, Any]]:
        """Get all minions (for external models endpoint)"""
        with self.Session() as session:
            try:
                # Get all active minions with traits loadout data using LEFT JOIN
                minions = session.query(ExternalAPIModel, TraitsLoadout).outerjoin(
                    TraitsLoadout, ExternalAPIModel.id == TraitsLoadout.minion_id
                ).filter(
                    ExternalAPIModel.is_active == True
                ).order_by(ExternalAPIModel.provider, ExternalAPIModel.display_name).all()
                
                # Convert to list of dicts (same format as get_user_minions)
                result = []
                for minion_data in minions:
                    minion, traits_loadout = minion_data  # Unpack the tuple
                    # Parse metadata and parameters safely
                    try:
                        metadata_obj = json.loads(minion.model_metadata) if minion.model_metadata and minion.model_metadata.strip() and minion.model_metadata.strip().startswith('{') else {}
                    except Exception:
                        metadata_obj = {}
                    try:
                        params_obj = json.loads(minion.parameters) if minion.parameters and minion.parameters.strip() and minion.parameters.strip().startswith('{') else {}
                    except Exception:
                        params_obj = {}

                    model_stats = metadata_obj.get('model_stats') if isinstance(metadata_obj, dict) else None

                    inferred_quant = None
                    if model_stats and isinstance(model_stats, dict):
                        inferred_quant = model_stats.get('quantization')
                    if not inferred_quant and isinstance(params_obj, dict):
                        inferred_quant = params_obj.get('quantization') or params_obj.get('dtype') or params_obj.get('precision')

                    inferred_architecture = None
                    if model_stats and isinstance(model_stats, dict):
                        inferred_architecture = model_stats.get('architecture')
                    if not inferred_architecture and isinstance(params_obj, dict):
                        inferred_architecture = params_obj.get('type') or params_obj.get('architecture')

                    avatar_url = minion.avatar_url
                    if (not avatar_url or avatar_url.strip() == '') and getattr(minion, 'avatar_path', None):
                        filename = os.path.basename(minion.avatar_path)
                        avatar_url = f"/api/avatars/{filename}"

                    # Calculate proper XP and level progression
                    total_xp = (minion.total_usage_xp or 0) + (minion.total_training_xp or 0)
                    xp_progress = XPCalculator.get_xp_progress(total_xp)

                    minion_dict = {
                        'id': minion.id,
                        'name': minion.name,
                        'display_name': minion.display_name,
                        'description': minion.description,
                        'provider': minion.provider,
                        'model_id': minion.model_id,
                        'capabilities': self._safe_json_parse(minion.capabilities, []),
                        'parameters': params_obj if params_obj else {},
                        'context_length': minion.context_length,
                        'max_tokens': minion.max_tokens,
                        'temperature': float(minion.temperature) if minion.temperature else 0.7,
                        'top_p': float(minion.top_p) if minion.top_p else 0.9,
                        'system_prompt': minion.system_prompt,
                        'experience': xp_progress['total_xp'],
                        'level': xp_progress['current_level'],
                        'total_usage_xp': minion.total_usage_xp or 0,
                        'total_training_xp': minion.total_training_xp or 0,
                        'xp_to_next_level': xp_progress['xp_to_next_level'],
                        'xp_progress_percentage': xp_progress['progress_percentage'],
                        'rank': xp_progress['rank_name'].lower(),
                        'rank_level': xp_progress['rank_level'],
                        'rank_display_name': xp_progress['rank_name'],
                        'score': minion.score or 0,
                        'score_breakdown': json.loads(minion.score_breakdown) if minion.score_breakdown and minion.score_breakdown.strip() and minion.score_breakdown.strip().startswith('{') else {},
                        'traits_slots': traits_loadout.slots if traits_loadout else 0,
                        'traits_points_available': traits_loadout.points_available if traits_loadout else 10,
                        'traits_points_spent': traits_loadout.points_spent if traits_loadout else 0,
                        'traits_intensities': traits_loadout.trait_intensities if traits_loadout else {},
                        'traits_compatibility_score': float(traits_loadout.compatibility_score) if traits_loadout and traits_loadout.compatibility_score else 0.0,
                        'traits_effectiveness_bonus': float(traits_loadout.effectiveness_bonus) if traits_loadout and traits_loadout.effectiveness_bonus else 0.0,
                        'avatar_url': avatar_url,
                        'quantization': inferred_quant or None,
                        'architecture': inferred_architecture or minion.model_type or 'unknown',
                        'license': 'AI Republic',
                        'tags': self._safe_json_parse(minion.tags, []),
                        'is_active': minion.is_active,
                        'is_favorite': False,  # Default to False since field doesn't exist
                        'minion_token': minion.minion_token,
                        'title': minion.title or 'AI Assistant',  # Minion title/role
                        'company': minion.company or 'AI Republic',  # Company affiliation
                        'theme_color': minion.theme_color or '#4f46e5',  # Theme color
                        'class_name': minion.class_name,  # Minion class
                        'created_at': minion.created_at.isoformat() if minion.created_at else None,
                        'updated_at': minion.updated_at.isoformat() if minion.updated_at else None,
                        'provider_display_name': minion.provider.title() if minion.provider else 'Unknown',
                        'provider_icon': 'settings_ethernet',  # Default icon
                        'provider_color': '#4f46e5',  # Default color
                        'model_stats': model_stats or None
                    }
                    result.append(minion_dict)
                
                return result
                
            except Exception as e:
                print(f"Error getting all minions: {e}")
                return []

    def get_user_minion(self, user_id: int, minion_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific minion for a user"""
        minions = self.get_user_minions(user_id)
        return next((m for m in minions if m['id'] == minion_id), None)
    
    def get_minion_by_id(self, minion_id: int) -> Optional[Dict[str, Any]]:
        """Get a minion by ID (for internal use)"""
        with self.Session() as session:
            try:
                minion = session.query(ExternalAPIModel).filter(
                    and_(
                        ExternalAPIModel.id == minion_id,
                        ExternalAPIModel.is_active == True
                    )
                ).first()
                
                if not minion:
                    return None
                
                # Convert to dictionary format
                minion_dict = {
                    'id': minion.id,
                    'name': minion.name,
                    'display_name': minion.display_name,
                    'provider': minion.provider,
                    'model_id': minion.model_id,
                    'api_key': minion.api_key,
                    'base_url': minion.base_url,
                    'temperature': minion.temperature,
                    'max_tokens': minion.max_tokens,
                    'system_prompt': minion.system_prompt,
                    'context_length': minion.context_length,
                    'capabilities': json.loads(minion.capabilities) if minion.capabilities and minion.capabilities.strip() and (minion.capabilities.strip().startswith('[') or minion.capabilities.strip().startswith('{')) else [],
                    'parameters': json.loads(minion.parameters) if minion.parameters and minion.parameters.strip() and minion.parameters.strip().startswith('{') else {},
                    'user_id': minion.user_id,
                    # RAG Configuration
                    'rag_enabled': minion.rag_enabled,
                    'rag_collection_name': minion.rag_collection_name,
                    'top_k': minion.top_k,
                    'similarity_threshold': minion.similarity_threshold,
                    'retrieval_method': minion.retrieval_method,
                    'enable_contextual_compression': minion.enable_contextual_compression,
                    'enable_source_citation': minion.enable_source_citation,
                    'enable_query_expansion': minion.enable_query_expansion,
                    'embedding_model': minion.embedding_model,
                    'chunk_size': minion.chunk_size,
                    'chunk_overlap': minion.chunk_overlap,
                    # LoRA Configuration
                    'lora_enabled': minion.lora_enabled,
                    'lora_rank': minion.lora_rank,
                    'lora_alpha': minion.lora_alpha,
                    'lora_dropout': minion.lora_dropout,
                    'lora_target_modules': json.loads(minion.lora_target_modules) if minion.lora_target_modules else [],
                    # Spirit Orchestration Configuration
                    'spirits_enabled': getattr(minion, 'spirits_enabled', False)  # Default to False if column doesn't exist yet
                }
                
                return minion_dict
                
            except Exception as e:
                print(f"Error getting minion by ID: {e}")
                return None
    
    def toggle_minion_favorite(self, user_id: int, minion_id: int) -> Dict[str, Any]:
        """Toggle minion favorite status"""
        with self.Session() as session:
            try:
                minion = session.query(ExternalAPIModel).filter(
                    and_(
                        ExternalAPIModel.id == minion_id,
                        ExternalAPIModel.user_id == user_id,
                        ExternalAPIModel.is_active == True
                    )
                ).first()
                
                if not minion:
                    return {'success': False, 'error': 'Minion not found'}
                
                minion.is_favorite = not minion.is_favorite
                session.commit()
                
                return {
                    'success': True,
                    'is_favorite': minion.is_favorite,
                    'message': f'Minion {"favorited" if minion.is_favorite else "unfavorited"} successfully'
                }
                
            except Exception as e:
                session.rollback()
                print(f"Error toggling minion favorite: {e}")
                return {'success': False, 'error': str(e)}
    
    def regenerate_minion_token(self, user_id: int, minion_id: int) -> Dict[str, Any]:
        """Regenerate minion token"""
        import secrets
        
        with self.Session() as session:
            try:
                minion = session.query(ExternalAPIModel).filter(
                    and_(
                        ExternalAPIModel.id == minion_id,
                        ExternalAPIModel.user_id == user_id
                    )
                ).first()
                
                if not minion:
                    return {'success': False, 'error': 'Minion not found'}
                
                new_token = secrets.token_urlsafe(32)
                minion.minion_token = new_token
                session.commit()
                
                return {
                    'success': True,
                    'new_token': new_token,
                    'message': 'Minion token regenerated successfully'
                }
                
            except Exception as e:
                session.rollback()
                print(f"Error regenerating minion token: {e}")
                return {'success': False, 'error': str(e)}
    
    def update_minion_xp(self, user_id: int, minion_id: int, xp_gain: int, xp_type: str = 'usage') -> Dict[str, Any]:
        """
        Update minion experience points
        
        Args:
            user_id: User ID owning the minion
            minion_id: Minion ID to update
            xp_gain: XP amount to add
            xp_type: 'usage' or 'training' - determines which column to update
        
        Returns:
            Dict with success status, new experience total, and level info
        """
        with self.Session() as session:
            try:
                minion = session.query(ExternalAPIModel).filter(
                    and_(
                        ExternalAPIModel.id == minion_id,
                        ExternalAPIModel.user_id == user_id
                    )
                ).first()
                
                if not minion:
                    return {'success': False, 'error': 'Minion not found'}
                
                # Update the appropriate XP column
                if xp_type == 'training':
                    minion.total_training_xp = (minion.total_training_xp or 0) + xp_gain
                else:  # 'usage' or default
                    minion.total_usage_xp = (minion.total_usage_xp or 0) + xp_gain
                
                # Calculate total XP (computed from both columns)
                total_xp = (minion.total_training_xp or 0) + (minion.total_usage_xp or 0)
                
                # Recalculate level and rank from total XP
                xp_progress = XPCalculator.get_xp_progress(total_xp)
                
                # Update level, rank, and rank_level in database
                old_level = minion.level
                minion.level = xp_progress['current_level']
                minion.rank = xp_progress['rank_name']
                minion.rank_level = xp_progress['rank_level']
                minion.xp_to_next_level = xp_progress['xp_to_next_level']
                
                # Check for level up or rank up
                leveled_up = xp_progress['current_level'] > old_level
                old_rank = minion.rank
                ranked_up = xp_progress['rank_name'] != old_rank
                
                session.commit()
                
                return {
                    'success': True,
                    'new_experience': total_xp,
                    'total_training_xp': minion.total_training_xp or 0,
                    'total_usage_xp': minion.total_usage_xp or 0,
                    'level': xp_progress['current_level'],
                    'rank': xp_progress['rank_name'],
                    'rank_level': xp_progress['rank_level'],
                    'xp_progress_percentage': xp_progress['progress_percentage'],
                    'xp_to_next_level': xp_progress['xp_to_next_level'],
                    'leveled_up': leveled_up,
                    'ranked_up': ranked_up,
                    'message': f'Minion gained {xp_gain} {xp_type} XP'
                }
                
            except Exception as e:
                session.rollback()
                print(f"Error updating minion XP: {e}")
                import traceback
                traceback.print_exc()
                return {'success': False, 'error': str(e)}
    
    def get_minion_capabilities(self, user_id: int, minion_id: int) -> Dict[str, Any]:
        """Get minion capabilities"""
        minion = self.get_user_minion(user_id, minion_id)
        if not minion:
            return {'success': False, 'error': 'Minion not found'}
        
        return {
            'success': True,
            'capabilities': minion.get('capabilities', []),
            'minion_name': minion.get('display_name', minion.get('name'))
        }
    
    def get_minion_stats(self, user_id: int, minion_id: int) -> Dict[str, Any]:
        """Get minion statistics"""
        minion = self.get_user_minion(user_id, minion_id)
        if not minion:
            return {'success': False, 'error': 'Minion not found'}
        
        # TODO: Add actual usage statistics from logs
        stats = {
            'total_requests': 0,
            'total_tokens': 0,
            'avg_response_time': 0,
            'success_rate': 100,
            'last_used': None
        }
        
        return {
            'success': True,
            'stats': stats,
            'minion_name': minion.get('display_name', minion.get('name'))
        }
    
    def create_minion(self, user_id: int, minion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new minion using SQLAlchemy"""
        import secrets
        
        with self.Session() as session:
            try:
                # Validate display_name is unique per user
                display_name = minion_data.get('display_name', minion_data.get('name'))
                if not display_name:
                    return {
                        'success': False,
                        'error': 'Display name is required'
                    }
                
                # Check for existing minion with same display_name for this user
                existing_minion = session.query(ExternalAPIModel).filter(
                    and_(
                        ExternalAPIModel.user_id == user_id,
                        ExternalAPIModel.display_name == display_name,
                        ExternalAPIModel.is_active == True
                    )
                ).first()
                
                if existing_minion:
                    return {
                        'success': False,
                        'error': f'Display name "{display_name}" already exists for your account. Please choose a unique name.'
                    }
                
                # Generate unique minion token
                minion_token = secrets.token_urlsafe(32)

                # Snapshot fields
                params_for_stats = minion_data.get('parameters', {}) or {}
                quantization_val = minion_data.get('quantization') or params_for_stats.get('quantization') or params_for_stats.get('dtype') or params_for_stats.get('precision')
                architecture_val = minion_data.get('model_type') or params_for_stats.get('type') or params_for_stats.get('architecture')
                model_stats = {
                    'provider': minion_data.get('provider'),
                    'model_id': minion_data.get('model_id') or minion_data.get('name'),
                    'parameters': params_for_stats,
                    'quantization': quantization_val,
                    'architecture': architecture_val,
                    'context_length': minion_data.get('context_length', 4096),
                    'max_tokens': minion_data.get('max_tokens', 2048),
                    'captured_at': datetime.utcnow().isoformat()
                }
                metadata_obj = {
                    'model_stats': model_stats,
                    'events': [
                        {
                            'type': 'created',
                            'timestamp': model_stats['captured_at'],
                            'payload': {'model_stats': model_stats}
                        }
                    ]
                }
                
                # Create new minion
                new_minion = ExternalAPIModel(
                    name=minion_data.get('name'),
                    display_name=minion_data.get('display_name', minion_data.get('name')),
                    description=minion_data.get('description', ''),
                    provider=minion_data.get('provider', 'custom'),
                    model_id=minion_data.get('model_id', minion_data.get('name')),
                    api_key=minion_data.get('api_key'),
                    base_url=minion_data.get('base_url'),
                    model_type=architecture_val or minion_data.get('model_type') or 'external',
                    capabilities=json.dumps(minion_data.get('capabilities', [])),
                    parameters=json.dumps(minion_data.get('parameters', {})),
                    context_length=minion_data.get('context_length', 4096),
                    max_tokens=minion_data.get('max_tokens', 2048),
                    temperature=minion_data.get('temperature', 0.7),
                    top_p=minion_data.get('top_p', 0.9),
                    system_prompt=minion_data.get('system_prompt', ''),
                    total_training_xp=0,
                    total_usage_xp=0,
                    level=1,
                    avatar_url=minion_data.get('avatar_url'),
                    avatar_path=minion_data.get('avatar_path'),
                    tags=json.dumps(minion_data.get('tags', [])),
                    is_active=True,
                    minion_token=minion_token,
                    user_id=user_id,
                    model_metadata=json.dumps(metadata_obj)
                )
                
                print(f"🔧 Adding minion to session: {new_minion.name}")
                session.add(new_minion)
                print(f"🔧 Committing minion to database...")
                session.commit()
                print(f"🔧 Minion committed successfully with ID: {new_minion.id}")
                session.refresh(new_minion)
                
                # Get the created minion with provider info
                created_minion = self.get_user_minion(user_id, new_minion.id)
                print(f"🔧 Retrieved created minion: {created_minion}")
                
                return {
                    'success': True,
                    'minion': created_minion,
                    'message': 'Minion created successfully',
                    'minion_id': new_minion.id
                }
                
            except Exception as e:
                session.rollback()
                print(f"Error creating minion: {e}")
                return {'success': False, 'error': str(e)}

    def update_minion(self, minion_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update minion data"""
        with self.Session() as session:
            try:
                minion = session.query(ExternalAPIModel).filter(
                    ExternalAPIModel.id == minion_id
                ).first()
                
                if not minion:
                    return {
                        'success': False,
                        'error': 'Minion not found'
                    }

                # Update fields
                if 'display_name' in update_data:
                    new_display_name = update_data['display_name']
                    
                    # Validate display_name is unique per user (if changed)
                    if new_display_name != minion.display_name:
                        existing_minion = session.query(ExternalAPIModel).filter(
                            and_(
                                ExternalAPIModel.user_id == minion.user_id,
                                ExternalAPIModel.display_name == new_display_name,
                                ExternalAPIModel.id != minion_id,
                                ExternalAPIModel.is_active == True
                            )
                        ).first()
                        
                        if existing_minion:
                            return {
                                'success': False,
                                'error': f'Display name "{new_display_name}" already exists for your account. Please choose a unique name.'
                            }
                    
                    minion.display_name = new_display_name
                if 'title' in update_data:
                    minion.title = update_data['title']
                if 'description' in update_data:
                    minion.description = update_data['description']
                if 'temperature' in update_data:
                    minion.temperature = float(update_data['temperature'])
                if 'max_tokens' in update_data:
                    minion.max_tokens = int(update_data['max_tokens'])
                if 'top_p' in update_data:
                    minion.top_p = float(update_data['top_p'])
                if 'system_prompt' in update_data:
                    minion.system_prompt = update_data['system_prompt']
                
                # RAG Configuration fields
                if 'rag_enabled' in update_data:
                    minion.rag_enabled = update_data['rag_enabled']
                if 'rag_collection_name' in update_data:
                    minion.rag_collection_name = update_data['rag_collection_name']
                if 'top_k' in update_data:
                    minion.top_k = update_data['top_k']
                if 'similarity_threshold' in update_data:
                    minion.similarity_threshold = update_data['similarity_threshold']
                if 'retrieval_method' in update_data:
                    minion.retrieval_method = update_data['retrieval_method']
                if 'enable_contextual_compression' in update_data:
                    minion.enable_contextual_compression = update_data['enable_contextual_compression']
                if 'enable_source_citation' in update_data:
                    minion.enable_source_citation = update_data['enable_source_citation']
                if 'enable_query_expansion' in update_data:
                    minion.enable_query_expansion = update_data['enable_query_expansion']
                if 'embedding_model' in update_data:
                    minion.embedding_model = update_data['embedding_model']
                if 'chunk_size' in update_data:
                    minion.chunk_size = update_data['chunk_size']
                if 'chunk_overlap' in update_data:
                    minion.chunk_overlap = update_data['chunk_overlap']

                session.commit()
                
                return {
                    'success': True,
                    'message': 'Minion updated successfully'
                }
                
            except Exception as e:
                session.rollback()
                print(f"Error updating minion: {e}")
                return {
                    'success': False,
                    'error': str(e)
                }

    def update_minion_traits(self, minion_id: int, traits_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update minion traits"""
        with self.Session() as session:
            try:
                # Check if minion exists
                minion = session.query(ExternalAPIModel).filter(
                    ExternalAPIModel.id == minion_id
                ).first()
                
                if not minion:
                    return {
                        'success': False,
                        'error': 'Minion not found'
                    }

                # Get or create traits loadout
                traits_loadout = session.query(TraitsLoadout).filter(
                    TraitsLoadout.minion_id == minion_id
                ).first()
                
                if not traits_loadout:
                    traits_loadout = TraitsLoadout(minion_id=minion_id)
                    session.add(traits_loadout)

                # Update traits
                if 'traits_intensities' in traits_data:
                    traits_loadout.trait_intensities = traits_data['traits_intensities']
                
                # Recalculate points spent
                if traits_loadout.trait_intensities:
                    total_points = sum(traits_loadout.trait_intensities.values())
                    traits_loadout.points_spent = total_points
                    traits_loadout.points_available = max(0, traits_loadout.points_available - total_points)

                session.commit()
                
                return {
                    'success': True,
                    'message': 'Minion traits updated successfully'
                }
                
            except Exception as e:
                session.rollback()
                print(f"Error updating minion traits: {e}")
                return {
                    'success': False,
                    'error': str(e)
                }
    
    def chat_with_minion(self, user_id: int, minion_id: int, message: str) -> Dict[str, Any]:
        """
        Chat with a minion using the unified orchestration pipeline.
        This method ensures both dashboard test modal and minion chatbot API
        use the same RAG and Spirit Orchestration logic.
        
        Args:
            user_id: User ID owning the minion
            minion_id: Minion ID to chat with
            message: User message
            
        Returns:
            Dict with success status, response, and metadata
        """
        try:
            # Verify minion exists and user owns it
            minion = self.get_user_minion(user_id, minion_id)
            if not minion:
                return {
                    'success': False,
                    'error': 'Minion not found or access denied'
                }
            
            # Import chat_with_model function to use unified orchestration
            # Import at function level to avoid circular import issues
            from app.routes.external_model_routes import chat_with_model
            
            # Get minion details for chat_with_model
            minion_details = self.get_minion_by_id(minion_id)
            if not minion_details:
                return {
                    'success': False,
                    'error': 'Minion configuration not found'
                }
            
            # Prepare parameters for chat_with_model
            system_prompt = minion_details.get('system_prompt', '')
            temperature = minion_details.get('temperature', 0.7)
            max_tokens = minion_details.get('max_tokens', 1000)
            top_p = minion_details.get('top_p', 0.9)
            context_length = minion_details.get('context_length', 4096)
            description = minion_details.get('description', '')
            capabilities = minion_details.get('capabilities', [])
            tags = minion_details.get('tags', [])
            
            # Let chat_with_model handle RAG and Spirits automatically
            # based on minion configuration (rag_enabled, spirits_enabled)
            result = chat_with_model(
                model_id=minion_id,
                message=message,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                context_length=context_length,
                description=description,
                capabilities=capabilities,
                tags=tags,
                use_rag=None,  # Let it use minion's rag_enabled setting
                use_spirits=None  # Let it use minion's spirits_enabled setting
            )
            
            # Update minion usage XP after successful chat
            if result.get('success'):
                # Award usage XP (small amount per chat interaction)
                usage_xp = 5  # Small XP gain per chat
                self.update_minion_xp(user_id, minion_id, usage_xp, xp_type='usage')
            
            return result
            
        except Exception as e:
            print(f"Error in chat_with_minion: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to chat with minion'
            }
