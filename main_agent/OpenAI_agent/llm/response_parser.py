#!/usr/bin/env python3
"""Parse and extract Verilog code from SLM responses"""

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ResponseParser:
    """Extract and validate Verilog code from SLM responses"""
    
    @staticmethod
    def _remove_reasoning_text(response: str) -> str:
        """
        Remove common LLM reasoning patterns before extraction
        
        Args:
            response: Raw response that may contain reasoning text
            
        Returns:
            Response with reasoning text removed
        """
        # Remove leading thinking/reasoning sections before first proper module
        # This handles cases like "Okay, let me think..." before the actual code
        patterns_to_remove = [
            r'^.*?(?=^\s*module\s+\w+\s*[\(#])',  # Remove everything before first proper module declaration
        ]
        
        cleaned = response
        for pattern in patterns_to_remove:
            cleaned = re.sub(pattern, '', cleaned, flags=re.DOTALL | re.MULTILINE | re.IGNORECASE)
        
        # If pattern didn't match (no proper module found), return original
        if cleaned.strip():
            return cleaned
        return response
    
    @staticmethod
    def extract_verilog(response: str) -> str:
        """
        Extract Verilog code from various response formats
        
        Tries multiple strategies:
        1. Markdown code blocks (```verilog, ```systemverilog, ```sv)
        2. Module boundaries (module...endmodule) with proper syntax
        3. Raw response (if no markers found)
        
        Args:
            response: Raw response from SLM
            
        Returns:
            Extracted Verilog code
        """
        if not response:
            logger.warning("Empty response received")
            return ""
        
        # Pre-process to remove reasoning text
        response = ResponseParser._remove_reasoning_text(response)
        
        # Strategy 1: Markdown code blocks
        markdown_patterns = [
            r'```(?:verilog|systemverilog|sv)\s*\n(.*?)\n```',
            r'```\s*\n(.*?)\n```',
        ]
        
        for pattern in markdown_patterns:
            match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
            if match:
                code = match.group(1).strip()
                logger.info(f"Extracted from markdown block: {len(code)} bytes")
                return code
        
        # Strategy 2: Module boundaries - require proper module declaration syntax
        if 'module ' in response.lower():
            # Match proper module declaration: module <name> followed by ( or #
            # This prevents matching "the module" or "module has to" in reasoning text
            match = re.search(
                r'^\s*module\s+\w+\s*[\(#].*?endmodule\s*$',
                response,
                re.DOTALL | re.MULTILINE | re.IGNORECASE
            )
            if match:
                code = match.group(0).strip()
                logger.info(f"Extracted module definition: {len(code)} bytes")
                return code
        
        # Strategy 3: Use raw response
        logger.info(f"Using raw response: {len(response)} bytes")
        return response.strip()
    
    @staticmethod
    def extract_module_name(code: str) -> Optional[str]:
        """
        Extract module name from Verilog code
        
        Args:
            code: Verilog source code
            
        Returns:
            Module name or None if not found
        """
        match = re.search(r'module\s+(\w+)', code, re.IGNORECASE)
        if match:
            module_name = match.group(1)
            logger.info(f"Module name: {module_name}")
            return module_name
        else:
            logger.warning("No module name found in code")
            return None
    
    @staticmethod
    def validate_basic_structure(code: str) -> bool:
        """
        Perform basic validation of Verilog structure
        
        Args:
            code: Verilog source code
            
        Returns:
            True if basic structure is valid
        """
        if not code:
            logger.warning("Empty code provided for validation")
            return False
        
        # Check for module keyword
        if 'module' not in code.lower():
            logger.warning("No 'module' keyword found")
            return False
        
        # Check for endmodule keyword
        if 'endmodule' not in code.lower():
            logger.warning("No 'endmodule' keyword found")
            return False
        
        # Check balanced parentheses
        open_parens = code.count('(')
        close_parens = code.count(')')
        if open_parens != close_parens:
            logger.warning(f"Unbalanced parentheses: {open_parens} open, {close_parens} close")
            return False
        
        logger.info("Basic structure validation passed")
        return True
