#!/usr/bin/env python3
"""Run CocoTB-based tests"""

import subprocess
import logging
from pathlib import Path
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
            Tuple of (success, error_messages) or (None, "") if tests not available
        """
        try:
            logger.info("Running CocoTB tests...")
            
            # Find test_runner.py in common locations
            test_paths = [
                "/src/test_runner.py",
                "/code/src/test_runner.py",
                "../src/test_runner.py"
            ]
            
            test_file = None
            for path in test_paths:
                if Path(path).exists():
                    test_file = path
                    logger.info(f"Found test file at: {test_file}")
                    break
            
            if not test_file:
                logger.info("ℹ️ CocoTB tests not available (test_runner.py not found)")
                return None, ""
            
            # Try to run pytest on test_runner.py
            result = subprocess.run(
                ["pytest", "-v", "-s", test_file],
                cwd="/code/rundir",
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            output = result.stdout + "\n" + result.stderr
            
            # Log full output for debugging
            logger.info(f"Test output:\n{output}")
            
            if result.returncode == 0:
                logger.info("✅ CocoTB tests PASSED")
                return True, ""
            else:
                logger.warning(f"❌ CocoTB tests FAILED (exit code: {result.returncode})")
                # Extract relevant errors - look for actual error messages
                error_lines = []
                in_error_section = False
                for line in output.split("\n"):
                    if "FAILED" in line or "ERROR" in line or "CalledProcessError" in line:
                        in_error_section = True
                    if in_error_section:
                        error_lines.append(line)
                
                # If no errors found, use last 100 lines
                if not error_lines:
                    error_lines = output.split("\n")[-100:]
                
                errors = "\n".join(error_lines)
                return False, errors
                
        except subprocess.TimeoutExpired:
            logger.error(f"⏱️ CocoTB tests timeout after {self.timeout}s")
            return False, f"Tests timed out after {self.timeout} seconds"
        
        except FileNotFoundError:
            logger.info("ℹ️ CocoTB tests not available (pytest not found)")
            return None, ""
        
        except Exception as e:
            logger.error(f"❌ Error running CocoTB tests: {e}")
            return False, str(e)
