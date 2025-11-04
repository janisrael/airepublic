#!/usr/bin/env python3
"""
User-Scoped Minion Endpoints
API endpoints for user-specific minion management with authentication
MIGRATED TO POSTGRESQL/SQLALCHEMY - No more PostgreSQL connections
"""

from flask import Blueprint, jsonify, request, g
from functools import wraps
import os
import json
import hashlib
import secrets

# Import PostgreSQL-based services
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))
from app.services.minion_service import MinionService

# Create blueprint
user_minion_bp = Blueprint('user_minion', __name__, url_prefix='/api/users')

# Initialize PostgreSQL-based minion service
minion_service = MinionService()

def require_auth(f):
    """Authentication decorator for user-scoped endpoints - TEMPORARILY DISABLED FOR TESTING"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # TEMPORARY: Bypass authentication for testing
        # Create a mock user object for testing
        g.user = {
            'user_id': 4,  # Use user ID 4 (the 'user' account)
            'username': 'user',
            'email': 'user@airepublic.com',
            'role': 'user',
            'is_active': True
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

def require_minion_token(f):
    """Authentication decorator for minion token endpoints - MIGRATED TO POSTGRESQL"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({
                'success': False,
                'error': 'Minion token required'
            }), 401
        
        # Check for Bearer token
        if not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'error': 'Invalid authorization format. Use: Bearer <minion_token>'
            }), 401
        
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        
        # Verify minion token
        minion = verify_minion_token(token)
        if not minion:
            return jsonify({
                'success': False,
                'error': 'Invalid or expired minion token'
            }), 401
        
        # Set minion in g for use in endpoints
        g.minion = minion
        return f(*args, **kwargs)
    
    return decorated_function

def verify_token(token):
    """Verify authentication token and return user info - MIGRATED TO POSTGRESQL"""
    try:
        # For now, since auth is disabled, return a mock user
        # TODO: Implement proper PostgreSQL-based token verification
        return {
            'user_id': 4,
            'username': 'user',
            'email': 'user@airepublic.com',
            'role': 'user',
            'is_active': True
        }
    except Exception as e:
        print(f"Token verification error: {e}")
        return None

def verify_minion_token(token):
    """Verify minion token and return minion info - MIGRATED TO POSTGRESQL"""
    try:
        # For now, return None since minion tokens are not implemented
        # TODO: Implement proper PostgreSQL-based minion token verification
        return None
    except Exception as e:
        print(f"Minion token verification error: {e}")
        return None

def get_user_minions(user_id):
    """Get minions for a specific user - MIGRATED TO POSTGRESQL/SQLALCHEMY"""
    try:
        # Use PostgreSQL-based minion service
        minions = minion_service.get_user_minions(user_id)
        return minions
    except Exception as e:
        print(f"Error getting user minions: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        return []

def get_user_minion(user_id, minion_id):
    """Get a specific minion for a user - MIGRATED TO POSTGRESQL/SQLALCHEMY"""
    try:
        # Use PostgreSQL-based minion service
        minion = minion_service.get_user_minion(user_id, minion_id)
        return minion
    except Exception as e:
        print(f"Error getting user minion: {e}")
        return None

# User-scoped endpoints

@user_minion_bp.route('/<int:user_id>/minions', methods=['GET'])
@require_auth
def get_user_minions_endpoint(user_id):
    """Get all minions for a specific user"""
    try:
        # Verify user can access this endpoint
        if g.user['user_id'] != user_id:
            return jsonify({
                'success': False,
                'error': 'Access denied: Cannot access other user\'s minions'
            }), 403
        
        minions = get_user_minions(user_id)
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'minions': minions,
            'total': len(minions)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to get user minions'
        }), 500

@user_minion_bp.route('/<int:user_id>/minions/<int:minion_id>', methods=['GET'])
@require_auth
def get_user_minion_endpoint(user_id, minion_id):
    """Get a specific minion for a user"""
    try:
        # Verify user can access this endpoint
        if g.user['user_id'] != user_id:
            return jsonify({
                'success': False,
                'error': 'Access denied: Cannot access other user\'s minions'
            }), 403
        
        minion = get_user_minion(user_id, minion_id)
        
        if not minion:
            return jsonify({
                'success': False,
                'error': 'Minion not found or access denied'
            }), 404
        
        return jsonify({
            'success': True,
            'minion': minion
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to get minion'
        }), 500

