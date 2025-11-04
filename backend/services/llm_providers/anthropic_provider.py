"""
Anthropic Provider Implementation

Anthropic Claude API provider for the dynamic LLM provider system.
Supports Claude models with chat and streaming capabilities.

Access: Admin, Superuser, Developer only
"""

from typing import List, Dict, Any, Generator
import logging
from .base import LLMProvider

logger = logging.getLogger(__name__)

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("Anthropic package not available. Install with: pip install anthropic")


class AnthropicProvider(LLMProvider):
    """
    Anthropic Claude API provider
    """
    
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022", **kwargs):
        """
        Initialize Anthropic provider
        
        Args:
            api_key: Anthropic API key
            model: Model name (e.g., claude-3-5-sonnet-20241022, claude-3-haiku-20240307)
            **kwargs: Additional configuration
        """
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("Anthropic package not available. Install with: pip install anthropic")
        
        super().__init__(api_key, None, model, **kwargs)
        
        # Initialize Anthropic client
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def _prepare_messages(self, messages: List[Dict[str, str]]) -> tuple:
        """
        Prepare messages for Anthropic API format
        
        Args:
            messages: List of message dicts
        
        Returns:
            Tuple of (system_prompt, user_messages)
        """
        system_prompt = ""
        user_messages = []
        
        for msg in messages:
            if msg['role'] == 'system':
                system_prompt += msg['content'] + "\n"
            elif msg['role'] == 'user':
                user_messages.append({"role": "user", "content": msg['content']})
            elif msg['role'] == 'assistant':
                user_messages.append({"role": "assistant", "content": msg['content']})
        
        return system_prompt.strip(), user_messages
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Send a chat completion request
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional parameters
        
        Returns:
            Response string from Claude
        """
        try:
            system_prompt, user_messages = self._prepare_messages(messages)
            
            response = self.client.messages.create(
                model=self.model,
                system=system_prompt if system_prompt else None,
                messages=user_messages,
                max_tokens=kwargs.get('max_tokens', 1024),
                temperature=kwargs.get('temperature', 0.7),
                top_p=kwargs.get('top_p', 1.0)
            )
            
            # Record usage
            if hasattr(response, 'usage'):
                self.record_usage(
                    tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                    cost=self._calculate_cost(response.usage)
                )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Anthropic chat request failed: {e}")
            raise
    
    def chat_stream(self, messages: List[Dict[str, str]], **kwargs) -> Generator[str, None, None]:
        """
        Send a streaming chat completion request
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional parameters
        
        Yields:
            Response chunks as strings
        """
        try:
            system_prompt, user_messages = self._prepare_messages(messages)
            
            with self.client.messages.stream(
                model=self.model,
                system=system_prompt if system_prompt else None,
                messages=user_messages,
                max_tokens=kwargs.get('max_tokens', 1024),
                temperature=kwargs.get('temperature', 0.7),
                top_p=kwargs.get('top_p', 1.0)
            ) as stream:
                for event in stream:
                    if event.type == "content_block_delta":
                        yield event.delta.text
            
        except Exception as e:
            logger.error(f"Anthropic streaming request failed: {e}")
            raise
    
    def _calculate_cost(self, usage) -> float:
        """
        Calculate cost based on usage
        
        Args:
            usage: Anthropic usage object
        
        Returns:
            Estimated cost in USD
        """
        # Anthropic pricing (as of 2024)
        pricing = {
            'claude-3-5-sonnet-20241022': {'input': 0.003, 'output': 0.015},
            'claude-3-5-haiku-20241022': {'input': 0.0008, 'output': 0.004},
            'claude-3-haiku-20240307': {'input': 0.00025, 'output': 0.00125},
            'claude-3-sonnet-20240229': {'input': 0.003, 'output': 0.015},
            'claude-3-opus-20240229': {'input': 0.015, 'output': 0.075}
        }
        
        model_pricing = pricing.get(self.model, pricing['claude-3-5-sonnet-20241022'])
        
        input_cost = (usage.input_tokens / 1000) * model_pricing['input']
        output_cost = (usage.output_tokens / 1000) * model_pricing['output']
        
        return input_cost + output_cost
    
    def get_display_name(self) -> str:
        """Get display name"""
        return "Anthropic"
    
    def get_capabilities(self) -> List[str]:
        """Get capabilities"""
        return ['chat', 'streaming', 'vision', 'function_calling']
    
    def get_default_models(self) -> List[str]:
        """Get default models"""
        return [
            'claude-3-5-sonnet-20241022',
            'claude-3-5-haiku-20241022',
            'claude-3-haiku-20240307',
            'claude-3-sonnet-20240229',
            'claude-3-opus-20240229'
        ]
    
    def get_config_schema(self) -> Dict[str, Any]:
        """Get configuration schema"""
        return {
            'type': 'object',
            'properties': {
                'temperature': {
                    'type': 'number',
                    'minimum': 0,
                    'maximum': 1,
                    'default': 0.7,
                    'description': 'Controls randomness in responses'
                },
                'max_tokens': {
                    'type': 'integer',
                    'minimum': 1,
                    'maximum': 4096,
                    'default': 1024,
                    'description': 'Maximum tokens to generate'
                },
                'top_p': {
                    'type': 'number',
                    'minimum': 0,
                    'maximum': 1,
                    'default': 1.0,
                    'description': 'Controls diversity via nucleus sampling'
                }
            }
        }
    
    def validate_config(self) -> bool:
        """Validate configuration"""
        if not self.api_key:
            return False
        
        # Check API key format
        if not self.api_key.startswith('sk-ant-'):
            logger.warning("Anthropic API key should start with 'sk-ant-'")
        
        return True
