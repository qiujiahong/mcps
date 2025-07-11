# MCP Python 服务器示例：集成千问大模型的智能工具服务
这是一个使用 Python 实现的 MCP（Model Context Protocol）服务器示例，展示了如何将大语言模型与本地工具服务集成，实现智能化的数学计算和文本处理功能。

## 🚀 项目特色
- MCP 协议实现 ：基于最新的 Model Context Protocol 标准
- 千问大模型集成 ：支持阿里云千问模型的 API 调用
- LangChain 框架 ：使用 LangChain 和 LangGraph 构建智能代理
- 工具链扩展 ：可轻松扩展更多自定义工具
- 异步处理 ：全异步架构，高性能处理

## 📋 功能特性
### 🔧 数学工具
- add(a, b) : 两数相加
- multiply(a, b) : 两数相乘

### 🤖 AI 增强功能
- 自然语言数学问题解析
- 智能工具选择和调用
- 上下文理解和推理

## 🛠️ 技术栈
- Python 3.11+
- MCP (Model Context Protocol) : 模型上下文协议
- LangChain : 大语言模型应用框架
- LangGraph : 智能代理构建
- FastMCP : 快速 MCP 服务器实现
- 千问大模型 : 阿里云 DashScope API

## 📦 安装依赖
### 1. 环境准备
```
# 激活 conda 环境
conda activate dba

# 安装项目依赖
pip install -r requirements.txt
```
### 2. 环境配置
创建 .env 文件并配置千问 API：

```
# 阿里云千问API配置
DASHSCOPE_API_KEY=your_api_key_here
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
DASHSCOPE_MODEL=qwen3-235b-a22b
```
💡 获取 API Key : 访问 阿里云 DashScope 注册并获取 API 密钥



## 📁 项目结构
```
mcp-frist/
├── .env                 # 环境变量配置
├── math_server.py       # MCP 服务器实现
├── client.py           # 客户端示例
├── requirements.txt    # 项目依赖
└── README.md          # 项目文档
```
## 🔍 核心代码解析


### MCP 服务器 (math_server.py)
```python
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
```python
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
###  运行客户端测试
```
python client.py
```
###  示例交互
客户端会自动向千问模型提问："what's (3 + 5) x 12?"，模型会：

1. 理解问题需要先计算 3+5，再乘以 12
2. 调用 add(3, 5) 工具得到 8
3. 调用 multiply(8, 12) 工具得到 96
4. 返回最终答案：96

## 🐛 常见问题
### Q: 遇到 "enable_thinking" 参数错误
A: 确保使用 qwen-turbo 模型，避免使用实验性模型参数。

### Q: API 调用失败
A: 检查 .env 文件中的 API Key 是否正确，确保网络连接正常。

### Q: 依赖安装失败
A: 建议使用 Python 3.11+ 版本，确保 pip 版本最新。

## 📚 相关资源
- MCP 官方文档
- [langchain-mcp-adapters](https://github.com/langchain-ai/langchain-mcp-adapters) 
- LangChain 文档
- [阿里云千问文档](https://bailian.console.aliyun.com/?spm=5176.29597918.J_SEsSjsNv72yRuRFS2VknO.2.72b17b08dibMxu&tab=doc#/doc)
- FastMCP 项目

- [笔者更多MCP经验分享](https://github.com/qiujiahong/mcps)