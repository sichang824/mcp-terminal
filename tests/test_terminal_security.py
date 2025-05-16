"""
Tests for the terminal tool security features.
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

# Add both src and project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
src_path = os.path.join(project_root, "src")
sys.path.insert(0, project_root)
sys.path.insert(0, src_path)

from mcp_terminal.tools.terminal import TerminalTool


class TestTerminalToolSecurity(unittest.TestCase):
    """Test cases for the terminal tool security features."""

    def setUp(self):
        """Set up the test case."""
        # Create temporary files for whitelist and blacklist
        self.whitelist_file = tempfile.NamedTemporaryFile(mode="w+", delete=False)
        self.blacklist_file = tempfile.NamedTemporaryFile(mode="w+", delete=False)

        # Write test data to whitelist
        self.whitelist_file.write("# Allowed commands\n")
        self.whitelist_file.write("ls\n")
        self.whitelist_file.write("echo\n")
        self.whitelist_file.write("cat\n")
        self.whitelist_file.flush()

        # Write test data to blacklist
        self.blacklist_file.write("# Blocked commands\n")
        self.blacklist_file.write("rm\n")
        self.blacklist_file.write("sudo\n")
        self.blacklist_file.write("eval\n")
        self.blacklist_file.flush()

        # Create patches for controller
        self.controller_patcher = patch(
            "src.mcp_terminal.tools.terminal.get_controller"
        )
        self.mock_get_controller = self.controller_patcher.start()
        self.mock_controller = AsyncMock()
        self.mock_get_controller.return_value = self.mock_controller

        # Mock successful command execution
        self.mock_controller.execute_command.return_value = {
            "success": True,
            "output": "Command output",
            "error": None,
        }

    def tearDown(self):
        """Clean up test resources."""
        # Close and remove temporary files
        self.whitelist_file.close()
        self.blacklist_file.close()
        os.unlink(self.whitelist_file.name)
        os.unlink(self.blacklist_file.name)

        # Stop patches
        self.controller_patcher.stop()

    @patch("src.mcp_terminal.tools.terminal.FastMCP")
    async def test_allowed_command_whitelist_mode(self, mock_fastmcp):
        """Test executing allowed command in whitelist mode."""
        # Setup terminal tool with whitelist mode
        tool = TerminalTool(
            whitelist_file=self.whitelist_file.name, whitelist_mode=True
        )

        # Execute an allowed command
        response = await tool.execute_command(command="ls -la")

        # Check that controller was called
        self.mock_controller.execute_command.assert_called_once_with(
            "ls -la", timeout=10
        )
        self.assertTrue(response.success)

    @patch("src.mcp_terminal.tools.terminal.FastMCP")
    async def test_blocked_command_whitelist_mode(self, mock_fastmcp):
        """Test executing blocked command in whitelist mode."""
        # Setup terminal tool with whitelist mode
        tool = TerminalTool(
            whitelist_file=self.whitelist_file.name, whitelist_mode=True
        )

        # Execute a blocked command
        response = await tool.execute_command(command="rm -rf /")

        # Check that controller was NOT called
        self.mock_controller.execute_command.assert_not_called()
        self.assertFalse(response.success)
        self.assertIn("not allowed", response.error)

    @patch("src.mcp_terminal.tools.terminal.FastMCP")
    async def test_allowed_command_blacklist_mode(self, mock_fastmcp):
        """Test executing allowed command in blacklist mode."""
        # Setup terminal tool with blacklist mode
        tool = TerminalTool(
            blacklist_file=self.blacklist_file.name, whitelist_mode=False
        )

        # Execute an allowed command
        response = await tool.execute_command(command="grep 'test' file.txt")

        # Check that controller was called
        self.mock_controller.execute_command.assert_called_once_with(
            "grep 'test' file.txt", timeout=10
        )
        self.assertTrue(response.success)

    @patch("src.mcp_terminal.tools.terminal.FastMCP")
    async def test_blocked_command_blacklist_mode(self, mock_fastmcp):
        """Test executing blocked command in blacklist mode."""
        # Setup terminal tool with blacklist mode
        tool = TerminalTool(
            blacklist_file=self.blacklist_file.name, whitelist_mode=False
        )

        # Execute a blocked command
        response = await tool.execute_command(command="sudo apt-get update")

        # Check that controller was NOT called
        self.mock_controller.execute_command.assert_not_called()
        self.assertFalse(response.success)
        self.assertIn("not allowed", response.error)

    @patch("src.mcp_terminal.tools.terminal.FastMCP")
    async def test_both_whitelist_blacklist(self, mock_fastmcp):
        """Test using both whitelist and blacklist."""
        # Setup terminal tool with both whitelist and blacklist
        tool = TerminalTool(
            whitelist_file=self.whitelist_file.name,
            blacklist_file=self.blacklist_file.name,
            whitelist_mode=True,  # Whitelist mode takes precedence
        )

        # Test command in whitelist
        response = await tool.execute_command(command="echo Hello")
        self.assertTrue(response.success)

        # Test command in blacklist but also in whitelist
        # In whitelist mode, this should be allowed since whitelist has priority
        self.mock_controller.execute_command.reset_mock()

        # First add this command to the whitelist
        with open(self.whitelist_file.name, "a") as f:
            f.write("rm\n")  # This is also in blacklist

        # Recreate tool to load updated whitelist
        tool = TerminalTool(
            whitelist_file=self.whitelist_file.name,
            blacklist_file=self.blacklist_file.name,
            whitelist_mode=True,
        )

        response = await tool.execute_command(command="rm file.txt")
        self.assertTrue(response.success)


if __name__ == "__main__":
    import asyncio

    # Run the async tests
    def run_async_test(test_case):
        """Run an async test."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(test_case)
            return result
        finally:
            loop.close()

    unittest.main()
