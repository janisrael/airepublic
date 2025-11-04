"""
Spirit Orchestrator Microservice Client
Client for AI Republic main system to communicate with Spirit Orchestrator microservice
"""

import httpx
import asyncio
from typing import Dict, Any, Optional
import json
from datetime import datetime

class SpiritOrchestratorClient:
    """Client for communicating with Spirit Orchestrator microservice"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.timeout = 30.0
        
    async def chat_with_spirits(
        self,
        minion_id: str,
        user_input: str,
        user_id: str,
        model: Optional[str] = None,
        temperature: Optional[float] = 0.7,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Chat with minion using Spirit Orchestration
        
        Args:
            minion_id: ID of the minion
            user_input: User's input message
            user_id: ID of the user
            model: Optional model override
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            
        Returns:
            Dict with response, spirits_used, tools_used, etc.
        """
        try:
            payload = {
                "user_input": user_input,
                "user_id": user_id,
                "minion_id": minion_id,
                "model": model,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/chat",
                    json=payload
                )
                
                if response.status_code == 200:
                    return {
                        "success": True,
                        "data": response.json()
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Microservice error: {response.status_code}",
                        "status_code": response.status_code,
                        "response": response.text
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": f"Error communicating with microservice: {str(e)}"
            }
    
    async def get_minion_spirits(self, minion_id: str) -> Dict[str, Any]:
        """Get spirits assigned to a minion"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/minions/{minion_id}/spirits"
                )
                
                if response.status_code == 200:
                    return {
                        "success": True,
                        "data": response.json()
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to get minion spirits: {response.status_code}",
                        "status_code": response.status_code
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting minion spirits: {str(e)}"
            }
    
    async def get_minion_status(self, minion_id: str) -> Dict[str, Any]:
        """Get minion orchestration status"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/minions/{minion_id}/status"
                )
                
                if response.status_code == 200:
                    return {
                        "success": True,
                        "data": response.json()
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to get minion status: {response.status_code}",
                        "status_code": response.status_code
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting minion status: {str(e)}"
            }
    
    async def test_minion_orchestration(self, minion_id: str) -> Dict[str, Any]:
        """Test minion orchestration"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/minions/{minion_id}/test"
                )
                
                if response.status_code == 200:
                    return {
                        "success": True,
                        "data": response.json()
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to test orchestration: {response.status_code}",
                        "status_code": response.status_code
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": f"Error testing orchestration: {str(e)}"
            }
    
    async def get_llm_providers(self) -> Dict[str, Any]:
        """Get available LLM providers"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/providers"
                )
                
                if response.status_code == 200:
                    return {
                        "success": True,
                        "data": response.json()
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to get providers: {response.status_code}",
                        "status_code": response.status_code
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting providers: {str(e)}"
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check microservice health"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/health"
                )
                
                if response.status_code == 200:
                    return {
                        "success": True,
                        "status": "healthy",
                        "data": response.json(),
                        "response_time": response.elapsed.total_seconds()
                    }
                else:
                    return {
                        "success": False,
                        "status": "unhealthy",
                        "status_code": response.status_code
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "status": "unreachable",
                "error": str(e)
            }


# Global client instance
spirit_orchestrator_client = SpiritOrchestratorClient()
