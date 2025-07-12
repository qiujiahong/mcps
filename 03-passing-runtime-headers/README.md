
# MCP 高级功能：在客户端和服务器之间传递运行时 Header

这是一个高级 MCP 示例，演示了如何在客户端请求中附加自定义 HTTP 头，并在服务器端的工具函数中接收和解析这些头信息。这对于实现认证、传递追踪 ID 或其他元数据非常有用。

## 🚀 项目特色

- **运行时 Header 传递**：客户端可以在每次请求时动态添加 HTTP 头。
- **服务器端 Header 接收**：服务器工具函数可以访问传入请求的完整头信息。
- **安全与追踪**：可用于实现 API 密钥认证、分布式追踪等高级功能。
- **基于 FastMCP**：利用 `fastmcp` 提供的依赖注入功能获取请求上下文。
- **异步架构**：完全异步，确保高性能。

## 📋 功能特性

- **天气工具 (Weather Tool)**：提供一个 `get_weather` 工具，它在返回天气信息的同时，会解析并打印出收到的 HTTP 头。
- **自定义 Header**：客户端示例代码演示了如何发送 `Authorization` 和 `X-Custom-Header` 等自定义头。

## 🛠️ 技术栈

- **Python 3.11+**
- **MCP (Model Context Protocol)**
- **FastMCP**：`fastmcp` 库，特别是其依赖注入功能 `get_http_request`。
- **LangChain & LangGraph**：用于构建和运行客户端的智能代理。
- **Starlette**：`FastMCP` 底层使用的 ASGI 框架，提供了 `Request` 对象。

## 📦 安装与环境设置

1.  **克隆项目**（如果尚未克隆）：
    ```bash
    git clone <your-repo-url>
    cd 03-passing-runtime-headers
    ```

