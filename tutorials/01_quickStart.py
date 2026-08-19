from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio
from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from rich import print
load_dotenv()


async def main():
    client = MultiServerMCPClient(
        {
            "mcp": {
                "transport": "http",
                # "url": "http://localhost:8000/mcp",  # Local server
                "url": "https://docs.langchain.com/mcp",  # Hosted server
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
        {
            "messages": [
                {
                    "role": "user",
                    "content": "How do I connect LangChain to an MCP server over HTTP?",
                }
            ]
        }
    )
    print(response)


if __name__ == "__main__":
    asyncio.run(main())