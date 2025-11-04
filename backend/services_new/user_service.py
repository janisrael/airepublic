"""
User service using SQLAlchemy models and repository pattern
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from repositories.user_repository import UserRepository, RoleRepository, PermissionRepository
from model.user import User, Role, Permission, UserRole, Session as UserSession
from model.payment import UserSubscription, SubscriptionStatus
import hashlib
import secrets
from datetime import datetime, timedelta

class UserService:
    """Service for user management operations"""
    
    def __init__(self, session: Session):
        self.session = session
        self.user_repo = UserRepository(session)
        self.role_repo = RoleRepository(session)
        self.permission_repo = PermissionRepository(session)
    
    def create_user(self, username: str, email: str, password: str, **kwargs) -> User:
        """Create a new user"""
        # Hash password
        password_hash = self._hash_password(password)
        
        # Create user
        user_data = {
            'username': username,
            'email': email,
            'password_hash': password_hash,
            **kwargs
        }
        
        return self.user_repo.create(**user_data)
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.user_repo.get_by_id(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.user_repo.get_by_username(username)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.user_repo.get_by_email(email)
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        user = self.user_repo.get_by_username(username)
        if user and self._verify_password(password, user.password_hash):
            # Update last login
            user.last_login = datetime.utcnow()
            self.session.commit()
            return user
        return None
    
    def update_user(self, user_id: int, **kwargs) -> Optional[User]:
        """Update user information"""
        # Remove password from kwargs if present
        if 'password' in kwargs:
            kwargs['password_hash'] = self._hash_password(kwargs.pop('password'))
        
        return self.user_repo.update(user_id, **kwargs)
    
    def delete_user(self, user_id: int) -> bool:
        """Delete user"""
        return self.user_repo.delete(user_id)
    
    def get_user_roles(self, user_id: int) -> List[Role]:
        """Get user's roles"""
        return self.user_repo.get_user_roles(user_id)
    
    def add_user_role(self, user_id: int, role_name: str, assigned_by: int = None) -> bool:
        """Add role to user"""
        role = self.role_repo.get_by_name(role_name)
        if role:
            self.user_repo.add_user_role(user_id, role.id, assigned_by)
            return True
        return False
    
    def remove_user_role(self, user_id: int, role_name: str) -> bool:
        """Remove role from user"""
        role = self.role_repo.get_by_name(role_name)
        if role:
            return self.user_repo.remove_user_role(user_id, role.id)
        return False
    
    def has_permission(self, user_id: int, permission_name: str) -> bool:
        """Check if user has specific permission"""
        return self.user_repo.has_permission(user_id, permission_name)
    
    def get_user_permissions(self, user_id: int) -> List[Permission]:
        """Get user's permissions"""
        return self.user_repo.get_user_permissions(user_id)
    
    def create_session(self, user_id: int, expires_hours: int = 24) -> UserSession:
        """Create user session"""
        session_token = self._generate_token()
        expires_at = datetime.utcnow() + timedelta(hours=expires_hours)
        
        return self.user_repo.create_user_session(
            user_id=user_id,
            session_token=session_token,
            expires_at=expires_at
        )
    
    def get_session(self, token: str) -> Optional[UserSession]:
        """Get session by token"""
        return self.user_repo.get_session_by_token(token)
    
    def deactivate_session(self, session_id: int) -> bool:
        """Deactivate session"""
        return self.user_repo.deactivate_session(session_id)
    
    def deactivate_all_user_sessions(self, user_id: int) -> int:
        """Deactivate all user sessions"""
        return self.user_repo.deactivate_all_user_sessions(user_id)
    
    def get_user_subscription(self, user_id: int) -> Optional[UserSubscription]:
        """Get user's current subscription"""
        return self.session.query(UserSubscription).filter(
            UserSubscription.user_id == user_id,
            UserSubscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL])
        ).first()
    
    def get_user_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get user statistics"""
        user = self.get_user_by_id(user_id)
        if not user:
            return {}
        
        roles = self.get_user_roles(user_id)
        permissions = self.get_user_permissions(user_id)
        subscription = self.get_user_subscription(user_id)
        
        return {
            'user_id': user_id,
            'username': user.username,
            'email': user.email,
            'is_active': user.is_active,
            'is_verified': user.is_verified,
            'roles': [role.name for role in roles],
            'permissions': [perm.name for perm in permissions],
            'subscription_status': subscription.status.value if subscription else 'no_subscription',
            'last_login': user.last_login,
            'created_at': user.created_at
        }
    
    def search_users(self, search_term: str) -> List[User]:
        """Search users"""
        return self.user_repo.search_users(search_term)
    
    def get_active_users(self) -> List[User]:
        """Get active users"""
        return self.user_repo.get_active_users()
    
    def get_verified_users(self) -> List[User]:
        """Get verified users"""
        return self.user_repo.get_verified_users()
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return self._hash_password(password) == password_hash
    
    def _generate_token(self, length: int = 32) -> str:
        """Generate random token"""
        return secrets.token_urlsafe(length)
