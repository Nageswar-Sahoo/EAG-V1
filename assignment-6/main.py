import asyncio
import logging
from typing import List, Dict, Any
from datetime import datetime
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

from perception import PerceptionLayer
from memory import MemoryLayer
from decision_making import DecisionMakingLayer
from action import ActionLayer
from prompts import get_system_prompt, get_current_query
from cognitive_agent import Agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_execution.log', mode='w'),
        logging.StreamHandler()
    ]
)

async def main():
    agent = Agent()
    original_query = """Find the result of ((15 + 5) - (18 / 2)) + (27 % 4)+ (100 // 9) """
    await agent.run(original_query)

if __name__ == "__main__":
    asyncio.run(main())