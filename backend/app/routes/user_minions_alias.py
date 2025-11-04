"""
User Minions Alias Routes - V2 Clean Architecture
Provides alias endpoints for frontend compatibility
"""

from flask import Blueprint, jsonify, request
from functools import wraps
import os
import sys

# Add backend directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Import the main user minion routes
from app.routes.user_minion_routes import require_auth, verify_token

user_minions_alias_bp = Blueprint('user_minions_alias', __name__, url_prefix='/api/v2')

@user_minions_alias_bp.route('/user-minions', methods=['GET'])
@require_auth
def get_user_minions_alias():
    """Alias endpoint for /api/user-minions-v2 -> /api/users/<user_id>/minions"""
    from flask import g
    
    user_id = g.user['user_id']
    
    # Redirect to the actual endpoint
    from flask import redirect, url_for
    return redirect(f'/api/users/{user_id}/minions')

@user_minions_alias_bp.route('/user-minions/<int:minion_id>', methods=['GET'])
@require_auth
def get_user_minion_alias(minion_id):
    """Alias endpoint for /api/user-minions-v2/<id> -> /api/users/<user_id>/minions/<id>"""
    from flask import g
    
    user_id = g.user['user_id']
    
    # Redirect to the actual endpoint
    from flask import redirect, url_for
    return redirect(f'/api/users/{user_id}/minions/{minion_id}')
