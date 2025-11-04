"""
Provider management models for AI Refinement Dashboard
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime

class ProviderCapability(Base):
    """Provider capability model for LLM providers"""
    
    __tablename__ = "provider_capabilities"
    
    # Provider information
    provider_name = Column(String(255), nullable=False, index=True)
    provider_type = Column(String(100), nullable=False)  # e.g., 'api', 'local', 'hybrid'
    
    # Capability information
    capability_name = Column(String(255), nullable=False)
    capability_type = Column(String(100), nullable=False)  # e.g., 'model', 'feature', 'tool'
    description = Column(Text)
    
    # Capability details
    is_available = Column(Boolean, default=True, nullable=False)
    is_premium = Column(Boolean, default=False, nullable=False)
    cost_per_token = Column(Float, default=0.0, nullable=False)
    rate_limit = Column(Integer, default=0, nullable=False)  # Requests per minute
    
    # Configuration
    config = Column(JSON)  # Provider-specific configuration
    requirements = Column(JSON)  # Requirements for using this capability
    
    # Metadata
    version = Column(String(50), default="1.0")
    last_updated = Column(DateTime, default=datetime.utcnow, nullable=False)

class UserProviderConfig(Base):
    """User provider configuration model"""
    
    __tablename__ = "user_provider_configs"
    
    # User and provider association
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider_name = Column(String(255), nullable=False)
    
    # Configuration
    config = Column(JSON)  # User-specific provider configuration
    api_key = Column(String(500))  # Encrypted API key
    api_url = Column(String(500))  # Custom API URL
    api_version = Column(String(50))  # API version
    
    # Usage limits and quotas
    monthly_limit = Column(Integer, default=0, nullable=False)  # Monthly request limit
    daily_limit = Column(Integer, default=0, nullable=False)  # Daily request limit
    current_monthly_usage = Column(Integer, default=0, nullable=False)
    current_daily_usage = Column(Integer, default=0, nullable=False)
    
    # Status and preferences
    is_active = Column(Boolean, default=True, nullable=False)
    is_preferred = Column(Boolean, default=False, nullable=False)
    auto_failover = Column(Boolean, default=True, nullable=False)  # Auto-failover to backup providers
    
    # Relationships
    user = relationship("User", back_populates="provider_configs")

class ProviderUsageLog(Base):
    """Provider usage logging model"""
    
    __tablename__ = "provider_usage_logs"
    
    # User and provider association
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider_name = Column(String(255), nullable=False)
    
    # Request information
    request_type = Column(String(100), nullable=False)  # e.g., 'chat', 'completion', 'embedding'
    model_name = Column(String(255), nullable=False)
    endpoint = Column(String(500))  # API endpoint used
    
    # Request details
    input_tokens = Column(Integer, default=0, nullable=False)
    output_tokens = Column(Integer, default=0, nullable=False)
    total_tokens = Column(Integer, default=0, nullable=False)
    
    # Response information
    response_time = Column(Float, default=0.0, nullable=False)  # Response time in seconds
    status_code = Column(Integer, nullable=False)
    success = Column(Boolean, default=True, nullable=False)
    error_message = Column(Text)
    
    # Cost information
    cost = Column(Float, default=0.0, nullable=False)  # Cost in USD
    cost_per_token = Column(Float, default=0.0, nullable=False)
    
    # Request metadata
    ip_address = Column(String(45))  # IPv6 compatible
    user_agent = Column(Text)
    request_id = Column(String(255))  # Unique request identifier
    
    # Relationships
    user = relationship("User", back_populates="usage_logs")

class ProviderTestResult(Base):
    """Provider test result model for health monitoring"""
    
    __tablename__ = "provider_test_results"
    
    # User and provider association
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider_name = Column(String(255), nullable=False)
    
    # Test information
    test_type = Column(String(100), nullable=False)  # e.g., 'connectivity', 'performance', 'accuracy'
    test_name = Column(String(255), nullable=False)
    test_description = Column(Text)
    
    # Test results
    success = Column(Boolean, nullable=False)
    score = Column(Float, default=0.0, nullable=False)  # Test score (0.0 to 100.0)
    response_time = Column(Float, default=0.0, nullable=False)  # Response time in seconds
    
    # Test details
    input_data = Column(JSON)  # Test input data
    expected_output = Column(JSON)  # Expected test output
    actual_output = Column(JSON)  # Actual test output
    error_message = Column(Text)
    
    # Test metadata
    test_duration = Column(Float, default=0.0, nullable=False)  # Test duration in seconds
    test_config = Column(JSON)  # Test configuration
    
    # Relationships
    user = relationship("User", back_populates="test_results")

class ProviderGroup(Base):
    """Provider group model for organizing providers"""
    
    __tablename__ = "provider_groups"
    
    # Group information
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    category = Column(String(100), nullable=False)  # e.g., 'llm', 'embedding', 'image'
    
    # Group configuration
    config = Column(JSON)  # Group-specific configuration
    is_active = Column(Boolean, default=True, nullable=False)
    is_public = Column(Boolean, default=False, nullable=False)  # Can be shared with other users
    
    # Group metadata
    version = Column(String(50), default="1.0")
    created_by = Column(Integer, ForeignKey("users.id"))
    last_updated = Column(DateTime, default=datetime.utcnow, nullable=False)

class UserAPIKey(Base):
    """User API key model for secure key management"""
    
    __tablename__ = "user_api_keys"
    
    # User association
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Key information
    provider_name = Column(String(255), nullable=False)
    key_name = Column(String(255), nullable=False)  # User-defined name for the key
    encrypted_key = Column(String(500), nullable=False)  # Encrypted API key
    key_hash = Column(String(255), nullable=False)  # Hash for key identification
    
    # Key metadata
    key_type = Column(String(100), default='api_key', nullable=False)  # e.g., 'api_key', 'bearer_token'
    permissions = Column(JSON)  # Key permissions and scopes
    rate_limits = Column(JSON)  # Rate limits for this key
    
    # Usage tracking
    last_used = Column(DateTime)
    usage_count = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Security
    expires_at = Column(DateTime)
    created_by_ip = Column(String(45))  # IPv6 compatible
    last_used_ip = Column(String(45))
    
    # Relationships
    user = relationship("User", back_populates="api_keys")
