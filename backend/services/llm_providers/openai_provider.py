"""
OpenAI Provider Implementation

OpenAI API provider for the dynamic LLM provider system.
Supports GPT models with chat and streaming capabilities.

Access: Admin, Superuser, Developer only
"""

from typing import List, Dict, Any, Generator
import logging
from .base import LLMProvider

logger = logging.getLogger(__name__)

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI package not available. Install with: pip install openai")


class OpenAIProvider(LLMProvider):
    """
    OpenAI API provider
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini", base_url: str = None, **kwargs):
        """
        Initialize OpenAI provider
        
        Args:
            api_key: OpenAI API key
            model: Model name (e.g., gpt-4o, gpt-4o-mini, gpt-3.5-turbo)
            base_url: Custom base URL (for OpenAI-compatible APIs)
            **kwargs: Additional configuration
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package not available. Install with: pip install openai")
        
        super().__init__(api_key, base_url, model, **kwargs)
        
        # Set default base URL if not provided
        if not self.base_url:
            self.base_url = "https://api.openai.com/v1"
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=api_key, base_url=base_url)
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Send a chat completion request
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional parameters
        
        Returns:
            Response string from OpenAI
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get('temperature', 0.7),
                max_tokens=kwargs.get('max_tokens', 1024),
                top_p=kwargs.get('top_p', 1.0),
                frequency_penalty=kwargs.get('frequency_penalty', 0.0),
                presence_penalty=kwargs.get('presence_penalty', 0.0),
                stream=False
            )
            
            # Record usage
            if hasattr(response, 'usage') and response.usage:
                self.record_usage(
                    tokens_used=response.usage.total_tokens,
                    cost=self._calculate_cost(response.usage)
                )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI chat request failed: {e}")
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
            response = self.client.chat.completions.create(
                model=self.model,
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
            logger.error(f"OpenAI streaming request failed: {e}")
            raise
    
    def _calculate_cost(self, usage) -> float:
        """
        Calculate cost based on usage
        
        Args:
            usage: OpenAI usage object
        
        Returns:
            Estimated cost in USD
        """
        # OpenAI pricing (as of 2024)
        pricing = {
            'gpt-4o': {'input': 0.005, 'output': 0.015},
            'gpt-4o-mini': {'input': 0.00015, 'output': 0.0006},
            'gpt-4': {'input': 0.03, 'output': 0.06},
            'gpt-3.5-turbo': {'input': 0.0015, 'output': 0.002}
        }
        
        model_pricing = pricing.get(self.model, pricing['gpt-4o-mini'])
        
        input_cost = (usage.prompt_tokens / 1000) * model_pricing['input']
        output_cost = (usage.completion_tokens / 1000) * model_pricing['output']
        
        return input_cost + output_cost
    
    def get_display_name(self) -> str:
        """Get display name"""
        return "OpenAI"
    
    def get_capabilities(self) -> List[str]:
        """Get capabilities"""
        return ['chat', 'streaming', 'function_calling', 'json_mode']
    
    def get_default_models(self) -> List[str]:
        """Get default models"""
        return [
            'gpt-4o',
            'gpt-4o-mini',
            'gpt-4',
            'gpt-3.5-turbo'
        ]
    
    def get_config_schema(self) -> Dict[str, Any]:
        """Get configuration schema"""
        return {
            'type': 'object',
            'properties': {
                'temperature': {
                    'type': 'number',
                    'minimum': 0,
                    'maximum': 2,
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
                },
                'frequency_penalty': {
                    'type': 'number',
                    'minimum': -2,
                    'maximum': 2,
                    'default': 0.0,
                    'description': 'Penalizes frequent tokens'
                },
                'presence_penalty': {
                    'type': 'number',
                    'minimum': -2,
                    'maximum': 2,
                    'default': 0.0,
                    'description': 'Penalizes new tokens'
                }
            }
        }
    
    def validate_config(self) -> bool:
        """Validate configuration"""
        if not self.api_key:
            return False
        
        # Check API key format
        if not self.api_key.startswith('sk-'):
            logger.warning("OpenAI API key should start with 'sk-'")
        
        return True
