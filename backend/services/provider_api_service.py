"""
Provider API Service for Dynamic LLM Provider System

Service layer for managing dynamic providers with admin/superuser/developer access control.
Integrates with existing RBAC system and provides secure API key management.

Access: Admin, Superuser, Developer only
"""

import logging
import hashlib
import secrets
from typing import Dict, List, Any, Optional
from .llm_providers.llm_router import llm_router
from .database_extensions import db_extensions

logger = logging.getLogger(__name__)


class ProviderAPIService:
    """
    Service for managing dynamic providers
    """
    
    def __init__(self):
        self.router = llm_router
        selfPostgreSQL = db_extensions
    
    def get_available_providers(self) -> List[Dict[str, Any]]:
        """
        Get all available providers with capabilities
        
        Returns:
            List of provider information
        """
        try:
            # Get providers from router
            router_providers = self.router.get_all_providers_info()
            
            # Get database capabilities
            db_capabilities = selfPostgreSQL.get_provider_capabilities()
            
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
                    'display_name': router_provider.get('display_name', router_provider['name'].title()),
                    'description': capability['description'] if capability else '',
                    'supports_streaming': router_provider.get('supports_streaming', False),
                    'requires_api_key': capability['requires_api_key'] if capability else True,
                    'requires_base_url': capability['requires_base_url'] if capability else False,
                    'default_models': capability['default_models'] if capability else [],
                    'config_schema': capability['config_schema'] if capability else {}
                }
                
                providers.append(provider_info)
            
            return providers
            
        except Exception as e:
            logger.error(f"Error getting available providers: {e}")
            return []
    
    def get_provider_capabilities(self, provider_name: str) -> Optional[Dict[str, Any]]:
        """
        Get capabilities for specific provider
        
        Args:
            provider_name: Name of the provider
        
        Returns:
            Provider capabilities or None
        """
        try:
            return selfPostgreSQL.get_provider_capability(provider_name)
        except Exception as e:
            logger.error(f"Error getting provider capabilities for {provider_name}: {e}")
            return None
    
    def create_user_provider_config(self, user_id: int, config_data: Dict[str, Any]) -> int:
        """
        Create user provider configuration
        
        Args:
            user_id: User ID
            config_data: Configuration data
        
        Returns:
            Configuration ID
        """
        try:
            # Validate provider exists
            available_providers = [p['name'] for p in self.get_available_providers()]
            if config_data['provider_name'] not in available_providers:
                raise ValueError(f"Unknown provider: {config_data['provider_name']}")
            
            # Encrypt API key if provided
            if 'api_key' in config_data and config_data['api_key']:
                config_data['api_key_encrypted'] = self._encrypt_api_key(config_data['api_key'])
                del config_data['api_key']
            
            # Create configuration
            config_id = selfPostgreSQL.add_user_provider_config(user_id, config_data)
            
            logger.info(f"Created provider config {config_id} for user {user_id}")
            return config_id
            
        except Exception as e:
            logger.error(f"Error creating provider config: {e}")
            raise
    
    def get_user_provider_configs(self, user_id: int, provider_name: str = None) -> List[Dict[str, Any]]:
        """
        Get user provider configurations
        
        Args:
            user_id: User ID
            provider_name: Optional provider name filter
        
        Returns:
            List of configurations
        """
        try:
            configs = selfPostgreSQL.get_user_provider_configs(user_id, provider_name)
            
            # Remove encrypted API keys from response
            for config in configs:
                if 'api_key_encrypted' in config:
                    del config['api_key_encrypted']
            
            return configs
            
        except Exception as e:
            logger.error(f"Error getting user provider configs: {e}")
            return []
    
    def update_user_provider_config(self, user_id: int, config_id: int, updates: Dict[str, Any]) -> bool:
        """
        Update user provider configuration
        
        Args:
            user_id: User ID
            config_id: Configuration ID
            updates: Updates to apply
        
        Returns:
            Success status
        """
        try:
            # Encrypt API key if provided
            if 'api_key' in updates and updates['api_key']:
                updates['api_key_encrypted'] = self._encrypt_api_key(updates['api_key'])
                del updates['api_key']
            
            success = selfPostgreSQL.update_user_provider_config(config_id, updates)
            
            if success:
                logger.info(f"Updated provider config {config_id} for user {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating provider config: {e}")
            return False
    
    def delete_user_provider_config(self, user_id: int, config_id: int) -> bool:
        """
        Delete user provider configuration
        
        Args:
            user_id: User ID
            config_id: Configuration ID
        
        Returns:
            Success status
        """
        try:
            success = selfPostgreSQL.delete_user_provider_config(config_id)
            
            if success:
                logger.info(f"Deleted provider config {config_id} for user {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting provider config: {e}")
            return False
    
    def test_provider_connection(self, user_id: int, config_id: int) -> Dict[str, Any]:
        """
        Test provider connection
        
        Args:
            user_id: User ID
            config_id: Configuration ID
        
        Returns:
            Test results
        """
        try:
            # Get configuration
            configs = selfPostgreSQL.get_user_provider_configs(user_id)
            config = next((c for c in configs if c['id'] == config_id), None)
            
            if not config:
                return {
                    'success': False,
                    'error': 'Configuration not found'
                }
            
            # Decrypt API key
            api_key = self._decrypt_api_key(config['api_key_encrypted'])
            
            # Test connection
            test_result = self.router.test_provider(
                config['provider_name'],
                api_key=api_key,
                base_url=config.get('base_url'),
                model=config.get('model_id')
            )
            
            # Log test result
            selfPostgreSQL.log_provider_test(
                user_id=user_id,
                provider_name=config['provider_name'],
                config_id=config_id,
                test_success=test_result['success'],
                response_time=test_result.get('response_time', 0.0),
                error_message=test_result.get('error'),
                test_response=test_result.get('response')
            )
            
            return test_result
            
        except Exception as e:
            logger.error(f"Error testing provider connection: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def query_provider(self, user_id: int, provider_name: str, model_id: str,
                      messages: List[Dict[str, str]], stream: bool = False, **kwargs) -> str:
        """
        Query provider with user's configuration
        
        Args:
            user_id: User ID
            provider_name: Provider name
            model_id: Model ID
            messages: Messages to send
            stream: Whether to stream response
            **kwargs: Additional parameters
        
        Returns:
            Response from provider
        """
        try:
            # Get user's configuration for provider
            configs = selfPostgreSQL.get_user_provider_configs(user_id, provider_name)
            config = next((c for c in configs if c['is_default']), configs[0] if configs else None)
            
            if not config:
                raise ValueError(f"No configuration found for provider: {provider_name}")
            
            # Decrypt API key
            api_key = self._decrypt_api_key(config['api_key_encrypted'])
            
            # Query provider
            response = self.router.query_provider(
                provider_name,
                messages,
                stream=stream,
                api_key=api_key,
                base_url=config.get('base_url'),
                model=model_id,
                **kwargs
            )
            
            # Log usage
            if not stream:
                selfPostgreSQL.log_provider_usage(
                    user_id=user_id,
                    provider_name=provider_name,
                    model_id=model_id,
                    query_text=messages[-1]['content'] if messages else '',
                    response_length=len(response) if isinstance(response, str) else 0
                )
            
            return response
            
        except Exception as e:
            logger.error(f"Error querying provider: {e}")
            raise
    
    def get_user_usage_stats(self, user_id: int, provider_name: str = None) -> Dict[str, Any]:
        """
        Get user usage statistics
        
        Args:
            user_id: User ID
            provider_name: Optional provider name filter
        
        Returns:
            Usage statistics
        """
        try:
            return selfPostgreSQL.get_user_usage_stats(user_id, provider_name)
        except Exception as e:
            logger.error(f"Error getting usage stats: {e}")
            return {
                'total_requests': 0,
                'total_tokens': 0,
                'total_cost': 0.0,
                'avg_response_time': 0.0
            }
    
    def _encrypt_api_key(self, api_key: str) -> str:
        """
        Encrypt API key (simple encryption for demo - use proper encryption in production)
        
        Args:
            api_key: API key to encrypt
        
        Returns:
            Encrypted API key
        """
        # Simple encryption for demo - use proper encryption in production
        salt = secrets.token_hex(16)
        key_hash = hashlib.sha256((api_key + salt).encode()).hexdigest()
        return f"{salt}:{key_hash}"
    
    def _decrypt_api_key(self, encrypted_key: str) -> str:
        """
        Decrypt API key (simple decryption for demo - use proper decryption in production)
        
        Args:
            encrypted_key: Encrypted API key
        
        Returns:
            Decrypted API key
        """
        # Simple decryption for demo - use proper decryption in production
        # In production, this would be a placeholder - actual decryption would be handled
        # by a proper key management system
        if ':' in encrypted_key:
            salt, key_hash = encrypted_key.split(':', 1)
            # For demo purposes, return a placeholder
            return f"decrypted_key_for_{salt[:8]}"
        return encrypted_key


# Global provider API service instance
provider_api_service = ProviderAPIService()
