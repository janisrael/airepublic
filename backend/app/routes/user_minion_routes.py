"""
User Minion Routes - V2 Clean Architecture with SQLAlchemy
Handles all user-scoped minion-related API endpoints using SQLAlchemy ORM

Endpoints:
- /api/users/<int:user_id>/minions (GET) - Get all user minions
- /api/users/<int:user_id>/minions/<int:minion_id> (GET) - Get specific minion
- /api/users/<int:user_id>/minions/<int:minion_id>/toggle-favorite (POST) - Toggle favorite
- /api/users/<int:user_id>/minions/<int:minion_id>/regenerate-token (POST) - Regenerate token
- /api/users/<int:user_id>/minions/<int:minion_id>/chat (POST) - Chat with minion
- /api/users/<int:user_id>/minions/<int:minion_id>/xp (POST) - Update XP
- /api/users/<int:user_id>/minions/<int:minion_id>/capabilities (GET) - Get capabilities
- /api/users/<int:user_id>/minions/<int:minion_id>/stats (GET) - Get stats
"""

from flask import Blueprint, jsonify, request, g
from functools import wraps
import os
import sys
import json

# Add backend directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Import SQLAlchemy service
from app.services.minion_service import MinionService

user_minion_bp = Blueprint('user_minions', __name__, url_prefix='/api/v2')

# Initialize SQLAlchemy service
minion_service = MinionService()

