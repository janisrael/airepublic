#!/usr/bin/env python3
"""
External API Service for AI Refinement Dashboard
Handles communication with various AI providers (OpenAI, Anthropic, NVIDIA, etc.)
"""

import json
import requests
from typing import Dict, Any, Optional, Generator

# Optional imports - only import when needed
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

try:
    import cohere
    COHERE_AVAILABLE = True
except ImportError:
    COHERE_AVAILABLE = False

class ExternalAPIService:
    def __init__(self):
        self.providers = {
            'openai': self._call_openai,
            'anthropic': self._call_anthropic,
            'google': self._call_google,
            'nvidia': self._call_nvidia,
            'moonshotai': self._call_moonshotai,
            'cohere': self._call_cohere,
            'huggingface': self._call_huggingface
        }
    
    def call_model(self, model_config: Dict[str, Any], message: str, **kwargs) -> Generator[str, None, None]:
        """
        Call external API model with streaming support
        
        Args:
            model_config: Model configuration from database
            message: User message
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
        
        Yields:
            str: Response chunks
        """
        provider = model_config.get('provider', 'openai')
        model_id = model_config.get('model_id')
        api_key = model_config.get('api_key')
        base_url = model_config.get('base_url')
        
        if provider not in self.providers:
            raise ValueError(f"Unsupported provider: {provider}")
        
        # Merge model config with kwargs
        params = {
            'temperature': model_config.get('temperature', 0.7),
            'top_p': model_config.get('top_p', 0.9),
            'max_tokens': model_config.get('max_tokens', 4096),
            'system_prompt': model_config.get('system_prompt', ''),
            **kwargs
        }
        
        # Call the appropriate provider
        yield from self.providers[provider](model_id, api_key, base_url, message, params)
    
    def _call_openai(self, model_id: str, api_key: str, base_url: Optional[str], message: str, params: Dict[str, Any]) -> Generator[str, None, None]:
        """Call OpenAI-compatible API (OpenAI, NVIDIA, etc.)"""
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not installed. Install with: pip install openai")
        
        client = OpenAI(
            api_key=api_key,
            base_url=base_url or "https://api.openai.com/v1"
        )
        
        # Build messages array with system prompt if provided
        messages = []
        
        # Add system prompt if provided
        system_prompt = params.get('system_prompt', '')
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add user message
        messages.append({"role": "user", "content": message})
        
        completion = client.chat.completions.create(
            model=model_id,
            messages=messages,
            temperature=params.get('temperature', 0.7),
            top_p=params.get('top_p', 0.9),
            max_tokens=params.get('max_tokens', 4096),
            stream=True
        )
        
        for chunk in completion:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    def _call_anthropic(self, model_id: str, api_key: str, base_url: Optional[str], message: str, params: Dict[str, Any]) -> Generator[str, None, None]:
        """Call Anthropic Claude API"""
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("Anthropic library not installed. Install with: pip install anthropic")
        
        client = anthropic.Anthropic(api_key=api_key)
        
        with client.messages.stream(
            model=model_id,
            max_tokens=params.get('max_tokens', 4096),
            temperature=params.get('temperature', 0.7),
            messages=[{"role": "user", "content": message}]
        ) as stream:
            for text in stream.text_stream:
                yield text
    
    def _call_google(self, model_id: str, api_key: str, base_url: Optional[str], message: str, params: Dict[str, Any]) -> Generator[str, None, None]:
        """Call Google Gemini API"""
        if not GOOGLE_AVAILABLE:
            raise ImportError("Google Generative AI library not installed. Install with: pip install google-generativeai")
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_id)
        
        response = model.generate_content(
            message,
            generation_config=genai.types.GenerationConfig(
                temperature=params.get('temperature', 0.7),
                top_p=params.get('top_p', 0.9),
                max_output_tokens=params.get('max_tokens', 4096)
            )
        )
        
        yield response.text
    
    def _call_nvidia(self, model_id: str, api_key: str, base_url: Optional[str], message: str, params: Dict[str, Any]) -> Generator[str, None, None]:
        """Call NVIDIA API (OpenAI-compatible)"""
        yield from self._call_openai(model_id, api_key, base_url or "https://integrate.api.nvidia.com/v1", message, params)
    
    def _call_moonshotai(self, model_id: str, api_key: str, base_url: Optional[str], message: str, params: Dict[str, Any]) -> Generator[str, None, None]:
        """Call Moonshot AI API (OpenAI-compatible)"""
        yield from self._call_openai(model_id, api_key, base_url or "https://api.moonshot.cn/v1", message, params)
    
    def _call_cohere(self, model_id: str, api_key: str, base_url: Optional[str], message: str, params: Dict[str, Any]) -> Generator[str, None, None]:
        """Call Cohere API"""
        if not COHERE_AVAILABLE:
            raise ImportError("Cohere library not installed. Install with: pip install cohere")
        
        client = cohere.Client(api_key)
        
        response = client.generate(
            model=model_id,
            prompt=message,
            temperature=params.get('temperature', 0.7),
            max_tokens=params.get('max_tokens', 4096),
            stream=True
        )
        
        for chunk in response:
            yield chunk.text
    
    def _call_huggingface(self, model_id: str, api_key: str, base_url: Optional[str], message: str, params: Dict[str, Any]) -> Generator[str, None, None]:
        """Call Hugging Face Inference API"""
        import requests
        
        # Hugging Face Inference API endpoint
        hf_url = f"https://api-inference.huggingface.co/models/{model_id}"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": message,
            "parameters": {
                "temperature": params.get('temperature', 0.7),
                "top_p": params.get('top_p', 0.9),
                "max_new_tokens": params.get('max_tokens', 4096),
                "return_full_text": False
            }
        }
        
        response = requests.post(hf_url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                # Extract generated text from HF response
                generated_text = result[0].get('generated_text', '')
                yield generated_text
            else:
                yield str(result)
        else:
            raise Exception(f"Hugging Face API error: {response.status_code} - {response.text}")
    
    def test_connection(self, model_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test connection to external API model
        
        Returns:
            Dict with success status and response details
        """
        try:
            # Send a simple test message
            test_message = "Hello, this is a test message. Please respond with 'Connection successful'."
            response_chunks = []
            
            for chunk in self.call_model(model_config, test_message, max_tokens=50):
                response_chunks.append(chunk)
            
            response_text = ''.join(response_chunks)
            
            return {
                'success': True,
                'response': response_text,
                'provider': model_config.get('provider'),
                'model_id': model_config.get('model_id')
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'provider': model_config.get('provider'),
                'model_id': model_config.get('model_id')
            }
    
    def get_supported_providers(self) -> Dict[str, Dict[str, Any]]:
        """Get list of supported providers with their configurations"""
        return {
            'openai': {
                'name': 'OpenAI',
                'base_url': 'https://api.openai.com/v1',
                'models': ['gpt-4', 'gpt-3.5-turbo', 'gpt-4-turbo'],
                'requires_api_key': True,
                'supports_streaming': True
            },
            'anthropic': {
                'name': 'Anthropic',
                'base_url': 'https://api.anthropic.com',
                'models': ['claude-3-sonnet', 'claude-3-haiku', 'claude-3-opus'],
                'requires_api_key': True,
                'supports_streaming': True
            },
            'google': {
                'name': 'Google',
                'base_url': 'https://generativelanguage.googleapis.com',
                'models': ['gemini-pro', 'gemini-pro-vision'],
                'requires_api_key': True,
                'supports_streaming': False
            },
            'nvidia': {
                'name': 'NVIDIA',
                'base_url': 'https://integrate.api.nvidia.com/v1',
                'models': ['meta/llama3-70b-instruct', 'mistralai/mistral-7b-instruct'],
                'requires_api_key': True,
                'supports_streaming': True
            },
            'moonshotai': {
                'name': 'Moonshot AI',
                'base_url': 'https://api.moonshot.cn/v1',
                'models': ['moonshotai/kimi-k2-instruct-0905'],
                'requires_api_key': True,
                'supports_streaming': True
            },
            'cohere': {
                'name': 'Cohere',
                'base_url': 'https://api.cohere.ai',
                'models': ['command', 'command-light'],
                'requires_api_key': True,
                'supports_streaming': True
            },
            'huggingface': {
                'name': 'Hugging Face',
                'base_url': 'https://api-inference.huggingface.co',
                'models': [
                    'microsoft/DialoGPT-medium',
                    'facebook/blenderbot-400M-distill',
                    'microsoft/DialoGPT-large',
                    'facebook/blenderbot-1B-distill',
                    'microsoft/DialoGPT-small',
                    'facebook/blenderbot-90M',
                    'gpt2',
                    'gpt2-medium',
                    'gpt2-large',
                    'gpt2-xl',
                    'distilgpt2',
                    'EleutherAI/gpt-neo-125M',
                    'EleutherAI/gpt-neo-1.3B',
                    'EleutherAI/gpt-neo-2.7B',
                    'EleutherAI/gpt-j-6B',
                    'microsoft/DialoGPT-medium',
                    'facebook/blenderbot-400M-distill',
                    'microsoft/DialoGPT-large',
                    'facebook/blenderbot-1B-distill',
                    'microsoft/DialoGPT-small',
                    'facebook/blenderbot-90M',
                    'gpt2',
                    'gpt2-medium',
                    'gpt2-large',
                    'gpt2-xl',
                    'distilgpt2',
                    'EleutherAI/gpt-neo-125M',
                    'EleutherAI/gpt-neo-1.3B',
                    'EleutherAI/gpt-neo-2.7B',
                    'EleutherAI/gpt-j-6B',
                    'bigscience/bloom-560m',
                    'bigscience/bloom-1b1',
                    'bigscience/bloom-1b7',
                    'bigscience/bloom-3b',
                    'bigscience/bloom-7b1',
                    'bigscience/bloomz-560m',
                    'bigscience/bloomz-1b1',
                    'bigscience/bloomz-1b7',
                    'bigscience/bloomz-3b',
                    'bigscience/bloomz-7b1',
                    'meta-llama/Llama-2-7b-chat-hf',
                    'meta-llama/Llama-2-13b-chat-hf',
                    'meta-llama/Llama-2-70b-chat-hf',
                    'mistralai/Mistral-7B-Instruct-v0.1',
                    'mistralai/Mistral-7B-Instruct-v0.2',
                    'mistralai/Mixtral-8x7B-Instruct-v0.1',
                    'mistralai/Mixtral-8x22B-Instruct-v0.1',
                    'Qwen/Qwen-7B-Chat',
                    'Qwen/Qwen-14B-Chat',
                    'Qwen/Qwen-32B-Chat',
                    'Qwen/Qwen-72B-Chat',
                    'Qwen/Qwen2-7B-Instruct',
                    'Qwen/Qwen2-14B-Instruct',
                    'Qwen/Qwen2-32B-Instruct',
                    'Qwen/Qwen2-72B-Instruct',
                    'microsoft/Orca-2-7b',
                    'microsoft/Orca-2-13b',
                    'microsoft/Orca-2-70b',
                    'NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO',
                    'NousResearch/Nous-Hermes-2-Mixtral-8x7B-SFT',
                    'NousResearch/Nous-Hermes-2-Yi-34B',
                    'NousResearch/Nous-Hermes-2-Llama-2-70b',
                    'NousResearch/Nous-Hermes-2-Llama-2-13b',
                    'NousResearch/Nous-Hermes-2-Llama-2-7b',
                    'NousResearch/Nous-Hermes-2-Mistral-7B-DPO',
                    'NousResearch/Nous-Hermes-2-Mistral-7B-SFT',
                    'NousResearch/Nous-Hermes-2-SOLAR-10.7B',
                    'NousResearch/Nous-Hermes-2-SOLAR-10.7B-Instruct',
                    'NousResearch/Nous-Hermes-2-SOLAR-10.7B-DPO',
                    'NousResearch/Nous-Hermes-2-SOLAR-10.7B-SFT',
                    'NousResearch/Nous-Hermes-2-SOLAR-10.7B-Instruct-v0.1',
                    'NousResearch/Nous-Hermes-2-SOLAR-10.7B-DPO-v0.1',
                    'NousResearch/Nous-Hermes-2-SOLAR-10.7B-SFT-v0.1',
                    'NousResearch/Nous-Hermes-2-SOLAR-10.7B-Instruct-v0.2',
                    'NousResearch/Nous-Hermes-2-SOLAR-10.7B-DPO-v0.2',
                    'NousResearch/Nous-Hermes-2-SOLAR-10.7B-SFT-v0.2',
                    'NousResearch/Nous-Hermes-2-SOLAR-10.7B-Instruct-v0.3',
                    'NousResearch/Nous-Hermes-2-SOLAR-10.7B-DPO-v0.3',
                    'NousResearch/Nous-Hermes-2-SOLAR-10.7B-SFT-v0.3',
                    'NousResearch/Nous-Hermes-2-SOLAR-10.7B-Instruct-v0.4',
                    'NousResearch/Nous-Hermes-2-SOLAR-10.7B-DPO-v0.4',
                    'NousResearch/Nous-Hermes-2-SOLAR-10.7B-SFT-v0.4',
                    'NousResearch/Nous-Hermes-2-SOLAR-10.7B-Instruct-v0.5',
                    'NousResearch/Nous-Hermes-2-SOLAR-10.7B-DPO-v0.5',
                    'NousResearch/Nous-Hermes-2-SOLAR-10.7B-SFT-v0.5',
                    'NousResearch/Nous-Hermes-2-SOLAR-10.7B-Instruct-v0.6',
                    'NousResearch/Nous-Hermes-2-SOLAR-10.7B-DPO-v0.6',
                    'NousResearch/Nous-Hermes-2-SOLAR-10.7B-SFT-v0.6',
                    'NousResearch/Nous-Hermes-2-SOLAR-10.7B-Instruct-v0.7',
                    'NousResearch/Nous-Hermes-2-SOLAR-10.7B-DPO-v0.7',
                    'NousResearch/Nous-Hermes-2-SOLAR-10.7B-SFT-v0.7',
                    'NousResearch/Nous-Hermes-2-SOLAR-10.7B-Instruct-v0.8',
                    'NousResearch/Nous-Hermes-2-SOLAR-10.7B-DPO-v0.8',
                    'NousResearch/Nous-Hermes-2-SOLAR-10.7B-SFT-v0.8',
                    'NousResearch/Nous-Hermes-2-SOLAR-10.7B-Instruct-v0.9',
                    'NousResearch/Nous-Hermes-2-SOLAR-10.7B-DPO-v0.9',
                    'NousResearch/Nous-Hermes-2-SOLAR-10.7B-SFT-v0.9',
                    'NousResearch/Nous-Hermes-2-SOLAR-10.7B-Instruct-v1.0',
                    'NousResearch/Nous-Hermes-2-SOLAR-10.7B-DPO-v1.0',
                    'NousResearch/Nous-Hermes-2-SOLAR-10.7B-SFT-v1.0'
                ],
                'requires_api_key': True,
                'supports_streaming': False
            }
        }

# Global service instance
external_api_service = ExternalAPIService()

if __name__ == '__main__':
    # Test the service
    service = ExternalAPIService()
    
    # Test NVIDIA API with your example
    nvidia_config = {
        'provider': 'nvidia',
        'model_id': 'moonshotai/kimi-k2-instruct-0905',
        'api_key': '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',
        'base_url': 'https://integrate.api.nvidia.com/v1',
        'temperature': 0.6,
        'top_p': 0.9,
        'max_tokens': 4096
    }
    
    print("Testing NVIDIA API connection...")
    result = service.test_connection(nvidia_config)
    print(f"Result: {result}")
    
    if result['success']:
        print("\nTesting streaming response...")
        for chunk in service.call_model(nvidia_config, "Hello, how are you?"):
            print(chunk, end="")
        print("\n")