2.  **创建并激活虚拟环境**：
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # on Windows, use `.venv\Scripts\activate`
    ```

3.  **安装依赖**：
    ```bash
    pip install -r requirements.txt
    ```

4.  **配置环境变量**：
    在项目根目录下创建一个 `.env` 文件，并填入您的千问模型 API 信息：
    ```dotenv
    DASHSCOPE_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    DASHSCOPE_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
    DASHSCOPE_MODEL="qwen-turbo"
    ```

## 📁 项目结构

```
03-passing-runtime-headers/
├── client.py           # 客户端：发送带header的请求
├── weather_server.py    # 服务器：接收并解析header
├── requirements.txt    # 项目依赖
└── README.md          # 本文档
```

## 🔍 核心代码解析

### 客户端 (client.py)

关键在于 `MultiServerMCPClient` 的配置。我们在服务器定义中添加了一个 `headers` 字典，这些头信息将随每次请求发送出去。

```python:client.py
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
        
        print("天气服务器: http://localhost:8000/mcp/")
        # 创建多服务器 MCP 客户端
        client = MultiServerMCPClient(
            {
                "weather": {
                    # 确保天气服务器在端口 8000 上运行
                    "url": "http://localhost:8000/mcp/",
                    "transport": "streamable_http",
                    # 添加header 
                    "headers": {
                        "Authorization": "Bearer YOUR_TOKEN",
                        "X-Custom-Header": "custom-value"
                    },
                },
                
            }
        )
        
        print("正在获取工具...")
        # 获取所有服务器的工具
        tools = await client.get_tools()
        print(f"已加载 {len(tools)} 个工具")
        
        # 使用千问模型配置
        print("正在配置 AI 模型...")
        llm = ChatOpenAI(
            model=os.getenv("DASHSCOPE_MODEL", "qwen-turbo"),
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url=os.getenv("DASHSCOPE_BASE_URL"),
            temperature=0.7,
            extra_body={"enable_thinking": False},
            timeout=30,
        )
        
        # 创建智能代理
        print("正在创建智能代理...")
        agent = create_react_agent(llm, tools)

        # 测试天气查询
        print("\n=== 测试天气查询 ===")
        weather_response = await agent.ainvoke({"messages": "what is the weather in NYC?"})
        print("天气查询结果:")
        print(weather_response)
        
        
    except Exception as e:
        print(f"发生错误: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
```

### 天气服务器 (weather_server.py)

服务器端使用 `fastmcp.server.dependencies` 中的 `get_http_request` 函数来获取当前的 `starlette.requests.Request` 对象。这个函数必须在工具函数内部调用。

```python:weather_server.py
# weather_server.py
from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_request
from starlette.requests import Request

mcp = FastMCP("Weather")

@mcp.tool()
async def get_weather(location: str) -> str:
    """Get weather for location."""
    request: Request = get_http_request()
    user_agent = request.headers.get("user-agent", "Unknown")
    Authorization = request.headers.get("Authorization", "Unknown")
    XCustomHeader = request.headers.get("X-Custom-Header", "Unknown")
    print(f"user_agent = {user_agent}")
    print(f"Authorization = {Authorization}")
    print(f"XCustomHeader = {XCustomHeader}")
    return "It's always sunny in New York"

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
```

## 🚀 项目使用

1.  **启动天气服务器**：
    打开一个终端，运行服务器。
    ```bash
    python weather_server.py
    ```
    服务器将在 `http://localhost:8000` 启动并等待请求。

2.  **运行客户端**：
    打开另一个终端，运行客户端。
    ```bash
    python client.py
    ```

### 预期输出

**服务器端**会打印出从客户端接收到的头信息：

```
user_agent = python-httpx/0.27.0
Authorization = Bearer YOUR_TOKEN
X-Custom-Header = custom-value
```

**客户端**会正常输出天气查询结果：

```
$ python client.py 
天气服务器: http://localhost:8000/mcp/
正在获取工具...
已加载 1 个工具
正在配置 AI 模型...
正在创建智能代理...

=== 测试天气查询 ===
天气查询结果:
{'messages': [HumanMessage(content='what is the weather in NYC?', additional_kwargs={}, response_metadata={}, id='cd2f78e4-5981-4bb5-9d8f-1d965d78742f'), AIMessage(content='', additional_kwargs={'tool_calls': [{'id': 'call_5992a21d83ac4fca8d0ad4', 'function': {'arguments': '{"location": "NYC"}', 'name': 'get_weather'}, 'type': 'function', 'index': 0}], 'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 20, 'prompt_tokens': 155, 'total_tokens': 175, 'completion_tokens_details': None, 'prompt_tokens_details': None}, 'model_name': 'qwen3-235b-a22b', 'system_fingerprint': None, 'id': 'chatcmpl-3f646b4e-f463-9fa2-adc9-659466110ee5', 'service_tier': None, 'finish_reason': 'tool_calls', 'logprobs': None}, id='run--3fdcb60d-6fc6-4cf1-84c4-c71b0b9b5bb6-0', tool_calls=[{'name': 'get_weather', 'args': {'location': 'NYC'}, 'id': 'call_5992a21d83ac4fca8d0ad4', 'type': 'tool_call'}], usage_metadata={'input_tokens': 155, 'output_tokens': 20, 'total_tokens': 175, 'input_token_details': {}, 'output_token_details': {}}), ToolMessage(content="It's always sunny in New York", name='get_weather', id='08ecf71c-421b-4e88-9f76-19829eac69d4', tool_call_id='call_5992a21d83ac4fca8d0ad4'), AIMessage(content='The weather in New York City is always sunny! 🌞', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 13, 'prompt_tokens': 196, 'total_tokens': 209, 'completion_tokens_details': None, 'prompt_tokens_details': None}, 'model_name': 'qwen3-235b-a22b', 'system_fingerprint': None, 'id': 'chatcmpl-d93e412d-1beb-9610-850f-2eed5bd4f02e', 'service_tier': None, 'finish_reason': 'stop', 'logprobs': None}, id='run--fff58713-b880-4f3c-b461-4918cd91fe72-0', usage_metadata={'input_tokens': 196, 'output_tokens': 13, 'total_tokens': 209, 'input_token_details': {}, 'output_token_details': {}})]}
```

## 🐛 常见问题

### Q: `get_http_request()` 抛出异常或返回 `None`

**A**: 确保您使用的是 `fastmcp` 库，并且 `get_http_request()` 是在工具函数内部调用的。这个函数依赖于请求处理的上下文，在工具函数之外调用是无效的。

### Q: 服务器没有打印头信息

**A**: 检查客户端的 `headers` 配置是否正确。同时确认服务器代码是否包含了打印逻辑。

## 🎯 项目亮点

- ✅ **运行时元数据**：展示了在 MCP 通信中附加和使用元数据的标准方法。
- ✅ **依赖注入**：利用 `FastMCP` 的依赖注入功能，代码简洁且功能强大。
- ✅ **实用场景**：为实现认证、日志、追踪等生产环境功能提供了基础。
- ✅ **代码清晰**：将头信息处理逻辑封装在工具函数内部，保持了代码的整洁性。
