"""
NVIDIA Provider Implementation

NVIDIA NIM API provider for the dynamic LLM provider system.
Supports NVIDIA models with OpenAI-compatible interface.

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


class NVIDIAProvider(LLMProvider):
    """
    NVIDIA NIM API provider (OpenAI-compatible)
    """
    
    def __init__(self, api_key: str, model: str = "nvidia/llama-3.3-nemotron-super-49b-v1.5", **kwargs):
        """
        Initialize NVIDIA provider
        
        Args:
            api_key: NVIDIA API key
            model: Model name (e.g., nvidia/llama-3.3-nemotron-super-49b-v1.5)
            **kwargs: Additional configuration
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package not available. Install with: pip install openai")
        
        # Set default base URL for NVIDIA NIM
        base_url = kwargs.get('base_url', 'https://integrate.api.nvidia.com/v1')
        
        super().__init__(api_key, base_url, model, **kwargs)
        
        # Initialize OpenAI client with NVIDIA base URL
        self.client = OpenAI(api_key=api_key, base_url=base_url)
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Send a chat completion request
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional parameters
        
        Returns:
            Response string from NVIDIA model
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
            logger.error(f"NVIDIA chat request failed: {e}")
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
            logger.error(f"NVIDIA streaming request failed: {e}")
            raise
    
    def _calculate_cost(self, usage) -> float:
        """
        Calculate cost based on usage
        
        Args:
            usage: OpenAI usage object
        
        Returns:
            Estimated cost in USD
        """
        # NVIDIA NIM pricing (as of 2024) - varies by model
        pricing = {
            'nvidia/llama-3.3-nemotron-super-49b-v1.5': {'input': 0.002, 'output': 0.006},
            'nvidia/llama-3.3-nemotron-8b-v1.5': {'input': 0.0005, 'output': 0.0015},
            'nvidia/llama-3.3-nemotron-70b-v1.5': {'input': 0.001, 'output': 0.003}
        }
        
        model_pricing = pricing.get(self.model, pricing['nvidia/llama-3.3-nemotron-super-49b-v1.5'])
        
        input_cost = (usage.prompt_tokens / 1000) * model_pricing['input']
        output_cost = (usage.completion_tokens / 1000) * model_pricing['output']
        
        return input_cost + output_cost
    
    def get_display_name(self) -> str:
        """Get display name"""
        return "NVIDIA"
    
    def get_capabilities(self) -> List[str]:
        """Get capabilities"""
        return ['chat', 'streaming', 'coding', 'reasoning']
    
    def get_default_models(self) -> List[str]:
        """Get default models"""
        return [
            'nvidia/llama-3.3-nemotron-super-49b-v1.5',
            'nvidia/llama-3.3-nemotron-8b-v1.5',
            'nvidia/llama-3.3-nemotron-70b-v1.5',
            'nvidia/llama-3.3-nemotron-405b-v1.5'
        ]
    
    def get_config_schema(self) -> Dict[str, Any]:
        """Get configuration schema"""
        return {
            'type': 'object',
            'properties': {
                'base_url': {
                    'type': 'string',
                    'default': 'https://integrate.api.nvidia.com/v1',
                    'description': 'NVIDIA NIM API base URL'
                },
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
        if not self.api_key.startswith('nvapi-'):
            logger.warning("NVIDIA API key should start with 'nvapi-'")
        
        return True
