"""
Anthropic Provider Implementation
Supports Claude models via Anthropic API
"""

from typing import List, Dict, Any, Optional, Generator
from .base_provider import BaseLLMProvider

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    anthropic = None


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude provider"""
    
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        super().__init__(api_key, None, model)
        self.initialize_client()
    
    def initialize_client(self) -> None:
        """Initialize Anthropic client"""
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("Anthropic package not available. Install with: pip install anthropic")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Send chat request to Anthropic API"""
        if not self.validate_messages(messages):
            raise ValueError("Invalid message format")
        
        # Convert messages to Anthropic format
        system_prompt = ""
        user_messages = []
        
        for message in messages:
            if message['role'] == 'system':
                system_prompt = message['content']
            elif message['role'] == 'user':
                user_messages.append({"role": "user", "content": message['content']})
            elif message['role'] == 'assistant':
                user_messages.append({"role": "assistant", "content": message['content']})
        
        try:
            response = self.client.messages.create(
                model=kwargs.get('model', self.model),
                max_tokens=kwargs.get('max_tokens', 1024),
                temperature=kwargs.get('temperature', 0.7),
                system=system_prompt if system_prompt else None,
                messages=user_messages
            )
            
            return response.content[0].text
            
        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")
    
    def chat_stream(self, messages: List[Dict[str, str]], **kwargs) -> Generator[str, None, None]:
        """Send streaming chat request"""
        if not self.validate_messages(messages):
            raise ValueError("Invalid message format")
        
        # Convert messages to Anthropic format
        system_prompt = ""
        user_messages = []
        
        for message in messages:
            if message['role'] == 'system':
                system_prompt = message['content']
            elif message['role'] == 'user':
                user_messages.append({"role": "user", "content": message['content']})
            elif message['role'] == 'assistant':
                user_messages.append({"role": "assistant", "content": message['content']})
        
        try:
            with self.client.messages.stream(
                model=kwargs.get('model', self.model),
                max_tokens=kwargs.get('max_tokens', 1024),
                temperature=kwargs.get('temperature', 0.7),
                system=system_prompt if system_prompt else None,
                messages=user_messages
            ) as stream:
                for event in stream:
                    if event.type == "content_block_delta":
                        yield event.delta.text
                        
        except Exception as e:
            raise Exception(f"Anthropic streaming API error: {str(e)}")
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        return [
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]
