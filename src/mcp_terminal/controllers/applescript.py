"""
AppleScript terminal controller.
Uses AppleScript to control the macOS Terminal app.
"""

import asyncio
import platform
import time
from typing import Any, Dict, List

from mcp_terminal.controllers.base import BaseTerminalController


class AppleScriptTerminalController(BaseTerminalController):
    """Terminal controller using AppleScript for macOS Terminal."""

    def __init__(self):
        """Initialize the AppleScript terminal controller."""
        if platform.system() != "Darwin":
            raise RuntimeError("AppleScript controller only works on macOS")

    async def execute_command(
        self, command: str, wait_for_output: bool = True, timeout: int = 10
    ) -> Dict[str, Any]:
        """
        Execute a command in macOS Terminal using AppleScript.

        Args:
            command: The command to execute
            wait_for_output: Whether to wait for output
            timeout: Timeout in seconds

        Returns:
            A dictionary with the result of the command execution
        """
        try:
            # Escape double quotes in the command for AppleScript
            escaped_command = command.replace('"', '\\"')

            # Create AppleScript to execute the command
            script = f"""
            tell application "Terminal"
                activate
                if not (exists window 1) then
                    do script ""
                else
                    do script "" in window 1
                end if
                do script "{escaped_command}" in window 1
            end tell
            """

            # Run the AppleScript
            proc = await asyncio.create_subprocess_exec(
                "osascript",
                "-e",
                script,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            # Wait for the AppleScript to complete
            await proc.wait()

            if wait_for_output:
                # Get output from the Terminal
                return await self._get_terminal_output(command, timeout)
            else:
                return {
                    "success": True,
                    "output": "Command sent (output not captured)",
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error executing command: {str(e)}",
            }

    async def _get_terminal_output(self, command: str, timeout: int) -> Dict[str, Any]:
        """
        Get output from the Terminal app.

        Args:
            command: The command that was executed
            timeout: Timeout in seconds

        Returns:
            A dictionary with the output
        """
        # AppleScript to get Terminal contents
        output_script = """
        tell application "Terminal"
            contents of window 1
        end tell
        """

        start_time = time.time()
        output = ""

        # Poll for output until timeout
        while time.time() - start_time < timeout:
            # Get current terminal content
            proc = await asyncio.create_subprocess_exec(
                "osascript",
                "-e",
                output_script,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            current_output = stdout.decode("utf-8", errors="replace").strip()

            # Check if we have new output
            if current_output and len(current_output) > len(output):
                output = current_output

            # Check if command has completed (output contains command and has more content)
            if command in current_output and len(current_output) > len(command):
                # Try to extract just the output after the command
                try:
                    output_lines = output.split("\n")
                    cmd_index = self._find_command_index(output_lines, command)
                    if cmd_index >= 0 and cmd_index < len(output_lines) - 1:
                        result = "\n".join(output_lines[cmd_index + 1 :])
                        return {"success": True, "output": result}
                except Exception as e:
                    pass  # Fall back to returning all output

                return {"success": True, "output": output}

            # Wait before checking again
            await asyncio.sleep(0.5)

        # If we get here, we timed out
        return {
            "success": True,
            "output": output,
            "warning": f"Command may still be running after {timeout} seconds",
        }

    def _find_command_index(self, lines: List[str], command: str) -> int:
        """
        Find the index of the line containing the command.

        Args:
            lines: List of output lines
            command: Command to find

        Returns:
            Index of the line containing the command, or -1 if not found
        """
        for i, line in enumerate(lines):
            if command in line:
                return i
        return -1

    async def get_terminal_type(self) -> str:
        """
        Get the terminal type.

        Returns:
            The terminal type
        """
        return "macOS Terminal"

    async def cleanup(self) -> None:
        """
        Clean up resources.
        """
        pass  # No resources to clean up
