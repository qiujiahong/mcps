# MCP 多服务器示例：集成千问大模型的多工具智能服务

这是一个使用 Python 实现的多服务器 MCP（Model Context Protocol）示例，展示了如何同时集成多个 MCP 服务器，实现数学计算和天气查询的智能化服务。

## 🚀 项目特色

- **多服务器架构**：同时运行数学和天气两个 MCP 服务器
- **MCP 协议实现**：基于最新的 Model Context Protocol 标准
- **千问大模型集成**：支持阿里云千问模型的 API 调用
- **LangChain 框架**：使用 LangChain 和 LangGraph 构建智能代理
- **工具链扩展**：可轻松扩展更多自定义工具服务器
- **异步处理**：全异步架构，高性能处理
- **多传输协议**：支持 stdio 和 HTTP 两种传输方式

## 📋 功能特性

### 🔧 数学工具服务器
- `add(a, b)`：两数相加
- `multiply(a, b)`：两数相乘
- 传输方式：stdio

### 🌤️ 天气工具服务器
- `get_weather(location)`：获取指定地点的天气信息
- 传输方式：HTTP (streamable-http)
- 服务端口：8000

### 🤖 AI 增强功能
- 自然语言问题解析
- 智能工具选择和调用
- 多服务器工具统一管理
- 上下文理解和推理

## 🛠️ 技术栈

- **Python 3.11+**
- **MCP (Model Context Protocol)**：模型上下文协议
- **LangChain**：大语言模型应用框架
- **LangGraph**：智能代理构建
- **FastMCP**：快速 MCP 服务器实现
- **MultiServerMCPClient**：多服务器客户端
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
02-multiple-mcp-server/
├── .env                 # 环境变量配置
├── math_server.py       # 数学计算 MCP 服务器
├── weather_server.py    # 天气查询 MCP 服务器
├── client.py           # 多服务器客户端示例
├── requirements.txt    # 依赖
└── README.md          # 项目文档
```

## 🔍 核心代码解析

### 数学服务器 (math_server.py)
```python:02-multiple-mcp-server/math_server.py
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

### 天气服务器 (weather_server.py)
```python:02-multiple-mcp-server/weather_server.py
# weather_server.py
from typing import List
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Weather")

@mcp.tool()
async def get_weather(location: str) -> str:
    """Get weather for location."""
    return "It's always sunny in New York"

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
```

### 多服务器客户端 (client.py)
```python:d:/codes/mcp-frist/02-multiple-mcp-server/client.py
import asyncio
import os
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

# 加载环境变量
load_dotenv()

async def main():
    try:
        # 获取当前脚本所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        math_server_script = os.path.join(current_dir, "math_server.py")
        
        # 创建多服务器 MCP 客户端
        client = MultiServerMCPClient(
            {
                "math": {
                    "command": "python",
                    "args": [math_server_script],
                    "transport": "stdio",
                },
                "weather": {
                    # 确保天气服务器在端口 8000 上运行
                    "url": "http://localhost:8000/mcp/",
                    "transport": "streamable_http",
                }
            }
        )
        
        # 获取所有服务器的工具
        tools = await client.get_tools()
        
        # 使用千问模型配置
        llm = ChatOpenAI(
            model=os.getenv("DASHSCOPE_MODEL", "qwen-turbo"),
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url=os.getenv("DASHSCOPE_BASE_URL"),
            temperature=0.7,
            extra_body={"enable_thinking": False},
        )
        
        # 创建智能代理
        agent = create_react_agent(llm, tools)
        
        # 测试数学计算
        math_response = await agent.ainvoke({"messages": "what's (3 + 5) x 12?"})
        print("数学计算结果:")
        print(math_response)
        
        # 测试天气查询
        weather_response = await agent.ainvoke({"messages": "what is the weather in NYC?"})
        print("天气查询结果:")
        print(weather_response)
        
    except Exception as e:
        print(f"发生错误: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 🚀 项目使用

### 1. 启动天气服务器
```bash
python weather_server.py
```
天气服务器将在 `http://localhost:8000` 启动

### 2. 运行多服务器客户端
```bash
python client.py
```

### 3. 示例交互

客户端会自动执行两个测试：

**数学计算测试**：
- 问题："what's (3 + 5) x 12?"
- 过程：
  1. 调用 `add(3, 5)` 工具得到 8
  2. 调用 `multiply(8, 12)` 工具得到 96
  3. 返回最终答案：96

**天气查询测试**：
- 问题："what is the weather in NYC?"
- 过程：
  1. 调用 `get_weather("NYC")` 工具
  2. 返回天气信息

## 🔧 服务器配置说明

### 传输协议对比

| 服务器 | 传输协议 | 端口 | 启动方式 |
|--------|----------|------|----------|
| Math Server | stdio | - | 自动启动 |
| Weather Server | streamable-http | 8000 | 手动启动 |

### 客户端配置

```python
client = MultiServerMCPClient({
    "math": {
        "command": "python",
        "args": ["math_server.py"],
        "transport": "stdio",
    },
    "weather": {
        "url": "http://localhost:8000",
        "transport": "streamable_http",
    }
})
```

## 🐛 常见问题

### Q: 天气服务器连接失败
**A**: 确保天气服务器已启动并运行在端口 8000：
```bash
python weather_server.py
```

### Q: 数学服务器路径错误
**A**: 确保 `math_server.py` 文件存在于当前目录，客户端会自动解析绝对路径。

### Q: API 调用失败
**A**: 检查 `.env` 文件中的 API Key 是否正确，确保网络连接正常。

### Q: 工具加载失败
**A**: 确保所有服务器都正常启动，检查服务器日志输出。

## 🔄 扩展开发

### 添加新的工具服务器

1. **创建新服务器**：
```python
# new_server.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("NewService")

@mcp.tool()
def new_tool(param: str) -> str:
    """新工具描述"""
    return f"处理结果: {param}"

if __name__ == "__main__":
    mcp.run(transport="stdio")  # 或 "streamable-http"
```

2. **更新客户端配置**：
```python
client = MultiServerMCPClient({
    "math": {...},
    "weather": {...},
    "new_service": {
        "command": "python",
        "args": ["new_server.py"],
        "transport": "stdio",
    }
})
```

## 📚 相关资源

- [MCP 官方文档](https://modelcontextprotocol.io/)
- [langchain-mcp-adapters](https://github.com/langchain-ai/langchain-mcp-adapters)
- [LangChain 文档](https://python.langchain.com/)
- [阿里云千问文档](https://bailian.console.aliyun.com/)
- [FastMCP 项目](https://github.com/jlowin/fastmcp)
- [笔者更多MCP经验分享](https://github.com/qiujiahong/mcps)

## 🎯 项目亮点

- ✅ **多服务器架构**：展示了如何同时管理多个 MCP 服务器
- ✅ **混合传输协议**：stdio 和 HTTP 协议的混合使用
- ✅ **统一工具管理**：通过 MultiServerMCPClient 统一管理所有工具
- ✅ **智能路由**：AI 自动选择合适的工具服务器
- ✅ **易于扩展**：简单的配置即可添加新的服务器
- ✅ **生产就绪**：包含完整的错误处理和日志记录
        