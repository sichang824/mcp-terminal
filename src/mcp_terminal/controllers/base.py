"""
Base terminal controller interface.
All terminal controllers should implement this interface.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseTerminalController(ABC):
    """Base interface for terminal controllers."""

    @abstractmethod
    async def execute_command(
        self, command: str, wait_for_output: bool = True, timeout: int = 10
    ) -> Dict[str, Any]:
        """
        Execute a command in the terminal.

        Args:
            command: The command to execute
            wait_for_output: Whether to wait for output
            timeout: Timeout in seconds

        Returns:
            A dictionary with the result of the command execution
        """
        pass

    @abstractmethod
    async def get_terminal_type(self) -> str:
        """
        Get the terminal type.

        Returns:
            The terminal type
        """
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """
        Clean up resources.
        """
        pass
