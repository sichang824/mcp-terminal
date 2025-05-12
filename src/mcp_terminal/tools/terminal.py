"""
Terminal tool for MCP.
Provides terminal control operations through the MCP interface.
"""

import logging
import os
from typing import Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from mcp_terminal.controllers import get_controller
from mcp_terminal.security.command_filter import CommandFilter

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("MCP:Terminal:Tool")


# Define the models for the execute command function
class ExecuteCommandRequest(BaseModel):
    """Request model for executing a terminal command."""

    command: str = Field(..., description="The command to execute in the terminal")
    wait_for_output: bool = Field(
        True, description="Whether to wait for the command output"
    )
    timeout: int = Field(
        10, description="Timeout in seconds for waiting for the command output"
    )


class ExecuteCommandResponse(BaseModel):
    """Response model for the executed terminal command."""

    success: bool = Field(
        ..., description="Whether the command execution was successful"
    )
    output: Optional[str] = Field(None, description="The command output if available")
    error: Optional[str] = Field(
        None, description="Error message if the command failed"
    )
    return_code: Optional[int] = Field(
        None, description="The command return code if available"
    )
    warning: Optional[str] = Field(None, description="Warning message if any")


class TerminalInfoResponse(BaseModel):
    """Response model for terminal information."""

    terminal_type: str = Field(..., description="The type of terminal being used")
    platform: str = Field(..., description="The platform the terminal is running on")
    current_directory: str = Field(
        ..., description="Current working directory of the terminal"
    )
    user: str = Field(..., description="Current user name")
    shell: Optional[str] = Field(None, description="Shell being used")
    terminal_size: Optional[dict] = Field(
        None, description="Terminal dimensions (rows, columns)"
    )


class TerminalTool:
    """
    MCP tool for terminal operations.

    This tool provides functions to execute commands in the terminal
    and get information about the terminal.
    """

    def __init__(
        self,
        controller_type: Optional[str] = None,
        whitelist_file: Optional[str] = None,
        blacklist_file: Optional[str] = None,
        whitelist_mode: bool = False,
    ):
        """
        Initialize the terminal tool.

        Args:
            controller_type: The type of controller to use ("iterm", "applescript", "subprocess")
                           or None to auto-detect
            whitelist_file: Path to whitelist file
            blacklist_file: Path to blacklist file
            whitelist_mode: If True, only whitelisted commands are allowed
        """
        self.name = "terminal"
        self.controller_type = controller_type
        self.controller = None
        self._init_controller()

        # Initialize command filter
        self.command_filter = CommandFilter(
            whitelist_file=whitelist_file,
            blacklist_file=blacklist_file,
            whitelist_mode=whitelist_mode,
        )

    def _init_controller(self):
        """Initialize the terminal controller."""
        try:
            self.controller = get_controller(self.controller_type)
            logger.info(
                f"Initialized terminal controller: {type(self.controller).__name__}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize terminal controller: {e}")
            raise

    def register_mcp(self, mcp: FastMCP) -> None:
        """Register the terminal tool with the MCP server."""

        @mcp.tool(name="execute_command", description="Executes a terminal command")
        async def execute_command(
            command: str,
            wait_for_output: bool = True,
            timeout: int = 10,
        ) -> ExecuteCommandResponse:
            try:
                # Check if command is allowed
                is_allowed, reason = self.command_filter.is_command_allowed(command)

                if not is_allowed:
                    logger.warning(
                        f"Command execution denied: {command}. Reason: {reason}"
                    )
                    return ExecuteCommandResponse(
                        success=False,
                        error=f"Command not allowed: {reason}",
                    )

                # Ensure we have a controller
                if not self.controller:
                    self._init_controller()

                # Execute the command
                result = await self.controller.execute_command(
                    command, wait_for_output, timeout
                )

                # Convert to response model
                return ExecuteCommandResponse(
                    success=result.get("success", False),
                    output=result.get("output"),
                    error=result.get("error"),
                    return_code=result.get("return_code"),
                    warning=result.get("warning"),
                )
            except Exception as e:
                logger.error(f"Error executing command: {e}")
                return ExecuteCommandResponse(
                    success=False, error=f"Error executing command: {str(e)}"
                )

        @mcp.tool(name="get_terminal_info", description="Gets terminal information")
        async def get_terminal_info() -> TerminalInfoResponse:
            try:
                # Ensure we have a controller
                if not self.controller:
                    self._init_controller()

                # Get terminal type
                terminal_type = await self.controller.get_terminal_type()

                # Get platform
                import getpass
                import os
                import platform
                import shutil

                platform_name = platform.system()

                # Get current directory directly
                current_dir = None
                try:
                    pwd_result = await self.controller.execute_command(
                        "pwd", wait_for_output=True, timeout=5
                    )
                    if pwd_result.get("success") and pwd_result.get("output"):
                        # Clean the output by splitting lines and finding a valid path
                        lines = pwd_result.get("output").splitlines()
                        for line in lines:
                            line = line.strip()
                            # On macOS/Linux, a valid path should start with /
                            if line.startswith("/"):
                                current_dir = line
                                break
                except Exception as e:
                    logger.debug(f"Error getting current directory from terminal: {e}")

                # Fallback to Python's os.getcwd()
                if not current_dir:
                    current_dir = os.getcwd()

                # Get user
                user = getpass.getuser()

                # Get shell
                shell = os.environ.get("SHELL", None)

                # Get terminal size if possible
                terminal_size = None
                try:
                    cols, rows = shutil.get_terminal_size(fallback=(80, 24))
                    terminal_size = {"rows": rows, "columns": cols}
                except Exception:
                    pass

                return TerminalInfoResponse(
                    terminal_type=terminal_type,
                    platform=platform_name,
                    current_directory=current_dir,
                    user=user,
                    shell=shell,
                    terminal_size=terminal_size,
                )
            except Exception as e:
                logger.error(f"Error getting terminal info: {e}")
                return TerminalInfoResponse(
                    terminal_type="unknown",
                    platform="unknown",
                    current_directory="unknown",
                    user="unknown",
                )
