"""
Authentication Routes - V2 Clean Architecture
Handles authentication using SQLAlchemy and JWT tokens

Endpoints:
- /api/auth/login (POST) - User login
- /api/auth/register (POST) - User registration
- /api/auth/logout (POST) - User logout
- /api/auth/verify (GET) - Verify token
- /api/auth/refresh (POST) - Refresh token
- /api/auth/forgot-password (POST) - Forgot password
- /api/auth/reset-password (POST) - Reset password
- /api/auth/profile (PUT) - Update profile
- /api/auth/change-password (POST) - Change password
"""

from flask import Blueprint, jsonify, request, g
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
import jwt
import datetime
import secrets
import sys
import os

# Add backend directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Import SQLAlchemy models and connection
from model.user import User
from database.postgres_connection import create_spirit_engine
from sqlalchemy.orm import sessionmaker

auth_bp = Blueprint('auth', __name__)

# Initialize SQLAlchemy engine and session
engine = create_spirit_engine()
Session = sessionmaker(bind=engine)

# JWT configuration
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_EXPIRATION_HOURS = 24

def generate_token(user_id, username):
    """Generate JWT token for user"""
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def verify_token(token):
    """Verify JWT token and return user info"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({
                'success': False,
                'message': 'Username and password are required'
            }), 400

        username = data['username']
        password = data['password']
        
        # Debug logging
        print(f"🔐 Login attempt - Username: {username}, Password length: {len(password)}")

        with Session() as session:
            # Find user by username or email
            user = session.query(User).filter(
                (User.username == username) | (User.email == username),
                User.is_active == True
            ).first()
            
            print(f"🔐 User found: {user is not None}")
            if user:
                print(f"🔐 User ID: {user.id}, Username: {user.username}, Email: {user.email}")
                print(f"🔐 Password hash exists: {user.password_hash is not None}")
                password_check = check_password_hash(user.password_hash, password)
                print(f"🔐 Password check result: {password_check}")

            if not user or not check_password_hash(user.password_hash, password):
                return jsonify({
                    'success': False,
                    'message': 'Invalid credentials'
                }), 401

            # Get user roles and permissions
            from app.services.rbac_service import RBACService
            rbac_service = RBACService()
            user_roles_result = rbac_service.get_user_roles(user.id)
            user_permissions = rbac_service.get_user_permissions(user.id)
            
            user_roles = user_roles_result.get('roles', []) if user_roles_result['success'] else []
            role_names = [role['name'] for role in user_roles]

            # Generate token
            token = generate_token(user.id, user.username)

            # Update last login
            user.last_login = datetime.datetime.utcnow()
            session.commit()

            return jsonify({
                'success': True,
                'message': 'Login successful',
                'token': token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'avatar_url': user.avatar_url,
                    'subscription_status': user.subscription_status,
                    'is_verified': user.is_verified,
                    'roles': role_names,
                    'permissions': user_permissions
                }
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Login failed: {str(e)}'
        }), 500

@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    """User registration endpoint"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'Registration data is required'
            }), 400

        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'{field} is required'
                }), 400

        username = data['username']
        email = data['email']
        password = data['password']

        with Session() as session:
            # Check if user already exists
            existing_user = session.query(User).filter(
                (User.username == username) | (User.email == email)
            ).first()

            if existing_user:
                return jsonify({
                    'success': False,
                    'message': 'Username or email already exists'
                }), 409

            # Create new user
            user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password),
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', ''),
                is_active=True,
                is_verified=False,
                subscription_status='no_subscription'
            )

            session.add(user)
            session.commit()

            # Generate token
            token = generate_token(user.id, user.username)

            return jsonify({
                'success': True,
                'message': 'Registration successful',
                'token': token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'subscription_status': user.subscription_status,
                    'is_verified': user.is_verified
                }
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Registration failed: {str(e)}'
        }), 500

@auth_bp.route('/api/auth/logout', methods=['POST'])
def logout():
    """User logout endpoint"""
    try:
        # For JWT, logout is handled client-side by removing the token
        # In a production system, you might want to implement token blacklisting
        return jsonify({
            'success': True,
            'message': 'Logout successful'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Logout failed: {str(e)}'
        }), 500

@auth_bp.route('/api/auth/verify', methods=['GET'])
def verify():
    """Verify token endpoint"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': 'Authorization header required'
            }), 401

        token = auth_header.split(' ')[1]
        payload = verify_token(token)

        if not payload:
            return jsonify({
                'success': False,
                'message': 'Invalid or expired token'
            }), 401

        with Session() as session:
            user = session.query(User).filter(
                User.id == payload['user_id'],
                User.is_active == True
            ).first()

            if not user:
                return jsonify({
                    'success': False,
                    'message': 'User not found'
                }), 401

            return jsonify({
                'success': True,
                'message': 'Token is valid',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'avatar_url': user.avatar_url,
                    'subscription_status': user.subscription_status,
                    'is_verified': user.is_verified
                }
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Token verification failed: {str(e)}'
        }), 500

@auth_bp.route('/api/auth/refresh', methods=['POST'])
def refresh():
    """Refresh token endpoint"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': 'Authorization header required'
            }), 401

        token = auth_header.split(' ')[1]
        payload = verify_token(token)

        if not payload:
            return jsonify({
                'success': False,
                'message': 'Invalid or expired token'
            }), 401

        # Generate new token
        new_token = generate_token(payload['user_id'], payload['username'])

        return jsonify({
            'success': True,
            'message': 'Token refreshed successfully',
            'token': new_token
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Token refresh failed: {str(e)}'
        }), 500

