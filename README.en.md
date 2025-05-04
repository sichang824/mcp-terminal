# MCP Terminal

MCP Terminal is a terminal control server based on MCP (Model Context Protocol), designed specifically for integration with Large Language Models (LLMs) and AI assistants. It provides a standardized interface that enables AI to execute terminal commands and retrieve output results.

## Features

- Implemented using the official MCP SDK
- Supports multiple terminal controllers:
  - **iTerm2 Controller**: Provides advanced control on macOS using iTerm2's Python API
  - **AppleScript Controller**: Controls Terminal.app on macOS using AppleScript
  - **Subprocess Controller**: Universal terminal control method for all platforms
- Supports multiple server modes:
  - **STDIO Mode**: Communicates with clients via standard input/output
  - **SSE Mode**: Provides HTTP API via Server-Sent Events
- Offers multiple tools:
  - **Terminal Tool**: Executes commands and retrieves output
  - **File Tool**: Performs file operations (read, write, append, insert)
- Automatically detects the best terminal controller
- Seamless integration with Claude Desktop
- Docker deployment support

## Installation

### Prerequisites

- Python 3.8+
- [uv](https://github.com/astral-sh/uv) package management tool

If you haven't installed uv yet, you can install it with the following commands:

```bash
# On macOS using Homebrew
brew install uv

# On other platforms
pip install uv
```

### Installation with uv (Recommended)

Clone the repository and install dependencies using uv:

```bash
# Clone the repository
git clone https://github.com/yourusername/mcp-terminal.git
cd mcp-terminal

# Create a virtual environment and install basic dependencies
uv venv
source .venv/bin/activate  # On Windows use .venv\Scripts\activate
uv pip install -e .

# If you need iTerm2 support (macOS only)
uv pip install -e ".[iterm]"

# If you need development tools (testing, code formatting, etc.)
uv pip install -e ".[dev]"
```

### Installation using Makefile

We provide a Makefile to simplify common operations:

```bash
# Install basic dependencies
make setup

# Install iTerm2 support
make setup-iterm

# Install development dependencies
make setup-dev
```

### Installation using Docker

We provide Docker support for quick deployment of the MCP Terminal server:

```bash
# Build the Docker image
docker build -t mcp-terminal .

# Run the Docker container (SSE mode, port 8000)
docker run -p 8000:8000 mcp-terminal
```

Or use docker-compose:

```bash
# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

## Usage

### Running the MCP Terminal Server

There are multiple ways to start the server:

```bash
# Run directly with Python (defaults to stdio mode and auto-detected terminal controller)
python mcp_terminal.py

# Run with Makefile (stdio mode)
make run-stdio

# Run with Makefile (SSE mode)
make run-sse

# Use a specific controller
make run-iterm     # Use iTerm2 controller
make run-applescript  # Use AppleScript controller
make run-subprocess   # Use Subprocess controller
```

### Running with Docker

Run the MCP Terminal server using Docker (defaults to SSE mode and Subprocess controller):

```bash
# Run directly
docker run -p 8000:8000 mcp-terminal

# Use a custom port
docker run -p 9000:8000 mcp-terminal

# Mount current directory (for local file access)
docker run -p 8000:8000 -v $(pwd):/workspace mcp-terminal
```

Default configuration:

- Server mode: SSE
- Host: 0.0.0.0 (allows remote connections)
- Port: 8000
- Controller: subprocess (suitable for containerized environments)

You can customize the configuration by modifying the Dockerfile or docker-compose.yml file.

### Claude Desktop Integration Configuration Example

Here's an example configuration for Claude Desktop:

```json
{
  "mcpServers": {
    "terminal": {
      "command": "/Users/ann/Workspace/mcp-terminal/.venv/bin/python",
      "args": [
        "/Users/ann/Workspace/mcp-terminal/mcp_terminal.py",
        "--controller",
        "subprocess"
      ]
    }
  }
}
```

### Command Line Options

The server supports various command line options:

```bash
python mcp_terminal.py --help
```

Main options:

- `--controller` or `-c`: Specify terminal controller type (auto, iterm, applescript, subprocess)
- `--mode` or `-m`: Specify server mode (stdio, sse)
- `--host`: Specify host address for SSE mode
- `--port` or `-p`: Specify port for SSE mode
- `--log-level` or `-l`: Specify logging level

## Integration with Claude Desktop

MCP Terminal can be seamlessly integrated with Claude Desktop to provide terminal control capabilities to Claude.

### Configuration Steps

1. **Start the MCP Terminal Server** (in stdio mode):

   ```bash
   # Run in a terminal window
   make run-stdio
   ```

2. **Configure Claude Desktop to use the MCP Server**:

   Open Claude Desktop, then:

   - Click the settings icon (usually in the top right corner)
   - Navigate to the "Extensions" or "Tools" tab
   - Enable the "Custom Tools" feature
   - Add the MCP Terminal configuration:
     - Tool name: Terminal
     - Tool path: Enter the full path to mcp_terminal.py
     - Use stdio mode: Check this option
     - Save the configuration

3. **Test the Integration**:

   In your conversation with Claude, you can now ask Claude to execute terminal commands, such as:

   - "Please list the files in my home directory"
   - "Check my current Python version"
   - "Create a new directory and write the current date to a file"

### Troubleshooting

If the integration is not working properly:

1. Make sure the MCP Terminal server is running
2. Check the log output for errors
3. Verify that the Claude Desktop tool configuration is correct
4. Try restarting both Claude Desktop and the MCP Terminal server

## API Specification

MCP Terminal provides the following MCP functions:

### execute_command

Executes a terminal command and retrieves the output.

**Parameters**:

- `command` (string): The command to execute
- `wait_for_output` (boolean, optional): Whether to wait for and return command output, defaults to true
- `timeout` (integer, optional): Timeout in seconds for waiting for output, defaults to 10

**Returns**:

- `success` (boolean): Whether the command executed successfully
- `output` (string, optional): The command output
- `error` (string, optional): Error message if the command failed
- `return_code` (integer, optional): The command return code
- `warning` (string, optional): Warning message

### get_terminal_info

Gets terminal information.

**Parameters**: None

**Returns**:

- `terminal_type` (string): The type of terminal being used
- `platform` (string): The running platform

### file_modify

Writes, appends, or inserts content to a file.

**Parameters**:

- `filepath` (string): File path
- `content` (string): Content to write
- `mode` (string, optional): Writing mode, options are "overwrite", "append", or "insert", defaults to "overwrite"
- `position` (integer, optional): Insertion position when using "insert" mode
- `create_dirs` (boolean, optional): Whether to create directories if they don't exist, defaults to true

**Returns**:

- `success` (boolean): Whether the operation was successful
- `error` (string, optional): Error message if the operation failed
- `filepath` (string): Path to the file that was operated on
- `details` (object, optional): Additional operation details

## Security Considerations

MCP Terminal allows execution of arbitrary terminal commands, which may pose security risks. When using it in a production environment, you should:

1. Limit the server to accepting connections only from trusted sources
2. Consider implementing command whitelists or blacklists
3. Regularly audit executed commands
4. Run the server under a dedicated account with limited permissions

## Development

### Directory Structure

```
mcp-terminal/
├── mcp_terminal.py            # Entry point script
├── pyproject.toml             # Project configuration and dependencies
├── README.md                  # Project documentation
├── Makefile                   # Build and run commands
├── Dockerfile                 # Docker build configuration
├── docker-compose.yml         # Docker Compose configuration
├── src/
│   ├── __init__.py
│   └── mcp_terminal/
│       ├── __init__.py
│       ├── server.py          # Main server implementation
│       ├── controllers/
│       │   ├── __init__.py    # Controller factory and imports
│       │   ├── base.py        # Base controller interface
│       │   ├── subprocess.py  # Universal subprocess controller
│       │   ├── applescript.py # AppleScript controller
│       │   └── iterm.py       # iTerm2 API controller
│       └── tools/
│           ├── __init__.py
│           ├── terminal.py    # Terminal operation tool
│           └── file.py        # File operation tool
└── tests/                     # Test directory
    ├── __init__.py
    └── test_subprocess_controller.py
```

### Running Tests

```bash
# Run all tests using pytest
make test

# Or directly using pytest
pytest tests/
```

### Code Formatting

```bash
# Check code formatting
make lint

# Automatically format code
make format
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Submit a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
