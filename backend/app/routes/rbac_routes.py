"""
RBAC Routes - Role-Based Access Control API
Handles role and permission management for the AI Refinement Dashboard
"""

from flask import Blueprint, request, jsonify, g
from app.services.rbac_service import RBACService, require_permission, require_role
from app.routes.auth_routes import require_auth

# Create blueprint for RBAC routes
rbac_bp = Blueprint('rbac', __name__, url_prefix='/api/v2')

# Initialize RBAC service
rbac_service = RBACService()

# ==================== ROLE MANAGEMENT ====================

@rbac_bp.route('/roles', methods=['GET'])
@require_auth
@require_permission('admin', 'read')
def get_all_roles():
    """Get all roles - Admin only"""
    try:
        result = rbac_service.get_all_roles()
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@rbac_bp.route('/roles', methods=['POST'])
@require_auth
@require_permission('admin', 'create')
def create_role():
    """Create a new role - Admin only"""
    try:
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({
                'success': False,
                'error': 'Role name is required'
            }), 400
        
        result = rbac_service.create_role(
            name=data['name'],
            description=data.get('description')
        )
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== PERMISSION MANAGEMENT ====================

@rbac_bp.route('/permissions', methods=['GET'])
@require_auth
@require_permission('admin', 'read')
def get_all_permissions():
    """Get all permissions - Admin only"""
    try:
        result = rbac_service.get_all_permissions()
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@rbac_bp.route('/permissions', methods=['POST'])
@require_auth
@require_permission('admin', 'create')
def create_permission():
    """Create a new permission - Admin only"""
    try:
        data = request.get_json()
        required_fields = ['name', 'resource', 'action']
        
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'{field} is required'
                }), 400
        
        result = rbac_service.create_permission(
            name=data['name'],
            resource=data['resource'],
            action=data['action'],
            description=data.get('description')
        )
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== USER ROLE MANAGEMENT ====================

@rbac_bp.route('/users/<int:user_id>/roles', methods=['GET'])
@require_auth
@require_permission('admin', 'read')
def get_user_roles(user_id):
    """Get roles for a specific user - Admin only"""
    try:
        result = rbac_service.get_user_roles(user_id)
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@rbac_bp.route('/users/<int:user_id>/roles', methods=['POST'])
@require_auth
@require_permission('admin', 'update')
def assign_role_to_user(user_id):
    """Assign a role to a user - Admin only"""
    try:
        data = request.get_json()
        if not data or 'role_name' not in data:
            return jsonify({
                'success': False,
                'error': 'role_name is required'
            }), 400
        
        result = rbac_service.assign_role_to_user(user_id, data['role_name'])
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@rbac_bp.route('/users/<int:user_id>/roles', methods=['DELETE'])
@require_auth
@require_permission('admin', 'update')
def remove_role_from_user(user_id):
    """Remove a role from a user - Admin only"""
    try:
        data = request.get_json()
        if not data or 'role_name' not in data:
            return jsonify({
                'success': False,
                'error': 'role_name is required'
            }), 400
        
        result = rbac_service.remove_role_from_user(user_id, data['role_name'])
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== ROLE PERMISSION MANAGEMENT ====================

@rbac_bp.route('/roles/<role_name>/permissions', methods=['POST'])
@require_auth
@require_permission('admin', 'update')
def assign_permission_to_role(role_name):
    """Assign a permission to a role - Admin only"""
    try:
        data = request.get_json()
        if not data or 'permission_id' not in data:
            return jsonify({
                'success': False,
                'error': 'permission_id is required'
            }), 400
        
        result = rbac_service.assign_permission_to_role(role_name, data['permission_id'])
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== USER PERMISSION CHECK ====================

@rbac_bp.route('/users/<int:user_id>/permissions', methods=['GET'])
@require_auth
def get_user_permissions(user_id):
    """Get all permissions for a user - User can check their own permissions, admin can check any user"""
    try:
        # Check if user is checking their own permissions or is admin
        current_user_id = g.user.get('user_id')
        is_admin = rbac_service.check_permission(current_user_id, 'admin', 'read')
        
        if user_id != current_user_id and not is_admin:
            return jsonify({
                'success': False,
                'error': 'Insufficient permissions to view other users'
            }), 403
        
        permissions = rbac_service.get_user_permissions(user_id)
        return jsonify({
            'success': True,
            'permissions': permissions
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@rbac_bp.route('/users/<int:user_id>/permissions/check', methods=['POST'])
@require_auth
def check_user_permission(user_id):
    """Check if user has specific permission"""
    try:
        # Check if user is checking their own permissions or is admin
        current_user_id = g.user.get('user_id')
        is_admin = rbac_service.check_permission(current_user_id, 'admin', 'read')
        
        if user_id != current_user_id and not is_admin:
            return jsonify({
                'success': False,
                'error': 'Insufficient permissions to check other users'
            }), 403
        
        data = request.get_json()
        if not data or 'resource' not in data or 'action' not in data:
            return jsonify({
                'success': False,
                'error': 'resource and action are required'
            }), 400
        
        has_permission = rbac_service.check_permission(user_id, data['resource'], data['action'])
        
        return jsonify({
            'success': True,
            'has_permission': has_permission,
            'resource': data['resource'],
            'action': data['action']
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== RBAC SYSTEM STATUS ====================

@rbac_bp.route('/rbac/status', methods=['GET'])
@require_auth
@require_permission('admin', 'read')
def rbac_status():
    """Get RBAC system status - Admin only"""
    try:
        roles_result = rbac_service.get_all_roles()
        permissions_result = rbac_service.get_all_permissions()
        
        return jsonify({
            'success': True,
            'system_status': {
                'roles_count': len(roles_result.get('roles', [])) if roles_result['success'] else 0,
                'permissions_count': len(permissions_result.get('permissions', [])) if permissions_result['success'] else 0,
                'rbac_active': True
            },
            'roles': roles_result.get('roles', []) if roles_result['success'] else [],
            'permissions': permissions_result.get('permissions', []) if permissions_result['success'] else []
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
