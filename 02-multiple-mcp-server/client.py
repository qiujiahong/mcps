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
        
        print(f"数学服务器路径: {math_server_script}")
        print("天气服务器: http://localhost:8000/mcp/")
        
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
        
        # 测试数学计算
        print("\n=== 测试数学计算 ===")
        math_response = await agent.ainvoke({"messages": "what's (3 + 5) x 12?"})
        print("数学计算结果:")
        print(math_response)
        
        # 测试天气查询
        print("\n=== 测试天气查询 ===")
        weather_response = await agent.ainvoke({"messages": "what is the weather in NYC?"})
        print("天气查询结果:")
        print(weather_response)
        
        # 关闭客户端连接
        await client.close()
        
    except Exception as e:
        print(f"发生错误: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())