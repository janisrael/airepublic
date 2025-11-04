"""
Payment and subscription models for AI Refinement Dashboard
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, Float, Enum
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime
import enum

class SubscriptionStatus(enum.Enum):
    """Subscription status enumeration"""
    ACTIVE = "ACTIVE"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
    NO_SUBSCRIPTION = "NO_SUBSCRIPTION"
    TRIAL = "TRIAL"

class PaymentStatus(enum.Enum):
    """Payment status enumeration"""
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"
    CANCELLED = "CANCELLED"

class UserSubscription(Base):
    """User subscription model for payment management"""
    
    __tablename__ = "user_subscriptions"
    
    # User association
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Subscription information
    subscription_type = Column(String(100), nullable=False)  # e.g., 'basic', 'premium', 'enterprise'
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.NO_SUBSCRIPTION, nullable=False)
    
    # Billing information
    billing_cycle = Column(String(50), default='monthly', nullable=False)  # e.g., 'monthly', 'yearly'
    amount = Column(Float, default=0.0, nullable=False)  # Subscription amount
    currency = Column(String(10), default='USD', nullable=False)
    
    # Payment provider information
    payment_provider = Column(String(100))  # e.g., 'stripe', 'paypal'
    provider_subscription_id = Column(String(255))  # Provider's subscription ID
    provider_customer_id = Column(String(255))  # Provider's customer ID
    
    # Subscription dates
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    next_billing_date = Column(DateTime)
    trial_end_date = Column(DateTime)
    
    # Cancellation information
    cancelled_at = Column(DateTime)
    cancellation_reason = Column(Text)
    cancel_at_period_end = Column(Boolean, default=False, nullable=False)
    
    # Subscription features and limits
    features = Column(JSON)  # Available features for this subscription
    limits = Column(JSON)  # Usage limits for this subscription
    
    # Metadata
    subscription_metadata = Column(JSON)  # Additional subscription metadata
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")
    payment_history = relationship("PaymentHistory", back_populates="subscription", cascade="all, delete-orphan")

class PaymentHistory(Base):
    """Payment history model for tracking payments"""
    
    __tablename__ = "payment_history"
    
    # User and subscription association
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("user_subscriptions.id", ondelete="CASCADE"))
    
    # Payment information
    payment_id = Column(String(255), unique=True, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default='USD', nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    
    # Payment provider information
    payment_provider = Column(String(100), nullable=False)  # e.g., 'stripe', 'paypal'
    provider_payment_id = Column(String(255))  # Provider's payment ID
    provider_transaction_id = Column(String(255))  # Provider's transaction ID
    
    # Payment details
    payment_method = Column(String(100))  # e.g., 'card', 'paypal', 'bank_transfer'
    payment_description = Column(Text)
    payment_metadata_json = Column(JSON)  # Additional payment metadata
    
    # Billing information
    billing_period_start = Column(DateTime)
    billing_period_end = Column(DateTime)
    invoice_url = Column(String(500))  # URL to invoice/receipt
    
    # Error information
    error_code = Column(String(100))
    error_message = Column(Text)
    failure_reason = Column(Text)
    
    # Refund information
    refunded_amount = Column(Float, default=0.0, nullable=False)
    refunded_at = Column(DateTime)
    refund_reason = Column(Text)
    
    # Relationships
    user = relationship("User", back_populates="payment_history")
    subscription = relationship("UserSubscription", back_populates="payment_history")

class UserUsageLimit(Base):
    """User usage limit model for tracking and enforcing limits"""
    
    __tablename__ = "user_usage_limits"
    
    # User association
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Limit information
    limit_type = Column(String(100), nullable=False)  # e.g., 'requests', 'tokens', 'storage'
    limit_period = Column(String(50), nullable=False)  # e.g., 'daily', 'monthly', 'yearly'
    
    # Limit values
    limit_value = Column(Integer, nullable=False)  # Maximum allowed value
    current_usage = Column(Integer, default=0, nullable=False)  # Current usage
    usage_percentage = Column(Float, default=0.0, nullable=False)  # Usage percentage (0.0 to 100.0)
    
    # Limit enforcement
    is_enforced = Column(Boolean, default=True, nullable=False)
    is_hard_limit = Column(Boolean, default=False, nullable=False)  # Hard limit vs soft limit
    warning_threshold = Column(Float, default=80.0, nullable=False)  # Warning threshold percentage
    
    # Limit metadata
    description = Column(Text)
    limit_metadata = Column(JSON)  # Additional limit metadata
    
    # Reset information
    last_reset = Column(DateTime, default=datetime.utcnow, nullable=False)
    next_reset = Column(DateTime, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="usage_limits")
