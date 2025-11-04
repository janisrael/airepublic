# External Model Training Service with Dynamic LLM Router - Implementation Plan V2

## Overview

This document outlines the implementation plan for a dynamic external model training system that supports any LLM provider through a plugin-based architecture. The system combines local LoRA fine-tuning, RAG (ChromaDB), and a dynamic LLM router that can connect to any external provider.

## Table of Contents

1. [Dynamic LLM Router Architecture](#dynamic-llm-router-architecture)
2. [Plugin-Based Provider System](#plugin-based-provider-system)
3. [LoRA + RAG + External LLM Pipeline](#lora--rag--external-llm-pipeline)
4. [Database Schema Updates](#database-schema-updates)
5. [Service Architecture](#service-architecture)
6. [API Endpoints](#api-endpoints)
7. [Frontend Integration](#frontend-integration)
8. [Implementation Phases](#implementation-phases)

---

## 1. Dynamic LLM Router Architecture

### 1.1 Core Concept

The dynamic LLM router provides a unified interface to any external LLM provider through a plugin-based architecture. This allows adding new providers without modifying existing code.

```
User Query → Local LoRA → RAG Context → Dynamic Router → Any External LLM → Final Response
```

### 1.2 Base Provider Interface

```python
# backend/services/llm_providers/base.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Generator, Optional

class LLMProvider(ABC):
    """
    Base class for all LLM providers
    """
    
    def __init__(self, api_key: str = None, base_url: str = None, model: str = None, **kwargs):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.config = kwargs
    
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
        return bool(self.api_key)
    
    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get provider information
        
        Returns:
            Dict with provider metadata
        """
        return {
            'name': self.__class__.__name__,
            'model': self.model,
            'base_url': self.base_url,
            'supports_streaming': hasattr(self, 'chat_stream')
        }
```

### 1.3 Dynamic Router

```python
# backend/services/llm_router.py
from typing import Dict, Type, Any, List
import importlib
import os
from .llm_providers.base import LLMProvider

class LLMRouter:
    """
    Dynamic router for LLM providers
    """
    
    def __init__(self):
        self.providers: Dict[str, Type[LLMProvider]] = {}
        self.active_providers: Dict[str, LLMProvider] = {}
        self._load_builtin_providers()
    
    def _load_builtin_providers(self):
        """Load built-in provider classes"""
        try:
            from .llm_providers.openai_provider import OpenAIProvider
            from .llm_providers.anthropic_provider import AnthropicProvider
            from .llm_providers.nvidia_provider import NVIDIAProvider
            from .llm_providers.huggingface_provider import HuggingFaceProvider
            from .llm_providers.ollama_provider import OllamaProvider
            from .llm_providers.cohere_provider import CohereProvider
            
            self.register_provider('openai', OpenAIProvider)
            self.register_provider('anthropic', AnthropicProvider)
            self.register_provider('nvidia', NVIDIAProvider)
            self.register_provider('huggingface', HuggingFaceProvider)
            self.register_provider('ollama', OllamaProvider)
            self.register_provider('cohere', CohereProvider)
            
        except ImportError as e:
            print(f"Warning: Could not load some providers: {e}")
    
    def register_provider(self, name: str, provider_class: Type[LLMProvider]):
        """
        Register a new provider
        
        Args:
            name: Provider name (e.g., 'openai', 'anthropic')
            provider_class: Provider class that extends LLMProvider
        """
        self.providers[name.lower()] = provider_class
        print(f"✅ Registered provider: {name}")
    
    def create_provider(self, name: str, **config) -> LLMProvider:
        """
        Create a provider instance
        
        Args:
            name: Provider name
            **config: Provider configuration
        
        Returns:
            Provider instance
        """
        name = name.lower()
        
        if name not in self.providers:
            raise ValueError(f"Unknown provider: {name}. Available: {list(self.providers.keys())}")
        
        provider_class = self.providers[name]
        provider = provider_class(**config)
        
        if not provider.validate_config():
            raise ValueError(f"Invalid configuration for provider: {name}")
        
        return provider
    
    def get_provider(self, name: str, **config) -> LLMProvider:
        """
        Get or create a provider instance (with caching)
        
        Args:
            name: Provider name
            **config: Provider configuration
        
        Returns:
            Provider instance
        """
        cache_key = f"{name}:{hash(str(sorted(config.items())))}"
        
        if cache_key not in self.active_providers:
            self.active_providers[cache_key] = self.create_provider(name, **config)
        
        return self.active_providers[cache_key]
    
    def list_providers(self) -> List[str]:
        """List all registered providers"""
        return list(self.providers.keys())
    
    def get_provider_info(self, name: str) -> Dict[str, Any]:
        """Get information about a provider"""
        if name not in self.providers:
            raise ValueError(f"Unknown provider: {name}")
        
        return {
            'name': name,
            'class': self.providers[name].__name__,
            'module': self.providers[name].__module__
        }

# Global router instance
llm_router = LLMRouter()
```

---

## 2. Plugin-Based Provider System

### 2.1 OpenAI Provider

```python
# backend/services/llm_providers/openai_provider.py
from openai import OpenAI
from typing import List, Dict, Any, Generator
from .base import LLMProvider

class OpenAIProvider(LLMProvider):
    """
    OpenAI API provider
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini", base_url: str = None, **kwargs):
        super().__init__(api_key, base_url, model, **kwargs)
        self.client = OpenAI(api_key=api_key, base_url=base_url)
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Chat completion"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=kwargs.get('temperature', 0.7),
            max_tokens=kwargs.get('max_tokens', 1024),
            stream=False
        )
        return response.choices[0].message.content
    
    def chat_stream(self, messages: List[Dict[str, str]], **kwargs) -> Generator[str, None, None]:
        """Streaming chat completion"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=kwargs.get('temperature', 0.7),
            max_tokens=kwargs.get('max_tokens', 1024),
            stream=True
        )
        
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
```

### 2.2 Anthropic Provider

```python
# backend/services/llm_providers/anthropic_provider.py
import anthropic
from typing import List, Dict, Any, Generator
from .base import LLMProvider

class AnthropicProvider(LLMProvider):
    """
    Anthropic Claude API provider
    """
    
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022", **kwargs):
        super().__init__(api_key, None, model, **kwargs)
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def _prepare_messages(self, messages: List[Dict[str, str]]) -> tuple:
        """Prepare messages for Anthropic API"""
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
        """Chat completion"""
        system_prompt, user_messages = self._prepare_messages(messages)
        
        response = self.client.messages.create(
            model=self.model,
            system=system_prompt,
            messages=user_messages,
            max_tokens=kwargs.get('max_tokens', 1024),
            temperature=kwargs.get('temperature', 0.7)
        )
        
        return response.content[0].text
    
    def chat_stream(self, messages: List[Dict[str, str]], **kwargs) -> Generator[str, None, None]:
        """Streaming chat completion"""
        system_prompt, user_messages = self._prepare_messages(messages)
        
        with self.client.messages.stream(
            model=self.model,
            system=system_prompt,
            messages=user_messages,
            max_tokens=kwargs.get('max_tokens', 1024),
            temperature=kwargs.get('temperature', 0.7)
        ) as stream:
            for event in stream:
                if event.type == "content_block_delta":
                    yield event.delta.text
```

### 2.3 NVIDIA Provider

```python
# backend/services/llm_providers/nvidia_provider.py
from openai import OpenAI
from typing import List, Dict, Any, Generator
from .base import LLMProvider

class NVIDIAProvider(LLMProvider):
    """
    NVIDIA NIM API provider (OpenAI-compatible)
    """
    
    def __init__(self, api_key: str, model: str = "nvidia/llama-3.3-nemotron-super-49b-v1.5", **kwargs):
        base_url = kwargs.get('base_url', 'https://integrate.api.nvidia.com/v1')
        super().__init__(api_key, base_url, model, **kwargs)
        self.client = OpenAI(api_key=api_key, base_url=base_url)
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Chat completion"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=kwargs.get('temperature', 0.7),
            max_tokens=kwargs.get('max_tokens', 1024),
            stream=False
        )
        return response.choices[0].message.content
    
    def chat_stream(self, messages: List[Dict[str, str]], **kwargs) -> Generator[str, None, None]:
        """Streaming chat completion"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=kwargs.get('temperature', 0.7),
            max_tokens=kwargs.get('max_tokens', 1024),
            stream=True
        )
        
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
```

### 2.4 Hugging Face Provider

```python
# backend/services/llm_providers/huggingface_provider.py
import requests
import json
from typing import List, Dict, Any, Generator
from .base import LLMProvider

class HuggingFaceProvider(LLMProvider):
    """
    Hugging Face Inference API provider
    """
    
    def __init__(self, api_key: str, model: str = None, base_url: str = None, **kwargs):
        super().__init__(api_key, base_url, model, **kwargs)
        if not self.base_url:
            raise ValueError("base_url is required for Hugging Face provider")
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Chat completion"""
        # Get the last user message
        user_message = ""
        for msg in reversed(messages):
            if msg['role'] == 'user':
                user_message = msg['content']
                break
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": user_message,
            "parameters": {
                "max_new_tokens": kwargs.get('max_tokens', 512),
                "temperature": kwargs.get('temperature', 0.7),
                "return_full_text": False
            }
        }
        
        response = requests.post(self.base_url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        if isinstance(result, list) and len(result) > 0:
            return result[0].get('generated_text', '')
        return str(result)
    
    def chat_stream(self, messages: List[Dict[str, str]], **kwargs) -> Generator[str, None, None]:
        """Streaming chat completion (fallback to non-streaming)"""
        # Hugging Face Inference API doesn't support streaming
        # Fall back to regular chat and yield the full response
        response = self.chat(messages, **kwargs)
        yield response
```

### 2.5 Ollama Provider

```python
# backend/services/llm_providers/ollama_provider.py
import requests
import json
from typing import List, Dict, Any, Generator
from .base import LLMProvider

class OllamaProvider(LLMProvider):
    """
    Ollama local server provider
    """
    
    def __init__(self, api_key: str = None, model: str = "llama3", base_url: str = "http://localhost:11434", **kwargs):
        super().__init__(api_key, base_url, model, **kwargs)
    
    def _prepare_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert messages to prompt format"""
        prompt_parts = []
        for msg in messages:
            role = msg['role']
            content = msg['content']
            if role == 'system':
                prompt_parts.append(f"System: {content}")
            elif role == 'user':
                prompt_parts.append(f"Human: {content}")
            elif role == 'assistant':
                prompt_parts.append(f"Assistant: {content}")
        
        return "\n\n".join(prompt_parts) + "\n\nAssistant:"
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Chat completion"""
        prompt = self._prepare_prompt(messages)
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get('temperature', 0.7),
                "num_predict": kwargs.get('max_tokens', 1024)
            }
        }
        
        response = requests.post(f"{self.base_url}/api/generate", json=payload)
        response.raise_for_status()
        
        result = response.json()
        return result.get('response', '')
    
    def chat_stream(self, messages: List[Dict[str, str]], **kwargs) -> Generator[str, None, None]:
        """Streaming chat completion"""
        prompt = self._prepare_prompt(messages)
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": kwargs.get('temperature', 0.7),
                "num_predict": kwargs.get('max_tokens', 1024)
            }
        }
        
        response = requests.post(f"{self.base_url}/api/generate", json=payload, stream=True)
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                try:
                    chunk = json.loads(line)
                    if 'response' in chunk:
                        yield chunk['response']
                except json.JSONDecodeError:
                    continue
```

### 2.6 Cohere Provider

```python
# backend/services/llm_providers/cohere_provider.py
import cohere
from typing import List, Dict, Any, Generator
from .base import LLMProvider

class CohereProvider(LLMProvider):
    """
    Cohere API provider
    """
    
    def __init__(self, api_key: str, model: str = "command-r-plus", **kwargs):
        super().__init__(api_key, None, model, **kwargs)
        self.client = cohere.Client(api_key)
    
    def _prepare_messages(self, messages: List[Dict[str, str]]) -> str:
        """Convert messages to Cohere format"""
        conversation = []
        for msg in messages:
            if msg['role'] == 'user':
                conversation.append({"role": "USER", "message": msg['content']})
            elif msg['role'] == 'assistant':
                conversation.append({"role": "CHATBOT", "message": msg['content']})
        
        return conversation
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Chat completion"""
        conversation = self._prepare_messages(messages)
        
        response = self.client.chat(
            model=self.model,
            message=conversation[-1]['message'] if conversation else "",
            chat_history=conversation[:-1] if len(conversation) > 1 else [],
            temperature=kwargs.get('temperature', 0.7),
            max_tokens=kwargs.get('max_tokens', 1024)
        )
        
        return response.text
    
    def chat_stream(self, messages: List[Dict[str, str]], **kwargs) -> Generator[str, None, None]:
        """Streaming chat completion (fallback to non-streaming)"""
        # Cohere doesn't support streaming in the same way
        # Fall back to regular chat and yield the full response
        response = self.chat(messages, **kwargs)
        yield response
```

---

## 3. LoRA + RAG + External LLM Pipeline

### 3.1 Hybrid Pipeline Service

```python
# backend/services/hybrid_pipeline_service.py
from typing import Dict, Any, List, Generator
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from peft import PeftModel
import chromadb
from .llm_router import llm_router
from .chromadb_service import chromadb_service

class HybridPipelineService:
    """
    Service that combines LoRA, RAG, and external LLM
    """
    
    def __init__(self, user_service, api_key_manager):
        self.user_service = user_service
        self.api_key_manager = api_key_manager
        self.lora_models = {}  # Cache for loaded LoRA models
        self.vector_client = chromadb_service
    
    def load_lora_model(self, user_id: int, model_path: str) -> pipeline:
        """
        Load LoRA model for user
        
        Args:
            user_id: User ID
            model_path: Path to LoRA model
        
        Returns:
            Text generation pipeline
        """
        cache_key = f"{user_id}:{model_path}"
        
        if cache_key not in self.lora_models:
            # Load base model
            base_model_name = "microsoft/DialoGPT-medium"
            tokenizer = AutoTokenizer.from_pretrained(base_model_name)
            model = AutoModelForCausalLM.from_pretrained(base_model_name)
            
            # Load LoRA adapters if they exist
            try:
                model = PeftModel.from_pretrained(model, model_path)
                print(f"✅ Loaded LoRA adapters from {model_path}")
            except Exception as e:
                print(f"⚠️ Could not load LoRA adapters: {e}")
            
            # Create pipeline
            pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)
            self.lora_models[cache_key] = pipe
        
        return self.lora_models[cache_key]
    
    def get_lora_style_output(self, user_id: int, user_query: str, model_path: str = None) -> str:
        """
        Get style-adapted output from local LoRA model
        
        Args:
            user_id: User ID
            user_query: User's query
            model_path: Path to LoRA model
        
        Returns:
            Style-adapted output
        """
        if not model_path:
            # Get user's default LoRA model
            model_path = self.user_service.get_user_lora_model(user_id)
        
        if not model_path:
            # Fallback to base model behavior
            return f"Style: User prefers concise, technical responses."
        
        try:
            lora_pipe = self.load_lora_model(user_id, model_path)
            
            # Generate style output
            style_prompt = f"Style adaptation for: {user_query}"
            output = lora_pipe(
                style_prompt,
                max_new_tokens=256,
                do_sample=True,
                temperature=0.7,
                pad_token_id=lora_pipe.tokenizer.eos_token_id
            )
            
            return output[0]["generated_text"]
            
        except Exception as e:
            print(f"⚠️ LoRA generation failed: {e}")
            return f"Style: User prefers concise, technical responses."
    
    def get_rag_context(self, user_id: int, user_query: str, n_results: int = 5) -> str:
        """
        Retrieve relevant context from RAG knowledge base
        
        Args:
            user_id: User ID
            user_query: User's query
            n_results: Number of results to retrieve
        
        Returns:
            Retrieved context
        """
        try:
            # Get user's knowledge base collection
            collection_name = f"user_{user_id}_kb"
            
            # Query ChromaDB
            results = self.vector_client.query_collection(
                collection_name, 
                user_query, 
                n_results=n_results
            )
            
            if results:
                context_docs = [doc['document'] for doc in results]
                return "\n\n".join(context_docs)
            else:
                return "No relevant context found."
                
        except Exception as e:
            print(f"⚠️ RAG retrieval failed: {e}")
            return "No relevant context found."
    
    def build_hybrid_prompt(self, user_id: int, user_query: str, lora_model_path: str = None) -> List[Dict[str, str]]:
        """
        Build hybrid prompt combining LoRA style and RAG context
        
        Args:
            user_id: User ID
            user_query: User's query
            lora_model_path: Path to LoRA model
        
        Returns:
            Messages for external LLM
        """
        # Step 1: Get LoRA style output
        style_output = self.get_lora_style_output(user_id, user_query, lora_model_path)
        
        # Step 2: Get RAG context
        rag_context = self.get_rag_context(user_id, user_query)
        
        # Step 3: Build messages for external LLM
        messages = [
            {
                "role": "system",
                "content": f"""You are a hybrid AI assistant that combines:
1. User's personal style preferences: {style_output}
2. Relevant knowledge context: {rag_context}

Please provide a response that incorporates both the user's preferred style and the relevant context."""
            },
            {
                "role": "user",
                "content": user_query
            }
        ]
        
        return messages
    
    def query_external_llm(self, user_id: int, provider_name: str, model_name: str, 
                          user_query: str, lora_model_path: str = None, 
                          stream: bool = False, **kwargs) -> str | Generator[str, None, None]:
        """
        Query external LLM through hybrid pipeline
        
        Args:
            user_id: User ID
            provider_name: LLM provider name
            model_name: Model name
            user_query: User's query
            lora_model_path: Path to LoRA model
            stream: Whether to stream response
            **kwargs: Additional parameters
        
        Returns:
            Response from external LLM
        """
        try:
            # Get API key for provider
            api_key = self.api_key_manager.get_api_key_for_provider(user_id, provider_name)
            
            # Get provider configuration
            provider_config = self.user_service.get_provider_config(user_id, provider_name)
            
            # Create provider
            provider = llm_router.get_provider(
                provider_name,
                api_key=api_key,
                model=model_name,
                **provider_config
            )
            
            # Build hybrid prompt
            messages = self.build_hybrid_prompt(user_id, user_query, lora_model_path)
            
            # Query external LLM
            if stream:
                return provider.chat_stream(messages, **kwargs)
            else:
                return provider.chat(messages, **kwargs)
                
        except Exception as e:
            print(f"❌ External LLM query failed: {e}")
            raise
    
    def get_available_providers(self) -> List[Dict[str, Any]]:
        """
        Get list of available providers
        
        Returns:
            List of provider information
        """
        providers = []
        for name in llm_router.list_providers():
            try:
                info = llm_router.get_provider_info(name)
                providers.append(info)
            except Exception as e:
                print(f"⚠️ Could not get info for provider {name}: {e}")
        
        return providers
```


---

## 4. Database Schema Updates

### 4.1 Dynamic Provider Configuration

```sql
-- Enhanced external model configurations with dynamic provider support
CREATE TABLE external_model_configs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    provider TEXT NOT NULL,  -- 'openai', 'anthropic', 'nvidia', 'huggingface', 'ollama', 'cohere'
    model_id TEXT NOT NULL,  -- Model identifier for the provider
    api_key_encrypted TEXT NOT NULL,  -- Encrypted API key
    base_url TEXT,  -- Custom base URL (for Hugging Face, custom endpoints)
    is_active BOOLEAN DEFAULT TRUE,
    is_shared BOOLEAN DEFAULT FALSE,
    provider_config TEXT,  -- JSON configuration specific to provider
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Provider capabilities and requirements
CREATE TABLE provider_capabilities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider_name TEXT UNIQUE NOT NULL,
    display_name TEXT NOT NULL,
    description TEXT,
    requires_api_key BOOLEAN DEFAULT TRUE,
    requires_base_url BOOLEAN DEFAULT FALSE,
    supports_streaming BOOLEAN DEFAULT TRUE,
    default_models TEXT,  -- JSON array of default models
    config_schema TEXT,  -- JSON schema for provider-specific config
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert provider capabilities
INSERT INTO provider_capabilities (provider_name, display_name, description, requires_api_key, requires_base_url, supports_streaming, default_models, config_schema) VALUES
('openai', 'OpenAI', 'OpenAI GPT models', TRUE, FALSE, TRUE, '["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]', '{}'),
('anthropic', 'Anthropic', 'Anthropic Claude models', TRUE, FALSE, TRUE, '["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"]', '{}'),
('nvidia', 'NVIDIA', 'NVIDIA NIM models', TRUE, TRUE, TRUE, '["nvidia/llama-3.3-nemotron-super-49b-v1.5", "nvidia/llama-3.3-nemotron-8b-v1.5"]', '{"base_url": "https://integrate.api.nvidia.com/v1"}'),
('huggingface', 'Hugging Face', 'Hugging Face Inference API', TRUE, TRUE, FALSE, '[]', '{"base_url": "https://api-inference.huggingface.co/models/"}'),
('ollama', 'Ollama', 'Local Ollama server', FALSE, TRUE, TRUE, '["llama3", "mistral", "codellama"]', '{"base_url": "http://localhost:11434"}'),
('cohere', 'Cohere', 'Cohere Command models', TRUE, FALSE, FALSE, '["command-r-plus", "command-r"]', '{}');

-- User LoRA model configurations
CREATE TABLE user_lora_models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    model_path TEXT NOT NULL,
    base_model TEXT NOT NULL,
    training_job_id INTEGER,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (training_job_id) REFERENCES training_jobs (id)
);

-- Hybrid training jobs with dynamic provider support
CREATE TABLE hybrid_training_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    job_id INTEGER REFERENCES training_jobs(id),
    lora_model_id INTEGER REFERENCES user_lora_models(id),
    rag_collection_name TEXT,
    external_model_config_id INTEGER REFERENCES external_model_configs(id),
    status TEXT DEFAULT 'PENDING',
    progress REAL DEFAULT 0.0,
    error_message TEXT,
    test_results TEXT,  -- JSON test results
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Model usage tracking
CREATE TABLE model_usage_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    provider TEXT NOT NULL,
    model_name TEXT NOT NULL,
    query_text TEXT,
    response_length INTEGER,
    tokens_used INTEGER,
    cost_estimate REAL,
    response_time REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
```

### 4.2 Enhanced User Service

```python
# backend/services/enhanced_user_service.py
from typing import Dict, Any, List, Optional
from .user_service import UserService

class EnhancedUserService(UserService):
    """
    Enhanced user service with dynamic provider support
    """
    
    def __init__(self):
        super().__init__()
    
    def get_user_lora_model(self, user_id: int) -> Optional[str]:
        """Get user's default LoRA model path"""
        try:
            result = self.db.execute(
                "SELECT model_path FROM user_lora_models WHERE user_id = ? AND is_default = TRUE",
                (user_id,)
            ).fetchone()
            
            return result[0] if result else None
        except Exception as e:
            print(f"Error getting user LoRA model: {e}")
            return None
    
    def get_user_lora_models(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all LoRA models for user"""
        try:
            results = self.db.execute(
                "SELECT * FROM user_lora_models WHERE user_id = ? ORDER BY created_at DESC",
                (user_id,)
            ).fetchall()
            
            models = []
            for row in results:
                models.append({
                    'id': row[0],
                    'name': row[2],
                    'model_path': row[3],
                    'base_model': row[4],
                    'training_job_id': row[5],
                    'is_default': bool(row[6]),
                    'created_at': row[7]
                })
            
            return models
        except Exception as e:
            print(f"Error getting user LoRA models: {e}")
            return []
    
    def set_default_lora_model(self, user_id: int, model_id: int) -> bool:
        """Set default LoRA model for user"""
        try:
            # First, unset all defaults
            self.db.execute(
                "UPDATE user_lora_models SET is_default = FALSE WHERE user_id = ?",
                (user_id,)
            )
            
            # Set new default
            self.db.execute(
                "UPDATE user_lora_models SET is_default = TRUE WHERE id = ? AND user_id = ?",
                (model_id, user_id)
            )
            
            self.db.commit()
            return True
        except Exception as e:
            print(f"Error setting default LoRA model: {e}")
            return False
    
    def get_provider_config(self, user_id: int, provider_name: str) -> Dict[str, Any]:
        """Get provider configuration for user"""
        try:
            result = self.db.execute(
                "SELECT provider_config FROM external_model_configs WHERE user_id = ? AND provider = ? AND is_active = TRUE",
                (user_id, provider_name)
            ).fetchone()
            
            if result and result[0]:
                import json
                return json.loads(result[0])
            else:
                return {}
        except Exception as e:
            print(f"Error getting provider config: {e}")
            return {}
    
    def get_provider_capabilities(self) -> List[Dict[str, Any]]:
        """Get all provider capabilities"""
        try:
            results = self.db.execute(
                "SELECT * FROM provider_capabilities ORDER BY display_name"
            ).fetchall()
            
            capabilities = []
            for row in results:
                import json
                capabilities.append({
                    'provider_name': row[1],
                    'display_name': row[2],
                    'description': row[3],
                    'requires_api_key': bool(row[4]),
                    'requires_base_url': bool(row[5]),
                    'supports_streaming': bool(row[6]),
                    'default_models': json.loads(row[7]) if row[7] else [],
                    'config_schema': json.loads(row[8]) if row[8] else {}
                })
            
            return capabilities
        except Exception as e:
            print(f"Error getting provider capabilities: {e}")
            return []
    
    def log_model_usage(self, user_id: int, provider: str, model_name: str, 
                       query_text: str, response_length: int, tokens_used: int = 0,
                       cost_estimate: float = 0.0, response_time: float = 0.0):
        """Log model usage for analytics"""
        try:
            self.db.execute(
                """INSERT INTO model_usage_logs 
                   (user_id, provider, model_name, query_text, response_length, 
                    tokens_used, cost_estimate, response_time) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (user_id, provider, model_name, query_text, response_length,
                 tokens_used, cost_estimate, response_time)
            )
            self.db.commit()
        except Exception as e:
            print(f"Error logging model usage: {e}")
```

---

## 5. Service Architecture

### 5.1 Dynamic External Model Service

```python
# backend/services/dynamic_external_model_service.py
from typing import Dict, Any, List, Optional, Generator
from .hybrid_pipeline_service import HybridPipelineService
from .enhanced_user_service import EnhancedUserService
from .llm_router import llm_router

class DynamicExternalModelService:
    """
    Dynamic external model service with plugin-based architecture
    """
    
    def __init__(self, user_service: EnhancedUserService, api_key_manager):
        self.user_service = user_service
        self.api_key_manager = api_key_manager
        self.hybrid_pipeline = HybridPipelineService(user_service, api_key_manager)
    
    def get_available_providers(self) -> List[Dict[str, Any]]:
        """Get all available providers with capabilities"""
        # Get built-in providers from router
        router_providers = self.hybrid_pipeline.get_available_providers()
        
        # Get database capabilities
        db_capabilities = self.user_service.get_provider_capabilities()
        
        # Merge information
        providers = []
        for router_provider in router_providers:
            # Find matching capability info
            capability = next(
                (cap for cap in db_capabilities if cap['provider_name'] == router_provider['name']),
                None
            )
            
            provider_info = {
                'name': router_provider['name'],
                'class': router_provider['class'],
                'module': router_provider['module']
            }
            
            if capability:
                provider_info.update(capability)
            
            providers.append(provider_info)
        
        return providers
    
    def create_provider_config(self, user_id: int, config_data: Dict[str, Any]) -> int:
        """Create new provider configuration"""
        try:
            # Validate provider exists
            available_providers = [p['name'] for p in self.get_available_providers()]
            if config_data['provider'] not in available_providers:
                raise ValueError(f"Unknown provider: {config_data['provider']}")
            
            # Encrypt API key
            encrypted_key = self.api_key_manager.encrypt_api_key(config_data.get('api_key'))
            
            # Prepare config
            config = {
                'user_id': user_id,
                'name': config_data['name'],
                'provider': config_data['provider'],
                'model_id': config_data['model_id'],
                'api_key_encrypted': encrypted_key,
                'base_url': config_data.get('base_url'),
                'provider_config': config_data.get('provider_config', {}),
                'is_active': True
            }
            
            # Insert into database
            config_id = self.user_service.db.add_external_model_config(config)
            
            return config_id
            
        except Exception as e:
            print(f"Error creating provider config: {e}")
            raise
    
    def test_provider_connection(self, user_id: int, config_id: int) -> Dict[str, Any]:
        """Test provider connection"""
        try:
            # Get config
            config = self.user_service.db.get_external_model_config(config_id)
            if not config or config['user_id'] != user_id:
                raise ValueError("Config not found or unauthorized")
            
            # Decrypt API key
            api_key = self.api_key_manager.decrypt_api_key(config['api_key_encrypted'])
            
            # Create provider
            provider = llm_router.get_provider(
                config['provider'],
                api_key=api_key,
                model=config['model_id'],
                base_url=config.get('base_url')
            )
            
            # Test with simple message
            test_messages = [
                {"role": "user", "content": "Hello, this is a test message."}
            ]
            
            response = provider.chat(test_messages, max_tokens=50)
            
            return {
                'success': True,
                'response': response,
                'provider': config['provider'],
                'model': config['model_id']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'provider': config.get('provider', 'unknown'),
                'model': config.get('model_id', 'unknown')
            }
    
    def query_hybrid_model(self, user_id: int, provider_name: str, model_name: str,
                          user_query: str, lora_model_path: str = None,
                          stream: bool = False, **kwargs) -> str | Generator[str, None, None]:
        """Query hybrid model with dynamic provider"""
        try:
            # Get user's config for provider
            config = self.user_service.db.get_external_model_config_by_provider(
                user_id, provider_name
            )
            
            if not config:
                raise ValueError(f"No configuration found for provider: {provider_name}")
            
            # Query through hybrid pipeline
            response = self.hybrid_pipeline.query_external_llm(
                user_id=user_id,
                provider_name=provider_name,
                model_name=model_name,
                user_query=user_query,
                lora_model_path=lora_model_path,
                stream=stream,
                **kwargs
            )
            
            # Log usage
            if not stream:
                self.user_service.log_model_usage(
                    user_id=user_id,
                    provider=provider_name,
                    model_name=model_name,
                    query_text=user_query,
                    response_length=len(response) if isinstance(response, str) else 0
                )
            
            return response
            
        except Exception as e:
            print(f"Error querying hybrid model: {e}")
            raise
    
    def get_user_models(self, user_id: int) -> Dict[str, Any]:
        """Get all models accessible to user"""
        try:
            # Get external model configs
            external_configs = self.user_service.db.get_external_model_configs_by_user(user_id)
            
            # Get LoRA models
            lora_models = self.user_service.get_user_lora_models(user_id)
            
            # Get hybrid training jobs
            hybrid_jobs = self.user_service.db.get_hybrid_training_jobs_by_user(user_id)
            
            return {
                'external_configs': external_configs,
                'lora_models': lora_models,
                'hybrid_jobs': hybrid_jobs
            }
            
        except Exception as e:
            print(f"Error getting user models: {e}")
            return {
                'external_configs': [],
                'lora_models': [],
                'hybrid_jobs': []
            }
    
    def create_hybrid_training_job(self, user_id: int, job_data: Dict[str, Any]) -> int:
        """Create hybrid training job"""
        try:
            # Validate required fields
            required_fields = ['name', 'provider', 'model_id']
            for field in required_fields:
                if field not in job_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Get or create external model config
            config = self.user_service.db.get_external_model_config_by_provider(
                user_id, job_data['provider']
            )
            
            if not config:
                # Create new config
                config_data = {
                    'name': f"{job_data['name']} Config",
                    'provider': job_data['provider'],
                    'model_id': job_data['model_id'],
                    'api_key': job_data.get('api_key'),
                    'base_url': job_data.get('base_url')
                }
                config_id = self.create_provider_config(user_id, config_data)
            else:
                config_id = config['id']
            
            # Create hybrid job record
            hybrid_job_data = {
                'user_id': user_id,
                'name': job_data['name'],
                'description': job_data.get('description', ''),
                'external_model_config_id': config_id,
                'status': 'PENDING'
            }
            
            hybrid_job_id = self.user_service.db.create_hybrid_training_job(hybrid_job_data)
            
            return hybrid_job_id
            
        except Exception as e:
            print(f"Error creating hybrid training job: {e}")
            raise
```

---

## 6. API Endpoints

### 6.1 Provider Management Endpoints

```python
# Get available providers
@app.route('/api/providers', methods=['GET'])
@require_auth
def get_available_providers():
    """Get all available LLM providers with capabilities"""
    try:
        providers = dynamic_external_service.get_available_providers()
        return jsonify({'success': True, 'providers': providers}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Get provider capabilities
@app.route('/api/providers/<provider_name>/capabilities', methods=['GET'])
@require_auth
def get_provider_capabilities(provider_name):
    """Get capabilities for specific provider"""
    try:
        capabilities = user_service.get_provider_capabilities()
        provider_cap = next(
            (cap for cap in capabilities if cap['provider_name'] == provider_name),
            None
        )
        
        if not provider_cap:
            return jsonify({'error': 'Provider not found'}), 404
        
        return jsonify({'success': True, 'capabilities': provider_cap}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Test provider connection
@app.route('/api/providers/test', methods=['POST'])
@require_auth
@require_permission('external_apis', 'read')
def test_provider_connection():
    """Test connection to a provider"""
    user_id = g.user['user_id']
    data = request.get_json()
    
    try:
        config_id = data.get('config_id')
        if not config_id:
            return jsonify({'error': 'config_id is required'}), 400
        
        result = dynamic_external_service.test_provider_connection(user_id, config_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
```

### 6.2 Dynamic Model Query Endpoints

```python
# Query any provider dynamically
@app.route('/api/query/<provider_name>/<model_name>', methods=['POST'])
@require_auth
@require_permission('models', 'read')
def query_dynamic_model(provider_name, model_name):
    """Query any provider model dynamically"""
    user_id = g.user['user_id']
    data = request.get_json()
    
    try:
        user_query = data.get('query')
        if not user_query:
            return jsonify({'error': 'query is required'}), 400
        
        stream = data.get('stream', False)
        lora_model_path = data.get('lora_model_path')
        
        # Query through hybrid pipeline
        response = dynamic_external_service.query_hybrid_model(
            user_id=user_id,
            provider_name=provider_name,
            model_name=model_name,
            user_query=user_query,
            lora_model_path=lora_model_path,
            stream=stream,
            temperature=data.get('temperature', 0.7),
            max_tokens=data.get('max_tokens', 1024)
        )
        
        if stream:
            def generate():
                for chunk in response:
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            
            return Response(generate(), mimetype='text/event-stream')
        else:
            return jsonify({'success': True, 'response': response}), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Get user's available models
@app.route('/api/user-models', methods=['GET'])
@require_auth
def get_user_models():
    """Get all models available to user"""
    user_id = g.user['user_id']
    
    try:
        models = dynamic_external_service.get_user_models(user_id)
        return jsonify({'success': True, 'models': models}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
```

### 6.3 LoRA Model Management Endpoints

```python
# Get user's LoRA models
@app.route('/api/lora-models', methods=['GET'])
@require_auth
def get_user_lora_models():
    """Get user's LoRA models"""
    user_id = g.user['user_id']
    
    try:
        models = user_service.get_user_lora_models(user_id)
        return jsonify({'success': True, 'models': models}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Set default LoRA model
@app.route('/api/lora-models/<int:model_id>/set-default', methods=['POST'])
@require_auth
@require_permission('models', 'update')
def set_default_lora_model(model_id):
    """Set default LoRA model for user"""
    user_id = g.user['user_id']
    
    try:
        success = user_service.set_default_lora_model(user_id, model_id)
        if success:
            return jsonify({'success': True}), 200
        else:
            return jsonify({'error': 'Failed to set default model'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400
```

---

## 7. Frontend Integration

### 7.1 Dynamic Provider Selector Component

```vue
<!-- frontend/src/components/providers/ProviderSelector.vue -->
<template>
    <div class="provider-selector">
        <h3>Select LLM Provider</h3>
        
        <div class="provider-grid">
            <div 
                v-for="provider in providers" 
                :key="provider.name"
                class="provider-card"
                :class="{ 'selected': selectedProvider?.name === provider.name }"
                @click="selectProvider(provider)"
            >
                <div class="provider-icon">
                    <i :class="getProviderIcon(provider.name)"></i>
                </div>
                
                <h4>{{ provider.display_name }}</h4>
                <p>{{ provider.description }}</p>
                
                <div class="provider-features">
                    <span v-if="provider.supports_streaming" class="feature">Streaming</span>
                    <span v-if="!provider.requires_api_key" class="feature">Free</span>
                </div>
                
                <div class="provider-models">
                    <small>Models: {{ provider.default_models.length }}</small>
                </div>
            </div>
        </div>
        
        <div v-if="selectedProvider" class="provider-config">
            <h4>Configure {{ selectedProvider.display_name }}</h4>
            
            <form @submit.prevent="saveProviderConfig">
                <div class="form-group">
                    <label>Configuration Name</label>
                    <input v-model="configForm.name" required />
                </div>
                
                <div class="form-group">
                    <label>Model</label>
                    <select v-model="configForm.model_id" required>
                        <option v-for="model in selectedProvider.default_models" :key="model" :value="model">
                            {{ model }}
                        </option>
                    </select>
                </div>
                
                <div v-if="selectedProvider.requires_api_key" class="form-group">
                    <label>API Key</label>
                    <input type="password" v-model="configForm.api_key" required />
                </div>
                
                <div v-if="selectedProvider.requires_base_url" class="form-group">
                    <label>Base URL</label>
                    <input v-model="configForm.base_url" :placeholder="selectedProvider.config_schema.base_url" />
                </div>
                
                <button type="submit" class="btn-primary">Save Configuration</button>
            </form>
        </div>
    </div>
</template>

<script>
import { authService } from '@/services/auth';

export default {
    name: 'ProviderSelector',
    data() {
        return {
            providers: [],
            selectedProvider: null,
            configForm: {
                name: '',
                model_id: '',
                api_key: '',
                base_url: ''
            }
        };
    },
    async mounted() {
        await this.loadProviders();
    },
    methods: {
        async loadProviders() {
            const response = await fetch('/api/providers', {
                headers: authService.getAuthHeaders()
            });
            
            const data = await response.json();
            if (data.success) {
                this.providers = data.providers;
            }
        },
        
        selectProvider(provider) {
            this.selectedProvider = provider;
            this.configForm.model_id = provider.default_models[0] || '';
            this.configForm.base_url = provider.config_schema.base_url || '';
        },
        
        getProviderIcon(providerName) {
            const icons = {
                'openai': 'fab fa-openai',
                'anthropic': 'fas fa-robot',
                'nvidia': 'fas fa-microchip',
                'huggingface': 'fas fa-heart',
                'ollama': 'fas fa-server',
                'cohere': 'fas fa-brain'
            };
            return icons[providerName] || 'fas fa-cube';
        },
        
        async saveProviderConfig() {
            const configData = {
                ...this.configForm,
                provider: this.selectedProvider.name
            };
            
            const response = await fetch('/api/external-models', {
                method: 'POST',
                headers: authService.getAuthHeaders(),
                body: JSON.stringify(configData)
            });
            
            if (response.ok) {
                this.$emit('config-saved');
                this.resetForm();
            }
        },
        
        resetForm() {
            this.selectedProvider = null;
            this.configForm = {
                name: '',
                model_id: '',
                api_key: '',
                base_url: ''
            };
        }
    }
};
</script>
```

### 7.2 Dynamic Model Query Interface

```vue
<!-- frontend/src/components/query/DynamicModelQuery.vue -->
<template>
    <div class="dynamic-model-query">
        <h2>Query Any LLM Provider</h2>
        
        <div class="query-form">
            <div class="form-row">
                <div class="form-group">
                    <label>Provider</label>
                    <select v-model="queryForm.provider" @change="onProviderChange">
                        <option v-for="provider in providers" :key="provider.name" :value="provider.name">
                            {{ provider.display_name }}
                        </option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>Model</label>
                    <select v-model="queryForm.model" :disabled="!queryForm.provider">
                        <option v-for="model in availableModels" :key="model" :value="model">
                            {{ model }}
                        </option>
                    </select>
                </div>
            </div>
            
            <div class="form-group">
                <label>Query</label>
                <textarea 
                    v-model="queryForm.query" 
                    placeholder="Enter your query here..."
                    rows="4"
                ></textarea>
            </div>
            
            <div class="form-row">
                <div class="form-group">
                    <label>Temperature</label>
                    <input type="range" v-model.number="queryForm.temperature" min="0" max="2" step="0.1" />
                    <span>{{ queryForm.temperature }}</span>
                </div>
                
                <div class="form-group">
                    <label>Max Tokens</label>
                    <input type="number" v-model.number="queryForm.max_tokens" min="1" max="4096" />
                </div>
            </div>
            
            <div class="form-group">
                <label>
                    <input type="checkbox" v-model="queryForm.stream" />
                    Stream Response
                </label>
            </div>
            
            <button @click="submitQuery" :disabled="loading" class="btn-primary">
                {{ loading ? 'Querying...' : 'Query Model' }}
            </button>
        </div>
        
        <div v-if="response" class="response-section">
            <h3>Response</h3>
            <div class="response-content">
                <pre v-if="!queryForm.stream">{{ response }}</pre>
                <div v-else class="streaming-response">
                    <div v-for="(chunk, index) in responseChunks" :key="index" class="chunk">
                        {{ chunk }}
                    </div>
                </div>
            </div>
        </div>
        
        <div v-if="error" class="error-message">
            {{ error }}
        </div>
    </div>
</template>

<script>
import { authService } from '@/services/auth';

export default {
    name: 'DynamicModelQuery',
    data() {
        return {
            providers: [],
            queryForm: {
                provider: '',
                model: '',
                query: '',
                temperature: 0.7,
                max_tokens: 1024,
                stream: false
            },
            response: '',
            responseChunks: [],
            loading: false,
            error: null
        };
    },
    computed: {
        availableModels() {
            const provider = this.providers.find(p => p.name === this.queryForm.provider);
            return provider ? provider.default_models : [];
        }
    },
    async mounted() {
        await this.loadProviders();
    },
    methods: {
        async loadProviders() {
            const response = await fetch('/api/providers', {
                headers: authService.getAuthHeaders()
            });
            
            const data = await response.json();
            if (data.success) {
                this.providers = data.providers;
            }
        },
        
        onProviderChange() {
            this.queryForm.model = this.availableModels[0] || '';
        },
        
        async submitQuery() {
            if (!this.queryForm.provider || !this.queryForm.model || !this.queryForm.query) {
                this.error = 'Please fill in all required fields';
                return;
            }
            
            this.loading = true;
            this.error = null;
            this.response = '';
            this.responseChunks = [];
            
            try {
                if (this.queryForm.stream) {
                    await this.streamQuery();
                } else {
                    await this.regularQuery();
                }
            } catch (err) {
                this.error = err.message;
            } finally {
                this.loading = false;
            }
        },
        
        async regularQuery() {
            const response = await fetch(`/api/query/${this.queryForm.provider}/${this.queryForm.model}`, {
                method: 'POST',
                headers: authService.getAuthHeaders(),
                body: JSON.stringify(this.queryForm)
            });
            
            const data = await response.json();
            if (data.success) {
                this.response = data.response;
            } else {
                throw new Error(data.error);
            }
        },
        
        async streamQuery() {
            const response = await fetch(`/api/query/${this.queryForm.provider}/${this.queryForm.model}`, {
                method: 'POST',
                headers: authService.getAuthHeaders(),
                body: JSON.stringify(this.queryForm)
            });
            
            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.error);
            }
            
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                
                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');
                
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.slice(6));
                            this.responseChunks.push(data.chunk);
                        } catch (e) {
                            // Ignore malformed JSON
                        }
                    }
                }
            }
        }
    }
};
</script>
```


---

## 8. Implementation Phases

### 📊 **Current Status Summary:**
- **Phase 1**: ✅ **COMPLETED** - Dynamic LLM Router Foundation
- **Phase 2**: 🔄 **IN PROGRESS** - Extended Provider Support  
- **Phase 3**: ⏳ **NEXT** - Hybrid Pipeline Integration
- **Phase 4**: ✅ **PARTIALLY COMPLETED** - Database and User Management
- **Phase 5**: ✅ **PARTIALLY COMPLETED** - API and Service Layer
- **Phase 6**: ✅ **PARTIALLY COMPLETED** - Frontend Integration
- **Phase 7**: ⏳ **PENDING** - Testing and Optimization
- **Phase 8**: ⏳ **PENDING** - Deployment and Documentation

### 🎯 **Next Priority:**
**Phase 3: Hybrid Pipeline Integration** - This is the core functionality that combines LoRA + RAG + External LLM

### Phase 1: Dynamic LLM Router Foundation (Week 1-2) ✅ COMPLETED

**Tasks:**
1. ✅ Create base provider interface and abstract class
2. ✅ Implement plugin-based provider system
3. ✅ Build dynamic router with provider registration
4. ✅ Create provider factory and caching system
5. ✅ Implement basic providers (OpenAI, Anthropic, NVIDIA)
6. ✅ Add provider validation and error handling

**Deliverables:**
- ✅ Base LLM provider interface (`backend/services/llm_providers/base.py`)
- ✅ Dynamic router with plugin system (`backend/services/llm_providers/llm_router.py`)
- ✅ Basic provider implementations (OpenAI, Anthropic, NVIDIA)
- ✅ Provider registration and management
- ✅ Database schema extensions (`backend/services/database_extensions.py`)
- ✅ API endpoints (`backend/services/provider_endpoints.py`)
- ✅ Frontend interface (`frontend/src/views/BaseModelProviders.vue`)
- ✅ RBAC integration (admin/superuser/developer access)

### Phase 2: Extended Provider Support (Week 3-4) 🔄 IN PROGRESS

**Tasks:**
1. 🔄 Implement Hugging Face Inference API provider
2. 🔄 Add Ollama local server provider
3. 🔄 Create Cohere API provider
4. ⏳ Add vLLM and TGI provider support
5. ⏳ Implement streaming support for all providers
6. ⏳ Add provider-specific configuration schemas

**Deliverables:**
- ⏳ Complete provider ecosystem
- ⏳ Streaming support across all providers
- ⏳ Provider configuration management
- ⏳ Error handling and fallbacks

### Phase 3: Hybrid Pipeline Integration (Week 5-6) ⏳ NEXT

**Tasks:**
1. ⏳ Integrate LoRA model loading and inference
2. ⏳ Connect ChromaDB RAG system
3. ⏳ Build hybrid prompt construction
4. ⏳ Implement pipeline orchestration
5. ⏳ Add LoRA model caching and management
6. ⏳ Create pipeline testing and validation

**Deliverables:**
- ⏳ Complete hybrid pipeline
- ⏳ LoRA + RAG + External LLM integration
- ⏳ Pipeline testing framework
- ⏳ Performance optimization

### Phase 4: Database and User Management (Week 7-8) ✅ PARTIALLY COMPLETED

**Tasks:**
1. ✅ Create enhanced database schema
2. ✅ Implement provider capabilities system
3. ⏳ Add user LoRA model management
4. ⏳ Create model usage tracking
5. ✅ Implement provider configuration storage
6. ✅ Add user-specific model access control

**Deliverables:**
- ✅ Enhanced database schema (`backend/services/database_extensions.py`)
- ⏳ User model management
- ⏳ Usage tracking and analytics
- ✅ Access control system (RBAC integration)

### Phase 5: API and Service Layer (Week 9-10) ✅ PARTIALLY COMPLETED

**Tasks:**
1. ⏳ Create dynamic external model service
2. ✅ Implement provider management endpoints
3. ⏳ Add dynamic model query endpoints
4. ⏳ Create LoRA model management APIs
5. ✅ Implement connection testing
6. ⏳ Add usage analytics endpoints

**Deliverables:**
- ⏳ Complete API layer
- ✅ Dynamic provider management (`backend/services/provider_endpoints.py`)
- ⏳ Model querying system
- ⏳ Analytics and monitoring

### Phase 6: Frontend Integration (Week 11-12) ✅ PARTIALLY COMPLETED

**Tasks:**
1. ✅ Create dynamic provider selector component
2. ⏳ Build model query interface
3. ⏳ Add LoRA model management UI
4. ⏳ Implement streaming response display
5. ✅ Create provider configuration forms
6. ⏳ Add usage analytics dashboard

**Deliverables:**
- ⏳ Complete frontend interface
- ✅ Dynamic provider selection (`frontend/src/views/BaseModelProviders.vue`)
- ⏳ Real-time querying
- ✅ User-friendly configuration (TabbedModal component)

### Phase 7: Testing and Optimization (Week 13-14)

**Tasks:**
1. Write comprehensive unit tests
2. Create integration tests for all providers
3. Perform load testing and optimization
4. Add error handling and recovery
5. Implement caching and performance tuning
6. Create monitoring and alerting

**Deliverables:**
- Complete test suite
- Performance optimization
- Monitoring system
- Error recovery mechanisms

### Phase 8: Deployment and Documentation (Week 15-16)

**Tasks:**
1. Create deployment scripts and configuration
2. Write comprehensive documentation
3. Create user guides and tutorials
4. Implement backup and recovery
5. Add security hardening
6. Deploy to production environment

**Deliverables:**
- Production deployment
- Complete documentation
- User guides
- Security implementation

---

## 9. Configuration and Environment

### 9.1 Environment Variables

```bash
# .env configuration for dynamic LLM system

# Database
DATABASE_PATH=backend/ai_dashboard.db

# JWT Authentication
JWT_SECRET=your-super-secret-jwt-key-change-this
JWT_ALGORITHM=HS256
JWT_EXPIRY_DAYS=7

# API Key Encryption
API_KEY_ENCRYPTION_KEY=your-fernet-encryption-key-change-this
API_KEY_SALT=ai-refinement-salt-change-this

# Provider Defaults
OPENAI_BASE_URL=https://api.openai.com/v1
ANTHROPIC_BASE_URL=https://api.anthropic.com
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
HUGGINGFACE_BASE_URL=https://api-inference.huggingface.co/models
OLLAMA_BASE_URL=http://localhost:11434
COHERE_BASE_URL=https://api.cohere.ai

# LoRA Model Settings
LORA_MODEL_CACHE_SIZE=10
LORA_MODEL_CACHE_TTL=3600
DEFAULT_LORA_BASE_MODEL=microsoft/DialoGPT-medium

# RAG Settings
CHROMADB_PATH=backend/chromadb_data
RAG_EMBEDDING_MODEL=all-MiniLM-L6-v2
RAG_DEFAULT_RESULTS=5

# Performance Settings
PROVIDER_CACHE_SIZE=20
PROVIDER_CACHE_TTL=1800
MAX_CONCURRENT_REQUESTS=10
REQUEST_TIMEOUT=60

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_DEFAULT_REQUESTS=100
RATE_LIMIT_DEFAULT_WINDOW=60
RATE_LIMIT_QUERY_REQUESTS=50
RATE_LIMIT_QUERY_WINDOW=60

# Logging
LOG_LEVEL=INFO
AUDIT_LOG_ENABLED=true
AUDIT_LOG_PATH=backend/logs/audit.log
PROVIDER_LOG_ENABLED=true
PROVIDER_LOG_PATH=backend/logs/providers.log

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Session
SESSION_TIMEOUT=1800  # 30 minutes
```

### 9.2 Provider Configuration Schema

```json
{
  "providers": {
    "openai": {
      "display_name": "OpenAI",
      "description": "OpenAI GPT models",
      "requires_api_key": true,
      "requires_base_url": false,
      "supports_streaming": true,
      "default_models": [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-3.5-turbo"
      ],
      "config_schema": {
        "type": "object",
        "properties": {
          "temperature": {
            "type": "number",
            "minimum": 0,
            "maximum": 2,
            "default": 0.7
          },
          "max_tokens": {
            "type": "integer",
            "minimum": 1,
            "maximum": 4096,
            "default": 1024
          }
        }
      }
    },
    "anthropic": {
      "display_name": "Anthropic",
      "description": "Anthropic Claude models",
      "requires_api_key": true,
      "requires_base_url": false,
      "supports_streaming": true,
      "default_models": [
        "claude-3-5-sonnet-20241022",
        "claude-3-haiku-20240307"
      ],
      "config_schema": {
        "type": "object",
        "properties": {
          "temperature": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "default": 0.7
          },
          "max_tokens": {
            "type": "integer",
            "minimum": 1,
            "maximum": 4096,
            "default": 1024
          }
        }
      }
    },
    "nvidia": {
      "display_name": "NVIDIA",
      "description": "NVIDIA NIM models",
      "requires_api_key": true,
      "requires_base_url": true,
      "supports_streaming": true,
      "default_models": [
        "nvidia/llama-3.3-nemotron-super-49b-v1.5",
        "nvidia/llama-3.3-nemotron-8b-v1.5"
      ],
      "config_schema": {
        "type": "object",
        "properties": {
          "base_url": {
            "type": "string",
            "default": "https://integrate.api.nvidia.com/v1"
          },
          "temperature": {
            "type": "number",
            "minimum": 0,
            "maximum": 2,
            "default": 0.7
          }
        }
      }
    },
    "huggingface": {
      "display_name": "Hugging Face",
      "description": "Hugging Face Inference API",
      "requires_api_key": true,
      "requires_base_url": true,
      "supports_streaming": false,
      "default_models": [],
      "config_schema": {
        "type": "object",
        "properties": {
          "base_url": {
            "type": "string",
            "pattern": "^https://api-inference\\.huggingface\\.co/models/.*"
          },
          "max_new_tokens": {
            "type": "integer",
            "minimum": 1,
            "maximum": 512,
            "default": 512
          }
        }
      }
    },
    "ollama": {
      "display_name": "Ollama",
      "description": "Local Ollama server",
      "requires_api_key": false,
      "requires_base_url": true,
      "supports_streaming": true,
      "default_models": [
        "llama3",
        "mistral",
        "codellama"
      ],
      "config_schema": {
        "type": "object",
        "properties": {
          "base_url": {
            "type": "string",
            "default": "http://localhost:11434"
          },
          "temperature": {
            "type": "number",
            "minimum": 0,
            "maximum": 2,
            "default": 0.7
          }
        }
      }
    },
    "cohere": {
      "display_name": "Cohere",
      "description": "Cohere Command models",
      "requires_api_key": true,
      "requires_base_url": false,
      "supports_streaming": false,
      "default_models": [
        "command-r-plus",
        "command-r"
      ],
      "config_schema": {
        "type": "object",
        "properties": {
          "temperature": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "default": 0.7
          }
        }
      }
    }
  }
}
```

---

## 10. Testing Strategy

### 10.1 Unit Tests

```python
# backend/tests/test_llm_router.py
import unittest
from unittest.mock import Mock, patch
from services.llm_router import LLMRouter
from services.llm_providers.base import LLMProvider

class TestLLMRouter(unittest.TestCase):
    def setUp(self):
        self.router = LLMRouter()
    
    def test_register_provider(self):
        """Test provider registration"""
        class TestProvider(LLMProvider):
            def chat(self, messages, **kwargs):
                return "test response"
            
            def chat_stream(self, messages, **kwargs):
                yield "test"
        
        self.router.register_provider("test", TestProvider)
        self.assertIn("test", self.router.list_providers())
    
    def test_create_provider(self):
        """Test provider creation"""
        provider = self.router.create_provider("openai", api_key="test-key")
        self.assertIsInstance(provider, LLMProvider)
    
    def test_get_provider_caching(self):
        """Test provider caching"""
        provider1 = self.router.get_provider("openai", api_key="test-key")
        provider2 = self.router.get_provider("openai", api_key="test-key")
        self.assertIs(provider1, provider2)
    
    def test_unknown_provider(self):
        """Test unknown provider error"""
        with self.assertRaises(ValueError):
            self.router.create_provider("unknown", api_key="test-key")

# backend/tests/test_hybrid_pipeline.py
import unittest
from unittest.mock import Mock, patch
from services.hybrid_pipeline_service import HybridPipelineService

class TestHybridPipelineService(unittest.TestCase):
    def setUp(self):
        self.user_service = Mock()
        self.api_key_manager = Mock()
        self.pipeline = HybridPipelineService(self.user_service, self.api_key_manager)
    
    @patch('services.hybrid_pipeline_service.chromadb_service')
    def test_get_rag_context(self, mock_chromadb):
        """Test RAG context retrieval"""
        mock_chromadb.query_collection.return_value = [
            {'document': 'Test document 1'},
            {'document': 'Test document 2'}
        ]
        
        context = self.pipeline.get_rag_context(1, "test query")
        
        self.assertIn("Test document 1", context)
        self.assertIn("Test document 2", context)
    
    @patch('services.hybrid_pipeline_service.AutoModelForCausalLM')
    @patch('services.hybrid_pipeline_service.AutoTokenizer')
    def test_load_lora_model(self, mock_tokenizer, mock_model):
        """Test LoRA model loading"""
        mock_tokenizer.from_pretrained.return_value = Mock()
        mock_model.from_pretrained.return_value = Mock()
        
        pipeline = self.pipeline.load_lora_model(1, "test/path")
        
        self.assertIsNotNone(pipeline)
        mock_tokenizer.from_pretrained.assert_called_once()
        mock_model.from_pretrained.assert_called_once()
```

### 10.2 Integration Tests

```python
# backend/tests/test_dynamic_external_service.py
import unittest
from unittest.mock import Mock, patch
from services.dynamic_external_model_service import DynamicExternalModelService

class TestDynamicExternalModelService(unittest.TestCase):
    def setUp(self):
        self.user_service = Mock()
        self.api_key_manager = Mock()
        self.service = DynamicExternalModelService(self.user_service, self.api_key_manager)
    
    def test_get_available_providers(self):
        """Test getting available providers"""
        providers = self.service.get_available_providers()
        
        self.assertIsInstance(providers, list)
        self.assertGreater(len(providers), 0)
        
        # Check provider structure
        for provider in providers:
            self.assertIn('name', provider)
            self.assertIn('display_name', provider)
            self.assertIn('description', provider)
    
    @patch('services.dynamic_external_model_service.llm_router')
    def test_test_provider_connection(self, mock_router):
        """Test provider connection testing"""
        # Mock database response
        self.user_service.db.get_external_model_config.return_value = {
            'user_id': 1,
            'provider': 'openai',
            'model_id': 'gpt-4o-mini',
            'api_key_encrypted': 'encrypted-key'
        }
        
        # Mock API key decryption
        self.api_key_manager.decrypt_api_key.return_value = 'test-key'
        
        # Mock provider
        mock_provider = Mock()
        mock_provider.chat.return_value = "Test response"
        mock_router.get_provider.return_value = mock_provider
        
        result = self.service.test_provider_connection(1, 1)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['response'], "Test response")
    
    def test_create_provider_config(self):
        """Test provider configuration creation"""
        config_data = {
            'name': 'Test Config',
            'provider': 'openai',
            'model_id': 'gpt-4o-mini',
            'api_key': 'test-key'
        }
        
        self.api_key_manager.encrypt_api_key.return_value = 'encrypted-key'
        self.user_service.db.add_external_model_config.return_value = 1
        
        config_id = self.service.create_provider_config(1, config_data)
        
        self.assertEqual(config_id, 1)
        self.api_key_manager.encrypt_api_key.assert_called_once_with('test-key')
```

### 10.3 End-to-End Tests

```python
# backend/tests/test_e2e_hybrid_pipeline.py
import unittest
import requests
import json
from unittest.mock import patch

class TestE2EHybridPipeline(unittest.TestCase):
    def setUp(self):
        self.base_url = "http://localhost:5000"
        self.headers = {
            "Authorization": "Bearer test-token",
            "Content-Type": "application/json"
        }
    
    @patch('services.dynamic_external_model_service.DynamicExternalModelService')
    def test_dynamic_model_query(self, mock_service):
        """Test end-to-end dynamic model query"""
        # Mock service response
        mock_service.query_hybrid_model.return_value = "Test response from hybrid model"
        
        # Test data
        query_data = {
            "query": "Test query",
            "temperature": 0.7,
            "max_tokens": 100
        }
        
        # Make request
        response = requests.post(
            f"{self.base_url}/api/query/openai/gpt-4o-mini",
            headers=self.headers,
            json=query_data
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['response'], "Test response from hybrid model")
    
    def test_provider_listing(self):
        """Test provider listing endpoint"""
        response = requests.get(
            f"{self.base_url}/api/providers",
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIsInstance(data['providers'], list)
        
        # Check provider structure
        for provider in data['providers']:
            self.assertIn('name', provider)
            self.assertIn('display_name', provider)
            self.assertIn('supports_streaming', provider)
```

---

## 11. Performance Optimization

### 11.1 Caching Strategy

```python
# backend/services/cache_service.py
import redis
import json
import hashlib
from typing import Any, Optional
from functools import wraps

class CacheService:
    """
    Caching service for providers and models
    """
    
    def __init__(self, redis_url: str = None):
        if redis_url:
            self.redis_client = redis.from_url(redis_url)
        else:
            # Fallback to in-memory cache
            self.redis_client = None
            self.memory_cache = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if self.redis_client:
            try:
                value = self.redis_client.get(key)
                return json.loads(value) if value else None
            except Exception:
                return None
        else:
            return self.memory_cache.get(key)
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache"""
        if self.redis_client:
            try:
                self.redis_client.setex(key, ttl, json.dumps(value))
            except Exception:
                pass
        else:
            self.memory_cache[key] = value
    
    def delete(self, key: str):
        """Delete value from cache"""
        if self.redis_client:
            try:
                self.redis_client.delete(key)
            except Exception:
                pass
        else:
            self.memory_cache.pop(key, None)
    
    def generate_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()

# Global cache service
cache_service = CacheService()

def cached(ttl: int = 3600):
    """Decorator for caching function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{cache_service.generate_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_result = cache_service.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_service.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator
```

### 11.2 Connection Pooling

```python
# backend/services/connection_pool.py
import asyncio
import aiohttp
from typing import Dict, Any
import time

class ConnectionPool:
    """
    Connection pool for external API calls
    """
    
    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self.sessions: Dict[str, aiohttp.ClientSession] = {}
        self.semaphore = asyncio.Semaphore(max_connections)
    
    async def get_session(self, base_url: str) -> aiohttp.ClientSession:
        """Get or create session for base URL"""
        if base_url not in self.sessions:
            connector = aiohttp.TCPConnector(
                limit=self.max_connections,
                limit_per_host=5,
                ttl_dns_cache=300,
                use_dns_cache=True
            )
            
            timeout = aiohttp.ClientTimeout(total=60)
            
            self.sessions[base_url] = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout
            )
        
        return self.sessions[base_url]
    
    async def close_all(self):
        """Close all sessions"""
        for session in self.sessions.values():
            await session.close()
        self.sessions.clear()

# Global connection pool
connection_pool = ConnectionPool()
```

### 11.3 Performance Monitoring

```python
# backend/services/performance_monitor.py
import time
import psutil
import threading
from typing import Dict, Any, List
from collections import defaultdict, deque

class PerformanceMonitor:
    """
    Performance monitoring for the dynamic LLM system
    """
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.lock = threading.Lock()
        self.start_time = time.time()
    
    def record_metric(self, metric_name: str, value: float, tags: Dict[str, str] = None):
        """Record a performance metric"""
        with self.lock:
            self.metrics[metric_name].append({
                'value': value,
                'timestamp': time.time(),
                'tags': tags or {}
            })
    
    def record_latency(self, operation: str, duration: float, provider: str = None):
        """Record operation latency"""
        tags = {'provider': provider} if provider else {}
        self.record_metric(f"{operation}_latency", duration, tags)
    
    def record_throughput(self, operation: str, count: int, provider: str = None):
        """Record operation throughput"""
        tags = {'provider': provider} if provider else {}
        self.record_metric(f"{operation}_throughput", count, tags)
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'uptime': time.time() - self.start_time
        }
    
    def get_metric_stats(self, metric_name: str, window: int = 300) -> Dict[str, float]:
        """Get statistics for a metric over time window"""
        with self.lock:
            now = time.time()
            recent_metrics = [
                m for m in self.metrics[metric_name]
                if now - m['timestamp'] <= window
            ]
            
            if not recent_metrics:
                return {}
            
            values = [m['value'] for m in recent_metrics]
            
            return {
                'count': len(values),
                'min': min(values),
                'max': max(values),
                'avg': sum(values) / len(values),
                'p95': sorted(values)[int(len(values) * 0.95)] if len(values) > 1 else values[0]
            }
    
    def get_provider_performance(self) -> Dict[str, Dict[str, Any]]:
        """Get performance metrics by provider"""
        provider_metrics = defaultdict(lambda: defaultdict(list))
        
        with self.lock:
            for metric_name, metrics in self.metrics.items():
                for metric in metrics:
                    if 'provider' in metric['tags']:
                        provider = metric['tags']['provider']
                        provider_metrics[provider][metric_name].append(metric['value'])
        
        result = {}
        for provider, metrics in provider_metrics.items():
            result[provider] = {}
            for metric_name, values in metrics.items():
                result[provider][metric_name] = {
                    'count': len(values),
                    'avg': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values)
                }
        
        return result

# Global performance monitor
performance_monitor = PerformanceMonitor()
```

---

## 12. Security Considerations

### 12.1 API Key Security

```python
# backend/services/secure_api_key_manager.py
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import os
import base64
import secrets

class SecureAPIKeyManager:
    """
    Enhanced API key management with additional security
    """
    
    def __init__(self):
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher = Fernet(self.encryption_key)
        self.salt = os.getenv('API_KEY_SALT', 'ai-refinement-salt').encode()
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key"""
        key_env = os.getenv('API_KEY_ENCRYPTION_KEY')
        
        if not key_env:
            if os.getenv('ENVIRONMENT') == 'production':
                raise RuntimeError("API_KEY_ENCRYPTION_KEY must be set in production")
            else:
                # Generate new key for development
                key = Fernet.generate_key()
                print(f"🔑 Generated new encryption key for development")
                print(f"⚠️ Add this to .env: API_KEY_ENCRYPTION_KEY={key.decode()}")
                return key
        
        return key_env.encode() if isinstance(key_env, str) else key_env
    
    def encrypt_api_key(self, api_key: str) -> str:
        """Encrypt API key with additional security"""
        if not api_key:
            return None
        
        # Add random padding to prevent pattern analysis
        padding = secrets.token_hex(16)
        padded_key = f"{api_key}:{padding}"
        
        encrypted = self.cipher.encrypt(padded_key.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt_api_key(self, encrypted_key: str) -> str:
        """Decrypt API key"""
        if not encrypted_key:
            return None
        
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_key.encode())
            decrypted = self.cipher.decrypt(encrypted_bytes)
            padded_key = decrypted.decode()
            
            # Remove padding
            api_key = padded_key.split(':')[0]
            return api_key
            
        except Exception as e:
            print(f"❌ Error decrypting API key: {e}")
            raise
    
    def rotate_encryption_key(self, new_key: str) -> bool:
        """Rotate encryption key (critical operation)"""
        try:
            # Validate new key
            test_cipher = Fernet(new_key.encode())
            test_cipher.encrypt(b"test")
            
            # Get all encrypted keys
            all_configs = db.get_all_external_configs()
            
            # Re-encrypt all keys
            for config in all_configs:
                decrypted = self.decrypt_api_key(config['api_key_encrypted'])
                new_encrypted = test_cipher.encrypt(decrypted.encode())
                new_encrypted_b64 = base64.urlsafe_b64encode(new_encrypted).decode()
                
                db.update_external_config(config['id'], {
                    'api_key_encrypted': new_encrypted_b64
                })
            
            # Update cipher
            self.cipher = test_cipher
            self.encryption_key = new_key.encode()
            
            return True
            
        except Exception as e:
            print(f"❌ Key rotation failed: {e}")
            return False
    
    def validate_api_key_format(self, provider: str, api_key: str) -> bool:
        """Validate API key format for specific provider"""
        if not api_key:
            return False
        
        # Provider-specific validation
        if provider == 'openai':
            return api_key.startswith('sk-')
        elif provider == 'anthropic':
            return api_key.startswith('sk-ant-')
        elif provider == 'nvidia':
            return api_key.startswith('nvapi-')
        elif provider == 'huggingface':
            return api_key.startswith('hf_')
        elif provider == 'cohere':
            return api_key.startswith('co-')
        elif provider == 'ollama':
            return True  # Ollama doesn't require API keys
        
        return True  # Default to valid for unknown providers
```

### 12.2 Request Validation

```python
# backend/middleware/request_validator.py
import re
from flask import request, jsonify
from functools import wraps

class RequestValidator:
    """
    Request validation middleware
    """
    
    @staticmethod
    def validate_provider_name(provider: str) -> bool:
        """Validate provider name"""
        if not provider or not isinstance(provider, str):
            return False
        
        # Only allow alphanumeric and hyphens
        return bool(re.match(r'^[a-zA-Z0-9-]+$', provider))
    
    @staticmethod
    def validate_model_name(model: str) -> bool:
        """Validate model name"""
        if not model or not isinstance(model, str):
            return False
        
        # Allow alphanumeric, hyphens, underscores, slashes, and dots
        return bool(re.match(r'^[a-zA-Z0-9._/-]+$', model))
    
    @staticmethod
    def validate_query_text(query: str) -> bool:
        """Validate query text"""
        if not query or not isinstance(query, str):
            return False
        
        # Check length
        if len(query) > 10000:  # 10KB limit
            return False
        
        # Check for potentially malicious content
        dangerous_patterns = [
            r'<script.*?>.*?</script>',
            r'javascript:',
            r'data:.*?base64',
            r'eval\(',
            r'exec\('
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return False
        
        return True
    
    @staticmethod
    def validate_temperature(temp: float) -> bool:
        """Validate temperature parameter"""
        return isinstance(temp, (int, float)) and 0 <= temp <= 2
    
    @staticmethod
    def validate_max_tokens(tokens: int) -> bool:
        """Validate max tokens parameter"""
        return isinstance(tokens, int) and 1 <= tokens <= 4096

def validate_request(f):
    """Decorator for request validation"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get request data
        data = request.get_json() or {}
        
        # Validate provider
        provider = kwargs.get('provider_name') or data.get('provider')
        if provider and not RequestValidator.validate_provider_name(provider):
            return jsonify({'error': 'Invalid provider name'}), 400
        
        # Validate model
        model = kwargs.get('model_name') or data.get('model')
        if model and not RequestValidator.validate_model_name(model):
            return jsonify({'error': 'Invalid model name'}), 400
        
        # Validate query
        query = data.get('query')
        if query and not RequestValidator.validate_query_text(query):
            return jsonify({'error': 'Invalid query text'}), 400
        
        # Validate parameters
        temperature = data.get('temperature')
        if temperature is not None and not RequestValidator.validate_temperature(temperature):
            return jsonify({'error': 'Invalid temperature value'}), 400
        
        max_tokens = data.get('max_tokens')
        if max_tokens is not None and not RequestValidator.validate_max_tokens(max_tokens):
            return jsonify({'error': 'Invalid max_tokens value'}), 400
        
        return f(*args, **kwargs)
    
    return decorated_function
```

---

## 13. Deployment and Scaling

### 13.1 Docker Configuration

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create necessary directories
RUN mkdir -p backend/logs backend/chromadb_data

# Set environment variables
ENV PYTHONPATH=/app
ENV FLASK_APP=backend/api_server.py
ENV FLASK_ENV=production

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Start application
CMD ["python", "backend/api_server.py"]
```

### 13.2 Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  ai-refinement-dashboard:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_PATH=/app/data/ai_dashboard.db
      - CHROMADB_PATH=/app/data/chromadb_data
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    depends_on:
      - redis
      - postgres
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=ai_refinement
      - POSTGRES_USER=ai_user
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - ai-refinement-dashboard
    restart: unless-stopped

volumes:
  redis_data:
  postgres_data:
```

### 13.3 Kubernetes Deployment

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-refinement-dashboard
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-refinement-dashboard
  template:
    metadata:
      labels:
        app: ai-refinement-dashboard
    spec:
      containers:
      - name: ai-refinement-dashboard
        image: ai-refinement-dashboard:latest
        ports:
        - containerPort: 5000
        env:
        - name: DATABASE_PATH
          value: "/app/data/ai_dashboard.db"
        - name: REDIS_URL
          value: "redis://redis-service:6379/0"
        volumeMounts:
        - name: data-volume
          mountPath: /app/data
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /api/health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/health
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: data-volume
        persistentVolumeClaim:
          claimName: ai-refinement-data-pvc

---
apiVersion: v1
kind: Service
metadata:
  name: ai-refinement-dashboard-service
spec:
  selector:
    app: ai-refinement-dashboard
  ports:
  - port: 80
    targetPort: 5000
  type: LoadBalancer

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: ai-refinement-data-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

---

## 14. Conclusion

This implementation plan provides a comprehensive roadmap for building a dynamic external model training system with the following key features:

### **Key Features:**
1. **Plugin-Based Architecture**: Easy to add new LLM providers
2. **Dynamic Provider Support**: OpenAI, Anthropic, NVIDIA, Hugging Face, Ollama, Cohere
3. **Hybrid Pipeline**: LoRA + RAG + External LLM integration
4. **User Management**: RBAC with user-specific configurations
5. **Security**: Encrypted API keys, request validation, rate limiting
6. **Performance**: Caching, connection pooling, monitoring
7. **Scalability**: Docker, Kubernetes, load balancing
8. **Testing**: Comprehensive test suite
9. **Documentation**: Complete implementation guide

### **Benefits:**
- **Provider Agnostic**: Switch between any LLM provider dynamically
- **Extensible**: Add new providers without code changes
- **Secure**: Enterprise-grade security and encryption
- **Scalable**: Production-ready deployment options
- **User-Friendly**: Intuitive frontend interface
- **Cost-Effective**: Optimize costs by choosing the right provider for each task

### **Implementation Timeline:**
- **16 weeks** total implementation
- **Phased approach** with clear deliverables
- **Testing and optimization** included
- **Production deployment** ready

This system enables users to leverage any external LLM provider while maintaining their personal style through LoRA fine-tuning and accessing relevant knowledge through RAG, creating a truly personalized and powerful AI assistant.
