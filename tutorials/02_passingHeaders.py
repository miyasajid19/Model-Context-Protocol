from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

client = MultiServerMCPClient(
    {
        "weather": {
            "transport": "http",
            "url": "http://localhost:8000/mcp",
            "headers": {
                "Authorization": "Bearer YOUR_TOKEN",
                "X-Custom-Header": "custom-value"
            },
        }
    }
)
tools =  client.get_tools()
agent = create_agent("openai:gpt-5.5", tools)
response = agent.ainvoke({"messages": "what is the weather in nyc?"})
print(response)