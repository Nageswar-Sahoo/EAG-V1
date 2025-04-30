import asyncio
import time
import os
import datetime
from perception import extract_perception
from memory import MemoryManager, MemoryItem
from decision import generate_plan
from action import execute_tool
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
 # use this to connect to running server

import shutil
import sys
from typing import List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log(stage: str, msg: str):
    now = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] [{stage}] {msg}")

max_steps = 3

class Agent:
    def __init__(self):
        self.memory = MemoryManager()
        self.tools = []  # Will be populated with available tools
        
    def log(self, stage: str, msg: str):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        logger.info(f"[{now}] [{stage}] {msg}")
        
    async def process_input(self, user_input: str) -> str:
        """Process user input through the agent's pipeline"""
        try:
            # 1. Perception
            self.log("perception", f"Processing input: {user_input}")
            perception = extract_perception(user_input)
            
            # 2. Memory
            relevant_memories = self.memory.retrieve(
                query=user_input,
                top_k=3
            )
            
            # 3. Decision
            plan = generate_plan(
                perception=perception,
                memory_items=relevant_memories,
                tool_descriptions=str([t.__doc__ for t in self.tools])
            )
            
            # 4. Action
            if plan.startswith("FUNCTION_CALL:"):
                result = await execute_tool(self.tools, plan)
                return str(result)
            elif plan.startswith("FINAL_ANSWER:"):
                return plan.replace("FINAL_ANSWER:", "").strip()
            else:
                return "I'm not sure how to handle that request."
                
        except Exception as e:
            self.log("error", f"Error processing input: {str(e)}")
            return f"An error occurred: {str(e)}"
            
    def register_tool(self, tool):
        """Register a new tool with the agent"""
        self.tools.append(tool)
        self.log("tool", f"Registered tool: {tool.__name__}")

async def main(user_input: str):
    try:
        print("[agent] Starting agent...")
        print(f"[agent] Current working directory: {os.getcwd()}")
        
        server_params = StdioServerParameters(
            command="python",
            args=["example3.py"],
            cwd="/Users/nageswar.sahoo/Desktop/ERAG/EAG-V1/S7/src/"
        )

        try:
            async with stdio_client(server_params) as (read, write):
                print("Connection established, creating session...")
                try:
                    async with ClientSession(read, write) as session:
                        print("[agent] Session created, initializing...")
 
                        try:
                            await session.initialize()
                            print("[agent] MCP session initialized")

                            # Your reasoning, planning, perception etc. would go here
                            tools = await session.list_tools()
                            print("Available tools:", [t.name for t in tools.tools])

                            # Get available tools
                            print("Requesting tool list...")
                            tools_result = await session.list_tools()
                            tools = tools_result.tools
                            tool_descriptions = "\n".join(
                                f"- {tool.name}: {getattr(tool, 'description', 'No description')}" 
                                for tool in tools
                            )

                            log("agent", f"{len(tools)} tools loaded")

                            memory = MemoryManager()
                            session_id = f"session-{int(time.time())}"
                            query = user_input  # Store original intent
                            step = 0

                            while step < max_steps:
                                log("loop", f"Step {step + 1} started")

                                perception = extract_perception(user_input)
                                log("perception", f"Intent: {perception.intent}, Tool hint: {perception.tool_hint}")

                                retrieved = memory.retrieve(query=user_input, top_k=3, session_filter=session_id)
                                log("memory", f"Retrieved {len(retrieved)} relevant memories")

                                plan = generate_plan(perception, retrieved, tool_descriptions=tool_descriptions)
                                log("plan", f"Plan generated: {plan}")

                                if plan.startswith("FINAL_ANSWER:"):
                                    log("agent", f"✅ FINAL RESULT: {plan}")
                                    break

                                try:
                                    result = await execute_tool(session, tools, plan)
                                    log("tool", f"{result.tool_name} returned: {result.result}")

                                    memory.add(MemoryItem(
                                        text=f"Tool call: {result.tool_name} with {result.arguments}, got: {result.result}",
                                        type="tool_output",
                                        tool_name=result.tool_name,
                                        user_query=user_input,
                                        tags=[result.tool_name],
                                        session_id=session_id
                                    ))

                                    user_input = f"Original task: {query}\nPrevious output: {result.result}\nWhat should I do next?"

                                except Exception as e:
                                    log("error", f"Tool execution failed: {e}")
                                    break

                                step += 1
                        except Exception as e:
                            print(f"[agent] Session initialization error: {str(e)}")
                except Exception as e:
                    print(f"[agent] Session creation error: {str(e)}")
        except Exception as e:
            print(f"[agent] Connection error: {str(e)}")
    except Exception as e:
        print(f"[agent] Overall error: {str(e)}")

    log("agent", "Agent session complete.")

if __name__ == "__main__":
    query = input("🧑 What do you want to solve today? → ")
    asyncio.run(main(query))


# Find the ASCII values of characters in INDIA and then return sum of exponentials of those values.
# How much Anmol singh paid for his DLF apartment via Capbridge? 
# What do you know about Don Tapscott and Anthony Williams?
# What is the relationship between Gensol and Go-Auto?