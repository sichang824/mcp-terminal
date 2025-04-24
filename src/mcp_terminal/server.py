#!/usr/bin/env python3
"""
MCP Terminal Server

This module implements a terminal control server using the Model Context Protocol (MCP).
It supports both standard input/output (stdio) and Server-Sent Events (SSE) transports.
"""

import argparse
import asyncio
import logging
import platform
import signal
import sys
from enum import Enum
from typing import Optional

from mcp.server.fastmcp import FastMCP

from mcp_terminal.tools.file import FileTool
from mcp_terminal.tools.terminal import TerminalTool

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("MCP:Terminal:Server")


class ServerMode(str, Enum):
    """Server transport modes."""

    STDIO = "stdio"
    SSE = "sse"


class MCPTerminalServer:
    """
    MCP Terminal Server that registers and exposes terminal tools.
    """

    def __init__(
        self,
        controller_type: Optional[str] = None,
        mode: ServerMode = ServerMode.STDIO,
        host: str = "127.0.0.1",
        port: int = 3000,
        log_level: str = "INFO",
    ):
        """
        Initialize the MCP Terminal Server.

        Args:
            controller_type: Type of terminal controller to use ("iterm", "applescript", "subprocess")
            mode: Server transport mode (stdio or sse)
            host: Host to bind the server to (for SSE mode)
            port: Port to bind the server to (for SSE mode)
            log_level: Logging level
        """
        self.controller_type = controller_type
        self.mode = mode
        self.host = host
        self.port = port

        # Set up logging
        logging.getLogger().setLevel(getattr(logging, log_level))

        # Create MCP server
        self.mcp = FastMCP("mcp-terminal", host=host, port=port, log_level=log_level)

        self.tools = {}
        self.tools_registered = False

    def register_tools(self) -> None:
        """
        Register all tools with the MCP server.
        """
        if self.tools_registered:
            return

        logger.info("Registering terminal tool with MCP server")

        try:
            # Create and register the terminal tool
            terminal_tool = TerminalTool(self.controller_type)
            file_tool = FileTool()
            terminal_tool.register_mcp(self.mcp)
            file_tool.register_mcp(self.mcp)
            self.tools["terminal"] = terminal_tool
            self.tools["file"] = file_tool

            self.tools_registered = True
            logger.info("Terminal tool registered with MCP server")
        except Exception as e:
            logger.error(f"Failed to register terminal tool: {str(e)}", exc_info=True)
            raise

    async def start(self) -> None:
        """
        Start the MCP Terminal Server.
        """
        # Register all tools
        self.register_tools()

        # Start the server using the appropriate transport
        if self.mode == ServerMode.SSE:
            logger.info(
                f"Starting MCP Terminal Server in SSE mode on {self.host}:{self.port}"
            )
            await self.mcp.run_sse_async()
        else:  # STDIO mode
            logger.info("Starting MCP Terminal Server in stdio mode")
            await self.mcp.run_stdio_async()

    async def cleanup(self) -> None:
        """
        Clean up resources before shutting down.
        """
        logger.info("Starting cleanup process")

        # First ensure MCP resources are properly cleaned up
        if hasattr(self.mcp, "_mcp_server") and hasattr(
            self.mcp._mcp_server, "_task_group"
        ):
            logger.info("Ensuring MCP task groups are properly closed")
            try:
                # Give in-flight requests a chance to complete
                await asyncio.sleep(0.1)
            except Exception as e:
                logger.warning(f"Error during MCP cleanup delay: {e}")

        # Then clean up tool controllers
        for tool_name, tool in self.tools.items():
            if hasattr(tool, "controller") and hasattr(tool.controller, "cleanup"):
                logger.info(f"Cleaning up {tool_name} controller")
                try:
                    await tool.controller.cleanup()
                except Exception as e:
                    logger.warning(f"Error cleaning up {tool_name} controller: {e}")

        logger.info("Cleanup process completed")


