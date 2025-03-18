# 将 MCP Terminal 与 Claude Desktop 集成

本文档详细介绍如何配置 Claude Desktop 使用 MCP Terminal 工具，使 Claude 能够执行终端命令并获取输出结果。

## 先决条件

- 已安装 Claude Desktop 应用
- 已安装并配置好 MCP Terminal
- Python 3.8+安装在系统上

## 配置步骤

### 1. 安装 MCP Terminal

如果您尚未安装 MCP Terminal，请按照以下步骤进行安装：

```bash
# 克隆仓库（或下载代码）
git clone https://github.com/yourusername/mcp-terminal.git
cd mcp-terminal

# 使用uv安装
uv venv
source .venv/bin/activate  # 在Windows上使用 .venv\Scripts\activate
uv pip install -e .

# 针对macOS用户，如果希望使用iTerm2支持
uv pip install -e ".[iterm]"
```

或使用 Makefile 简化安装：

```bash
make setup        # 基本安装
make setup-iterm  # 安装iTerm2支持（仅限macOS）
```

### 2. 获取 MCP Terminal 的绝对路径

您需要获取 MCP Terminal 入口点脚本的绝对路径：

```bash
# 在项目目录中执行
realpath mcp_terminal.py  # 在macOS和Linux上使用
# 或在Windows上使用
cd && echo %CD%\mcp_terminal.py
```

请记下输出的路径，例如`/Users/username/Workspace/mcp-terminal/mcp_terminal.py`。

### 3. 配置 Claude Desktop

1. 打开 Claude Desktop 应用
2. 点击右上角的设置图标（⚙️）
3. 在设置菜单中，找到并点击"扩展功能"（Extensions）或"工具"（Tools）选项卡
4. 启用"自定义工具"（Custom Tools）功能（如果有此选项）
5. 点击"添加工具"（Add Tool）按钮
6. 在表单中填写以下信息：
   - **工具名称**：`Terminal`（或您喜欢的任何名称）
   - **工具路径**：输入步骤 2 中获取的 MCP Terminal 的完整路径
   - **使用 stdio 模式**：勾选此选项
   - **工具描述**（可选）：`允许执行终端命令并获取输出结果`
7. 点击"保存"按钮

### 4. 启动 MCP Terminal 服务器

在与 Claude Desktop 交互之前，您需要先启动 MCP Terminal 服务器：

```bash
# 打开一个新的终端窗口，导航到项目目录
cd path/to/mcp-terminal

# 启动服务器（stdio模式）
python mcp_terminal.py
# 或使用Makefile
make run-stdio
```

保持此终端窗口打开和服务器运行，这是 Claude Desktop 与 MCP Terminal 通信的管道。

### 5. 测试集成

现在，您可以在 Claude Desktop 中测试终端命令执行：

1. 打开或继续一个与 Claude 的对话
2. 发送包含终端命令请求的消息，例如：
   - "请列出我当前目录的文件"
   - "查看我的系统信息"
   - "创建一个名为'test'的新文件夹"

Claude 应该能够执行这些命令并返回输出结果。

## 高级配置

### 使用特定的终端控制器

如果您希望 Claude 使用特定的终端控制器（而不是自动检测），可以在启动时指定：

```bash
# 使用iTerm2控制器（仅限macOS）
python mcp_terminal.py --controller iterm

# 使用AppleScript控制器（仅限macOS）
python mcp_terminal.py --controller applescript

# 使用subprocess控制器（所有平台）
python mcp_terminal.py --controller subprocess
```

在 Claude Desktop 的工具配置中，您需要相应地更新命令行参数。

### 调整日志级别

如果您需要调试集成问题，可以增加日志级别：

```bash
python mcp_terminal.py --log-level DEBUG
```

### 创建启动脚本

为了简化启动过程，您可以创建一个启动脚本：

**macOS/Linux** (start_for_claude.sh):

```bash
#!/bin/bash
cd "$(dirname "$0")"
source .venv/bin/activate
python mcp_terminal.py
```

**Windows** (start_for_claude.bat):

```batch
@echo off
cd /d "%~dp0"
call .venv\Scripts\activate
python mcp_terminal.py
```

然后在 Claude Desktop 工具配置中使用这个脚本的路径。

## 使用提示

### 基本命令

Claude 可以执行各种终端命令，例如：

- 文件操作：`ls`, `mkdir`, `cat`, `cp`, `mv`, `rm`
- 系统信息：`uname -a`, `whoami`, `pwd`, `df -h`
- 进程管理：`ps`, `top`（短时间运行）
- 网络命令：`ping`, `ifconfig`/`ipconfig`
- 简单的编辑器操作：`echo "text" > file.txt`

### 注意事项

- **避免长时间运行的命令**：命令超时可能导致不完整的输出
- **敏感命令**：避免执行可能会修改系统配置的命令，除非您明确知道自己在做什么
- **上下文限制**：Claude 无法记住之前命令的输出，如需要跨命令引用，可能需要将结果存储在文件中

## 故障排除

### 集成不工作

1. **检查服务器是否运行**：确保 MCP Terminal 服务器正在运行并且没有错误消息
2. **验证路径**：确保在 Claude Desktop 中配置的路径是正确的
3. **检查权限**：确保脚本有执行权限（`chmod +x mcp_terminal.py`）
4. **尝试重启**：重启 Claude Desktop 应用和 MCP Terminal 服务器
5. **检查日志**：使用`--log-level DEBUG`检查更详细的日志输出

### 特定终端控制器问题

#### iTerm2 控制器

- 确保 iTerm2 已安装在您的 Mac 上
- 确保已安装 iterm2 Python 包：`uv pip install iterm2`
- 首次运行时，iTerm2 可能会请求权限，请允许

#### AppleScript 控制器

- 确保已授予终端应用所需的权限
- 某些命令可能需要特殊权限，尤其是涉及系统文件的命令

#### Subprocess 控制器

- 此控制器在所有平台上都应正常工作
- 某些命令可能在不同操作系统上有不同的行为

## 安全考虑

MCP Terminal 允许 Claude 执行任意终端命令，这带来一定的安全风险：

1. **限制访问**：只在您信任的环境中使用此集成
2. **注意命令**：审查 Claude 要执行的命令，尤其是修改系统或删除文件的命令
3. **考虑权限**：在专用账户下运行服务器，限制其权限
4. **敏感信息**：避免通过终端命令暴露敏感信息，Claude 可能会处理这些信息

## 技术细节

MCP Terminal 通过 MCP（Model Context Protocol）与 Claude Desktop 通信：

1. Claude Desktop 将命令请求发送给 MCP Terminal
2. MCP Terminal 使用适当的控制器执行命令
3. 命令输出被捕获并返回给 Claude Desktop
4. Claude 处理输出并将其呈现给用户

这种集成使用的是标准输入/输出（stdio）作为通信通道，这是 Claude Desktop 支持的标准扩展机制。
