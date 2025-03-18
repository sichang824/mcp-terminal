.PHONY: setup setup-dev clean install run-stdio run-sse test lint format help

# 默认目标
help:
	@echo "MCP Terminal Makefile"
	@echo ""
	@echo "Usage:"
	@echo "  make setup         安装基本依赖"
	@echo "  make setup-iterm   安装iTerm2支持"
	@echo "  make setup-dev     安装开发依赖"
	@echo "  make install       安装包"
	@echo "  make run-stdio     以stdio模式运行服务器"
	@echo "  make run-sse       以SSE模式运行服务器"
	@echo "  make test          运行测试"
	@echo "  make lint          运行代码检查"
	@echo "  make format        格式化代码"
	@echo "  make clean         清理生成的文件"
	@echo ""

# 使用uv安装基本依赖
setup:
	@echo "Installing dependencies with uv..."
	uv pip install -e .

# 安装iTerm2支持
setup-iterm:
	@echo "Installing iTerm2 support with uv..."
	uv pip install -e ".[iterm]"

# 安装开发依赖
setup-dev:
	@echo "Installing development dependencies with uv..."
	uv pip install -e ".[dev]"

# 安装包
install:
	uv venv .venv
	@echo "Installing package with uv..."
	uv pip install -e .

# 清理生成的文件
clean:
	@echo "Cleaning up..."
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ __pycache__/
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "*.pyd" -delete
	find . -name ".pytest_cache" -type d -exec rm -rf {} +

# 运行stdio模式服务器
run-stdio:
	@echo "Running MCP Terminal server in stdio mode..."
	python mcp_terminal.py

# 运行SSE模式服务器
run-sse:
	@echo "Running MCP Terminal server in SSE mode..."
	python mcp_terminal.py --mode sse --host 127.0.0.1 --port 3000

# 以指定控制器运行
run-iterm:
	@echo "Running MCP Terminal server with iTerm2 controller..."
	python mcp_terminal.py --controller iterm

run-applescript:
	@echo "Running MCP Terminal server with AppleScript controller..."
	python mcp_terminal.py --controller applescript

run-subprocess:
	@echo "Running MCP Terminal server with subprocess controller..."
	python mcp_terminal.py --controller subprocess

# 运行测试
test:
	@echo "Running tests..."
	pytest tests/

# 运行代码检查
lint:
	@echo "Running linters..."
	black --check src tests
	isort --check-only src tests

# 格式化代码
format:
	@echo "Formatting code..."
	black src tests
	isort src tests
