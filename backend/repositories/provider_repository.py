"""
Provider repository for provider management operations
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from model.provider import ProviderCapability, UserProviderConfig, ProviderUsageLog, ProviderTestResult, ProviderGroup, UserAPIKey
from .base import BaseRepository

class ProviderRepository(BaseRepository[ProviderCapability]):
    """Repository for provider capability operations"""
    
    def __init__(self, session: Session):
        super().__init__(ProviderCapability, session)
    
    def get_by_provider(self, provider_name: str) -> List[ProviderCapability]:
        """Get capabilities by provider"""
        return self.filter_by(provider_name=provider_name)
    
    def get_available_capabilities(self) -> List[ProviderCapability]:
        """Get available capabilities"""
        return self.filter_by(is_available=True)
    
    def get_premium_capabilities(self) -> List[ProviderCapability]:
        """Get premium capabilities"""
        return self.filter_by(is_premium=True)
    
    def get_by_capability_type(self, capability_type: str) -> List[ProviderCapability]:
        """Get capabilities by type"""
        return self.filter_by(capability_type=capability_type)
    
    def get_provider_capabilities(self, provider_name: str, capability_type: str = None) -> List[ProviderCapability]:
        """Get provider capabilities by type"""
        query = self.session.query(ProviderCapability).filter(
            ProviderCapability.provider_name == provider_name,
            ProviderCapability.is_available == True
        )
        
        if capability_type:
            query = query.filter(ProviderCapability.capability_type == capability_type)
        
        return query.all()
    
    def get_capabilities_by_cost_range(self, min_cost: float = 0.0, max_cost: float = None) -> List[ProviderCapability]:
        """Get capabilities by cost range"""
        query = self.session.query(ProviderCapability).filter(
            ProviderCapability.cost_per_token >= min_cost
        )
        
        if max_cost is not None:
            query = query.filter(ProviderCapability.cost_per_token <= max_cost)
        
        return query.all()

class UserProviderConfigRepository(BaseRepository[UserProviderConfig]):
    """Repository for user provider configuration operations"""
    
    def __init__(self, session: Session):
        super().__init__(UserProviderConfig, session)
    
    def get_by_user(self, user_id: int) -> List[UserProviderConfig]:
        """Get provider configurations for a user"""
        return self.filter_by(user_id=user_id)
    
    def get_by_provider(self, provider_name: str) -> List[UserProviderConfig]:
        """Get user configurations for a provider"""
        return self.filter_by(provider_name=provider_name)
    
    def get_user_provider_config(self, user_id: int, provider_name: str) -> Optional[UserProviderConfig]:
        """Get user's configuration for a specific provider"""
        return self.session.query(UserProviderConfig).filter(
            UserProviderConfig.user_id == user_id,
            UserProviderConfig.provider_name == provider_name
        ).first()
    
    def get_active_configs(self, user_id: int) -> List[UserProviderConfig]:
        """Get active provider configurations for a user"""
        return self.session.query(UserProviderConfig).filter(
            UserProviderConfig.user_id == user_id,
            UserProviderConfig.is_active == True
        ).all()
    
    def get_preferred_configs(self, user_id: int) -> List[UserProviderConfig]:
        """Get preferred provider configurations for a user"""
        return self.session.query(UserProviderConfig).filter(
            UserProviderConfig.user_id == user_id,
            UserProviderConfig.is_preferred == True
        ).all()
    
    def update_usage(self, config_id: int, monthly_usage: int = 0, daily_usage: int = 0) -> bool:
        """Update usage statistics for a configuration"""
        config = self.get_by_id(config_id)
        if config:
            config.current_monthly_usage += monthly_usage
            config.current_daily_usage += daily_usage
            self.session.commit()
            return True
        return False
    
    def reset_daily_usage(self, user_id: int) -> int:
        """Reset daily usage for all user configurations"""
        configs = self.get_by_user(user_id)
        count = 0
        for config in configs:
            config.current_daily_usage = 0
            count += 1
        self.session.commit()
        return count
    
    def reset_monthly_usage(self, user_id: int) -> int:
        """Reset monthly usage for all user configurations"""
        configs = self.get_by_user(user_id)
        count = 0
        for config in configs:
            config.current_monthly_usage = 0
            count += 1
        self.session.commit()
        return count

