#!/usr/bin/env python3
"""Main entry point for SLM Agent"""

import sys
from core.agent import IterativeRefinementAgent
from config.settings import AgentConfig


def main():
    """Main entry point"""
    # Custom configuration
    # Config class get os.getenv variables if set
    config = AgentConfig(
        max_iterations=3,
        # slm_model will be read from ENV variable
        enable_port_validation=True,
        use_few_shot_examples=True
    )

    # Create and run agent
    agent = IterativeRefinementAgent(config)
    exit_code = agent.run()
    return exit_code


if __name__ == "__main__":
    sys.exit(main())