import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_core.messages import ToolMessage
import json
from dotenv import load_dotenv
llm=ChatOllama(model="minimax-m3:cloud", base_url="http://localhost:11434")
print(llm.invoke(""))