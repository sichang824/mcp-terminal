"""
Tests for the command filtering functionality.
"""

import os
import sys
import tempfile
import unittest

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Direct import from file
from src.mcp_terminal.security.command_filter import CommandFilter


class TestCommandFilter(unittest.TestCase):
    """Test cases for the command filtering functionality."""

    def setUp(self):
        """Set up the test case."""
        # Create temporary files for whitelist and blacklist
        self.whitelist_file = tempfile.NamedTemporaryFile(mode="w+", delete=False)
        self.blacklist_file = tempfile.NamedTemporaryFile(mode="w+", delete=False)

        # Write test data to whitelist
        self.whitelist_file.write("# Whitelist test file\n")
        self.whitelist_file.write("ls\n")
        self.whitelist_file.write("cat\n")
        self.whitelist_file.write("pwd\n")
        self.whitelist_file.write("^git.*\n")  # Regex pattern for git commands
        self.whitelist_file.flush()

        # Write test data to blacklist
        self.blacklist_file.write("# Blacklist test file\n")
        self.blacklist_file.write("rm\n")
        self.blacklist_file.write("sudo\n")
        self.blacklist_file.write("^.*eval.*\n")  # Regex pattern containing eval
        self.blacklist_file.flush()

    def tearDown(self):
        """Clean up test resources."""
        # Close and remove temporary files
        self.whitelist_file.close()
        self.blacklist_file.close()
        os.unlink(self.whitelist_file.name)
        os.unlink(self.blacklist_file.name)

    def test_init_without_files(self):
        """Test initializing CommandFilter without files."""
        cmd_filter = CommandFilter()
        self.assertEqual(len(cmd_filter.whitelist), 0)
        self.assertEqual(len(cmd_filter.blacklist), 0)

    def test_init_with_files(self):
        """Test initializing CommandFilter with files."""
        cmd_filter = CommandFilter(
            whitelist_file=self.whitelist_file.name,
            blacklist_file=self.blacklist_file.name,
        )
        # Check whitelist loaded correctly (4 commands)
        self.assertEqual(len(cmd_filter.whitelist), 4)
        self.assertIn("ls", cmd_filter.whitelist)
        self.assertIn("cat", cmd_filter.whitelist)
        self.assertIn("pwd", cmd_filter.whitelist)
        self.assertIn("^git.*", cmd_filter.whitelist)

        # Check blacklist loaded correctly (3 commands)
        self.assertEqual(len(cmd_filter.blacklist), 3)
        self.assertIn("rm", cmd_filter.blacklist)
        self.assertIn("sudo", cmd_filter.blacklist)
        self.assertIn("^.*eval.*", cmd_filter.blacklist)

    def test_whitelist_mode(self):
        """Test whitelist mode functionality."""
        cmd_filter = CommandFilter(
            whitelist_file=self.whitelist_file.name, whitelist_mode=True
        )

        # Test allowed commands in whitelist mode
        allowed, _ = cmd_filter.is_command_allowed("ls -la")
        self.assertTrue(allowed)

        allowed, _ = cmd_filter.is_command_allowed("cat file.txt")
        self.assertTrue(allowed)

        allowed, _ = cmd_filter.is_command_allowed("git status")
        self.assertTrue(allowed)

        allowed, _ = cmd_filter.is_command_allowed("git clone repo")
        self.assertTrue(allowed)

        # Test blocked commands in whitelist mode
        allowed, reason = cmd_filter.is_command_allowed("rm file.txt")
        self.assertFalse(allowed)
        self.assertIn("not in whitelist", reason)

        allowed, reason = cmd_filter.is_command_allowed("docker ps")
        self.assertFalse(allowed)
        self.assertIn("not in whitelist", reason)

    def test_blacklist_mode(self):
        """Test blacklist mode functionality."""
        cmd_filter = CommandFilter(
            blacklist_file=self.blacklist_file.name, whitelist_mode=False
        )

        # Test allowed commands in blacklist mode
        allowed, _ = cmd_filter.is_command_allowed("ls -la")
        self.assertTrue(allowed)

        allowed, _ = cmd_filter.is_command_allowed("cat file.txt")
        self.assertTrue(allowed)

        allowed, _ = cmd_filter.is_command_allowed("echo Hello")
        self.assertTrue(allowed)

        # Test blocked commands in blacklist mode
        allowed, reason = cmd_filter.is_command_allowed("rm file.txt")
        self.assertFalse(allowed)
        self.assertIn("blacklisted", reason)

        allowed, reason = cmd_filter.is_command_allowed("sudo apt-get update")
        self.assertFalse(allowed)
        self.assertIn("blacklisted", reason)

        allowed, reason = cmd_filter.is_command_allowed(
            "python -c 'eval(\"print(1)\")'"
        )
        self.assertFalse(allowed)
        self.assertIn("blacklisted", reason)

    def test_empty_whitelist_mode(self):
        """Test whitelist mode with empty whitelist."""
        cmd_filter = CommandFilter(whitelist_mode=True)

        allowed, reason = cmd_filter.is_command_allowed("ls")
        self.assertFalse(allowed)
        self.assertIn("whitelist is empty", reason)

    def test_regex_patterns(self):
        """Test regex pattern matching."""
        # Create a filter with specific patterns
        cmd_filter = CommandFilter()
        cmd_filter.whitelist.add("^git (pull|push|status)$")
        cmd_filter.whitelist.add("^ls( -[la]+)?$")
        cmd_filter.whitelist_mode = True

        # Test pattern matching
        allowed, _ = cmd_filter.is_command_allowed("git status")
        self.assertTrue(allowed)

        allowed, _ = cmd_filter.is_command_allowed("git pull")
        self.assertTrue(allowed)

        allowed, _ = cmd_filter.is_command_allowed("ls")
        self.assertTrue(allowed)

        allowed, _ = cmd_filter.is_command_allowed("ls -la")
        self.assertTrue(allowed)

        # Test non-matching patterns
        allowed, _ = cmd_filter.is_command_allowed("git clone")
        self.assertFalse(allowed)

        allowed, _ = cmd_filter.is_command_allowed("ls -R")
        self.assertFalse(allowed)

    def test_invalid_regex_pattern(self):
        """Test handling invalid regex patterns."""
        cmd_filter = CommandFilter()
        cmd_filter.whitelist.add("^*invalid")  # Invalid regex
        cmd_filter.whitelist_mode = True

        # Should not raise exception, but should not match
        allowed, _ = cmd_filter.is_command_allowed("invalid regex")
        self.assertFalse(allowed)


if __name__ == "__main__":
    unittest.main()