class ProviderUsageLogRepository(BaseRepository[ProviderUsageLog]):
    """Repository for provider usage log operations"""
    
    def __init__(self, session: Session):
        super().__init__(ProviderUsageLog, session)
    
    def get_by_user(self, user_id: int) -> List[ProviderUsageLog]:
        """Get usage logs for a user"""
        return self.filter_by(user_id=user_id)
    
    def get_by_provider(self, provider_name: str) -> List[ProviderUsageLog]:
        """Get usage logs for a provider"""
        return self.filter_by(provider_name=provider_name)
    
    def get_successful_requests(self, user_id: int) -> List[ProviderUsageLog]:
        """Get successful requests for a user"""
        return self.session.query(ProviderUsageLog).filter(
            ProviderUsageLog.user_id == user_id,
            ProviderUsageLog.success == True
        ).all()
    
    def get_failed_requests(self, user_id: int) -> List[ProviderUsageLog]:
        """Get failed requests for a user"""
        return self.session.query(ProviderUsageLog).filter(
            ProviderUsageLog.user_id == user_id,
            ProviderUsageLog.success == False
        ).all()
    
    def get_usage_by_date_range(self, user_id: int, start_date, end_date) -> List[ProviderUsageLog]:
        """Get usage logs by date range"""
        return self.session.query(ProviderUsageLog).filter(
            ProviderUsageLog.user_id == user_id,
            ProviderUsageLog.created_at >= start_date,
            ProviderUsageLog.created_at <= end_date
        ).all()
    
    def get_usage_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get usage statistics for a user"""
        logs = self.get_by_user(user_id)
        
        if not logs:
            return {
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'total_tokens': 0,
                'total_cost': 0.0,
                'average_response_time': 0.0,
                'success_rate': 0.0
            }
        
        successful_requests = [l for l in logs if l.success]
        failed_requests = [l for l in logs if not l.success]
        
        total_tokens = sum(l.total_tokens for l in logs)
        total_cost = sum(l.cost for l in logs)
        average_response_time = sum(l.response_time for l in logs) / len(logs)
        success_rate = (len(successful_requests) / len(logs)) * 100
        
        return {
            'total_requests': len(logs),
            'successful_requests': len(successful_requests),
            'failed_requests': len(failed_requests),
            'total_tokens': total_tokens,
            'total_cost': round(total_cost, 4),
            'average_response_time': round(average_response_time, 3),
            'success_rate': round(success_rate, 2)
        }
    
    def get_provider_usage_statistics(self, provider_name: str) -> Dict[str, Any]:
        """Get usage statistics for a provider"""
        logs = self.get_by_provider(provider_name)
        
        if not logs:
            return {
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'total_tokens': 0,
                'total_cost': 0.0,
                'average_response_time': 0.0,
                'success_rate': 0.0,
                'unique_users': 0
            }
        
        successful_requests = [l for l in logs if l.success]
        failed_requests = [l for l in logs if not l.success]
        unique_users = len(set(l.user_id for l in logs))
        
        total_tokens = sum(l.total_tokens for l in logs)
        total_cost = sum(l.cost for l in logs)
        average_response_time = sum(l.response_time for l in logs) / len(logs)
        success_rate = (len(successful_requests) / len(logs)) * 100
        
        return {
            'total_requests': len(logs),
            'successful_requests': len(successful_requests),
            'failed_requests': len(failed_requests),
            'total_tokens': total_tokens,
            'total_cost': round(total_cost, 4),
            'average_response_time': round(average_response_time, 3),
            'success_rate': round(success_rate, 2),
            'unique_users': unique_users
        }

class ProviderTestResultRepository(BaseRepository[ProviderTestResult]):
    """Repository for provider test result operations"""
    
    def __init__(self, session: Session):
        super().__init__(ProviderTestResult, session)
    
    def get_by_user(self, user_id: int) -> List[ProviderTestResult]:
        """Get test results for a user"""
        return self.filter_by(user_id=user_id)
    
    def get_by_provider(self, provider_name: str) -> List[ProviderTestResult]:
        """Get test results for a provider"""
        return self.filter_by(provider_name=provider_name)
    
    def get_successful_tests(self, user_id: int) -> List[ProviderTestResult]:
        """Get successful test results for a user"""
        return self.session.query(ProviderTestResult).filter(
            ProviderTestResult.user_id == user_id,
            ProviderTestResult.success == True
        ).all()
    
    def get_failed_tests(self, user_id: int) -> List[ProviderTestResult]:
        """Get failed test results for a user"""
        return self.session.query(ProviderTestResult).filter(
            ProviderTestResult.user_id == user_id,
            ProviderTestResult.success == False
        ).all()
    
    def get_tests_by_type(self, test_type: str) -> List[ProviderTestResult]:
        """Get test results by type"""
        return self.filter_by(test_type=test_type)
    
    def get_latest_test_results(self, provider_name: str, limit: int = 10) -> List[ProviderTestResult]:
        """Get latest test results for a provider"""
        return self.session.query(ProviderTestResult).filter(
            ProviderTestResult.provider_name == provider_name
        ).order_by(desc(ProviderTestResult.created_at)).limit(limit).all()
    
    def get_test_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get test statistics for a user"""
        tests = self.get_by_user(user_id)
        
        if not tests:
            return {
                'total_tests': 0,
                'successful_tests': 0,
                'failed_tests': 0,
                'average_score': 0.0,
                'average_response_time': 0.0,
                'success_rate': 0.0
            }
        
        successful_tests = [t for t in tests if t.success]
        failed_tests = [t for t in tests if not t.success]
        
        average_score = sum(t.score for t in tests) / len(tests)
        average_response_time = sum(t.response_time for t in tests) / len(tests)
        success_rate = (len(successful_tests) / len(tests)) * 100
        
        return {
            'total_tests': len(tests),
            'successful_tests': len(successful_tests),
            'failed_tests': len(failed_tests),
            'average_score': round(average_score, 2),
            'average_response_time': round(average_response_time, 3),
            'success_rate': round(success_rate, 2)
        }

