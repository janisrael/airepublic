"""
User management models for AI Refinement Dashboard
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime

class User(Base):
    """User model for authentication and user management"""
    
    __tablename__ = "users"
    
    # Basic user information
    username = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(255))
    last_name = Column(String(255))
    avatar_url = Column(String(500))
    
    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Email verification
    email_verification_token = Column(String(255))
    password_reset_token = Column(String(255))
    password_reset_expires = Column(DateTime)
    
    # Activity tracking
    last_login = Column(DateTime)
    
    # Subscription information
    subscription_status = Column(String(50), default='no_subscription')
    subscription_expires = Column(DateTime)
    trial_ends_at = Column(DateTime)
    payment_customer_id = Column(String(255))  # Stripe/PayPal customer ID
    
    # Additional data
    user_metadata = Column(Text)  # JSON for additional user data
    
    # Relationships
    roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan", foreign_keys="UserRole.user_id")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("UserSubscription", back_populates="user", cascade="all, delete-orphan")
    payment_history = relationship("PaymentHistory", back_populates="user", cascade="all, delete-orphan")
    usage_limits = relationship("UserUsageLimit", back_populates="user", cascade="all, delete-orphan")
    provider_configs = relationship("UserProviderConfig", back_populates="user", cascade="all, delete-orphan")
    usage_logs = relationship("ProviderUsageLog", back_populates="user", cascade="all, delete-orphan")
    test_results = relationship("ProviderTestResult", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship("UserAPIKey", back_populates="user", cascade="all, delete-orphan")
    training_datasets = relationship("UserTrainingDataset", back_populates="user", cascade="all, delete-orphan")
    training_jobs = relationship("ExternalTrainingJob", back_populates="user", cascade="all, delete-orphan")
    minions = relationship("ExternalAPIModel", back_populates="user", cascade="all, delete-orphan")
    # Training results history created by this user
    training_results = relationship("TrainingResult", back_populates="user", cascade="all, delete-orphan")

class Role(Base):
    """Role model for RBAC system"""
    
    __tablename__ = "roles"
    
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    is_system_role = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    users = relationship("UserRole", back_populates="role", cascade="all, delete-orphan")
    permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")

class Permission(Base):
    """Permission model for RBAC system"""
    
    __tablename__ = "permissions"
    
    name = Column(String(255), unique=True, nullable=False)
    resource = Column(String(255), nullable=False)  # e.g., 'models', 'datasets', 'training'
    action = Column(String(255), nullable=False)    # e.g., 'read', 'write', 'delete', 'admin'
    description = Column(Text)
    
    # Relationships
    roles = relationship("RolePermission", back_populates="permission", cascade="all, delete-orphan")

class UserRole(Base):
    """Many-to-many relationship between users and roles"""
    
    __tablename__ = "user_roles"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    assigned_by = Column(Integer, ForeignKey("users.id"))
    assigned_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="roles", foreign_keys=[user_id])
    role = relationship("Role", back_populates="users")
    assigned_by_user = relationship("User", foreign_keys=[assigned_by])
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'role_id', name='unique_user_role'),
    )

class RolePermission(Base):
    """Many-to-many relationship between roles and permissions"""
    
    __tablename__ = "role_permissions"
    
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    permission_id = Column(Integer, ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    role = relationship("Role", back_populates="permissions")
    permission = relationship("Permission", back_populates="roles")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('role_id', 'permission_id', name='unique_role_permission'),
    )

class Session(Base):
    """User session model for authentication"""
    
    __tablename__ = "sessions"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    refresh_token = Column(String(255), unique=True)
    expires_at = Column(DateTime, nullable=False)
    last_accessed = Column(DateTime, default=datetime.utcnow, nullable=False)
    ip_address = Column(String(45))  # IPv6 compatible
    user_agent = Column(Text)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
