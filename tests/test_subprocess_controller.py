"""
Tests for the subprocess terminal controller.
"""

import asyncio
import os
import sys
import unittest
from unittest import IsolatedAsyncioTestCase

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.mcp_terminal.controllers.subprocess import SubprocessTerminalController


class TestSubprocessTerminalController(IsolatedAsyncioTestCase):
    """Test cases for the subprocess terminal controller."""

    async def asyncSetUp(self):
        """Set up the test case."""
        self.controller = SubprocessTerminalController()

    async def test_execute_command(self):
        """Test executing a simple command."""
        result = await self.controller.execute_command("echo 'Hello, World!'")
        self.assertTrue(result["success"])
        self.assertIn("Hello, World!", result["output"])

    async def test_execute_command_with_error(self):
        """Test executing a command that produces an error."""
        result = await self.controller.execute_command("ls /nonexistent")
        self.assertFalse(result["success"])
        self.assertTrue(result["error"])

    async def test_get_terminal_type(self):
        """Test getting the terminal type."""
        terminal_type = await self.controller.get_terminal_type()
        self.assertEqual(terminal_type, "subprocess")

    async def test_cleanup(self):
        """Test cleaning up resources."""
        await self.controller.cleanup()
        # No assertions needed as cleanup does nothing for subprocess controller


if __name__ == "__main__":
    unittest.main()
