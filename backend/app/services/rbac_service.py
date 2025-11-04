"""
Role-Based Access Control (RBAC) Service
Handles user roles, permissions, and authorization for the AI Refinement Dashboard
"""

import os
import sys
from typing import List, Dict, Any, Optional
from functools import wraps
from flask import request, g, jsonify

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from model.user import User, Role, Permission, UserRole, RolePermission
from database.postgres_connection import create_spirit_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_, or_

# Initialize SQLAlchemy engine and session
engine = create_spirit_engine()
Session = sessionmaker(bind=engine)

class RBACService:
    """Service for managing roles, permissions, and authorization"""
    
    def __init__(self):
        self.engine = engine
        self.Session = Session
    
    def get_session(self):
        """Get SQLAlchemy session"""
        return self.Session()
    
    # ==================== ROLE MANAGEMENT ====================
    
    def create_role(self, name: str, description: str = None) -> Dict[str, Any]:
        """Create a new role"""
        with self.get_session() as session:
            try:
                # Check if role already exists
                existing_role = session.query(Role).filter(Role.name == name).first()
                if existing_role:
                    return {'success': False, 'error': 'Role already exists'}
                
                role = Role(
                    name=name,
                    description=description or f"Role: {name}"
                )
                session.add(role)
                session.commit()
                
                return {
                    'success': True,
                    'role': {
                        'id': role.id,
                        'name': role.name,
                        'description': role.description,
                        'created_at': role.created_at.isoformat() if role.created_at else None
                    }
                }
            except Exception as e:
                session.rollback()
                return {'success': False, 'error': str(e)}
    
    def get_all_roles(self) -> Dict[str, Any]:
        """Get all roles"""
        with self.get_session() as session:
            try:
                roles = session.query(Role).all()
                return {
                    'success': True,
                    'roles': [
                        {
                            'id': role.id,
                            'name': role.name,
                            'description': role.description,
                            'created_at': role.created_at.isoformat() if role.created_at else None,
                            'permissions_count': len(role.permissions)
                        }
                        for role in roles
                    ]
                }
            except Exception as e:
                return {'success': False, 'error': str(e)}
    
    # ==================== PERMISSION MANAGEMENT ====================
    
    def create_permission(self, name: str, resource: str, action: str, description: str = None) -> Dict[str, Any]:
        """Create a new permission"""
        with self.get_session() as session:
            try:
                # Check if permission already exists
                existing_permission = session.query(Permission).filter(
                    and_(Permission.resource == resource, Permission.action == action)
                ).first()
                if existing_permission:
                    return {'success': False, 'error': 'Permission already exists'}
                
                permission = Permission(
                    name=name,
                    resource=resource,
                    action=action,
                    description=description or f"{action} on {resource}"
                )
                session.add(permission)
                session.commit()
                
                return {
                    'success': True,
                    'permission': {
                        'id': permission.id,
                        'name': permission.name,
                        'resource': permission.resource,
                        'action': permission.action,
                        'description': permission.description,
                        'created_at': permission.created_at.isoformat() if permission.created_at else None
                    }
                }
            except Exception as e:
                session.rollback()
                return {'success': False, 'error': str(e)}
    
    def get_all_permissions(self) -> Dict[str, Any]:
        """Get all permissions"""
        with self.get_session() as session:
            try:
                permissions = session.query(Permission).all()
                return {
                    'success': True,
                    'permissions': [
                        {
                            'id': permission.id,
                            'name': permission.name,
                            'resource': permission.resource,
                            'action': permission.action,
                            'description': permission.description,
                            'created_at': permission.created_at.isoformat() if permission.created_at else None
                        }
                        for permission in permissions
                    ]
                }
            except Exception as e:
                return {'success': False, 'error': str(e)}
    
    # ==================== USER ROLE ASSIGNMENT ====================
    
    def assign_role_to_user(self, user_id: int, role_name: str) -> Dict[str, Any]:
        """Assign a role to a user"""
        with self.get_session() as session:
            try:
                # Get user and role
                user = session.query(User).filter(User.id == user_id).first()
                role = session.query(Role).filter(Role.name == role_name).first()
                
                if not user:
                    return {'success': False, 'error': 'User not found'}
                if not role:
                    return {'success': False, 'error': 'Role not found'}
                
                # Check if user already has this role
                existing_assignment = session.query(UserRole).filter(
                    and_(UserRole.user_id == user_id, UserRole.role_id == role.id)
                ).first()
                
                if existing_assignment:
                    return {'success': False, 'error': 'User already has this role'}
                
                user_role = UserRole(user_id=user_id, role_id=role.id)
                session.add(user_role)
                session.commit()
                
                return {'success': True, 'message': f'Role {role_name} assigned to user {user.username}'}
            except Exception as e:
                session.rollback()
                return {'success': False, 'error': str(e)}
    
    def remove_role_from_user(self, user_id: int, role_name: str) -> Dict[str, Any]:
        """Remove a role from a user"""
        with self.get_session() as session:
            try:
                role = session.query(Role).filter(Role.name == role_name).first()
                if not role:
                    return {'success': False, 'error': 'Role not found'}
                
                user_role = session.query(UserRole).filter(
                    and_(UserRole.user_id == user_id, UserRole.role_id == role.id)
                ).first()
                
                if not user_role:
                    return {'success': False, 'error': 'User does not have this role'}
                
                session.delete(user_role)
                session.commit()
                
                return {'success': True, 'message': f'Role {role_name} removed from user'}
            except Exception as e:
                session.rollback()
                return {'success': False, 'error': str(e)}
    
    def get_user_roles(self, user_id: int) -> Dict[str, Any]:
        """Get all roles for a user"""
        with self.get_session() as session:
            try:
                user_roles = session.query(UserRole).filter(UserRole.user_id == user_id).all()
                roles = []
                for user_role in user_roles:
                    role = user_role.role
                    roles.append({
                        'id': role.id,
                        'name': role.name,
                        'description': role.description,
                        'assigned_at': user_role.created_at.isoformat() if user_role.created_at else None
                    })
                
                return {'success': True, 'roles': roles}
            except Exception as e:
                return {'success': False, 'error': str(e)}
    
    # ==================== ROLE PERMISSION MANAGEMENT ====================
    
    def assign_permission_to_role(self, role_name: str, permission_id: int) -> Dict[str, Any]:
        """Assign a permission to a role"""
        with self.get_session() as session:
            try:
                role = session.query(Role).filter(Role.name == role_name).first()
                permission = session.query(Permission).filter(Permission.id == permission_id).first()
                
                if not role:
                    return {'success': False, 'error': 'Role not found'}
                if not permission:
                    return {'success': False, 'error': 'Permission not found'}
                
                # Check if role already has this permission
                existing_assignment = session.query(RolePermission).filter(
                    and_(RolePermission.role_id == role.id, RolePermission.permission_id == permission_id)
                ).first()
                
                if existing_assignment:
                    return {'success': False, 'error': 'Role already has this permission'}
                
                role_permission = RolePermission(role_id=role.id, permission_id=permission_id)
                session.add(role_permission)
                session.commit()
                
                return {'success': True, 'message': f'Permission {permission.name} assigned to role {role_name}'}
            except Exception as e:
                session.rollback()
                return {'success': False, 'error': str(e)}
    
    # ==================== AUTHORIZATION ====================
    
    def check_permission(self, user_id: int, resource: str, action: str) -> bool:
        """Check if user has permission for resource and action"""
        with self.get_session() as session:
            try:
                # Get user's roles
                user_roles = session.query(UserRole).filter(UserRole.user_id == user_id).all()
                role_ids = [ur.role_id for ur in user_roles]
                
                if not role_ids:
                    return False
                
                # Check if any of the user's roles have the required permission
                permission_exists = session.query(RolePermission).join(Permission).filter(
                    and_(
                        RolePermission.role_id.in_(role_ids),
                        Permission.resource == resource,
                        Permission.action == action
                    )
                ).first()
                
                return permission_exists is not None
            except Exception as e:
                print(f"Permission check error: {e}")
                return False
    
    def get_user_permissions(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all permissions for a user"""
        with self.get_session() as session:
            try:
                # Get user's roles
                user_roles = session.query(UserRole).filter(UserRole.user_id == user_id).all()
                role_ids = [ur.role_id for ur in user_roles]
                
                if not role_ids:
                    return []
                
                # Get all permissions for user's roles
                permissions = session.query(Permission).join(RolePermission).filter(
                    RolePermission.role_id.in_(role_ids)
                ).distinct().all()
                
                return [
                    {
                        'id': perm.id,
                        'name': perm.name,
                        'resource': perm.resource,
                        'action': perm.action,
                        'description': perm.description
                    }
                    for perm in permissions
                ]
            except Exception as e:
                print(f"Get user permissions error: {e}")
                return []

# ==================== DECORATORS ====================

def require_permission(resource: str, action: str):
    """Decorator to require specific permission for an endpoint"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get user from g (set by auth middleware)
            if not hasattr(g, 'user') or not g.user:
                return jsonify({'success': False, 'error': 'Authentication required'}), 401
            
            user_id = g.user.get('user_id')
            if not user_id:
                return jsonify({'success': False, 'error': 'Invalid user'}), 401
            
            # Check permission
            rbac_service = RBACService()
            if not rbac_service.check_permission(user_id, resource, action):
                return jsonify({
                    'success': False, 
                    'error': f'Insufficient permissions. Required: {action} on {resource}'
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_role(role_name: str):
    """Decorator to require specific role for an endpoint"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get user from g (set by auth middleware)
            if not hasattr(g, 'user') or not g.user:
                return jsonify({'success': False, 'error': 'Authentication required'}), 401
            
            user_id = g.user.get('user_id')
            if not user_id:
                return jsonify({'success': False, 'error': 'Invalid user'}), 401
            
            # Check role
            rbac_service = RBACService()
            user_roles_result = rbac_service.get_user_roles(user_id)
            
            if not user_roles_result['success']:
                return jsonify({'success': False, 'error': 'Failed to check user roles'}), 500
            
            user_roles = [role['name'] for role in user_roles_result['roles']]
            if role_name not in user_roles:
                return jsonify({
                    'success': False, 
                    'error': f'Insufficient role. Required: {role_name}'
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ==================== HELPER FUNCTIONS ====================

def is_admin(user_id: int) -> bool:
    """Check if user is an admin"""
    rbac_service = RBACService()
    return rbac_service.check_permission(user_id, 'admin', 'access')

def is_superuser(user_id: int) -> bool:
    """Check if user is a superuser"""
    rbac_service = RBACService()
    user_roles_result = rbac_service.get_user_roles(user_id)
    if user_roles_result['success']:
        user_roles = [role['name'] for role in user_roles_result['roles']]
        return 'superuser' in user_roles
    return False

def has_model_access(user_id: int) -> bool:
    """Check if user has model access"""
    rbac_service = RBACService()
    return rbac_service.check_permission(user_id, 'models', 'read')

def has_training_access(user_id: int) -> bool:
    """Check if user has training access"""
    rbac_service = RBACService()
    return rbac_service.check_permission(user_id, 'training', 'create')

def has_admin_access(user_id: int) -> bool:
    """Check if user has admin access"""
    rbac_service = RBACService()
    return rbac_service.check_permission(user_id, 'admin', 'access')
