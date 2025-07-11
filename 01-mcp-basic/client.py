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
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    server_script = os.path.join(current_dir, "math_server.py")
    
    # Create server parameters for stdio connection
    server_params = StdioServerParameters(
        command="python",
        args=[server_script],
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