"""
LLM Router for Dynamic Provider System

Main router class that manages the dynamic LLM provider system.
Provides a unified interface for querying any registered provider.

Access: Admin, Superuser, Developer only
"""

from typing import Dict, Any, List, Optional, Generator
import logging
import time
from .provider_factory import provider_factory
from .base import LLMProvider

logger = logging.getLogger(__name__)


class LLMRouter:
    """
    Main router for the dynamic LLM provider system
    """
    
    def __init__(self):
        self.factory = provider_factory
        self.usage_stats = {}
        self.rate_limits = {}
    
    def get_provider(self, name: str, **config) -> LLMProvider:
        """
        Get a provider instance
        
        Args:
            name: Provider name
            **config: Provider configuration
        
        Returns:
            Provider instance
        """
        return self.factory.get_provider(name, **config)
    
    def list_providers(self) -> List[str]:
        """
        List all available providers
        
        Returns:
            List of provider names
        """
        return self.factory.list_providers()
    
    def get_provider_info(self, name: str) -> Dict[str, Any]:
        """
        Get provider information
        
        Args:
            name: Provider name
        
        Returns:
            Provider information
        """
        return self.factory.get_provider_info(name)
    
    def get_all_providers_info(self) -> List[Dict[str, Any]]:
        """
        Get information about all providers
        
        Returns:
            List of provider information
        """
        return self.factory.get_all_provider_info()
    
    def test_provider(self, name: str, **config) -> Dict[str, Any]:
        """
        Test a provider connection
        
        Args:
            name: Provider name
            **config: Provider configuration
        
        Returns:
            Test results
        """
        return self.factory.test_provider(name, **config)
    
    def query_provider(self, name: str, messages: List[Dict[str, str]], 
                      stream: bool = False, **kwargs) -> str | Generator[str, None, None]:
        """
        Query a provider with messages
        
        Args:
            name: Provider name
            messages: List of message dicts
            stream: Whether to stream the response
            **kwargs: Additional parameters
        
        Returns:
            Response string or generator for streaming
        """
        start_time = time.time()
        
        try:
            # Get provider instance
            provider = self.get_provider(name, **kwargs)
            
            # Check rate limits
            if not self._check_rate_limit(name):
                raise Exception(f"Rate limit exceeded for provider: {name}")
            
            # Query provider
            if stream:
                response = provider.chat_stream(messages, **kwargs)
            else:
                response = provider.chat(messages, **kwargs)
            
            # Record usage
            self._record_usage(name, time.time() - start_time)
            
            return response
            
        except Exception as e:
            logger.error(f"Query failed for provider {name}: {e}")
            raise
    
    def _check_rate_limit(self, provider_name: str) -> bool:
        """
        Check if provider is within rate limits
        
        Args:
            provider_name: Name of the provider
        
        Returns:
            True if within limits
        """
        # Simple rate limiting - can be enhanced
        if provider_name not in self.rate_limits:
            self.rate_limits[provider_name] = {
                'requests': 0,
                'last_reset': time.time()
            }
        
        rate_limit = self.rate_limits[provider_name]
        current_time = time.time()
        
        # Reset counter every minute
        if current_time - rate_limit['last_reset'] > 60:
            rate_limit['requests'] = 0
            rate_limit['last_reset'] = current_time
        
        # Check if within limit (100 requests per minute)
        if rate_limit['requests'] >= 100:
            return False
        
        rate_limit['requests'] += 1
        return True
    
    def _record_usage(self, provider_name: str, response_time: float):
        """
        Record usage statistics
        
        Args:
            provider_name: Name of the provider
            response_time: Response time in seconds
        """
        if provider_name not in self.usage_stats:
            self.usage_stats[provider_name] = {
                'request_count': 0,
                'total_response_time': 0.0,
                'avg_response_time': 0.0
            }
        
        stats = self.usage_stats[provider_name]
        stats['request_count'] += 1
        stats['total_response_time'] += response_time
        stats['avg_response_time'] = stats['total_response_time'] / stats['request_count']
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get usage statistics for all providers
        
        Returns:
            Usage statistics
        """
        return {
            'providers': self.usage_stats,
            'rate_limits': self.rate_limits,
            'cache_stats': self.factory.get_cache_stats()
        }
    
    def clear_cache(self):
        """Clear provider cache"""
        self.factory.clear_cache()
        logger.info("✅ Cleared LLM router cache")
    
    def register_provider(self, name: str, provider_class):
        """
        Register a new provider
        
        Args:
            name: Provider name
            provider_class: Provider class
        """
        self.factory.register_provider(name, provider_class)
        logger.info(f"✅ Registered provider in router: {name}")
    
    def unregister_provider(self, name: str):
        """
        Unregister a provider
        
        Args:
            name: Provider name
        """
        self.factory.unregister_provider(name)
        logger.info(f"✅ Unregistered provider from router: {name}")


# Global LLM router instance
llm_router = LLMRouter()