@user_minion_bp.route('/<int:user_id>/minions/<int:minion_id>/toggle-favorite', methods=['POST'])
@require_auth
def toggle_favorite_minion(user_id, minion_id):
    """Toggle favorite status for a minion"""
    try:
        # Verify user can access this endpoint
        if g.user['user_id'] != user_id:
            return jsonify({
                'success': False,
                'error': 'Access denied: Cannot modify other user\'s minions'
            }), 403
        
        # Use PostgreSQL-based minion service
        result = minion_service.toggle_favorite(user_id, minion_id)
        
        if not result['success']:
            return jsonify(result), 400
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to toggle favorite'
        }), 500

@user_minion_bp.route('/<int:user_id>/minions/<int:minion_id>/chat', methods=['POST'])
@require_auth
def chat_with_minion(user_id, minion_id):
    """Chat with a minion"""
    try:
        # Verify user can access this endpoint
        if g.user['user_id'] != user_id:
            return jsonify({
                'success': False,
                'error': 'Access denied: Cannot chat with other user\'s minions'
            }), 403
        
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        # Use PostgreSQL-based minion service
        result = minion_service.chat_with_minion(user_id, minion_id, message)
        
        if not result['success']:
            return jsonify(result), 400
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to chat with minion'
        }), 500

@user_minion_bp.route('/<int:user_id>/minions/<int:minion_id>/xp', methods=['POST'])
@require_auth
def update_minion_xp(user_id, minion_id):
    """Update minion experience points"""
    try:
        # Verify user can access this endpoint
        if g.user['user_id'] != user_id:
            return jsonify({
                'success': False,
                'error': 'Access denied: Cannot modify other user\'s minions'
            }), 403
        
        data = request.get_json()
        xp_amount = data.get('xp', 0)
        xp_type = data.get('type', 'usage')  # 'training' or 'usage'
        
        if not xp_amount:
            return jsonify({
                'success': False,
                'error': 'XP amount is required'
            }), 400
        
        # Use PostgreSQL-based minion service
        result = minion_service.update_minion_xp(user_id, minion_id, xp_amount, xp_type)
        
        if not result['success']:
            return jsonify(result), 400
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to update minion XP'
        }), 500

@user_minion_bp.route('/<int:user_id>/minions/<int:minion_id>/regenerate-token', methods=['POST'])
@require_auth
def regenerate_minion_token(user_id, minion_id):
    """Regenerate minion token"""
    try:
        # Verify user can access this endpoint
        if g.user['user_id'] != user_id:
            return jsonify({
                'success': False,
                'error': 'Access denied: Cannot modify other user\'s minions'
            }), 403
        
        # Use PostgreSQL-based minion service
        result = minion_service.regenerate_minion_token(user_id, minion_id)
        
        if not result['success']:
            return jsonify(result), 400
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to regenerate token'
        }), 500

@user_minion_bp.route('/<int:user_id>/minions/<int:minion_id>/capabilities', methods=['GET'])
@require_auth
def get_minion_capabilities(user_id, minion_id):
    """Get minion capabilities"""
    try:
        # Verify user can access this endpoint
        if g.user['user_id'] != user_id:
            return jsonify({
                'success': False,
                'error': 'Access denied: Cannot access other user\'s minions'
            }), 403
        
        minion = get_user_minion(user_id, minion_id)
        
        if not minion:
            return jsonify({
                'success': False,
                'error': 'Minion not found or access denied'
            }), 404
        
        return jsonify({
            'success': True,
            'capabilities': minion.get('capabilities', [])
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to get minion capabilities'
        }), 500

@user_minion_bp.route('/<int:user_id>/minions/<int:minion_id>/stats', methods=['GET'])
@require_auth
def get_minion_stats(user_id, minion_id):
    """Get minion statistics"""
    try:
        # Verify user can access this endpoint
        if g.user['user_id'] != user_id:
            return jsonify({
                'success': False,
                'error': 'Access denied: Cannot access other user\'s minions'
            }), 403
        
        # Use PostgreSQL-based minion service
        result = minion_service.get_minion_stats(user_id, minion_id)
        
        if not result['success']:
            return jsonify(result), 400
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to get minion stats'
        }), 500

@user_minion_bp.route('/<int:user_id>/minions/health', methods=['GET'])
@require_auth
def get_user_minions_health(user_id):
    """Get health status of user's minions"""
    try:
        # Verify user can access this endpoint
        if g.user['user_id'] != user_id:
            return jsonify({
                'success': False,
                'error': 'Access denied: Cannot access other user\'s minions'
            }), 403
        
        minions = get_user_minions(user_id)
        
        # Simple health check - just return count
        return jsonify({
            'success': True,
            'user_id': user_id,
            'total_minions': len(minions),
            'active_minions': len([m for m in minions if m.get('is_active', False)]),
            'status': 'healthy'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to get minions health'
        }), 500