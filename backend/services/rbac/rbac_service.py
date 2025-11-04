#!/usr/bin/env python3
"""
RBAC Service
Role-Based Access Control service for managing permissions and authorization
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta

from ..auth_database import auth_db

class RBACService:
    """Role-Based Access Control service"""
    
    def __init__(self):
        pass
    
    def check_permission(self, user_id: int, resource: str, action: str) -> Dict:
        """
        Check if user has permission for resource and action
        
        Args:
            user_id: User ID
            resource: Resource name (e.g., 'models', 'datasets')
            action: Action name (e.g., 'read', 'write', 'delete')
        
        Returns:
            Dict with permission check result
        """
        try:
            has_permission = auth_db.check_permission(user_id, resource, action)
            
            return {
                'success': True,
                'has_permission': has_permission,
                'user_id': user_id,
                'resource': resource,
                'action': action
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Permission check failed: {str(e)}'}
    
    def get_user_permissions(self, user_id: int) -> Dict:
        """
        Get all permissions for a user
        
        Args:
            user_id: User ID
        
        Returns:
            Dict with user permissions
        """
        try:
            permissions = auth_db.get_user_permissions(user_id)
            roles = auth_db.get_user_roles(user_id)
            
            return {
                'success': True,
                'permissions': permissions,
                'roles': roles,
                'user_id': user_id
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to get user permissions: {str(e)}'}
    
    def assign_role_to_user(self, user_id: int, role_name: str, assigned_by: int, 
                           expires_at: datetime = None) -> Dict:
        """
        Assign role to user
        
        Args:
            user_id: User ID
            role_name: Role name
            assigned_by: User ID who assigned the role
            expires_at: Optional expiration date
        
        Returns:
            Dict with assignment status
        """
        try:
            # Check if assigner has permission
            if not auth_db.check_permission(assigned_by, 'users', 'admin'):
                return {'success': False, 'error': 'Insufficient permissions to assign roles'}
            
            # Get role ID
            with auth_dbPostgreSQL_path as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT id FROM roles WHERE name = ?', (role_name,))
                role_result = cursor.fetchone()
                
                if not role_result:
                    return {'success': False, 'error': 'Role not found'}
                
                role_id = role_result[0]
                
                # Check if user already has this role
                cursor.execute('''
                    SELECT id FROM user_roles 
                    WHERE user_id = ? AND role_id = ? AND is_active = TRUE
                ''', (user_id, role_id))
                
                if cursor.fetchone():
                    return {'success': False, 'error': 'User already has this role'}
                
                # Assign role
                cursor.execute('''
                    INSERT INTO user_roles (user_id, role_id, assigned_by, expires_at)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, role_id, assigned_by, expires_at))
                
                conn.commit()
            
            return {
                'success': True,
                'message': f'Role {role_name} assigned to user successfully'
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to assign role: {str(e)}'}
    
    def remove_role_from_user(self, user_id: int, role_name: str, removed_by: int) -> Dict:
        """
        Remove role from user
        
        Args:
            user_id: User ID
            role_name: Role name
            removed_by: User ID who removed the role
        
        Returns:
            Dict with removal status
        """
        try:
            # Check if remover has permission
            if not auth_db.check_permission(removed_by, 'users', 'admin'):
                return {'success': False, 'error': 'Insufficient permissions to remove roles'}
            
            # Get role ID
            with auth_dbPostgreSQL_path as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT id FROM roles WHERE name = ?', (role_name,))
                role_result = cursor.fetchone()
                
                if not role_result:
                    return {'success': False, 'error': 'Role not found'}
                
                role_id = role_result[0]
                
                # Remove role
                cursor.execute('''
                    UPDATE user_roles 
                    SET is_active = FALSE
                    WHERE user_id = ? AND role_id = ? AND is_active = TRUE
                ''', (user_id, role_id))
                
                if cursor.rowcount == 0:
                    return {'success': False, 'error': 'User does not have this role'}
                
                conn.commit()
            
            return {
                'success': True,
                'message': f'Role {role_name} removed from user successfully'
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to remove role: {str(e)}'}
    
    def get_all_roles(self) -> Dict:
        """
        Get all available roles
        
        Returns:
            Dict with roles list
        """
        try:
            with auth_dbPostgreSQL_path as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, name, description, is_system_role, created_at
                    FROM roles
                    ORDER BY name
                ''')
                
                roles = []
                for row in cursor.fetchall():
                    roles.append({
                        'id': row[0],
                        'name': row[1],
                        'description': row[2],
                        'is_system_role': bool(row[3]),
                        'created_at': row[4]
                    })
                
                return {
                    'success': True,
                    'roles': roles,
                    'total': len(roles)
                }
                
        except Exception as e:
            return {'success': False, 'error': f'Failed to get roles: {str(e)}'}
    
    def get_all_permissions(self) -> Dict:
        """
        Get all available permissions
        
        Returns:
            Dict with permissions list
        """
        try:
            with auth_dbPostgreSQL_path as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, name, resource, action, description, created_at
                    FROM permissions
                    ORDER BY resource, action
                ''')
                
                permissions = []
                for row in cursor.fetchall():
                    permissions.append({
                        'id': row[0],
                        'name': row[1],
                        'resource': row[2],
                        'action': row[3],
                        'description': row[4],
                        'created_at': row[5]
                    })
                
                return {
                    'success': True,
                    'permissions': permissions,
                    'total': len(permissions)
                }
                
        except Exception as e:
            return {'success': False, 'error': f'Failed to get permissions: {str(e)}'}
    
    def get_role_permissions(self, role_name: str) -> Dict:
        """
        Get permissions for a specific role
        
        Args:
            role_name: Role name
        
        Returns:
            Dict with role permissions
        """
        try:
            with auth_dbPostgreSQL_path as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT p.name, p.resource, p.action, p.description
                    FROM role_permissions rp
                    JOIN permissions p ON rp.permission_id = p.id
                    JOIN roles r ON rp.role_id = r.id
                    WHERE r.name = ?
                    ORDER BY p.resource, p.action
                ''', (role_name,))
                
                permissions = []
                for row in cursor.fetchall():
                    permissions.append({
                        'name': row[0],
                        'resource': row[1],
                        'action': row[2],
                        'description': row[3]
                    })
                
                return {
                    'success': True,
                    'role': role_name,
                    'permissions': permissions,
                    'total': len(permissions)
                }
                
        except Exception as e:
            return {'success': False, 'error': f'Failed to get role permissions: {str(e)}'}
    
    def create_custom_role(self, role_name: str, description: str, permissions: List[str], 
                          created_by: int) -> Dict:
        """
        Create a custom role with specific permissions
        
        Args:
            role_name: Role name
            description: Role description
            permissions: List of permission names
            created_by: User ID who created the role
        
        Returns:
            Dict with creation status
        """
        try:
            # Check if creator has permission
            if not auth_db.check_permission(created_by, 'users', 'admin'):
                return {'success': False, 'error': 'Insufficient permissions to create roles'}
            
            with auth_dbPostgreSQL_path as conn:
                cursor = conn.cursor()
                
                # Check if role already exists
                cursor.execute('SELECT id FROM roles WHERE name = ?', (role_name,))
                if cursor.fetchone():
                    return {'success': False, 'error': 'Role already exists'}
                
                # Create role
                cursor.execute('''
                    INSERT INTO roles (name, description, is_system_role)
                    VALUES (?, ?, FALSE)
                ''', (role_name, description))
                
                role_id = cursor.lastrowid
                
                # Assign permissions to role
                for perm_name in permissions:
                    cursor.execute('SELECT id FROM permissions WHERE name = ?', (perm_name,))
                    perm_result = cursor.fetchone()
                    
                    if perm_result:
                        perm_id = perm_result[0]
                        cursor.execute('''
                            INSERT INTO role_permissions (role_id, permission_id)
                            VALUES (?, ?)
                        ''', (role_id, perm_id))
                
                conn.commit()
            
            return {
                'success': True,
                'message': f'Custom role {role_name} created successfully',
                'role_id': role_id
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to create custom role: {str(e)}'}
    
    def delete_custom_role(self, role_name: str, deleted_by: int) -> Dict:
        """
        Delete a custom role
        
        Args:
            role_name: Role name
            deleted_by: User ID who deleted the role
        
        Returns:
            Dict with deletion status
        """
        try:
            # Check if deleter has permission
            if not auth_db.check_permission(deleted_by, 'users', 'admin'):
                return {'success': False, 'error': 'Insufficient permissions to delete roles'}
            
            with auth_dbPostgreSQL_path as conn:
                cursor = conn.cursor()
                
                # Check if role exists and is not a system role
                cursor.execute('''
                    SELECT id, is_system_role FROM roles WHERE name = ?
                ''', (role_name,))
                role_result = cursor.fetchone()
                
                if not role_result:
                    return {'success': False, 'error': 'Role not found'}
                
                if role_result[1]:  # is_system_role
                    return {'success': False, 'error': 'Cannot delete system roles'}
                
                role_id = role_result[0]
                
                # Check if role is assigned to any users
                cursor.execute('''
                    SELECT COUNT(*) FROM user_roles 
                    WHERE role_id = ? AND is_active = TRUE
                ''', (role_id,))
                
                if cursor.fetchone()[0] > 0:
                    return {'success': False, 'error': 'Cannot delete role that is assigned to users'}
                
                # Delete role permissions
                cursor.execute('DELETE FROM role_permissions WHERE role_id = ?', (role_id,))
                
                # Delete role
                cursor.execute('DELETE FROM roles WHERE id = ?', (role_id,))
                
                conn.commit()
            
            return {
                'success': True,
                'message': f'Custom role {role_name} deleted successfully'
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to delete custom role: {str(e)}'}

# Global instance
rbac_service = RBACService()