class UserAPIKeyRepository(BaseRepository[UserAPIKey]):
    """Repository for user API key operations"""
    
    def __init__(self, session: Session):
        super().__init__(UserAPIKey, session)
    
    def get_by_user(self, user_id: int) -> List[UserAPIKey]:
        """Get API keys for a user"""
        return self.filter_by(user_id=user_id)
    
    def get_by_provider(self, provider_name: str) -> List[UserAPIKey]:
        """Get API keys for a provider"""
        return self.filter_by(provider_name=provider_name)
    
    def get_active_keys(self, user_id: int) -> List[UserAPIKey]:
        """Get active API keys for a user"""
        return self.session.query(UserAPIKey).filter(
            UserAPIKey.user_id == user_id,
            UserAPIKey.is_active == True
        ).all()
    
    def get_key_by_hash(self, key_hash: str) -> Optional[UserAPIKey]:
        """Get API key by hash"""
        return self.get_by_field('key_hash', key_hash)
    
    def update_usage(self, key_id: int, usage_count: int = 1) -> bool:
        """Update API key usage"""
        key = self.get_by_id(key_id)
        if key:
            key.usage_count += usage_count
            self.session.commit()
            return True
        return False
    
    def deactivate_key(self, key_id: int) -> bool:
        """Deactivate API key"""
        key = self.get_by_id(key_id)
        if key:
            key.is_active = False
            self.session.commit()
            return True
        return False
    
    def get_key_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get API key statistics for a user"""
        keys = self.get_by_user(user_id)
        
        if not keys:
            return {
                'total_keys': 0,
                'active_keys': 0,
                'total_usage': 0,
                'providers': []
            }
        
        active_keys = [k for k in keys if k.is_active]
        total_usage = sum(k.usage_count for k in keys)
        providers = list(set(k.provider_name for k in keys))
        
        return {
            'total_keys': len(keys),
            'active_keys': len(active_keys),
            'total_usage': total_usage,
            'providers': providers
        }
