#!/usr/bin/env python3
"""Manage Verilog code files and context gathering"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class CodeManager:
    """Manage HDL code files and context"""
    
    def read_prompt(self, prompt_file: str = "/code/prompt.json") -> str:
        """
        Read task from prompt.json
        
        Args:
            prompt_file: Path to prompt JSON file
            
        Returns:
            Task description string
        """
        try:
            with open(prompt_file, "r") as f:
                data = json.load(f)
                prompt = data.get("prompt", "")
                logger.info(f"Read task from {prompt_file}")
                logger.info(f"   Task preview: {prompt[:150]}...")
                return prompt
        except FileNotFoundError:
            logger.error(f"Prompt file not found: {prompt_file}")
            return ""
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in prompt file: {e}")
            return ""
        except Exception as e:
            logger.error(f"Error reading prompt: {e}")
            return ""
    
    def gather_context(self, base_dir: str = "/code") -> Dict[str, str]:
        """
        Gather all existing files as context
        
        Args:
            base_dir: Base directory to search
            
        Returns:
            Dictionary mapping file_path -> content
        """
        context = {}
        
        # Directories to search
        search_dirs = ["docs", "rtl", "verif", "rundir"]
        
        for dir_name in search_dirs:
            dir_path = Path(base_dir) / dir_name
            
            if not dir_path.exists():
                logger.info(f"   Directory not found: {dir_name}/")
                continue
            
            # Recursively find all files
            for file_path in dir_path.rglob("*"):
                if file_path.is_file():
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            relative_path = file_path.relative_to(base_dir)
                            content = f.read()
                            context[str(relative_path)] = content
                            logger.info(f"   Loaded: {relative_path} ({len(content)} bytes)")
                    except Exception as e:
                        logger.warning(f"   Could not read {file_path}: {e}")
        
        logger.info(f"Gathered context from {len(context)} files")
        return context
    
    def find_target_file(self, rtl_dir: str = "/code/rtl") -> Optional[Path]:
        """
        Find the file that needs to be created/modified
        
        Args:
            rtl_dir: RTL directory path
            
        Returns:
            Path to target file or None
        """
        rtl_path = Path(rtl_dir)
        
        # Check if RTL directory exists
        if not rtl_path.exists():
            logger.warning(f"RTL directory not found: {rtl_dir}")
            rtl_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"   Created RTL directory: {rtl_dir}")
        
        # Strategy 1: Find empty files
        for file_path in rtl_path.iterdir():
            if file_path.is_file() and file_path.stat().st_size == 0:
                logger.info(f"Found empty target file: {file_path}")
                return file_path
        
        # Strategy 2: Look for common top-level names
        common_names = ["top.sv", "top.v", "top_module.sv", "top_module.v", "design.sv", "design.v"]
        for name in common_names:
            path = rtl_path / name
            if not path.exists():
                logger.info(f"Will create target file: {path}")
                return path
        
        # Strategy 3: Use first .sv or .v file
        for file_path in rtl_path.glob("*.sv"):
            logger.info(f"Using existing file: {file_path}")
            return file_path
        
        for file_path in rtl_path.glob("*.v"):
            logger.info(f"Using existing file: {file_path}")
            return file_path
        
        # Default: create top.sv
        default_path = rtl_path / "top.sv"
        logger.info(f"Using default: {default_path}")
        return default_path
    
    def write_code(self, file_path: Path, code: str) -> bool:
        """
        Write code to file
        
        Args:
            file_path: Target file path
            code: Code content to write
            
        Returns:
            True if successful
        """
        try:
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write code
            with open(file_path, "w") as f:
                f.write(code)
            
            logger.info(f"Wrote {len(code)} bytes to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error writing to {file_path}: {e}")
            return False
    
    def backup_code(self, file_path: Path) -> bool:
        """
        Create backup of existing file
        
        Args:
            file_path: File to backup
            
        Returns:
            True if successful
        """
        try:
            if not file_path.exists():
                return True
            
            backup_path = file_path.with_suffix(file_path.suffix + ".bak")
            content = file_path.read_text()
            backup_path.write_text(content)
            
            logger.info(f"Created backup: {backup_path}")
            return True
            
        except Exception as e:
            logger.warning(f"Could not create backup: {e}")
            return False
