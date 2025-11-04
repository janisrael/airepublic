"""
OpenAI Provider Implementation
Supports OpenAI API and OpenAI-compatible endpoints (NVIDIA, etc.)
"""

from typing import List, Dict, Any, Optional, Generator
from .base_provider import BaseLLMProvider

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None


class OpenAIProvider(BaseLLMProvider):
    """OpenAI-compatible provider (OpenAI, NVIDIA, etc.)"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1", model: str = "gpt-4o-mini"):
        super().__init__(api_key, base_url, model)
        self.initialize_client()
    
    def initialize_client(self) -> None:
        """Initialize OpenAI client"""
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package not available. Install with: pip install openai")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Send chat request to OpenAI-compatible API"""
        if not self.validate_messages(messages):
            raise ValueError("Invalid message format")
        
        try:
            response = self.client.chat.completions.create(
                model=kwargs.get('model', self.model),
                messages=messages,
                temperature=kwargs.get('temperature', 0.7),
                max_tokens=kwargs.get('max_tokens', 1024),
                top_p=kwargs.get('top_p', 1.0),
                frequency_penalty=kwargs.get('frequency_penalty', 0.0),
                presence_penalty=kwargs.get('presence_penalty', 0.0)
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def chat_stream(self, messages: List[Dict[str, str]], **kwargs) -> Generator[str, None, None]:
        """Send streaming chat request"""
        if not self.validate_messages(messages):
            raise ValueError("Invalid message format")
        
        try:
            response = self.client.chat.completions.create(
                model=kwargs.get('model', self.model),
                messages=messages,
                temperature=kwargs.get('temperature', 0.7),
                max_tokens=kwargs.get('max_tokens', 1024),
                top_p=kwargs.get('top_p', 1.0),
                frequency_penalty=kwargs.get('frequency_penalty', 0.0),
                presence_penalty=kwargs.get('presence_penalty', 0.0),
                stream=True
            )
            
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            raise Exception(f"OpenAI streaming API error: {str(e)}")
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        try:
            models = self.client.models.list()
            return [model.id for model in models.data]
        except Exception:
            # Fallback to common models
            return [
                "gpt-4o",
                "gpt-4o-mini", 
                "gpt-4-turbo",
                "gpt-3.5-turbo"
            ]
