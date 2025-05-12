"""
Command filtering module for MCP Terminal.
Provides functionality to whitelist and blacklist commands.
"""

import logging
import os
import re
from typing import List, Optional, Set, Tuple

# Configure logging
logger = logging.getLogger("MCP:Terminal:Security")


class CommandFilter:
    """
    Filter for terminal commands based on whitelist and blacklist.
    """

    def __init__(
        self,
        whitelist_file: Optional[str] = None,
        blacklist_file: Optional[str] = None,
        whitelist_mode: bool = False,
    ):
        """
        Initialize command filter.

        Args:
            whitelist_file: Path to whitelist file
            blacklist_file: Path to blacklist file
            whitelist_mode: If True, only whitelisted commands are allowed.
                           If False, all commands except blacklisted ones are allowed.
        """
        self.whitelist_file = whitelist_file
        self.blacklist_file = blacklist_file
        self.whitelist_mode = whitelist_mode
        self.whitelist: Set[str] = set()
        self.blacklist: Set[str] = set()

        # Load lists if files are provided
        if whitelist_file:
            self._load_list(whitelist_file, self.whitelist)
        if blacklist_file:
            self._load_list(blacklist_file, self.blacklist)

    def _load_list(self, file_path: str, command_set: Set[str]) -> None:
        """
        Load commands from a file into a set.

        Args:
            file_path: Path to the command list file
            command_set: Set to load the commands into
        """
        if not file_path or not os.path.exists(file_path):
            logger.warning(f"Command list file not found: {file_path}")
            return

        try:
            with open(file_path, "r") as f:
                for line in f:
                    # Skip comments and empty lines
                    line = line.strip()
                    if line and not line.startswith("#"):
                        command_set.add(line)
            logger.info(f"Loaded {len(command_set)} commands from {file_path}")
        except Exception as e:
            logger.error(f"Error loading command list from {file_path}: {e}")

    def is_command_allowed(self, command: str) -> Tuple[bool, Optional[str]]:
        """
        Check if a command is allowed based on whitelist/blacklist rules.

        Args:
            command: The command to check

        Returns:
            Tuple of (is_allowed, reason_if_not_allowed)
        """
        # Extract the base command (usually the first word before any arguments)
        base_command = command.split()[0] if command else ""

        # In whitelist mode, command must be in the whitelist
        if self.whitelist_mode:
            if not self.whitelist:
                logger.warning("Whitelist mode enabled but whitelist is empty")
                return False, "Whitelist mode enabled but whitelist is empty"

            for allowed_cmd in self.whitelist:
                # Match whole command or pattern
                if base_command == allowed_cmd or self._match_pattern(
                    command, allowed_cmd
                ):
                    return True, None

            return False, f"Command not in whitelist: {base_command}"

        # In blacklist mode, command must not be in the blacklist
        else:
            for blocked_cmd in self.blacklist:
                # Match whole command or pattern
                if base_command == blocked_cmd or self._match_pattern(
                    command, blocked_cmd
                ):
                    return False, f"Command blacklisted: {base_command}"

            return True, None

    def _match_pattern(self, command: str, pattern: str) -> bool:
        """
        Check if a command matches a pattern.
        Patterns starting with ^ are treated as regular expressions.

        Args:
            command: The command to check
            pattern: The pattern to match against

        Returns:
            True if command matches the pattern
        """
        if pattern.startswith("^"):
            try:
                return bool(re.match(pattern, command))
            except re.error:
                logger.error(f"Invalid regex pattern: {pattern}")
                return False

        return False
