"""
Provider Factory for Dynamic LLM Provider System

Factory class for creating and managing LLM provider instances.
Handles provider registration, instantiation, and configuration.

Access: Admin, Superuser, Developer only
"""

from typing import Dict, Type, Any, List, Optional
import importlib
import logging
from .base import LLMProvider

logger = logging.getLogger(__name__)


class ProviderFactory:
    """
    Factory class for creating and managing LLM providers
    """
    
    def __init__(self):
        self.providers: Dict[str, Type[LLMProvider]] = {}
        self.provider_instances: Dict[str, LLMProvider] = {}
        self._load_builtin_providers()
    
    def _load_builtin_providers(self):
        """Load built-in provider classes"""
        try:
            # Import built-in providers
            from .openai_provider import OpenAIProvider
            from .anthropic_provider import AnthropicProvider
            from .nvidia_provider import NVIDIAProvider
            
            # Register built-in providers
            self.register_provider('openai', OpenAIProvider)
            self.register_provider('anthropic', AnthropicProvider)
            self.register_provider('nvidia', NVIDIAProvider)
            
            logger.info("✅ Loaded built-in providers: openai, anthropic, nvidia")
            
        except ImportError as e:
            logger.warning(f"⚠️ Could not load some built-in providers: {e}")
    
    def register_provider(self, name: str, provider_class: Type[LLMProvider]):
        """
        Register a new provider class
        
        Args:
            name: Provider name (e.g., 'openai', 'anthropic')
            provider_class: Provider class that extends LLMProvider
        """
        if not issubclass(provider_class, LLMProvider):
            raise ValueError(f"Provider class must extend LLMProvider")
        
        self.providers[name.lower()] = provider_class
        logger.info(f"✅ Registered provider: {name}")
    
    def unregister_provider(self, name: str):
        """
        Unregister a provider
        
        Args:
            name: Provider name to unregister
        """
        name = name.lower()
        if name in self.providers:
            del self.providers[name]
            # Also remove any cached instances
            if name in self.provider_instances:
                del self.provider_instances[name]
            logger.info(f"✅ Unregistered provider: {name}")
    
    def create_provider(self, name: str, **config) -> LLMProvider:
        """
        Create a new provider instance
        
        Args:
            name: Provider name
            **config: Provider configuration
        
        Returns:
            Provider instance
        """
        name = name.lower()
        
        if name not in self.providers:
            available = list(self.providers.keys())
            raise ValueError(f"Unknown provider: {name}. Available: {available}")
        
        provider_class = self.providers[name]
        
        try:
            provider = provider_class(**config)
            
            if not provider.validate_config():
                raise ValueError(f"Invalid configuration for provider: {name}")
            
            return provider
            
        except Exception as e:
            logger.error(f"Failed to create provider {name}: {e}")
            raise
    
    def get_provider(self, name: str, **config) -> LLMProvider:
        """
        Get or create a provider instance (with caching)
        
        Args:
            name: Provider name
            **config: Provider configuration
        
        Returns:
            Provider instance
        """
        # Create cache key based on name and config
        cache_key = f"{name}:{hash(str(sorted(config.items())))}"
        
        if cache_key not in self.provider_instances:
            self.provider_instances[cache_key] = self.create_provider(name, **config)
        
        return self.provider_instances[cache_key]
    
    def list_providers(self) -> List[str]:
        """
        List all registered providers
        
        Returns:
            List of provider names
        """
        return list(self.providers.keys())
    
    def get_provider_info(self, name: str) -> Dict[str, Any]:
        """
        Get information about a provider
        
        Args:
            name: Provider name
        
        Returns:
            Dict with provider information
        """
        name = name.lower()
        
        if name not in self.providers:
            raise ValueError(f"Unknown provider: {name}")
        
        provider_class = self.providers[name]
        
        # Create a temporary instance to get info
        try:
            # Try with dummy API key for info retrieval
            temp_provider = provider_class(api_key="dummy_key_for_info")
            return temp_provider.get_provider_info()
        except Exception as e:
            logger.warning(f"Could not get info for provider {name}: {e}")
            return {
                'name': name,
                'class': provider_class.__name__,
                'module': provider_class.__module__
            }
    
    def get_all_provider_info(self) -> List[Dict[str, Any]]:
        """
        Get information about all registered providers
        
        Returns:
            List of provider information dicts
        """
        providers_info = []
        
        for name in self.list_providers():
            try:
                info = self.get_provider_info(name)
                providers_info.append(info)
            except Exception as e:
                logger.warning(f"Could not get info for provider {name}: {e}")
        
        return providers_info
    
    def test_provider(self, name: str, **config) -> Dict[str, Any]:
        """
        Test a provider connection
        
        Args:
            name: Provider name
            **config: Provider configuration
        
        Returns:
            Test results
        """
        try:
            provider = self.create_provider(name, **config)
            return provider.test_connection()
        except Exception as e:
            logger.error(f"Provider test failed for {name}: {e}")
            return {
                'success': False,
                'error': str(e),
                'provider': name
            }
    
    def clear_cache(self):
        """Clear provider instance cache"""
        self.provider_instances.clear()
        logger.info("✅ Cleared provider cache")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dict with cache statistics
        """
        return {
            'cached_instances': len(self.provider_instances),
            'registered_providers': len(self.providers),
            'cache_keys': list(self.provider_instances.keys())
        }


# Global provider factory instance
provider_factory = ProviderFactory()
