"""
Base LLM Provider Interface

Abstract base class for all LLM providers in the dynamic provider system.
Provides a unified interface for different LLM services.

Access: Admin, Superuser, Developer only
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Generator, Optional
import time
import logging

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """
    Abstract base class for all LLM providers
    
    This class defines the interface that all LLM providers must implement
    to work with the dynamic provider system.
    """
    
    def __init__(self, api_key: str = None, base_url: str = None, model: str = None, **kwargs):
        """
        Initialize the provider
        
        Args:
            api_key: API key for the provider
            base_url: Base URL for the provider API
            model: Model identifier
            **kwargs: Additional provider-specific configuration
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.config = kwargs
        self.name = self.__class__.__name__.replace('Provider', '').lower()
        
        # Performance tracking
        self.request_count = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        self.last_request_time = None
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Send a chat request and return a response string
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
        
        Returns:
            Response string from the LLM
        """
        pass
    
    @abstractmethod
    def chat_stream(self, messages: List[Dict[str, str]], **kwargs) -> Generator[str, None, None]:
        """
        Send a streaming chat request
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional parameters
        
        Yields:
            Response chunks as strings
        """
        pass
    
    def validate_config(self) -> bool:
        """
        Validate provider configuration
        
        Returns:
            True if configuration is valid
        """
        return bool(self.api_key) if self.requires_api_key() else True
    
    def requires_api_key(self) -> bool:
        """
        Check if this provider requires an API key
        
        Returns:
            True if API key is required
        """
        return True  # Default to requiring API key
    
    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get provider information
        
        Returns:
            Dict with provider metadata
        """
        return {
            'name': self.name,
            'display_name': self.get_display_name(),
            'model': self.model,
            'base_url': self.base_url,
            'supports_streaming': hasattr(self, 'chat_stream'),
            'requires_api_key': self.requires_api_key(),
            'capabilities': self.get_capabilities(),
            'default_models': self.get_default_models(),
            'config_schema': self.get_config_schema()
        }
    
    def get_display_name(self) -> str:
        """
        Get human-readable display name
        
        Returns:
            Display name for the provider
        """
        return self.name.title()
    
    def get_capabilities(self) -> List[str]:
        """
        Get list of provider capabilities
        
        Returns:
            List of capability strings
        """
        capabilities = ['chat']
        if hasattr(self, 'chat_stream'):
            capabilities.append('streaming')
        return capabilities
    
    def get_default_models(self) -> List[str]:
        """
        Get list of default models for this provider
        
        Returns:
            List of default model identifiers
        """
        return []
    
    def get_config_schema(self) -> Dict[str, Any]:
        """
        Get configuration schema for this provider
        
        Returns:
            JSON schema for provider configuration
        """
        return {
            'type': 'object',
            'properties': {
                'temperature': {
                    'type': 'number',
                    'minimum': 0,
                    'maximum': 2,
                    'default': 0.7
                },
                'max_tokens': {
                    'type': 'integer',
                    'minimum': 1,
                    'maximum': 4096,
                    'default': 1024
                }
            }
        }
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test connection to the provider
        
        Returns:
            Dict with test results
        """
        try:
            start_time = time.time()
            
            # Simple test message
            test_messages = [
                {"role": "user", "content": "Hello, this is a connection test."}
            ]
            
            response = self.chat(test_messages, max_tokens=10)
            response_time = time.time() - start_time
            
            return {
                'success': True,
                'response': response,
                'response_time': response_time,
                'provider': self.name,
                'model': self.model
            }
            
        except Exception as e:
            logger.error(f"Connection test failed for {self.name}: {e}")
            return {
                'success': False,
                'error': str(e),
                'provider': self.name,
                'model': self.model
            }
    
    def record_usage(self, tokens_used: int = 0, cost: float = 0.0):
        """
        Record usage statistics
        
        Args:
            tokens_used: Number of tokens used
            cost: Cost of the request
        """
        self.request_count += 1
        self.total_tokens += tokens_used
        self.total_cost += cost
        self.last_request_time = time.time()
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get usage statistics
        
        Returns:
            Dict with usage statistics
        """
        return {
            'request_count': self.request_count,
            'total_tokens': self.total_tokens,
            'total_cost': self.total_cost,
            'last_request_time': self.last_request_time,
            'provider': self.name
        }
    
    def __str__(self) -> str:
        return f"{self.get_display_name()}Provider(model={self.model})"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(api_key={'***' if self.api_key else None}, model={self.model})"
