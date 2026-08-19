from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
import asyncio
from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from rich import print

load_dotenv()


async def main():
    client = MultiServerMCPClient(
        {
            "weather": {
                "transport": "http",
                "url": "http://localhost:8000/mcp",
                "headers": {
                    "Authorization": "Bearer YOUR_TOKEN",
                    "X-Custom-Header": "custom-value",
                },
            }
        }
    )
    tools = await client.get_tools()
    print(tools)
    agent = create_agent(
        ChatOpenAI(
            model_name="MiniMax-M3",
            api_key=os.getenv("MINIMAX_API_KEY"),
            base_url=os.getenv("MINIMAX_BASE_URL"),
        ),
        tools,
    )
    response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "what is the weather in nyc?"}]}
    )
    print(response)


if __name__ == "__main__":
    asyncio.run(main())