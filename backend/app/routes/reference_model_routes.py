"""
Reference Model Routes - V2 Clean Architecture
Handles reference models (public models anyone can use) using SQLAlchemy

Endpoints:
- /api/reference-models-v2 (GET) - Get all reference models
- /api/reference-models-v2/<int:model_id> (GET) - Get specific reference model
- /api/reference-models-v2/health (GET) - Health check
"""

from flask import Blueprint, jsonify, request
from sqlalchemy.orm import Session
from sqlalchemy import and_
import sys
import os

# Add backend directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Import SQLAlchemy models and connection
from model.reference_models import ReferenceModel
from database.postgres_connection import create_spirit_engine
from sqlalchemy.orm import sessionmaker

reference_model_bp = Blueprint('reference_models', __name__, url_prefix='/api/v2')

# Initialize SQLAlchemy engine and session
engine = create_spirit_engine()
Session = sessionmaker(bind=engine)

@reference_model_bp.route('/reference-models', methods=['GET'])
def get_reference_models_v2():
    """Get all reference models - V2 SQLAlchemy"""
    try:
        with Session() as session:
            # Get all active reference models
            models = session.query(ReferenceModel).filter(
                ReferenceModel.is_active == True
            ).order_by(ReferenceModel.created_at.desc()).all()
            
            # Convert to list of dicts
            result = []
            for model in models:
                model_dict = {
                    'id': model.id,
                    'name': model.name,
                    'display_name': model.display_name,
                    'description': model.description,
                    'title': model.title or '',
                    'company': model.company or '',
                    'theme_color': model.theme_color or '#4f46e5',
                    'model_type': model.model_type,
                    'provider': model.provider,
                    'model_id': model.model_id,
                    'api_key': model.api_key,
                    'base_url': model.base_url,
                    'temperature': float(model.temperature) if model.temperature else 0.6,
                    'top_p': float(model.top_p) if model.top_p else 0.9,
                    'max_tokens': model.max_tokens,
                    'stream': model.stream,
                    'capabilities': model.capabilities or [],
                    'parameters': model.parameters or {},
                    'context_length': model.context_length,
                    'system_prompt': model.system_prompt,
                    'is_active': model.is_active,
                    'is_favorite': model.is_favorite,
                    'tags': model.tags or [],
                    'created_at': model.created_at.isoformat() if model.created_at else None,
                    'updated_at': model.updated_at.isoformat() if model.updated_at else None
                }
                result.append(model_dict)
            
            return jsonify({
                'success': True,
                'models': result,
                'total': len(result),
                'version': '2.0.0',
                'database': 'SQLAlchemy + PostgreSQL'
            }), 200
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to retrieve reference models'
        }), 500

@reference_model_bp.route('/reference-models/<int:model_id>', methods=['GET'])
def get_reference_model_v2(model_id):
    """Get a specific reference model - V2 SQLAlchemy"""
    try:
        with Session() as session:
            model = session.query(ReferenceModel).filter(
                and_(
                    ReferenceModel.id == model_id,
                    ReferenceModel.is_active == True
                )
            ).first()
            
            if not model:
                return jsonify({
                    'success': False,
                    'error': 'Reference model not found'
                }), 404
            
            model_dict = {
                'id': model.id,
                'name': model.name,
                'display_name': model.display_name,
                'description': model.description,
                'title': model.title or '',
                'company': model.company or '',
                'theme_color': model.theme_color or '#4f46e5',
                'model_type': model.model_type,
                'provider': model.provider,
                'model_id': model.model_id,
                'api_key': model.api_key,
                'base_url': model.base_url,
                'temperature': float(model.temperature) if model.temperature else 0.6,
                'top_p': float(model.top_p) if model.top_p else 0.9,
                'max_tokens': model.max_tokens,
                'stream': model.stream,
                'capabilities': model.capabilities or [],
                'parameters': model.parameters or {},
                'context_length': model.context_length,
                'system_prompt': model.system_prompt,
                'is_active': model.is_active,
                'is_favorite': model.is_favorite,
                'tags': model.tags or [],
                'created_at': model.created_at.isoformat() if model.created_at else None,
                'updated_at': model.updated_at.isoformat() if model.updated_at else None
            }
            
            return jsonify({
                'success': True,
                'model': model_dict,
                'version': '2.0.0',
                'database': 'SQLAlchemy + PostgreSQL'
            }), 200
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to retrieve reference model'
        }), 500

@reference_model_bp.route('/reference-models/health', methods=['GET'])
def reference_models_health_v2():
    """Health check for reference models API - V2 SQLAlchemy"""
    return jsonify({
        'success': True,
        'message': 'Reference Models V2 API is healthy',
        'version': '2.0.0',
        'database': 'SQLAlchemy + PostgreSQL',
        'architecture': 'Clean V2 Architecture'
    }), 200
