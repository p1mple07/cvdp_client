#!/usr/bin/env python3
"""Centralized configuration management"""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AgentConfig:
    """Configuration for SLM Agent with validation"""
    
    # Iteration settings
    max_iterations: int = 3
    early_exit_on_success: bool = False
    
    # OpenAI API settings
    slm_api_url: str = field(default_factory=lambda: os.getenv("OPENAI_API_URL", "https://api.openai.com"))
    slm_model: str = field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    slm_max_length: int = field(default_factory=lambda: int(os.getenv("OPENAI_MAX_TOKENS", "16000")))
    slm_timeout: int = field(default_factory=lambda: int(os.getenv("OPENAI_TIMEOUT", "300")))
    
    # Prompt engineering settings
    use_few_shot_examples: bool = True
    max_context_files: int = 10
    enable_port_validation: bool = True
    
    # Testing settings
    test_timeout: int = 120
    lint_timeout: int = 30
    
    # Logging
    log_file: str = '/code/rundir/agent_detailed.log'
    
    def validate(self) -> None:
        """Validate configuration values"""
        assert self.max_iterations > 0, "max_iterations must be positive"
        assert self.slm_timeout > 0, "slm_timeout must be positive"
        assert self.slm_max_length >= 1024, "slm_max_length too small (min: 1024)"
        assert self.test_timeout > 0, "test_timeout must be positive"
        assert self.lint_timeout > 0, "lint_timeout must be positive"
        assert self.max_context_files > 0, "max_context_files must be positive"
    
    def __post_init__(self):
        """Validate on initialization"""
        self.validate()
