#!/usr/bin/env python3
"""Orchestrate test execution (CocoTB and lint checks)"""

import logging
from pathlib import Path
from typing import Tuple, List
from testing.cocotb_runner import CocotbRunner
from testing.lint_runner import LintRunner

logger = logging.getLogger(__name__)


class TestRunner:
    """Orchestrate test execution"""
    
    def __init__(self, test_timeout: int = 120, lint_timeout: int = 30):
        """
        Initialize test runner
        
        Args:
            test_timeout: Timeout for CocoTB tests
            lint_timeout: Timeout for lint checks
        """
        self.cocotb_runner = CocotbRunner(timeout=test_timeout)
        self.lint_runner = LintRunner(timeout=lint_timeout)
    
    def run(self) -> Tuple[bool, str]:
        """
        Run tests using available tools
        
        Returns:
            Tuple of (success, error_messages)
        """
        logger.info("Starting test execution...")

        # First check if code compiles
        logger.info("Step 1: Checking if code compiles...")
        lint_success, lint_errors = self._run_lint_checks()
        
        if not lint_success:
            # Compilation failed, return errors
            logger.warning("Compilation failed, skipping testbench execution")
            return False, lint_errors

        # Compilation succeeded (possibly with warnings)
        logger.info("Code compiles successfully!")
        
        # Now try to run actual testbench if available
        rundir = Path("/code/rundir")
        
        # Check if there's a pytest-based test
        if (rundir / "../harness").exists() or Path("/src/test_runner.py").exists():
            logger.info("Step 2: Running actual testbench tests...")
            # Check if CocoTB tests are available
            cocotb_success, cocotb_errors = self.cocotb_runner.run()
            if cocotb_errors or cocotb_success is not None:  # CocoTB tests were found and executed
                return cocotb_success, cocotb_errors
        
        # No testbench available, compilation success is enough
        logger.info("No testbench found, compilation success is sufficient")
        return True, ""
    
    def _run_lint_checks(self) -> Tuple[bool, str]:
        """Run lint checks on RTL files"""
        # Find RTL files
        rtl_files = self._find_rtl_files()
        
        if not rtl_files:
            logger.warning("No RTL files found for linting")
            return False, "No RTL files found"
        
        return self.lint_runner.run(rtl_files)
    
    def _find_rtl_files(self) -> List[Path]:
        """Find all RTL files for linting"""
        rtl_files = []
        rtl_dir = Path("/code/rtl")
        
        if not rtl_dir.exists():
            return rtl_files
        
        # Find .v and .sv files
        rtl_files.extend(rtl_dir.glob("*.v"))
        rtl_files.extend(rtl_dir.glob("*.sv"))
        
        return list(rtl_files)
    
    def categorize_errors(self, errors: str) -> str:
        """
        Categorize error messages
        
        Args:
            errors: Error messages from tests
            
        Returns:
            Error category (syntax, logic, timing, etc.)
        """
        errors_lower = errors.lower()
        
        # Syntax errors
        if any(kw in errors_lower for kw in ["syntax error", "parse error", "unexpected", "expected"]):
            return "syntax"
        
        # Undefined/undeclared
        if any(kw in errors_lower for kw in ["undeclared", "undefined", "not declared"]):
            return "undeclared"
        
        # Type errors
        if any(kw in errors_lower for kw in ["type mismatch", "incompatible types"]):
            return "type"
        
        # Width mismatches
        if any(kw in errors_lower for kw in ["width", "bit width", "size mismatch"]):
            return "width"
        
        # Latch inference
        if "latch" in errors_lower:
            return "latch"
        
        # Timing
        if any(kw in errors_lower for kw in ["timing", "setup", "hold"]):
            return "timing"
        
        # Default
        return "general"
