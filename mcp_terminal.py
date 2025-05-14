#!/usr/bin/env python3
"""
Entry point script for MCP Terminal server.
"""

import os
import sys


# Add the src directory to the Python path
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
sys.path.insert(0, src_path)

from mcp_terminal.server import main

if __name__ == "__main__":
    sys.exit(main())
