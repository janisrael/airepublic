#!/usr/bin/env python3
"""
NVIDIA NIM Service for fetching model details
"""

import requests
import json
import os
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class NVIDIANIMService:
    def __init__(self):
        self.api_base = "https://integrate.api.nvidia.com/v1"
        self.api_key = os.environ.get("NV_API_KEY")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }
    
    def get_models_list(self) -> List[Dict[str, Any]]:
        """Get list of all available models from NVIDIA NIM"""
        try:
            response = requests.get(
                f"{self.api_base}/models", 
                headers=self.headers, 
                timeout=15
            )
            response.raise_for_status()
            data = response.json()
            
            # Handle different response formats
            if isinstance(data, dict):
                if "data" in data:
                    return data["data"]
                elif "models" in data:
                    return data["models"]
                elif "items" in data:
                    return data["items"]
                else:
                    return [data]
            elif isinstance(data, list):
                return data
            else:
                logger.warning(f"Unexpected response format: {type(data)}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch models list: {e}")
            return []
        except Exception as e:
            logger.error(f"Error parsing models list: {e}")
            return []
    
    def get_model_details(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific model"""
        try:
            # Try direct model endpoint first
            response = requests.get(
                f"{self.api_base}/models/{model_name}",
                headers=self.headers,
                timeout=15
            )
            
            if response.status_code == 200:
                return response.json()
            
            # If direct endpoint fails, search in models list
            models = self.get_models_list()
            for model in models:
                if (model.get("name") == model_name or 
                    model.get("id") == model_name or
                    model.get("model") == model_name):
                    return model
            
            logger.warning(f"Model {model_name} not found")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch model details for {model_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error parsing model details for {model_name}: {e}")
            return None
    
    def get_model_specs_from_name(self, model_name: str) -> Dict[str, Any]:
        """Get model specifications based on known model names"""
        specs = {}
        
        # Known model specifications
        model_specs = {
            "nvidia/llama-3.3-nemotron-super-49b-v1.5": {
                "architecture": "llama",
                "parameters": "49B",
                "context_length": 131072,
                "max_tokens": 4096,
                "capabilities": ["chat", "reasoning", "coding"],
                "quantization": "fp8",
                "license": "NVIDIA",
                "description": "NVIDIA Llama 3.3 Nemotron Super 49B - Advanced reasoning and coding model"
            },
            "moonshotai/kimi-k2-instruct-0905": {
                "architecture": "moe",
                "parameters": "32B active, 1T total",
                "context_length": 262144,
                "max_tokens": 4096,
                "capabilities": ["chat", "tools", "long-context"],
                "quantization": "fp8",
                "license": "Moonshot AI",
                "description": "Moonshot AI Kimi K2 - Advanced reasoning with 256K context"
            },
            "deepseek-ai/deepseek-r1": {
                "architecture": "deepseek",
                "parameters": "7B",
                "context_length": 65536,
                "max_tokens": 4096,
                "capabilities": ["chat", "reasoning", "coding"],
                "quantization": "fp8",
                "license": "DeepSeek",
                "description": "DeepSeek R1 - Advanced reasoning model with chain-of-thought"
            }
        }
        
        return model_specs.get(model_name, {})
    
    def extract_model_metadata(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and normalize model metadata from NVIDIA NIM response"""
        metadata = {}
        
        # Basic info
        model_id = model_data.get("id") or model_data.get("name") or model_data.get("model")
        metadata["name"] = model_id
        metadata["display_name"] = model_data.get("display_name") or model_id
        metadata["description"] = model_data.get("description") or model_data.get("summary")
        
        # Get known specifications for this model
        known_specs = self.get_model_specs_from_name(model_id)
        
        # Architecture and parameters
        metadata["architecture"] = known_specs.get("architecture") or model_data.get("architecture") or model_data.get("family")
        metadata["parameters"] = known_specs.get("parameters") or model_data.get("parameters") or model_data.get("active_parameters")
        
        # Context length
        metadata["context_length"] = known_specs.get("context_length") or model_data.get("context_length") or model_data.get("context_window")
        
        # Max tokens
        metadata["max_tokens"] = known_specs.get("max_tokens") or model_data.get("max_tokens") or model_data.get("max_output_tokens")
        
        # Capabilities
        metadata["capabilities"] = known_specs.get("capabilities") or model_data.get("capabilities") or model_data.get("features")
        
        # Quantization
        metadata["quantization"] = known_specs.get("quantization") or model_data.get("quantization") or model_data.get("format")
        
        # License
        metadata["license"] = known_specs.get("license") or model_data.get("license")
        
        # Description
        if not metadata["description"]:
            metadata["description"] = known_specs.get("description")
        
        # Embedding length
        metadata["embedding_length"] = model_data.get("embedding_length") or model_data.get("embedding_dim")
        
        # System prompt
        metadata["system_prompt"] = model_data.get("system_prompt")
        
        # Temperature and top_p defaults
        metadata["temperature"] = model_data.get("temperature", 0.7)
        metadata["top_p"] = model_data.get("top_p", 0.9)
        
        # Provider info
        metadata["provider"] = "nvidia"
        metadata["model_id"] = model_id
        metadata["base_url"] = self.api_base
        
        return metadata
    
    def fetch_and_store_model_details(self, model_name: str, db_service) -> bool:
        """Fetch model details from NVIDIA NIM and store in database"""
        try:
            # Get model details from NVIDIA NIM
            model_data = self.get_model_details(model_name)
            if not model_data:
                logger.error(f"No data found for model {model_name}")
                return False
            
            # Extract metadata
            metadata = self.extract_model_metadata(model_data)
            
            # Check if model already exists in database
            existing_models = db_service.get_external_api_models()
            existing_model = None
            for model in existing_models:
                if model["name"] == model_name or model["model_id"] == model_name:
                    existing_model = model
                    break
            
            if existing_model:
                # Update existing model
                update_data = {
                    "context_length": metadata.get("context_length"),
                    "max_tokens": metadata.get("max_tokens"),
                    "capabilities": metadata.get("capabilities", []),
                    "parameters": metadata.get("parameters"),
                    "quantization": metadata.get("quantization"),
                    "architecture": metadata.get("architecture"),
                    "license": metadata.get("license"),
                    "embedding_length": metadata.get("embedding_length"),
                    "system_prompt": metadata.get("system_prompt"),
                    "temperature": metadata.get("temperature"),
                    "top_p": metadata.get("top_p")
                }
                
                # Remove None values
                update_data = {k: v for k, v in update_data.items() if v is not None}
                
                if update_data:
                    db_service.update_external_api_model(existing_model["id"], update_data)
                    logger.info(f"Updated model {model_name} with NVIDIA NIM data")
                    return True
            else:
                logger.warning(f"Model {model_name} not found in database to update")
                return False
                
        except Exception as e:
            logger.error(f"Error fetching and storing model details for {model_name}: {e}")
            return False
    
    def sync_all_models(self, db_service) -> Dict[str, bool]:
        """Sync all NVIDIA models in database with latest details from NIM API"""
        results = {}
        
        # Get all NVIDIA models from database
        existing_models = db_service.get_external_api_models()
        nvidia_models = [model for model in existing_models if model.get("provider") == "nvidia"]
        
        for model in nvidia_models:
            model_name = model["model_id"] or model["name"]
            if model_name:
                success = self.fetch_and_store_model_details(model_name, db_service)
                results[model_name] = success
        
        return results

# Global instance
nvidia_nim_service = NVIDIANIMService()
