"""
Terminal tool for MCP.
Provides terminal control operations through the MCP interface.
"""

import logging
from typing import Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from mcp_terminal.controllers import get_controller

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


class TerminalTool:
    """
    MCP tool for terminal operations.

    This tool provides functions to execute commands in the terminal
    and get information about the terminal.
    """

    def __init__(self, controller_type: Optional[str] = None):
        """
        Initialize the terminal tool.

        Args:
            controller_type: The type of controller to use ("iterm", "applescript", "subprocess")
                           or None to auto-detect
        """
        self.name = "terminal"
        self.controller_type = controller_type
        self.controller = None
        self._init_controller()

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
                import platform

                platform_name = platform.system()

                return TerminalInfoResponse(
                    terminal_type=terminal_type,
                    platform=platform_name,
                )
            except Exception as e:
                logger.error(f"Error getting terminal info: {e}")
                return TerminalInfoResponse(
                    terminal_type="unknown",
                    platform="unknown",
                )
