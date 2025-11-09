#!/usr/bin/env python3
"""Run CocoTB-based tests"""

import subprocess
import logging
from typing import Tuple

logger = logging.getLogger(__name__)


class CocotbRunner:
    """Run CocoTB-based tests if available"""
    
    def __init__(self, timeout: int = 120):
        """
        Initialize CocoTB runner
        
        Args:
            timeout: Timeout for test execution in seconds
        """
        self.timeout = timeout
    
    def run(self) -> Tuple[bool, str]:
        """
        Run CocoTB tests
        
        Returns:
            Tuple of (success, error_messages)
        """
        try:
            logger.info("Running CocoTB tests...")
            
            # Try to run pytest on test_runner.py
            result = subprocess.run(
                ["pytest", "-v", "-s", "/src/test_runner.py"],
                cwd="/code/rundir",
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            output = result.stdout + "\n" + result.stderr
            
            # Log first 1000 chars of output
            logger.info(f"Test output preview:\n{output[:1000]}")
            
            if result.returncode == 0:
                logger.info("CocoTB tests PASSED")
                return True, ""
            else:
                logger.warning(f"CocoTB tests FAILED (exit code: {result.returncode})")
                # Extract relevant errors (last 50 lines)
                error_lines = output.split("\n")[-50:]
                errors = "\n".join(error_lines)
                return False, errors
                
        except subprocess.TimeoutExpired:
            logger.error(f"CocoTB tests timeout after {self.timeout}s")
            return False, f"Tests timed out after {self.timeout} seconds"
        
        except FileNotFoundError:
            logger.info("CocoTB tests not available (pytest not found)")
            return False, ""
        
        except Exception as e:
            logger.error(f"Error running CocoTB tests: {e}")
            return False, str(e)
