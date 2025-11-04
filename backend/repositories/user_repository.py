"""
User repository for user management operations
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from model.user import User, Role, Permission, UserRole, RolePermission, Session as UserSession
from .base import BaseRepository

class UserRepository(BaseRepository[User]):
    """Repository for user operations"""
    
    def __init__(self, session: Session):
        super().__init__(User, session)
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.get_by_field('username', username)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.get_by_field('email', email)
    
    def get_active_users(self) -> List[User]:
        """Get all active users"""
        return self.filter_by(is_active=True)
    
    def get_verified_users(self) -> List[User]:
        """Get all verified users"""
        return self.filter_by(is_verified=True)
    
    def get_users_by_subscription_status(self, status: str) -> List[User]:
        """Get users by subscription status"""
        return self.filter_by(subscription_status=status)
    
    def search_users(self, search_term: str) -> List[User]:
        """Search users by username, email, or name"""
        return self.search(search_term, ['username', 'email', 'first_name', 'last_name'])
    
    def get_users_with_roles(self) -> List[Dict[str, Any]]:
        """Get users with their roles"""
        return self.session.query(User).join(UserRole).join(Role).all()
    
    def get_user_roles(self, user_id: int) -> List[Role]:
        """Get user's roles"""
        return self.session.query(Role).join(UserRole).filter(
            UserRole.user_id == user_id,
            UserRole.is_active == True
        ).all()
    
    def add_user_role(self, user_id: int, role_id: int, assigned_by: int = None) -> UserRole:
        """Add role to user"""
        user_role = UserRole(
            user_id=user_id,
            role_id=role_id,
            assigned_by=assigned_by
        )
        self.session.add(user_role)
        self.session.commit()
        return user_role
    
    def remove_user_role(self, user_id: int, role_id: int) -> bool:
        """Remove role from user"""
        user_role = self.session.query(UserRole).filter(
            UserRole.user_id == user_id,
            UserRole.role_id == role_id
        ).first()
        
        if user_role:
            self.session.delete(user_role)
            self.session.commit()
            return True
        return False
    
    def get_user_permissions(self, user_id: int) -> List[Permission]:
        """Get user's permissions through roles"""
        return self.session.query(Permission).join(RolePermission).join(Role).join(UserRole).filter(
            UserRole.user_id == user_id,
            UserRole.is_active == True
        ).all()
    
    def has_permission(self, user_id: int, permission_name: str) -> bool:
        """Check if user has specific permission"""
        permission = self.session.query(Permission).join(RolePermission).join(Role).join(UserRole).filter(
            UserRole.user_id == user_id,
            UserRole.is_active == True,
            Permission.name == permission_name
        ).first()
        return permission is not None
    
    def get_user_sessions(self, user_id: int) -> List[UserSession]:
        """Get user's active sessions"""
        return self.session.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.is_active == True
        ).all()
    
    def create_user_session(self, user_id: int, session_token: str, expires_at, **kwargs) -> UserSession:
        """Create new user session"""
        session = UserSession(
            user_id=user_id,
            session_token=session_token,
            expires_at=expires_at,
            **kwargs
        )
        self.session.add(session)
        self.session.commit()
        return session
    
    def get_session_by_token(self, token: str) -> Optional[UserSession]:
        """Get session by token"""
        return self.session.query(UserSession).filter(
            UserSession.session_token == token,
            UserSession.is_active == True
        ).first()
    
    def deactivate_session(self, session_id: int) -> bool:
        """Deactivate user session"""
        session = self.session.query(UserSession).filter(UserSession.id == session_id).first()
        if session:
            session.is_active = False
            self.session.commit()
            return True
        return False
    
    def deactivate_all_user_sessions(self, user_id: int) -> int:
        """Deactivate all user sessions"""
        sessions = self.session.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.is_active == True
        ).all()
        
        count = 0
        for session in sessions:
            session.is_active = False
            count += 1
        
        self.session.commit()
        return count

class RoleRepository(BaseRepository[Role]):
    """Repository for role operations"""
    
    def __init__(self, session: Session):
        super().__init__(Role, session)
    
    def get_by_name(self, name: str) -> Optional[Role]:
        """Get role by name"""
        return self.get_by_field('name', name)
    
    def get_system_roles(self) -> List[Role]:
        """Get system roles"""
        return self.filter_by(is_system_role=True)
    
    def get_custom_roles(self) -> List[Role]:
        """Get custom roles"""
        return self.filter_by(is_system_role=False)
    
    def get_role_permissions(self, role_id: int) -> List[Permission]:
        """Get role's permissions"""
        return self.session.query(Permission).join(RolePermission).filter(
            RolePermission.role_id == role_id
        ).all()
    
    def add_role_permission(self, role_id: int, permission_id: int) -> RolePermission:
        """Add permission to role"""
        role_permission = RolePermission(
            role_id=role_id,
            permission_id=permission_id
        )
        self.session.add(role_permission)
        self.session.commit()
        return role_permission
    
    def remove_role_permission(self, role_id: int, permission_id: int) -> bool:
        """Remove permission from role"""
        role_permission = self.session.query(RolePermission).filter(
            RolePermission.role_id == role_id,
            RolePermission.permission_id == permission_id
        ).first()
        
        if role_permission:
            self.session.delete(role_permission)
            self.session.commit()
            return True
        return False

class PermissionRepository(BaseRepository[Permission]):
    """Repository for permission operations"""
    
    def __init__(self, session: Session):
        super().__init__(Permission, session)
    
    def get_by_name(self, name: str) -> Optional[Permission]:
        """Get permission by name"""
        return self.get_by_field('name', name)
    
    def get_by_resource(self, resource: str) -> List[Permission]:
        """Get permissions by resource"""
        return self.filter_by(resource=resource)
    
    def get_by_action(self, action: str) -> List[Permission]:
        """Get permissions by action"""
        return self.filter_by(action=action)
    
    def get_by_resource_and_action(self, resource: str, action: str) -> List[Permission]:
        """Get permissions by resource and action"""
        return self.filter_by(resource=resource, action=action)
