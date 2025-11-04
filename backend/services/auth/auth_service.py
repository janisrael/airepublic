#!/usr/bin/env python3
"""
Authentication Service
Core authentication logic for user login, registration, and session management
"""

import jwt
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from flask import request
import os

from ..auth_database import auth_db

class AuthService:
    """Core authentication service"""
    
    def __init__(self):
        self.jwt_secret = os.getenv('JWT_SECRET', 'your-super-secret-jwt-key-change-this')
        self.jwt_algorithm = os.getenv('JWT_ALGORITHM', 'HS256')
        self.jwt_expiry_days = int(os.getenv('JWT_EXPIRY_DAYS', '7'))
    
    def register_user(self, username: str, email: str, password: str, 
                     first_name: str = None, last_name: str = None) -> Dict:
        """
        Register a new user
        
        Args:
            username: Username
            email: Email address
            password: Plain text password
            first_name: First name
            last_name: Last name
        
        Returns:
            Dict with user info and tokens
        """
        try:
            # Validate input
            if not username or not email or not password:
                return {'success': False, 'error': 'Username, email, and password are required'}
            
            if len(password) < 8:
                return {'success': False, 'error': 'Password must be at least 8 characters long'}
            
            # Create user
            user_id = auth_db.create_user(username, email, password, first_name, last_name)
            
            # Get user info
            user = auth_db.get_user_by_id(user_id)
            
            # Create session
            session_token = auth_db.create_session(
                user_id, 
                request.remote_addr if request else None,
                request.headers.get('User-Agent') if request else None
            )
            
            # Generate JWT token
            jwt_token = self._generate_jwt_token(user_id, username)
            
            return {
                'success': True,
                'user': user,
                'session_token': session_token,
                'jwt_token': jwt_token,
                'message': 'User registered successfully'
            }
            
        except ValueError as e:
            return {'success': False, 'error': str(e)}
        except Exception as e:
            return {'success': False, 'error': f'Registration failed: {str(e)}'}
    
    def login_user(self, username_or_email: str, password: str) -> Dict:
        """
        Login user with credentials
        
        Args:
            username_or_email: Username or email
            password: Plain text password
        
        Returns:
            Dict with user info and tokens
        """
        try:
            # Validate input
            if not username_or_email or not password:
                return {'success': False, 'error': 'Username/email and password are required'}
            
            # Authenticate user
            user = auth_db.get_user_by_credentials(username_or_email, password)
            if not user:
                return {'success': False, 'error': 'Invalid credentials'}
            
            # Check if user is active
            if not user['is_active']:
                return {'success': False, 'error': 'Account is deactivated'}
            
            # Create session
            session_token = auth_db.create_session(
                user['id'], 
                request.remote_addr if request else None,
                request.headers.get('User-Agent') if request else None
            )
            
            # Generate JWT token
            jwt_token = self._generate_jwt_token(user['id'], user['username'])
            
            # Get user roles and permissions
            roles = auth_db.get_user_roles(user['id'])
            permissions = auth_db.get_user_permissions(user['id'])
            
            return {
                'success': True,
                'user': user,
                'roles': roles,
                'permissions': permissions,
                'session_token': session_token,
                'jwt_token': jwt_token,
                'message': 'Login successful'
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Login failed: {str(e)}'}
    
    def logout_user(self, session_token: str) -> Dict:
        """
        Logout user by invalidating session
        
        Args:
            session_token: Session token to invalidate
        
        Returns:
            Dict with logout status
        """
        try:
            if not session_token:
                return {'success': False, 'error': 'Session token required'}
            
            # Delete session
            success = auth_db.delete_session(session_token)
            
            if success:
                return {'success': True, 'message': 'Logout successful'}
            else:
                return {'success': False, 'error': 'Invalid session token'}
                
        except Exception as e:
            return {'success': False, 'error': f'Logout failed: {str(e)}'}
    
    def verify_session(self, session_token: str) -> Dict:
        """
        Verify session token and return user info
        
        Args:
            session_token: Session token to verify
        
        Returns:
            Dict with user info if valid
        """
        try:
            if not session_token:
                return {'success': False, 'error': 'Session token required'}
            
            # Get session
            session = auth_db.get_session(session_token)
            if not session:
                return {'success': False, 'error': 'Invalid or expired session'}
            
            # Get user info
            user = auth_db.get_user_by_id(session['user_id'])
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            # Get user roles and permissions
            roles = auth_db.get_user_roles(user['id'])
            permissions = auth_db.get_user_permissions(user['id'])
            
            return {
                'success': True,
                'user': user,
                'roles': roles,
                'permissions': permissions,
                'session': session
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Session verification failed: {str(e)}'}
    
    def verify_jwt_token(self, jwt_token: str) -> Dict:
        """
        Verify JWT token and return user info
        
        Args:
            jwt_token: JWT token to verify
        
        Returns:
            Dict with user info if valid
        """
        try:
            if not jwt_token:
                return {'success': False, 'error': 'JWT token required'}
            
            # Decode JWT token
            payload = jwt.decode(jwt_token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            
            # Get user info
            user = auth_db.get_user_by_id(payload['user_id'])
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            # Check if user is active
            if not user['is_active']:
                return {'success': False, 'error': 'Account is deactivated'}
            
            # Get user roles and permissions
            roles = auth_db.get_user_roles(user['id'])
            permissions = auth_db.get_user_permissions(user['id'])
            
            return {
                'success': True,
                'user': user,
                'roles': roles,
                'permissions': permissions,
                'payload': payload
            }
            
        except jwt.ExpiredSignatureError:
            return {'success': False, 'error': 'Token has expired'}
        except jwt.InvalidTokenError:
            return {'success': False, 'error': 'Invalid token'}
        except Exception as e:
            return {'success': False, 'error': f'Token verification failed: {str(e)}'}
    
    def refresh_jwt_token(self, jwt_token: str) -> Dict:
        """
        Refresh JWT token
        
        Args:
            jwt_token: Current JWT token
        
        Returns:
            Dict with new JWT token
        """
        try:
            # Verify current token
            verification = self.verify_jwt_token(jwt_token)
            if not verification['success']:
                return verification
            
            # Generate new token
            new_jwt_token = self._generate_jwt_token(
                verification['user']['id'], 
                verification['user']['username']
            )
            
            return {
                'success': True,
                'jwt_token': new_jwt_token,
                'user': verification['user']
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Token refresh failed: {str(e)}'}
    
    def _generate_jwt_token(self, user_id: int, username: str) -> str:
        """
        Generate JWT token for user
        
        Args:
            user_id: User ID
            username: Username
        
        Returns:
            JWT token string
        """
        payload = {
            'user_id': user_id,
            'username': username,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(days=self.jwt_expiry_days)
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    def validate_password_strength(self, password: str) -> Tuple[bool, str]:
        """
        Validate password strength
        
        Args:
            password: Password to validate
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one number"
        
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            return False, "Password must contain at least one special character"
        
        return True, "Password is strong"
    
    def generate_password_reset_token(self, email: str) -> Dict:
        """
        Generate password reset token
        
        Args:
            email: User email
        
        Returns:
            Dict with reset token info
        """
        try:
            # Get user by email
            with auth_dbPostgreSQL_path as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
                user = cursor.fetchone()
                
                if not user:
                    return {'success': False, 'error': 'Email not found'}
                
                # Generate reset token
                reset_token = secrets.token_urlsafe(32)
                expires_at = datetime.now() + timedelta(hours=1)  # 1 hour expiry
                
                # Store reset token
                cursor.execute('''
                    UPDATE users 
                    SET password_reset_token = ?, password_reset_expires = ?
                    WHERE id = ?
                ''', (reset_token, expires_at, user[0]))
                
                conn.commit()
                
                return {
                    'success': True,
                    'reset_token': reset_token,
                    'expires_at': expires_at,
                    'message': 'Password reset token generated'
                }
                
        except Exception as e:
            return {'success': False, 'error': f'Password reset token generation failed: {str(e)}'}
    
    def reset_password(self, reset_token: str, new_password: str) -> Dict:
        """
        Reset password using reset token
        
        Args:
            reset_token: Password reset token
            new_password: New password
        
        Returns:
            Dict with reset status
        """
        try:
            # Validate password strength
            is_valid, error_msg = self.validate_password_strength(new_password)
            if not is_valid:
                return {'success': False, 'error': error_msg}
            
            # Get user by reset token
            with auth_dbPostgreSQL_path as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id FROM users 
                    WHERE password_reset_token = ? 
                    AND password_reset_expires > CURRENT_TIMESTAMP
                ''', (reset_token,))
                user = cursor.fetchone()
                
                if not user:
                    return {'success': False, 'error': 'Invalid or expired reset token'}
                
                # Hash new password
                password_hash = auth_db.hash_password(new_password)
                
                # Update password and clear reset token
                cursor.execute('''
                    UPDATE users 
                    SET password_hash = ?, password_reset_token = NULL, password_reset_expires = NULL
                    WHERE id = ?
                ''', (password_hash, user[0]))
                
                conn.commit()
                
                return {'success': True, 'message': 'Password reset successfully'}
                
        except Exception as e:
            return {'success': False, 'error': f'Password reset failed: {str(e)}'}

# Global instance
auth_service = AuthService()
