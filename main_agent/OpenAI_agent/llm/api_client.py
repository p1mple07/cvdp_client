#!/usr/bin/env python3
"""OpenAI API client for code generation"""

import os
import logging
from typing import Optional
from openai import OpenAI

logger = logging.getLogger(__name__)


class SLMAPIClient:
    """Interface to OpenAI API (keeping class name for compatibility)"""
    
    def __init__(self, api_url: str, model: str, max_length: int, timeout: int, temperature: float = 0.3):
        """
        Initialize OpenAI API client
        
        Args:
            api_url: Not used for OpenAI (kept for compatibility)
            model: Model name (e.g., 'gpt-4o-mini')
            max_length: Maximum generation tokens
            timeout: Request timeout in seconds
            temperature: Default sampling temperature
        """
        self.model = model
        self.max_length = max_length
        self.timeout = timeout
        self.temperature = temperature
        
        # Initialize OpenAI client with API key from environment
        # Try OPENAI_API_KEY first, then fall back to OPENAI_USER_KEY (used by benchmark)
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_USER_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY or OPENAI_USER_KEY environment variable not set")
        
        self.client = OpenAI(api_key=api_key, timeout=timeout)
        
        logger.info(f"Initialized OpenAI API Client")
        logger.info(f"  Model: {model}")
        logger.info(f"  Max tokens: {max_length}")
        logger.info(f"  Temperature: {temperature}")
    
    def generate(self, prompt: str, temperature: float = None) -> Optional[str]:
        """
        Generate code using OpenAI API
        
        Args:
            prompt: Input prompt with TASK, REQUIREMENTS, etc.
            temperature: Sampling temperature (uses default if None)
            
        Returns:
            Generated text or None on failure
        """
        if temperature is None:
            temperature = self.temperature
            
        try:
            logger.info(f"Calling OpenAI API")
            logger.info(f"  Model: {self.model}, Temperature: {temperature}")
            logger.info(f"  Prompt length: {len(prompt)} chars")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_length,
                temperature=temperature
            )
            
            result = response.choices[0].message.content
            logger.info(f"Received {len(result)} bytes from OpenAI")
            return result
                
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return None
