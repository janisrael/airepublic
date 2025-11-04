"""
Model Routes - New Clean Architecture
API endpoints for model operations using SQLAlchemy service

This is the new pipeline alongside existing code.
Original api_server.py remains untouched for backward compatibility.
"""

from flask import Blueprint, jsonify, request, g
from app.services.model_service import ModelService
from app.routes.auth_routes import require_auth

# Create blueprint for model routes
model_bp = Blueprint('models', __name__, url_prefix='/api/v2')

# Initialize service
model_service = ModelService()


@model_bp.route('/models', methods=['GET', 'POST'])
@require_auth
def models_v2():
    """
    Get all models (GET) or Create new model (POST) - NEW SQLAlchemy implementation
    
    This is the new clean endpoint using SQLAlchemy service.
    Original /api/models endpoint remains untouched.
    """
    if request.method == 'GET':
        try:
            result = model_service.get_all_models()
            
            if result['success']:
                return jsonify(result), 200
            else:
                return jsonify(result), 500
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'models': [],
                'total': 0
            }), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No data provided'
                }), 400
            
            # Add the authenticated user's ID to the data
            data['userId'] = g.user['user_id']
            
            # Create new model using the service
            result = model_service.create_model(data)
            
            if result['success']:
                return jsonify(result), 201
            else:
                return jsonify(result), 400
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500


@model_bp.route('/models/<path:model_name>/details', methods=['GET'])
def get_model_details_endpoint_v2(model_name):
    """
    Get detailed information about a specific model - Details endpoint
    """
    try:
        model = model_service.get_model_by_name(model_name)
        
        if model:
            return jsonify({
                'success': True,
                'details': model
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'Model {model_name} not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@model_bp.route('/models/<path:model_name>', methods=['GET'])
def get_model_details_v2(model_name):
    """
    Get detailed information about a specific model - NEW SQLAlchemy implementation
    
    This is the new clean endpoint using SQLAlchemy service.
    Original /api/models/<model_name>/details endpoint remains untouched.
    """
    try:
        model = model_service.get_model_by_name(model_name)
        
        if model:
            return jsonify({
                'success': True,
                'model': model
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'Model {model_name} not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@model_bp.route('/models-v2/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for the new models service
    """
    try:
        # Test if service can connect to database
        session = model_service.get_session()
        session.close()
        
        return jsonify({
            'success': True,
            'message': 'Models service is healthy',
            'service': 'SQLAlchemy Models Service v2.0'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Models service health check failed'
        }), 500
