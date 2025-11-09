#!/usr/bin/env python3
"""SLM API client for code generation"""

import requests
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class SLMAPIClient:
    """Interface to Small Language Model API"""
    
    def __init__(self, api_url: str, model: str, max_length: int, timeout: int):
        """
        Initialize SLM API client
        
        Args:
            api_url: Base URL of SLM API
            model: Model name/identifier
            max_length: Maximum generation length
            timeout: Request timeout in seconds
        """
        self.api_url = api_url
        self.model = model
        self.max_length = max_length
        self.timeout = timeout
        
        logger.info(f"Initialized SLM API Client")
        logger.info(f"  URL: {api_url}")
        logger.info(f"  Model: {model}")
        logger.info(f"  Max length: {max_length}")
    
    def generate(self, prompt: str, temperature: float = 0.7) -> Optional[str]:
        """
        Generate code using SLM API
        
        Args:
            prompt: Input prompt with TASK, REQUIREMENTS, etc.
            temperature: Sampling temperature (0.0-1.0)
            
        Returns:
            Generated text or None on failure
        """
        try:
            payload = {
                "prompt": prompt,
                "max_length": self.max_length,
                "model": self.model,
                "temperature": temperature
            }
            
            logger.info(f"Calling SLM API: {self.api_url}/generate")
            logger.info(f"  Model: {self.model}, Temperature: {temperature}")
            logger.info(f"  Prompt length: {len(prompt)} chars")
            
            response = requests.post(
                f"{self.api_url}/generate",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Try multiple field names that different SLM APIs might use
                for field in ['generated_text', 'text', 'response', 'output', 'result']:
                    if field in data:
                        result = data[field]
                        logger.info(f"Received {len(result)} bytes from SLM (field: {field})")
                        return result
                
                # Fallback: return whole response as string
                result = str(data)
                logger.warning(f"Unknown response format, returning as string: {len(result)} bytes")
                return result
            else:
                logger.error(f"SLM API error {response.status_code}: {response.text}")
                return None
                
        except requests.Timeout:
            logger.error(f"SLM API timeout after {self.timeout}s")
            return None
        except requests.RequestException as e:
            logger.error(f"SLM API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error calling SLM API: {e}")
            return None