def main() -> None:
    """
    Main entry point for the MCP Terminal Server.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="MCP Terminal Server")

    # Terminal controller options
    controller_group = parser.add_argument_group("Terminal Controller Options")
    controller_group.add_argument(
        "--controller",
        "-c",
        choices=["auto", "iterm", "applescript", "subprocess"],
        default="auto",
        help="Terminal controller to use (default: auto-detect)",
    )

    # Server mode options
    server_group = parser.add_argument_group("Server Options")
    server_group.add_argument(
        "--mode",
        "-m",
        choices=[mode.value for mode in ServerMode],
        default=ServerMode.STDIO.value,
        help=f"Server mode (default: {ServerMode.STDIO.value})",
    )
    server_group.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind the server to in SSE mode (default: 127.0.0.1)",
    )
    server_group.add_argument(
        "--port",
        "-p",
        type=int,
        default=3000,
        help="Port to bind the server to in SSE mode (default: 3000)",
    )

    # Logging options
    logging_group = parser.add_argument_group("Logging Options")
    logging_group.add_argument(
        "--log-level",
        "-l",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Logging level (default: INFO)",
    )

    args = parser.parse_args()

    # Determine controller type
    controller_type = None if args.controller == "auto" else args.controller

    # Adjust controller based on platform
    if controller_type in ["iterm", "applescript"] and platform.system() != "Darwin":
        logger.warning(
            f"{controller_type} controller not available on {platform.system()}. Falling back to subprocess."
        )
        controller_type = "subprocess"

    # Create the server
    server = MCPTerminalServer(
        controller_type=controller_type,
        mode=args.mode,
        host=args.host,
        port=args.port,
        log_level=args.log_level,
    )

    # Run the server
    loop = asyncio.get_event_loop()
    shutdown_in_progress = False

    # Define a shutdown handler that ensures we only run shutdown once
    async def handle_shutdown():
        nonlocal shutdown_in_progress
        if shutdown_in_progress:
            logger.info("Shutdown already in progress, ignoring additional signal")
            return

        shutdown_in_progress = True
        await shutdown(loop, server)

    try:
        # Set up signal handlers for graceful shutdown
        if (
            sys.platform != "win32"
        ):  # Windows doesn't support SIGTERM/SIGINT handling in the same way
            for signal_name in ["SIGTERM", "SIGINT"]:
                loop.add_signal_handler(
                    getattr(signal, signal_name),
                    lambda: asyncio.create_task(handle_shutdown()),
                )

        # Run the server
        loop.run_until_complete(server.start())
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
        # Handle KeyboardInterrupt manually by running the shutdown coroutine
        if not shutdown_in_progress:
            try:
                # Make sure we properly shut down even if interrupted
                loop.run_until_complete(handle_shutdown())
            except Exception as e:
                logger.error(f"Error during shutdown after keyboard interrupt: {e}")
    except Exception as e:
        logger.error(f"Error during server execution: {e}", exc_info=True)
    finally:
        logger.info("Server shutting down")

        # Close the event loop
        try:
            # Gather any remaining tasks
            pending = asyncio.all_tasks(loop)
            if pending:
                # Cancel all remaining tasks
                for task in pending:
                    task.cancel()

                # Use a separate try/except block to avoid suppressing the original exception
                try:
                    # Wait for a short time for tasks to cancel
                    loop.run_until_complete(asyncio.wait(pending, timeout=0.5))
                except (asyncio.CancelledError, RuntimeError):
                    # Ignore cancelled errors and "Event loop stopped before Future completed"
                    pass
        except Exception as e:
            logger.error(f"Error during final cleanup: {e}")
        finally:
            # Close the event loop
            try:
                loop.close()
            except Exception as e:
                logger.error(f"Error closing event loop: {e}")

        # Exit with a success code
        sys.exit(0)


async def shutdown(loop, server):
    """Handle graceful shutdown."""
    logger.info("Shutdown signal received")

    # Give pending tasks a chance to complete
    await asyncio.sleep(0.2)

    # Perform cleanup
    await server.cleanup()

    # Cancel all running tasks
    tasks = [t for t in asyncio.all_tasks(loop) if t is not asyncio.current_task()]
    if tasks:
        logger.info(f"Cancelling {len(tasks)} pending tasks")
        for task in tasks:
            task.cancel()

        # Wait for tasks to cancel with a timeout
        try:
            await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=3.0,  # Increased timeout
            )
        except asyncio.TimeoutError:
            logger.warning("Some tasks did not cancel within the timeout period")
        except Exception as e:
            logger.warning(f"Error during task cancellation: {e}")

    # Stop the loop
    loop.stop()


if __name__ == "__main__":
    main()
