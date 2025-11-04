"""
NVIDIA Provider Implementation
Supports NVIDIA Nemotron models via NVIDIA API
"""

from typing import List, Dict, Any, Optional, Generator
from .base_provider import BaseLLMProvider

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None


class NVIDIAProvider(BaseLLMProvider):
    """NVIDIA Nemotron provider using OpenAI-compatible API"""
    
    def __init__(self, api_key: str, model: str = "nvidia/llama-3.3-nemotron-super-49b-v1.5"):
        base_url = "https://integrate.api.nvidia.com/v1"
        super().__init__(api_key, base_url, model)
        self.initialize_client()
    
    def initialize_client(self) -> None:
        """Initialize NVIDIA client using OpenAI-compatible interface"""
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package not available. Install with: pip install openai")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Send chat request to NVIDIA API"""
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
            raise Exception(f"NVIDIA API error: {str(e)}")
    
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
            raise Exception(f"NVIDIA streaming API error: {str(e)}")
    
    def get_available_models(self) -> List[str]:
        """Get list of available NVIDIA models"""
        return [
            "nvidia/llama-3.3-nemotron-super-49b-v1.5",
            "nvidia/llama-3.3-nemotron-large-8b-v1.5",
            "nvidia/llama-3.3-nemotron-medium-8b-v1.5",
            "nvidia/llama-3.3-nemotron-small-8b-v1.5"
        ]
