# 使用 uv 构建和管理 MCP Terminal 项目

本指南详细介绍如何使用[uv](https://github.com/astral-sh/uv)工具来构建、管理和部署 MCP Terminal 项目。uv 是一个快速的 Python 包管理器和虚拟环境管理工具，它可以大大加速你的 Python 开发工作流程。

## 什么是 uv？

uv 是一个现代化的 Python 包管理器，具有以下特点：

- 比 pip 快 10-100 倍的包安装速度
- 自动解决依赖冲突
- 集成的虚拟环境管理
- 与现有的 Python 工具链兼容

## 安装 uv

在开始之前，您需要安装 uv：

### macOS

```bash
# 使用Homebrew
brew install uv

# 或使用pip
pip install uv
```

### Linux

```bash
pip install uv
```

### Windows

```bash
pip install uv
```

## 使用 uv 管理 MCP Terminal 项目

### 1. 创建和激活虚拟环境

uv 可以轻松创建和管理虚拟环境：

```bash
# 导航到项目目录
cd /path/to/mcp-terminal

# 创建虚拟环境
uv venv

# 激活虚拟环境
# 在macOS/Linux上：
source .venv/bin/activate
# 在Windows上：
.venv\Scripts\activate
```

### 2. 安装项目依赖

使用 uv 安装项目依赖比传统的 pip 快得多：

```bash
# 安装基本依赖
uv pip install -e .

# 安装iTerm2支持（仅限macOS）
uv pip install -e ".[iterm]"

# 安装开发依赖
uv pip install -e ".[dev]"
```

### 3. 管理依赖

uv 提供了更好的依赖管理能力：

```bash
# 查看已安装的包
uv pip list

# 查看过时的包
uv pip list --outdated

# 更新所有包
uv pip install --upgrade -e .
```

### 4. 编译和构建项目

使用 uv 构建项目发布包：

```bash
# 构建源代码分发和wheel包
uv pip install build
python -m build
```

这将在`dist/`目录中创建源代码归档和 wheel 包。

### 5. 创建可执行文件

要创建可执行文件，您可以使用 uv 与 PyInstaller 结合：

```bash
# 安装PyInstaller
uv pip install pyinstaller

# 创建单文件可执行文件
pyinstaller --onefile mcp_terminal.py
```

这将在`dist/`目录下创建一个独立的可执行文件。

## 与 Makefile 集成

MCP Terminal 项目包含了一个 Makefile，它已经配置为使用 uv：

```bash
# 使用uv安装基本依赖
make setup

# 使用uv安装iTerm2支持
make setup-iterm

# 使用uv安装开发依赖
make setup-dev
```

## 使用 uv 加速测试

uv 可以加速测试运行，特别是在需要安装测试依赖时：

```bash
# 安装测试依赖
uv pip install pytest pytest-cov

# 运行测试
pytest
```

## 使用 uv 构建发布版本

当您准备发布 MCP Terminal 时，可以使用 uv 来准备发布包：

```bash
# 确保构建工具已安装
uv pip install build twine

# 构建分发包
python -m build

# 检查构建的包
twine check dist/*

# 上传到PyPI（如果适用）
twine upload dist/*
```

## 使用 uv 进行环境复制

如果您需要在不同机器上复制开发环境，uv 提供了一种便捷的方式：

```bash
# 在源环境中导出依赖
uv pip freeze > requirements.txt

# 在目标环境中重新创建
uv venv
source .venv/bin/activate  # 或在Windows上使用 .venv\Scripts\activate
uv pip install -r requirements.txt
```

## 集成开发环境(IDE)配置

大多数 Python IDE 能够自动检测并使用 uv 创建的虚拟环境：

### VS Code

在 VS Code 中，确保在设置中选择正确的 Python 解释器：

1. 按`Ctrl+Shift+P`（或`Cmd+Shift+P`在 macOS 上）
2. 输入"Python: Select Interpreter"
3. 选择对应于您的 uv 虚拟环境的 Python 解释器（通常在`.venv/bin/python`或`.venv\Scripts\python.exe`）

### PyCharm

在 PyCharm 中配置 uv 虚拟环境：

1. 转到`File > Settings > Project > Python Interpreter`
2. 点击齿轮图标，然后选择"Add..."
3. 选择"Existing Environment"
4. 导航到并选择 uv 虚拟环境的 Python 解释器

## 故障排除

### 依赖冲突

如果遇到依赖冲突，uv 通常能够自动解决。如果仍有问题：

```bash
# 清除缓存并重新安装
uv pip cache clear
uv pip install -e . --force-reinstall
```

### 虚拟环境问题

如果虚拟环境出现问题：

```bash
# 删除并重新创建虚拟环境
rm -rf .venv
uv venv
source .venv/bin/activate  # 或在Windows上使用 .venv\Scripts\activate
uv pip install -e .
```

## 性能提示

- 使用 uv 的 pip 缓存功能可以大大加速重复安装
- 对于大型依赖，uv 的并行下载功能提供显著速度提升
- 在 CI/CD 环境中，uv 可以减少构建时间

## 结论

uv 提供了一种更快、更可靠的方式来管理 Python 项目依赖。对于 MCP Terminal 项目，使用 uv 可以显著改善开发体验，减少等待依赖安装的时间，并提供更稳定的环境管理。
