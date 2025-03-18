"""
iTerm2 controller using the official iTerm2 Python API.
This provides more advanced control over iTerm2.
"""

import asyncio
import platform
import time
from typing import Any, Dict, List, Optional

try:
    import iterm2

    ITERM2_AVAILABLE = True
except ImportError:
    ITERM2_AVAILABLE = False

from mcp_terminal.controllers.base import BaseTerminalController


class ITermController(BaseTerminalController):
    """Terminal controller using the iTerm2 Python API."""

    def __init__(self):
        """Initialize the iTerm2 controller."""
        if platform.system() != "Darwin":
            raise RuntimeError("iTerm2 controller only works on macOS")

        if not ITERM2_AVAILABLE:
            raise ImportError(
                "iTerm2 Python API not available. Install with 'pip install iterm2'"
            )

        self.connection = None
        self.app = None
        self.current_session = None

    async def _ensure_connection(self) -> bool:
        """
        Ensure connection to iTerm2.

        Returns:
            True if connected, False otherwise
        """
        if self.connection is not None:
            return True

        try:
            self.connection = await iterm2.Connection.async_create()
            self.app = await iterm2.async_get_app(self.connection)
            return True
        except Exception as e:
            print(f"Failed to connect to iTerm2: {e}")
            return False

    async def _ensure_session(self) -> Optional[iterm2.Session]:
        """
        Ensure there's an active window and session.

        Returns:
            The active session or None if failed
        """
        # First, use AppleScript to ensure iTerm2 is running with a window and tab
        try:
            import subprocess
            import time

            print(
                "Ensuring iTerm2 is running with a window and tab using AppleScript..."
            )

            # AppleScript to launch iTerm2, create a window if none exists, and create a tab if none exists
            applescript = """
            tell application "iTerm2"
                activate
                if (count of windows) is 0 then
                    create window with default profile
                end if
                tell current window
                    if (count of tabs) is 0 then
                        create tab with default profile
                    end if
                    tell current session
                        -- Just to ensure the session is ready
                        write text ""
                    end tell
                end tell
            end tell
            """

            # Run the AppleScript
            result = subprocess.run(
                ["osascript", "-e", applescript], capture_output=True, text=True
            )

            if result.returncode != 0:
                print(f"Error running AppleScript: {result.stderr}")
            else:
                print("Successfully launched iTerm2 with AppleScript")

            # Wait for iTerm2 to fully initialize
            time.sleep(3)

        except Exception as e:
            print(f"Error launching iTerm2 with AppleScript: {e}")

        # Try to ensure connection multiple times
        max_attempts = 5  # Increased number of attempts
        for attempt in range(max_attempts):
            if await self._ensure_connection():
                print(f"Successfully connected to iTerm2 on attempt {attempt+1}")
                break
            print(f"Connection attempt {attempt+1}/{max_attempts} failed. Retrying...")
            await asyncio.sleep(2)  # Longer delay between attempts
        else:
            print("Failed to connect to iTerm2 after multiple attempts")
            return None

        try:
            # Get all windows
            windows = await self.app.async_get_windows()
            if not windows:
                print("No windows found even after AppleScript initialization")
                return None

            window = windows[0]
            print(f"Found {len(windows)} window(s)")

            # Get all tabs
            tabs = await window.async_get_tabs()
            if not tabs:
                print("No tabs found even after AppleScript initialization")
                return None

            tab = tabs[0]
            print(f"Found {len(tabs)} tab(s)")

            # Get current session
            self.current_session = await tab.async_get_active_session()
            if self.current_session is None:
                print("No active session found even after AppleScript initialization")
                return None

            print("Successfully obtained iTerm2 session")
            return self.current_session
        except Exception as e:
            print(f"Error ensuring iTerm2 session: {e}")
            return None

    async def execute_command(
        self, command: str, wait_for_output: bool = True, timeout: int = 10
    ) -> Dict[str, Any]:
        """
        Execute a command in iTerm2.

        Args:
            command: The command to execute
            wait_for_output: Whether to wait for output
            timeout: Timeout in seconds

        Returns:
            A dictionary with the result of the command execution
        """
        try:
            session = await self._ensure_session()
            if session is None:
                return {
                    "success": False,
                    "error": "Failed to get iTerm2 session",
                }

            # Send the command
            await session.async_send_text(command + "\n")

            if wait_for_output:
                # Wait for a moment to let the command execute
                await asyncio.sleep(0.5)

                # Initialize variables for capturing output
                start_time = time.time()
                initial_lines = await session.async_get_screen_contents()
                last_line_count = len(initial_lines.contents)
                last_update = time.time()

                # Wait for output to stop changing
                while True:
                    # Check if we've exceeded the timeout
                    current_time = time.time()
                    if current_time - start_time > timeout:
                        break

                    # Get current screen contents
                    screen = await session.async_get_screen_contents()
                    current_line_count = len(screen.contents)

                    # If output has changed, update the last_update time
                    if current_line_count != last_line_count:
                        last_line_count = current_line_count
                        last_update = current_time

                    # If output hasn't changed for a second, we're probably done
                    if current_time - last_update > 1.0:
                        break

                    # Sleep to avoid consuming too much CPU
                    await asyncio.sleep(0.2)

                # Get the final output
                screen = await session.async_get_screen_contents()
                lines = [line.string for line in screen.contents]

                # Try to extract just the command output by removing the command itself
                try:
                    # Find the command in the output
                    cmd_line_index = -1
                    for i, line in enumerate(lines):
                        if command in line:
                            cmd_line_index = i
                            break

                    # If we found the command, return everything after it
                    if cmd_line_index >= 0 and cmd_line_index < len(lines) - 1:
                        output = "\n".join(lines[cmd_line_index + 1 :])
                    else:
                        output = "\n".join(lines)

                    return {"success": True, "output": output}
                except Exception as e:
                    # If parsing fails, return all output
                    return {
                        "success": True,
                        "output": "\n".join(lines),
                        "parse_error": str(e),
                    }

            return {"success": True, "output": "Command sent (output not captured)"}

        except Exception as e:
            return {"success": False, "error": f"Error executing command: {str(e)}"}

    async def get_terminal_type(self) -> str:
        """
        Get the terminal type.

        Returns:
            The terminal type
        """
        return "iTerm2"

    async def cleanup(self) -> None:
        """
        Clean up resources.
        """
        try:
            if self.connection:
                # Try to close the connection gracefully
                try:
                    await asyncio.wait_for(self.connection.async_close(), timeout=2.0)
                except asyncio.TimeoutError:
                    # If it times out, log a warning but continue cleanup
                    print("Warning: iTerm2 connection close timed out")
                except Exception as e:
                    # If any other error occurs, log it but continue cleanup
                    print(f"Error closing iTerm2 connection: {e}")

                # Ensure references are cleared even if close fails
                self.connection = None
                self.app = None
                self.current_session = None
        except Exception as e:
            print(f"Error during iTerm2 controller cleanup: {e}")


if __name__ == "__main__":
    controller = ITermController()
    print(controller.execute_command("ls -l"))
