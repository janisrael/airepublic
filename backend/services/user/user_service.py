#!/usr/bin/env python3
"""
User Service
User management operations including profile management and user data
"""

from typing import Dict, List, Optional
from datetime import datetime
import os

from ..auth_database import auth_db

class UserService:
    """User management service"""
    
    def __init__(self):
        self.avatar_upload_path = os.path.join(os.path.dirname(__file__), '../../uploads/avatars')
        os.makedirs(self.avatar_upload_path, exist_ok=True)
    
    def get_user_profile(self, user_id: int) -> Dict:
        """
        Get user profile information
        
        Args:
            user_id: User ID
        
        Returns:
            Dict with user profile
        """
        try:
            user = auth_db.get_user_by_id(user_id)
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            # Get user roles and permissions
            roles = auth_db.get_user_roles(user_id)
            permissions = auth_db.get_user_permissions(user_id)
            
            # Get usage limits
            usage_limits = self.get_user_usage_limits(user_id)
            
            # Get subscription info
            subscription_info = self.get_user_subscription(user_id)
            
            return {
                'success': True,
                'user': user,
                'roles': roles,
                'permissions': permissions,
                'usage_limits': usage_limits,
                'subscription': subscription_info
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to get user profile: {str(e)}'}
    
    def update_user_profile(self, user_id: int, profile_data: Dict) -> Dict:
        """
        Update user profile
        
        Args:
            user_id: User ID
            profile_data: Profile data to update
        
        Returns:
            Dict with update status
        """
        try:
            # Validate user exists
            user = auth_db.get_user_by_id(user_id)
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            # Prepare update fields
            update_fields = []
            update_values = []
            
            allowed_fields = ['first_name', 'last_name', 'avatar_url']
            
            for field, value in profile_data.items():
                if field in allowed_fields and value is not None:
                    update_fields.append(f"{field} = ?")
                    update_values.append(value)
            
            if not update_fields:
                return {'success': False, 'error': 'No valid fields to update'}
            
            # Add updated_at
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            update_values.append(user_id)
            
            # Update user
            with auth_dbPostgreSQL_path as conn:
                cursor = conn.cursor()
                query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
                cursor.execute(query, update_values)
                conn.commit()
            
            # Get updated user
            updated_user = auth_db.get_user_by_id(user_id)
            
            return {
                'success': True,
                'user': updated_user,
                'message': 'Profile updated successfully'
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to update profile: {str(e)}'}
    
    def change_password(self, user_id: int, current_password: str, new_password: str) -> Dict:
        """
        Change user password
        
        Args:
            user_id: User ID
            current_password: Current password
            new_password: New password
        
        Returns:
            Dict with change status
        """
        try:
            # Get user
            user = auth_db.get_user_by_id(user_id)
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            # Verify current password
            with auth_dbPostgreSQL_path as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT password_hash FROM users WHERE id = ?', (user_id,))
                result = cursor.fetchone()
                
                if not result:
                    return {'success': False, 'error': 'User not found'}
                
                if not auth_db.verify_password(current_password, result[0]):
                    return {'success': False, 'error': 'Current password is incorrect'}
            
            # Validate new password strength
            from .auth_service import auth_service
            is_valid, error_msg = auth_service.validate_password_strength(new_password)
            if not is_valid:
                return {'success': False, 'error': error_msg}
            
            # Hash new password
            new_password_hash = auth_db.hash_password(new_password)
            
            # Update password
            with auth_dbPostgreSQL_path as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users 
                    SET password_hash = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (new_password_hash, user_id))
                conn.commit()
            
            return {'success': True, 'message': 'Password changed successfully'}
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to change password: {str(e)}'}
    
    def get_user_usage_limits(self, user_id: int) -> Dict:
        """
        Get user usage limits and current usage
        
        Args:
            user_id: User ID
        
        Returns:
            Dict with usage limits
        """
        try:
            with auth_dbPostgreSQL_path as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT resource_type, limit_value, used_value, reset_period, reset_date
                    FROM user_usage_limits
                    WHERE user_id = ?
                ''', (user_id,))
                
                limits = {}
                for row in cursor.fetchall():
                    limits[row[0]] = {
                        'limit': row[1],
                        'used': row[2],
                        'remaining': row[1] - row[2],
                        'reset_period': row[3],
                        'reset_date': row[4]
                    }
                
                return {'success': True, 'limits': limits}
                
        except Exception as e:
            return {'success': False, 'error': f'Failed to get usage limits: {str(e)}'}
    
    def update_user_usage(self, user_id: int, resource_type: str, amount: int = 1) -> Dict:
        """
        Update user usage for a resource
        
        Args:
            user_id: User ID
            resource_type: Type of resource (e.g., 'training_jobs', 'api_calls')
            amount: Amount to add to usage
        
        Returns:
            Dict with update status
        """
        try:
            with auth_dbPostgreSQL_path as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE user_usage_limits 
                    SET used_value = used_value + ?, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ? AND resource_type = ?
                ''', (amount, user_id, resource_type))
                
                if cursor.rowcount == 0:
                    return {'success': False, 'error': 'Usage limit not found'}
                
                conn.commit()
            
            return {'success': True, 'message': 'Usage updated successfully'}
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to update usage: {str(e)}'}
    
    def check_usage_limit(self, user_id: int, resource_type: str) -> Dict:
        """
        Check if user has reached usage limit
        
        Args:
            user_id: User ID
            resource_type: Type of resource
        
        Returns:
            Dict with limit status
        """
        try:
            with auth_dbPostgreSQL_path as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT limit_value, used_value
                    FROM user_usage_limits
                    WHERE user_id = ? AND resource_type = ?
                ''', (user_id, resource_type))
                
                result = cursor.fetchone()
                if not result:
                    return {'success': False, 'error': 'Usage limit not found'}
                
                limit_value, used_value = result
                remaining = limit_value - used_value
                
                return {
                    'success': True,
                    'limit': limit_value,
                    'used': used_value,
                    'remaining': remaining,
                    'can_use': remaining > 0
                }
                
        except Exception as e:
            return {'success': False, 'error': f'Failed to check usage limit: {str(e)}'}
    
    def get_user_subscription(self, user_id: int) -> Dict:
        """
        Get user subscription information
        
        Args:
            user_id: User ID
        
        Returns:
            Dict with subscription info
        """
        try:
            with auth_dbPostgreSQL_path as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT plan_name, plan_type, status, current_period_start, 
                           current_period_end, trial_start, trial_end
                    FROM user_subscriptions
                    WHERE user_id = ? AND status = 'active'
                    ORDER BY created_at DESC
                    LIMIT 1
                ''', (user_id,))
                
                result = cursor.fetchone()
                if not result:
                    return {'success': True, 'subscription': None}
                
                subscription = {
                    'plan_name': result[0],
                    'plan_type': result[1],
                    'status': result[2],
                    'current_period_start': result[3],
                    'current_period_end': result[4],
                    'trial_start': result[5],
                    'trial_end': result[6]
                }
                
                return {'success': True, 'subscription': subscription}
                
        except Exception as e:
            return {'success': False, 'error': f'Failed to get subscription: {str(e)}'}
    
    def get_all_users(self, limit: int = 50, offset: int = 0) -> Dict:
        """
        Get all users (admin only)
        
        Args:
            limit: Number of users to return
            offset: Offset for pagination
        
        Returns:
            Dict with users list
        """
        try:
            with auth_dbPostgreSQL_path as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, username, email, first_name, last_name, 
                           is_active, is_verified, subscription_status, created_at, last_login
                    FROM users
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                ''', (limit, offset))
                
                users = []
                for row in cursor.fetchall():
                    users.append({
                        'id': row[0],
                        'username': row[1],
                        'email': row[2],
                        'first_name': row[3],
                        'last_name': row[4],
                        'is_active': bool(row[5]),
                        'is_verified': bool(row[6]),
                        'subscription_status': row[7],
                        'created_at': row[8],
                        'last_login': row[9]
                    })
                
                # Get total count
                cursor.execute('SELECT COUNT(*) FROM users')
                total = cursor.fetchone()[0]
                
                return {
                    'success': True,
                    'users': users,
                    'total': total,
                    'limit': limit,
                    'offset': offset
                }
                
        except Exception as e:
            return {'success': False, 'error': f'Failed to get users: {str(e)}'}
    
    def deactivate_user(self, user_id: int, admin_user_id: int) -> Dict:
        """
        Deactivate user account (admin only)
        
        Args:
            user_id: User ID to deactivate
            admin_user_id: Admin user ID performing the action
        
        Returns:
            Dict with deactivation status
        """
        try:
            # Check if admin has permission
            if not auth_db.check_permission(admin_user_id, 'users', 'admin'):
                return {'success': False, 'error': 'Insufficient permissions'}
            
            with auth_dbPostgreSQL_path as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users 
                    SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (user_id,))
                
                if cursor.rowcount == 0:
                    return {'success': False, 'error': 'User not found'}
                
                conn.commit()
            
            return {'success': True, 'message': 'User deactivated successfully'}
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to deactivate user: {str(e)}'}

# Global instance
user_service = UserService()
