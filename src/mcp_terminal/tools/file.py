#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File tool for MCP.
Provides file operations through the MCP interface.
"""

import logging
import os
from enum import Enum
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("MCP:Terminal:FileTool")


class WriteMode(str, Enum):
    """Enum representing different file writing modes."""

    OVERWRITE = "overwrite"  # Overwrite the entire file
    APPEND = "append"  # Append to the end of the file
    INSERT = "insert"  # Insert at a specific position


# Define the models for the write_file function
class WriteFileRequest(BaseModel):
    """Request model for writing to a file."""

    filepath: str = Field(..., description="Path to the file to write")
    content: str = Field(..., description="Content to write to the file")
    mode: WriteMode = Field(
        WriteMode.OVERWRITE, description="Writing mode (overwrite, append, or insert)"
    )
    position: Optional[int] = Field(
        None, description="Position to insert content (only used with insert mode)"
    )
    create_dirs: bool = Field(
        True, description="Create parent directories if they don't exist"
    )


class FileOperationResponse(BaseModel):
    """Response model for file operations."""

    success: bool = Field(..., description="Whether the operation was successful")
    error: Optional[str] = Field(
        None, description="Error message if the operation failed"
    )
    filepath: str = Field(..., description="Path to the file that was operated on")
    details: Optional[Dict[str, Any]] = Field(
        None, description="Additional operation details"
    )


class FileTool:
    """
    MCP tool for file operations.

    This tool provides functions to perform various file operations
    such as reading, writing, and manipulating files.
    """

    name = "file"

    def register_mcp(self, mcp: FastMCP) -> None:
        """Register the file tool with the MCP server."""

        @mcp.tool(name="file_modify", description="Writes content to a file")
        async def file_modify(
            filepath: str,
            content: str,
            mode: WriteMode = WriteMode.OVERWRITE,
            position: Optional[int] = None,
            create_dirs: bool = True,
        ) -> FileOperationResponse:
            try:
                # Create directories if they don't exist
                if create_dirs:
                    directory = os.path.dirname(filepath)
                    if directory and not os.path.exists(directory):
                        os.makedirs(directory)

                # Handle different write modes
                details = {"mode": mode}

                if mode == WriteMode.INSERT:
                    if position is None:
                        raise ValueError(
                            "Position must be specified when using INSERT mode"
                        )

                    # Read existing content if file exists
                    existing_content = ""
                    if os.path.exists(filepath):
                        with open(filepath, "r", encoding="utf-8") as f:
                            existing_content = f.read()

                    # Insert the new content at the specified position
                    position = min(position, len(existing_content))
                    new_content = (
                        existing_content[:position]
                        + content
                        + existing_content[position:]
                    )
                    details["position"] = position

                    # Write the combined content
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(new_content)

                elif mode == WriteMode.APPEND:
                    # Append to file
                    with open(filepath, "a", encoding="utf-8") as f:
                        f.write(content)

                else:  # OVERWRITE
                    # Overwrite file
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(content)

                return FileOperationResponse(
                    success=True, filepath=filepath, details=details
                )

            except Exception as e:
                logger.error(f"Error writing to file {filepath}: {e}")
                return FileOperationResponse(
                    success=False,
                    error=f"Error writing to file: {str(e)}",
                    filepath=filepath,
                )
