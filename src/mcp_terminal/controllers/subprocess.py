"""
Subprocess terminal controller.
Uses Python's subprocess module to execute commands.
Works on all platforms.
"""

import asyncio
from typing import Any, Dict

from mcp_terminal.controllers.base import BaseTerminalController


class SubprocessTerminalController(BaseTerminalController):
    """Terminal controller using subprocess."""

    async def execute_command(
        self, command: str, wait_for_output: bool = True, timeout: int = 10
    ) -> Dict[str, Any]:
        """
        Execute a command using subprocess.

        Args:
            command: The command to execute
            wait_for_output: Whether to wait for output
            timeout: Timeout in seconds

        Returns:
            A dictionary with the result of the command execution
        """
        try:
            # Create subprocess
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            if wait_for_output:
                try:
                    # Wait for the process to complete with timeout
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(), timeout=timeout
                    )

                    return {
                        "success": process.returncode == 0,
                        "output": stdout.decode("utf-8", errors="replace"),
                        "error": stderr.decode("utf-8", errors="replace"),
                        "return_code": process.returncode,
                    }
                except asyncio.TimeoutError:
                    # Kill the process if it times out
                    try:
                        process.kill()
                    except ProcessLookupError:
                        pass
                    return {
                        "success": False,
                        "error": f"Command timed out after {timeout} seconds",
                    }
            else:
                # Don't wait for output
                return {
                    "success": True,
                    "output": "Command sent (output not captured)",
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error executing command: {str(e)}",
            }

    async def get_terminal_type(self) -> str:
        """
        Get the terminal type.

        Returns:
            The terminal type
        """
        return "subprocess"

    async def cleanup(self) -> None:
        """
        Clean up resources.
        """
        pass  # No resources to clean up
