"""
SQLAlchemy models for Spirit System
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, DECIMAL, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base

# User model is defined in model/user.py to avoid conflicts

class SpiritRegistry(Base):
    """Spirits registry table - defines all available spirits"""
    __tablename__ = 'spirits_registry'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    category = Column(String(50), nullable=False)
    description = Column(Text)
    icon = Column(String(10))  # Emoji or icon name
    
    # Unlock requirements
    unlock_rank = Column(String(20), default='Novice')
    unlock_level = Column(Integer, default=1)
    max_spirit_level = Column(Integer, default=10)
    
    # Tools and relationships
    tools = Column(JSON, default=list)  # Available tools for this spirit
    synergies = Column(JSON, default=dict)  # Compatible spirits with bonuses
    conflicts = Column(JSON, default=dict)  # Conflicting spirits with penalties
    
    # Purchase information
    price_usd = Column(DECIMAL(10, 2), default=0.00)
    price_points = Column(Integer, default=0)
    is_purchaseable = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    free_with_subscription = Column(Boolean, default=False)
    tier = Column(String(20), default='free')  # free, basic, professional, premium
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships (commented out to avoid import issues)
    # minion_spirits = relationship("MinionSpirit", back_populates="spirit")
    # user_purchases = relationship("UserSpiritPurchase", back_populates="spirit")
    # user_access = relationship("UserSpiritAccess", back_populates="spirit")

class MinionSpirit(Base):
    """Minion spirits assignment table"""
    __tablename__ = 'minion_spirits'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    minion_id = Column(Integer, nullable=False)  # References minions table
    spirit_id = Column(Integer, nullable=False)
    spirit_level = Column(Integer, default=1)
    spirit_xp = Column(Integer, default=0)
    xp_to_next_level = Column(Integer, default=100)
    is_active = Column(Boolean, default=True)
    assigned_at = Column(DateTime, default=func.current_timestamp())
    
    # Relationships (commented out to avoid import issues)
    # spirit = relationship("SpiritRegistry", back_populates="minion_spirits")
    # spirit_mastery = relationship("SpiritMastery", back_populates="minion_spirit")

class SpiritMastery(Base):
    """Spirit mastery tracking table"""
    __tablename__ = 'spirit_mastery'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    minion_spirit_id = Column(Integer, nullable=False)
    tool_name = Column(String(100), nullable=False)
    usage_count = Column(Integer, default=0)
    mastery_level = Column(Integer, default=1)
    xp_earned = Column(Integer, default=0)
    last_used = Column(DateTime)
    
    # Relationships (commented out to avoid import issues)
    # minion_spirit = relationship("MinionSpirit", back_populates="spirit_mastery")

class SpiritBundle(Base):
    """Spirit bundles for bulk purchases"""
    __tablename__ = 'spirit_bundles'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    spirits = Column(JSON, nullable=False)  # Array of spirit names
    original_price_usd = Column(DECIMAL(10, 2), nullable=False)
    bundle_price_usd = Column(DECIMAL(10, 2), nullable=False)
    savings_usd = Column(DECIMAL(10, 2), nullable=False)
    savings_percentage = Column(Integer, nullable=False)
    points_cost = Column(Integer, nullable=False)
    category = Column(String(50), nullable=False)
    icon = Column(String(10))
    is_popular = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.current_timestamp())

class SubscriptionPlan(Base):
    """Subscription plans for spirit access"""
    __tablename__ = 'subscription_plans'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    price_usd = Column(DECIMAL(10, 2), nullable=False)
    billing_cycle = Column(String(20), nullable=False)  # monthly, yearly
    free_spirits = Column(JSON)  # Array of spirit names or "ALL"
    discount_on_purchases = Column(Integer, default=0)
    exclusive_spirits = Column(JSON, default=list)
    max_minions = Column(Integer, default=-1)  # -1 for unlimited
    max_spirits_per_minion = Column(Integer, default=5)
    features = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.current_timestamp())

class UserSpiritPurchase(Base):
    """User spirit purchases tracking"""
    __tablename__ = 'user_spirit_purchases'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)  # References users table
    spirit_id = Column(Integer, nullable=False)
    purchase_type = Column(String(20), nullable=False)  # individual, bundle, subscription
    payment_method = Column(String(20), nullable=False)  # usd, points, subscription
    amount_paid_usd = Column(DECIMAL(10, 2), default=0.00)
    amount_paid_points = Column(Integer, default=0)
    bundle_id = Column(Integer)  # References spirit_bundles
    subscription_plan_id = Column(Integer)  # References subscription_plans
    purchase_date = Column(DateTime, default=func.current_timestamp())
    expires_at = Column(DateTime)  # For subscription-based access
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.current_timestamp())
    
    # Relationships (commented out to avoid import issues)
    # spirit = relationship("SpiritRegistry", back_populates="user_purchases")

class UserSpiritSubscription(Base):
    """User spirit subscriptions tracking"""
    __tablename__ = 'user_spirit_subscriptions'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)  # References users table
    plan_id = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False)  # active, cancelled, expired
    start_date = Column(DateTime, default=func.current_timestamp())
    end_date = Column(DateTime)
    auto_renew = Column(Boolean, default=True)
    payment_method = Column(String(50))  # paypal, stripe, etc.
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())

class UserPoints(Base):
    """User points tracking for alternative currency"""
    __tablename__ = 'user_points'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, unique=True)  # References users table
    total_points = Column(Integer, default=0)
    earned_points = Column(Integer, default=0)
    spent_points = Column(Integer, default=0)
    bonus_points = Column(Integer, default=0)
    last_updated = Column(DateTime, default=func.current_timestamp())
    created_at = Column(DateTime, default=func.current_timestamp())

class PointsTransaction(Base):
    """Points transactions tracking"""
    __tablename__ = 'points_transactions'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)  # References users table
    transaction_type = Column(String(20), nullable=False)  # earned, spent, bonus, refund
    amount = Column(Integer, nullable=False)
    description = Column(Text)
    reference_id = Column(Integer)  # ID of related purchase or earning
    reference_type = Column(String(50))  # purchase, training, achievement, etc.
    created_at = Column(DateTime, default=func.current_timestamp())

class UserSpiritAccess(Base):
    """Tracks which spirits user has access to"""
    __tablename__ = 'user_spirit_access'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)  # References users table
    spirit_id = Column(Integer, nullable=False)
    access_type = Column(String(20), nullable=False)  # purchased, subscription, free, trial
    source = Column(String(30), nullable=False)  # individual_purchase, bundle, subscription, free_tier
    granted_at = Column(DateTime, default=func.current_timestamp())
    expires_at = Column(DateTime)  # NULL for permanent access
    is_active = Column(Boolean, default=True)
    
    # Relationships (commented out to avoid import issues)
    # spirit = relationship("SpiritRegistry", back_populates="user_access")

class ToolRegistry(Base):
    """Tools registry for spirit capabilities"""
    __tablename__ = 'tools_registry'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    category = Column(String(50), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.current_timestamp())

# Minions table with spirit integration (from IMPORTANT_DYNAMIC_SPIRIT_SYSTEM.md)
class SpiritMinion(Base):
    """Enhanced minions table with spirit system integration"""
    __tablename__ = 'spirit_minions'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)  # References users table
    model_id = Column(Integer, nullable=False)  # References models table
    name = Column(String(100), nullable=False)
    display_name = Column(String(100))
    description = Column(Text)
    avatar_url = Column(String(255))
    
    # XP & Rank System
    experience = Column(Integer, default=0)
    level = Column(Integer, default=1)
    rank = Column(String(20), default='Novice')  # Novice, Skilled, Specialist, Expert, Master, Grandmaster, Legend
    rank_level = Column(Integer, default=1)
    total_training_xp = Column(Integer, default=0)
    total_usage_xp = Column(Integer, default=0)
    xp_to_next_level = Column(Integer, default=100)
    
    # Traits System
    trait_slots_available = Column(Integer, default=0)
    trait_points_spent = Column(Integer, default=0)
    trait_intensities = Column(JSON, default=dict)
    compatibility_score = Column(DECIMAL(5, 2), default=0.00)
    effectiveness_bonus = Column(DECIMAL(5, 2), default=0.00)
    
    # Skillset Mastery
    skillset_mastery = Column(JSON, default=dict)
    unlocked_tools = Column(JSON, default=list)
    tool_usage_counts = Column(JSON, default=dict)
    
    # Spirit Pattern
    is_visible_minion = Column(Boolean, default=False)
    spirit_role = Column(String(20))  # writer, analyst, builder, connector, checker
    
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())

# ReferenceModel moved to model/reference_models.py to avoid import conflicts
