"""
Base LLM Provider Interface
Abstract base class for all external LLM providers
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Generator


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, api_key: str, base_url: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.client = None
    
    @abstractmethod
    def initialize_client(self) -> None:
        """Initialize the provider's client"""
        pass
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Send a chat request and return a response string
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional provider-specific parameters
            
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
            **kwargs: Additional provider-specific parameters
            
        Yields:
            Response chunks as strings
        """
        pass
    
    def validate_messages(self, messages: List[Dict[str, str]]) -> bool:
        """Validate message format"""
        if not messages:
            return False
        
        for message in messages:
            if not isinstance(message, dict):
                return False
            if 'role' not in message or 'content' not in message:
                return False
            if message['role'] not in ['system', 'user', 'assistant']:
                return False
        
        return True
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get provider information"""
        return {
            'name': self.__class__.__name__,
            'base_url': self.base_url,
            'model': self.model,
            'supports_streaming': hasattr(self, 'chat_stream')
        }