@auth_bp.route('/api/auth/forgot-password', methods=['POST'])
def forgot_password():
    """Forgot password endpoint"""
    try:
        data = request.get_json()
        if not data or not data.get('email'):
            return jsonify({
                'success': False,
                'message': 'Email is required'
            }), 400

        email = data['email']

        with Session() as session:
            user = session.query(User).filter(
                User.email == email,
                User.is_active == True
            ).first()

            if not user:
                # Don't reveal if email exists or not for security
                return jsonify({
                    'success': True,
                    'message': 'If the email exists, a password reset link has been sent'
                })

            # Generate reset token (in production, send email)
            reset_token = secrets.token_urlsafe(32)
            user.password_reset_token = reset_token
            user.password_reset_expires = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            session.commit()

            # In production, send email with reset link
            print(f"Password reset token for {email}: {reset_token}")

            return jsonify({
                'success': True,
                'message': 'If the email exists, a password reset link has been sent'
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Password reset request failed: {str(e)}'
        }), 500

@auth_bp.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    """Reset password endpoint"""
    try:
        data = request.get_json()
        if not data or not data.get('token') or not data.get('password'):
            return jsonify({
                'success': False,
                'message': 'Token and new password are required'
            }), 400

        token = data['token']
        new_password = data['password']

        with Session() as session:
            user = session.query(User).filter(
                User.password_reset_token == token,
                User.password_reset_expires > datetime.datetime.utcnow(),
                User.is_active == True
            ).first()

            if not user:
                return jsonify({
                    'success': False,
                    'message': 'Invalid or expired reset token'
                }), 400

            # Update password
            user.password_hash = generate_password_hash(new_password)
            user.password_reset_token = None
            user.password_reset_expires = None
            session.commit()

            return jsonify({
                'success': True,
                'message': 'Password reset successful'
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Password reset failed: {str(e)}'
        }), 500

@auth_bp.route('/api/auth/profile', methods=['PUT'])
def update_profile():
    """Update user profile endpoint"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': 'Authorization header required'
            }), 401

        token = auth_header.split(' ')[1]
        payload = verify_token(token)

        if not payload:
            return jsonify({
                'success': False,
                'message': 'Invalid or expired token'
            }), 401

        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'Profile data is required'
            }), 400

        with Session() as session:
            user = session.query(User).filter(
                User.id == payload['user_id'],
                User.is_active == True
            ).first()

            if not user:
                return jsonify({
                    'success': False,
                    'message': 'User not found'
                }), 404

            # Update allowed fields
            if 'first_name' in data:
                user.first_name = data['first_name']
            if 'last_name' in data:
                user.last_name = data['last_name']
            if 'avatar_url' in data:
                user.avatar_url = data['avatar_url']

            session.commit()

            return jsonify({
                'success': True,
                'message': 'Profile updated successfully',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'avatar_url': user.avatar_url,
                    'subscription_status': user.subscription_status,
                    'is_verified': user.is_verified
                }
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Profile update failed: {str(e)}'
        }), 500

@auth_bp.route('/api/auth/change-password', methods=['POST'])
def change_password():
    """Change password endpoint"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': 'Authorization header required'
            }), 401

        token = auth_header.split(' ')[1]
        payload = verify_token(token)

        if not payload:
            return jsonify({
                'success': False,
                'message': 'Invalid or expired token'
            }), 401

        data = request.get_json()
        if not data or not data.get('current_password') or not data.get('new_password'):
            return jsonify({
                'success': False,
                'message': 'Current password and new password are required'
            }), 400

        current_password = data['current_password']
        new_password = data['new_password']

        with Session() as session:
            user = session.query(User).filter(
                User.id == payload['user_id'],
                User.is_active == True
            ).first()

            if not user:
                return jsonify({
                    'success': False,
                    'message': 'User not found'
                }), 404

            # Verify current password
            if not check_password_hash(user.password_hash, current_password):
                return jsonify({
                    'success': False,
                    'message': 'Current password is incorrect'
                }), 400

            # Update password
            user.password_hash = generate_password_hash(new_password)
            session.commit()

            return jsonify({
                'success': True,
                'message': 'Password changed successfully'
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Password change failed: {str(e)}'
        }), 500

@auth_bp.route('/api/auth/health', methods=['GET'])
def require_auth(f):
    """Decorator to require authentication for an endpoint - TEMPORARILY DISABLED"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # TEMPORARY: Bypass authentication for testing
        # Create a mock user object for testing
        g.user = {
            'user_id': 1,
            'username': 'swordfish',
            'email': 'swordfish@airepublic.com'
        }
        return f(*args, **kwargs)
        
        # Original authentication code (commented out)
        # token = None
        # 
        # # Check for token in Authorization header
        # if 'Authorization' in request.headers:
        #     auth_header = request.headers['Authorization']
        #     try:
        #         token = auth_header.split(" ")[1]  # Bearer <token>
        #     except IndexError:
        #         return jsonify({'success': False, 'error': 'Invalid authorization header format'}), 401
        # 
        # if not token:
        #     return jsonify({'success': False, 'error': 'Authentication required'}), 401
        # 
        # # Verify token
        # user_info = verify_token(token)
        # if not user_info:
        #     return jsonify({'success': False, 'error': 'Invalid or expired token'}), 401
        # 
        # # Add user info to Flask's g object
        # g.user = user_info
        # return f(*args, **kwargs)
    
    return decorated_function

def auth_health():
    """Authentication service health check"""
    return jsonify({
        'success': True,
        'message': 'Authentication service is healthy',
        'version': '2.0.0',
        'database': 'SQLAlchemy + PostgreSQL'
    })
