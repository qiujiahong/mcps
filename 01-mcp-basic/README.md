# MCP Python 服务器示例：集成千问大模型的智能工具服务

这是一个使用 Python 实现的 MCP（Model Context Protocol）服务器示例，展示了如何将大语言模型与本地工具服务集成，实现智能化的数学计算和文本处理功能。

## 🚀 项目特色

- **MCP 协议实现**：基于最新的 Model Context Protocol 标准
- **千问大模型集成**：支持阿里云千问模型的 API 调用
- **LangChain 框架**：使用 LangChain 和 LangGraph 构建智能代理
- **工具链扩展**：可轻松扩展更多自定义工具
- **异步处理**：全异步架构，高性能处理
- **简单易用**：单服务器架构，快速上手

## 📋 功能特性

### 🔧 数学工具
- `add(a, b)`：两数相加
- `multiply(a, b)`：两数相乘
- 传输方式：stdio

### 🤖 AI 增强功能
- 自然语言数学问题解析
- 智能工具选择和调用
- 上下文理解和推理
- 多步骤计算处理

## 🛠️ 技术栈

- **Python 3.11+**
- **MCP (Model Context Protocol)**：模型上下文协议
- **LangChain**：大语言模型应用框架
- **LangGraph**：智能代理构建
- **FastMCP**：快速 MCP 服务器实现
- **千问大模型**：阿里云 DashScope API

## 📦 安装依赖

### 1. 环境准备

* 依赖文件准备

```python:requirements.txt
mcp>=1.11.0
pydantic>=2.0.0
typing-extensions>=4.14.1
openai>=1.95.0
python-dotenv>=1.0.0
requests>=2.25.0
```

* 启动Python环境

```bash
# 激活 conda 环境
conda activate dba

# 安装项目依赖
pip install -r requirements.txt
```

### 2. 环境配置
创建 `.env` 文件并配置千问 API：

```env
# 阿里云千问API配置
DASHSCOPE_API_KEY=your_api_key_here
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
DASHSCOPE_MODEL=qwen3-235b-a22b
```

💡 **获取 API Key**：访问 [阿里云 DashScope](https://bailian.console.aliyun.com/) 注册并获取 API 密钥

## 📁 项目结构

```
01-mcp-basic/
├── .env                 # 环境变量配置
├── math_server.py       # MCP 服务器实现
├── client.py           # 客户端示例
├── requirements.txt    # 项目依赖
├── test.json          # 测试数据
└── README.md          # 项目文档
```

## 🔍 核心代码解析

### MCP 服务器 (math_server.py)
```python:d:/codes/mcp-frist/01-mcp-basic/math_server.py
# math_server.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Math")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### 智能客户端 (client.py)
```python:d:/codes/mcp-frist/01-mcp-basic/client.py
import asyncio
import os
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

# 加载环境变量
load_dotenv()

async def main():
    # Create server parameters for stdio connection
    server_params = StdioServerParameters(
        command="python",
        # Make sure to update to the full absolute path to your math_server.py file
        args=["./math_server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            # Get tools
            tools = await load_mcp_tools(session)

            # 使用千问模型配置，移除不支持的参数
            llm = ChatOpenAI(
                model=os.getenv("DASHSCOPE_MODEL", "qwen-turbo"),  # 使用更稳定的模型
                api_key=os.getenv("DASHSCOPE_API_KEY"),
                base_url=os.getenv("DASHSCOPE_BASE_URL"),
                temperature=0.7,
                extra_body={"enable_thinking": False},
            )

            # Create and run the agent with Qwen model
            agent = create_react_agent(llm, tools)
            agent_response = await agent.ainvoke({"messages": "what's (3 + 5) x 12?"})
            
            print(agent_response)

if __name__ == "__main__":
    asyncio.run(main())
```

## 🚀 项目使用

### 1. 运行客户端测试
```bash
python client.py
```

### 2. 示例交互

客户端会自动向千问模型提问："what's (3 + 5) x 12?"，模型会：

**数学计算过程**：
1. 理解问题需要先计算 3+5，再乘以 12
2. 调用 `add(3, 5)` 工具得到 8
3. 调用 `multiply(8, 12)` 工具得到 96
4. 返回最终答案：96

**完整交互流程**：
```
用户问题: "what's (3 + 5) x 12?"
↓
AI 分析: 需要先做加法，再做乘法
↓
工具调用 1: add(3, 5) → 返回 8
↓
工具调用 2: multiply(8, 12) → 返回 96
↓
最终答案: 96
```

## 🔧 服务器配置说明

### 传输协议
- **协议类型**：stdio
- **启动方式**：自动启动（客户端调用时）
- **通信方式**：标准输入输出流

### 客户端配置
```python
server_params = StdioServerParameters(
    command="python",
    args=["./math_server.py"],
)
```

## 🐛 常见问题

### Q: 遇到 "enable_thinking" 参数错误
**A**: 确保使用 `qwen-turbo` 模型，避免使用实验性模型参数。

### Q: API 调用失败
**A**: 检查 `.env` 文件中的 API Key 是否正确，确保网络连接正常。

### Q: 依赖安装失败
**A**: 建议使用 Python 3.11+ 版本，确保 pip 版本最新。

### Q: 服务器路径错误
**A**: 确保 `math_server.py` 文件路径正确，建议使用绝对路径。

### Q: 连接超时
**A**: 检查防火墙设置，确保 Python 进程可以正常通信。

## 🔄 扩展开发

### 添加新的工具

1. **在服务器中添加新工具**：
```python
@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Subtract two numbers"""
    return a - b

@mcp.tool()
def divide(a: float, b: float) -> float:
    """Divide two numbers"""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```

2. **重启服务器**：
工具会自动被客户端发现和使用。

### 自定义AI提示
```python
# 自定义系统提示
system_prompt = "你是一个数学计算助手，专门帮助用户解决数学问题。"
agent = create_react_agent(llm, tools, system_prompt=system_prompt)
```

## 📚 相关资源

- [MCP 官方文档](https://modelcontextprotocol.io/)
- [langchain-mcp-adapters](https://github.com/langchain-ai/langchain-mcp-adapters)
- [LangChain 文档](https://python.langchain.com/)
- [阿里云千问文档](https://bailian.console.aliyun.com/)
- [FastMCP 项目](https://github.com/jlowin/fastmcp)
- [笔者更多MCP经验分享](https://github.com/qiujiahong/mcps)

## 🎯 项目亮点

- ✅ **简单易用**：单文件服务器，快速上手
- ✅ **标准协议**：完全遵循 MCP 协议规范
- ✅ **AI 集成**：无缝集成千问大模型
- ✅ **工具扩展**：轻松添加新的计算工具
- ✅ **异步处理**：高性能异步架构
- ✅ **错误处理**：完善的异常处理机制
- ✅ **生产就绪**：包含完整的配置和文档
