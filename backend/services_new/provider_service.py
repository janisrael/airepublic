"""
Provider service using SQLAlchemy models and repository pattern
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from repositories.provider_repository import (
    ProviderRepository, UserProviderConfigRepository, 
    ProviderUsageLogRepository, ProviderTestResultRepository, UserAPIKeyRepository
)
from model.provider import ProviderCapability, UserProviderConfig, ProviderUsageLog, ProviderTestResult, UserAPIKey

class ProviderService:
    """Service for provider management operations"""
    
    def __init__(self, session: Session):
        self.session = session
        self.provider_repo = ProviderRepository(session)
        self.config_repo = UserProviderConfigRepository(session)
        self.usage_repo = ProviderUsageLogRepository(session)
        self.test_repo = ProviderTestResultRepository(session)
        self.api_key_repo = UserAPIKeyRepository(session)
    
    def get_provider_capabilities(self, provider_name: str) -> List[ProviderCapability]:
        """Get capabilities for a provider"""
        return self.provider_repo.get_by_provider(provider_name)
    
    def get_available_capabilities(self) -> List[ProviderCapability]:
        """Get available capabilities"""
        return self.provider_repo.get_available_capabilities()
    
    def get_user_provider_config(self, user_id: int, provider_name: str) -> Optional[UserProviderConfig]:
        """Get user's configuration for a provider"""
        return self.config_repo.get_user_provider_config(user_id, provider_name)
    
    def create_user_provider_config(self, user_id: int, provider_name: str, **kwargs) -> UserProviderConfig:
        """Create user provider configuration"""
        config_data = {
            'user_id': user_id,
            'provider_name': provider_name,
            **kwargs
        }
        return self.config_repo.create(**config_data)
    
    def log_provider_usage(self, user_id: int, provider_name: str, **kwargs) -> ProviderUsageLog:
        """Log provider usage"""
        usage_data = {
            'user_id': user_id,
            'provider_name': provider_name,
            **kwargs
        }
        return self.usage_repo.create(**usage_data)
    
    def get_user_usage_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get usage statistics for a user"""
        return self.usage_repo.get_usage_statistics(user_id)
    
    def create_api_key(self, user_id: int, provider_name: str, key_name: str, encrypted_key: str) -> UserAPIKey:
        """Create API key for user"""
        key_data = {
            'user_id': user_id,
            'provider_name': provider_name,
            'key_name': key_name,
            'encrypted_key': encrypted_key,
            'key_hash': f"hash_{encrypted_key[:10]}"  # Simplified hash
        }
        return self.api_key_repo.create(**key_data)
    
    def get_user_api_keys(self, user_id: int) -> List[UserAPIKey]:
        """Get API keys for a user"""
        return self.api_key_repo.get_by_user(user_id)
