# MCP Terminal 快速入门指南

本指南将帮助您快速设置并开始使用 MCP Terminal，一个为 Claude 等 AI 助手提供终端控制能力的工具。

## 1. 安装

### 先决条件

- Python 3.8+
- uv 包管理工具（推荐）

### 一键安装

在终端中执行：

```bash
# 克隆仓库（或下载代码）
git clone https://github.com/yourusername/mcp-terminal.git
cd mcp-terminal

# 使用uv安装（推荐）
uv venv
source .venv/bin/activate  # 在Windows上使用 .venv\Scripts\activate
uv pip install -e .

# 或使用Makefile
make setup
```

对于 macOS 用户，如果希望使用 iTerm2 功能：

```bash
uv pip install -e ".[iterm]"  # 或 make setup-iterm
```

## 2. 基本用法

### 启动服务器

```bash
# 使用自动检测的终端控制器（推荐）
python mcp_terminal.py

# 或使用Makefile
make run-stdio
```

### 指定控制器类型

```bash
# 使用iTerm2控制器（仅限macOS）
python mcp_terminal.py --controller iterm

# 使用AppleScript控制器（仅限macOS Terminal）
python mcp_terminal.py --controller applescript

# 使用通用Subprocess控制器（所有平台）
python mcp_terminal.py --controller subprocess
```

### 使用 SSE 模式（HTTP API）

```bash
python mcp_terminal.py --mode sse --host 127.0.0.1 --port 3000
```

## 3. 与 Claude Desktop 集成

1. **启动 MCP Terminal 服务器**：

   ```bash
   python mcp_terminal.py
   ```

2. **配置 Claude Desktop**：

   - 打开 Claude Desktop 设置
   - 导航到"扩展"或"工具"选项卡
   - 添加新工具：
     - 名称：Terminal
     - 路径：输入 mcp_terminal.py 的完整路径
     - 勾选"使用 stdio 模式"
     - 保存配置

3. **测试集成**：
   - 在与 Claude 的对话中，尝试："请列出当前目录的文件"

详细设置请参考[Claude Desktop 集成指南](./claude_desktop_integration.md)。

## 4. 支持的命令

MCP Terminal 支持执行任何终端命令，例如：

- 文件操作：`ls`, `mkdir`, `cat`, `touch`
- 系统信息：`uname -a`, `whoami`, `ps`
- 开发工具：`git status`, `npm list`, `python --version`

## 5. 常见问题

### 找不到控制器

如果遇到"Controller not found"错误：

- 在 macOS 上使用 iTerm2 控制器时，确保已安装 iTerm2 和 iterm2 包
- 尝试使用`--controller subprocess`选项，它在所有平台上都能工作

### 命令执行超时

如果命令执行时间过长：

- 增加超时时间：`python mcp_terminal.py --timeout 30`
- 或在执行特定命令时设置更长的超时：`execute_command(command="long_running_command", timeout=60)`

### Claude 无法接收输出

如果 Claude 无法正确接收命令输出：

- 确保 MCP Terminal 服务器正在运行
- 检查 Claude Desktop 工具配置是否正确
- 尝试重启服务器和 Claude Desktop

## 6. 下一步

- 查看[完整文档](../README.md)了解更多选项和用法
- 探索[使用 uv 管理项目](./uv_guide.md)的高级技巧
- 参考[工具 API 规范](../README.md#api-规范)了解更多函数细节

## 7. 获取帮助

如果您遇到问题：

- 查看日志输出寻找错误信息
- 增加日志级别以获取更多信息：`python mcp_terminal.py --log-level DEBUG`
- 提交 GitHub issue 或联系项目维护者