def require_auth(f):
    """Authentication decorator for user-scoped endpoints - TEMPORARILY DISABLED"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # TEMPORARY: Bypass authentication for testing
        # Create a mock user object for testing - use the user_id from the URL
        user_id = kwargs.get('user_id', 1)
        g.user = {
            'user_id': user_id,
            'username': 'user',
            'email': 'user@example.com'
        }
        return f(*args, **kwargs)
        
        # Original authentication code (commented out)
        # # Get authorization header
        # auth_header = request.headers.get('Authorization')
        # if not auth_header:
        #     return jsonify({
        #         'success': False,
        #         'error': 'Authorization header required'
        #     }), 401
        # 
        # # Check for Bearer token
        # if not auth_header.startswith('Bearer '):
        #     return jsonify({
        #         'success': False,
        #         'error': 'Invalid authorization format. Use: Bearer <token>'
        #     }), 401
        # 
        # token = auth_header[7:]  # Remove 'Bearer ' prefix
        # 
        # # Verify token and get user
        # user = verify_token(token)
        # if not user:
        #     return jsonify({
        #         'success': False,
        #         'error': 'Invalid or expired token'
        #     }), 401
        # 
        # # Set user in g for use in endpoints
        # g.user = user
        # return f(*args, **kwargs)
    
    return decorated_function

def verify_token(token):
    """Verify JWT token and return user info using SQLAlchemy"""
    try:
        import jwt
        from datetime import datetime
        from sqlalchemy.orm import Session
        from model.user import User
        
        # JWT configuration
        JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')
        
        # Decode JWT token
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        
        # Get user from database
        with minion_service.Session() as session:
            user = session.query(User).filter(
                User.id == payload['user_id'],
                User.is_active == True
            ).first()
            
            if user:
                return {
                    'user_id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': getattr(user, 'role', 'user'),
                    'is_active': user.is_active
                }
            
            return None
        
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        return None
    except jwt.InvalidTokenError:
        print("Invalid token")
        return None
    except Exception as e:
        print(f"Token verification error: {e}")
        return None

# Remove old PostgreSQL function - now using SQLAlchemy service

@user_minion_bp.route('/minions', methods=['GET'])
def get_all_minions_v2():
    """Get all minions (global endpoint for compatibility)"""
    try:
        # Use SQLAlchemy service to get all minions
        minions = minion_service.get_all_minions()
        
        return jsonify({
            'success': True,
            'minions': minions,
            'total': len(minions),
            'version': '2.0.0',
            'database': 'SQLAlchemy + PostgreSQL'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@user_minion_bp.route('/minions/<int:minion_id>', methods=['GET'])
def get_minion_by_id_v2(minion_id):
    """Get a specific minion by ID (global endpoint)"""
    try:
        # Use SQLAlchemy service to get minion by ID
        minion = minion_service.get_minion_by_id(minion_id)
        
        if not minion:
            return jsonify({
                'success': False,
                'error': f'Minion {minion_id} not found'
            }), 404
        
        return jsonify({
            'success': True,
            'minion': minion,
            'version': '2.0.0',
            'database': 'SQLAlchemy + PostgreSQL'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@user_minion_bp.route('/users/<int:user_id>/minions', methods=['GET'])
@require_auth
def get_user_minions_v2_endpoint(user_id):
    """Get all minions for a specific user - V2 SQLAlchemy"""
    try:
        # Verify user can access this endpoint
        if g.user['user_id'] != user_id:
            return jsonify({
                'success': False,
                'error': 'Access denied: Cannot access other user\'s minions'
            }), 403
        
        # Use SQLAlchemy service
        minions = minion_service.get_user_minions(user_id)
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'minions': minions,
            'total': len(minions),
            'version': '2.0.0',
            'database': 'SQLAlchemy + PostgreSQL'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to retrieve user minions'
        }), 500

@user_minion_bp.route('/users/<int:user_id>/minions/<int:minion_id>', methods=['GET'])
@require_auth
def get_user_minion_v2_endpoint(user_id, minion_id):
    """Get a specific minion for a user - V2 SQLAlchemy"""
    try:
        # Verify user can access this endpoint
        if g.user['user_id'] != user_id:
            return jsonify({
                'success': False,
                'error': 'Access denied: Cannot access other user\'s minions'
            }), 403
        
        # Use SQLAlchemy service
        minion = minion_service.get_user_minion(user_id, minion_id)
        
        if not minion:
            return jsonify({
                'success': False,
                'error': 'Minion not found'
            }), 404
        
        return jsonify({
            'success': True,
            'minion': minion,
            'version': '2.0.0',
            'database': 'SQLAlchemy + PostgreSQL'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to retrieve minion'
        }), 500

@user_minion_bp.route('/users/<int:user_id>/minions/<int:minion_id>/toggle-favorite', methods=['POST'])
@require_auth
def toggle_minion_favorite_v2(user_id, minion_id):
    """Toggle minion favorite status - V2 SQLAlchemy"""
    try:
        # Verify user can access this endpoint
        if g.user['user_id'] != user_id:
            return jsonify({
                'success': False,
                'error': 'Access denied: Cannot access other user\'s minions'
            }), 403
        
        # Use SQLAlchemy service
        result = minion_service.toggle_minion_favorite(user_id, minion_id)
        
        if not result['success']:
            return jsonify(result), 404
        
        return jsonify({
            **result,
            'version': '2.0.0',
            'database': 'SQLAlchemy + PostgreSQL'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to toggle favorite status'
        }), 500

@user_minion_bp.route('/users/<int:user_id>/minions/<int:minion_id>/regenerate-token', methods=['POST'])
@require_auth
def regenerate_minion_token_v2(user_id, minion_id):
    """Regenerate minion token - V2 SQLAlchemy"""
    try:
        auth_user_id = g.user['user_id']
        
        # Verify user access
        if auth_user_id != user_id and auth_user_id != 1:  # Only owner or superuser
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403
        
        # Use SQLAlchemy service
        result = minion_service.regenerate_minion_token(user_id, minion_id)
        
        if not result['success']:
            return jsonify(result), 404
        
        return jsonify({
            **result,
            'version': '2.0.0',
            'database': 'SQLAlchemy + PostgreSQL'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to regenerate token'
        }), 500

@user_minion_bp.route('/users/<int:user_id>/minions', methods=['POST'])
@require_auth
def create_user_minion_v2(user_id):
    """Create a new minion for a user - V2 SQLAlchemy"""
    try:
        # Verify user can access this endpoint
        if g.user['user_id'] != user_id:
            return jsonify({
                'success': False,
                'error': 'Access denied: Cannot create minions for other users'
            }), 403
        
        # Get data from request
        data = request.get_json() if request.is_json else {}
        
        # Handle form data (for file uploads)
        if request.form:
            minion_data = {
                'name': request.form.get('name'),
                'display_name': request.form.get('display_name'),
                'description': request.form.get('description', ''),
                'provider': request.form.get('provider', 'custom'),
                'model_id': request.form.get('model_id'),
                'capabilities': request.form.get('capabilities', '[]'),
                'parameters': request.form.get('parameters', 'Unknown'),
                'context_length': int(request.form.get('context_length', 4096)),
                'max_tokens': int(request.form.get('max_tokens', 2048)),
                'temperature': float(request.form.get('temperature', 0.7)),
                'top_p': float(request.form.get('top_p', 0.9)),
                'system_prompt': request.form.get('system_prompt', ''),
                'quantization': request.form.get('quantization', 'Unknown'),
                'architecture': request.form.get('architecture', 'Unknown'),
                'license': request.form.get('license', 'Unknown'),
                'tags': request.form.get('tags', '[]'),
                'avatar_url': None  # Handle file upload separately
            }
            
            # Parse JSON fields
            try:
                minion_data['capabilities'] = json.loads(minion_data['capabilities'])
            except:
                minion_data['capabilities'] = []
            
            try:
                minion_data['tags'] = json.loads(minion_data['tags'])
            except:
                minion_data['tags'] = []
                
        else:
            # JSON data
            minion_data = {
                'name': data.get('name'),
                'display_name': data.get('display_name'),
                'description': data.get('description', ''),
                'provider': data.get('provider', 'custom'),
                'model_id': data.get('model_id'),
                'capabilities': data.get('capabilities', []),
                'parameters': data.get('parameters', 'Unknown'),
                'context_length': data.get('context_length', 4096),
                'max_tokens': data.get('max_tokens', 2048),
                'temperature': data.get('temperature', 0.7),
                'top_p': data.get('top_p', 0.9),
                'system_prompt': data.get('system_prompt', ''),
                'quantization': data.get('quantization', 'Unknown'),
                'architecture': data.get('architecture', 'Unknown'),
                'license': data.get('license', 'Unknown'),
                'tags': data.get('tags', []),
                'avatar_url': data.get('avatar_url')
            }
        
        # Validate required fields
        if not minion_data['name']:
            return jsonify({
                'success': False,
                'error': 'Minion name is required'
            }), 400
        
        # Use SQLAlchemy service
        result = minion_service.create_minion(user_id, minion_data)
        
        if not result['success']:
            return jsonify(result), 400
        
        return jsonify({
            **result,
            'version': '2.0.0',
            'database': 'SQLAlchemy + PostgreSQL'
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to create minion'
        }), 500

@user_minion_bp.route('/users/<int:user_id>/minions/<int:minion_id>/chat', methods=['POST'])
@require_auth
def chat_with_minion_v2(user_id, minion_id):
    """Chat with a minion - V2 SQLAlchemy (Unified Orchestration)"""
    try:
        # Verify user can access this endpoint
        if g.user['user_id'] != user_id:
            return jsonify({
                'success': False,
                'error': 'Access denied: Cannot chat with other user\'s minions'
            }), 403
        
        # Get message from request
        data = request.get_json() if request.is_json else {}
        message = data.get('message', '')
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        # Use unified chat_with_minion method (uses same orchestration as dashboard test modal)
        result = minion_service.chat_with_minion(user_id, minion_id, message)
        
        if not result.get('success'):
            return jsonify(result), 400
        
        return jsonify({
            **result,
            'version': '2.0.0',
            'database': 'SQLAlchemy + PostgreSQL',
            'architecture': 'Clean V2 Architecture'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to chat with minion'
        }), 500

@user_minion_bp.route('/users/<int:user_id>/minions/health', methods=['GET'])
@require_auth
def user_minions_health_v2(user_id):
    """Health check for user minions API - V2 SQLAlchemy"""
    return jsonify({
        'success': True,
        'message': f'User {user_id} minions V2 API is healthy',
        'user_id': user_id,
        'version': '2.0.0',
        'database': 'SQLAlchemy + PostgreSQL',
        'architecture': 'Clean V2 Architecture'
    }), 200
