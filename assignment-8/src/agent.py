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
import shutil
import sys
from typing import List, Optional
import logging
import random
import aiohttp
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('agent.log')
    ]
)
logger = logging.getLogger(__name__)

def log_with_timestamp(message: str, level: str = "INFO"):
    """Helper function to log messages with timestamp"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    if level == "INFO":
        logger.info(log_message)
    elif level == "DEBUG":
        logger.debug(log_message)
    elif level == "WARNING":
        logger.warning(log_message)
    elif level == "ERROR":
        logger.error(log_message)

max_steps = 3
MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 1  # seconds
SHEETS_MCP_URL = "http://localhost:8051/process_result"

async def retry_with_backoff(func, *args, **kwargs):
    """Retry a function with exponential backoff"""
    retry_delay = INITIAL_RETRY_DELAY
    last_exception = None
    
    for attempt in range(MAX_RETRIES):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            if "503" in str(e) or "overloaded" in str(e).lower():
                if attempt < MAX_RETRIES - 1:
                    # Add jitter to prevent thundering herd
                    jitter = random.uniform(0, 0.1 * retry_delay)
                    wait_time = retry_delay + jitter
                    log_with_timestamp(f"Attempt {attempt + 1} failed. Retrying in {wait_time:.2f} seconds...", "WARNING")
                    await asyncio.sleep(wait_time)
                    retry_delay *= 2  # Exponential backoff
                else:
                    log_with_timestamp(f"All {MAX_RETRIES} attempts failed", "ERROR")
                    raise last_exception
            else:
                # For non-retryable errors, re-raise immediately
                raise e
    
    raise last_exception

async def store_result_in_sheets(result_data: dict) -> str:
    """Store result in Google Sheets via MCP server"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(SHEETS_MCP_URL, json=result_data) as response:
                if response.status == 200:
                    result = await response.json()
                    if result["status"] == "success":
                        return result["spreadsheet_link"]
                    else:
                        raise Exception(f"Error from Sheets MCP: {result['message']}")
                else:
                    raise Exception(f"HTTP error: {response.status}")
    except Exception as e:
        log_with_timestamp(f"Error storing result in sheets: {str(e)}", "ERROR")
        raise

class Agent:
    def __init__(self):
        log_with_timestamp("Initializing Agent...")
        self.memory = MemoryManager()
        self.tools = []  # Will be populated with available tools
        log_with_timestamp("Agent initialized with empty tool list")
        
    def log(self, stage: str, msg: str):
        log_with_timestamp(f"[{stage}] {msg}")
        
    async def process_input(self, user_input: str) -> str:
        """Process user input through the agent's pipeline"""
        try:
            # 1. Perception
            self.log("perception", f"Processing input: {user_input}")
            perception = extract_perception(user_input)
            self.log("perception", f"Extracted perception - Intent: {perception.intent}, Tool hint: {perception.tool_hint}")
            
            # 2. Memory
            self.log("memory", "Retrieving relevant memories...")
            relevant_memories = self.memory.retrieve(
                query=user_input,
                top_k=3
            )
            self.log("memory", f"Found {len(relevant_memories)} relevant memories")
            
            # 3. Decision
            self.log("decision", "Generating plan...")
            plan = generate_plan(
                perception=perception,
                memory_items=relevant_memories,
                tool_descriptions=str([t.__doc__ for t in self.tools])
            )
            self.log("decision", f"Generated plan: {plan}")
            
            # 4. Action
            self.log("action", "Executing plan...")
            if plan.startswith("FUNCTION_CALL:"):
                self.log("action", "Executing function call...")
                result = await retry_with_backoff(execute_tool, self.tools, plan)
                self.log("action", f"Function call result: {result}")
                return str(result)
            elif plan.startswith("FINAL_ANSWER:"):
                final_answer = plan.replace("FINAL_ANSWER:", "").strip()
                self.log("action", f"Returning final answer: {final_answer}")
                return final_answer
            else:
                self.log("action", "No valid action found in plan")
                return "I'm not sure how to handle that request."
                
        except Exception as e:
            self.log("error", f"Error processing input: {str(e)}")
            return f"An error occurred: {str(e)}"
            
    def register_tool(self, tool):
        """Register a new tool with the agent"""
        self.tools.append(tool)
        self.log("tool", f"Registered tool: {tool.__name__}")

    async def main(self, user_input: str):
        try:
            log_with_timestamp("Starting agent...")
            log_with_timestamp(f"Current working directory: {os.getcwd()}")
            
            server_params = StdioServerParameters(
                command="python",
                args=["example3.py"],
                cwd="/Users/nageswar.sahoo/Desktop/ERAG/EAG-V1/assignment-8/src/"
            )

            try:
                log_with_timestamp("Connecting to MCP server...")
                async with stdio_client(server_params) as (read, write):
                    log_with_timestamp("Connection established, creating session...")
                    try:
                        async with ClientSession(read, write) as session:
                            log_with_timestamp("Session created, initializing...")
 
                            try:
                                await session.initialize()
                                log_with_timestamp("MCP session initialized")

                                # Get available tools
                                log_with_timestamp("Requesting tool list...")
                                tools_result = await retry_with_backoff(session.list_tools)
                                tools = tools_result.tools
                                log_with_timestamp("tool list received...")

                                print(tools)
                                tool_descriptions = "\n".join(
                                    f"- {tool.name}: {getattr(tool, 'description', 'No description')}" 
                                    for tool in tools
                                )

                                log_with_timestamp(f"{len(tools)} tools loaded")
                                log_with_timestamp("Available tools:\n" + tool_descriptions)

                                memory = MemoryManager()
                                session_id = f"session-{int(time.time())}"
                                query = user_input  # Store original intent
                                step = 0

                                while step < max_steps:
                                    log_with_timestamp(f"Step {step + 1} started")

                                    perception = extract_perception(user_input)
                                    log_with_timestamp(f"Intent: {perception.intent}, Tool hint: {perception.tool_hint}")

                                    retrieved = memory.retrieve(query=user_input, top_k=3, session_filter=session_id)
                                    log_with_timestamp(f"Retrieved {len(retrieved)} relevant memories")

                                    plan = generate_plan(
                                        perception=perception,
                                        memory_items=retrieved,
                                        tool_descriptions=tool_descriptions
                                    )
                                    log_with_timestamp(f"Plan generated: {plan}")

                                    if plan.startswith("FINAL_ANSWER:"):
                                        final_answer = plan.replace("FINAL_ANSWER:", "").strip()
                                        log_with_timestamp(f"✅ FINAL RESULT: {final_answer}")
                                        
                                        # Store result in Google Sheets
                                        result_data = {
                                            "query": query,
                                            "answer": final_answer,
                                            "timestamp": datetime.datetime.now().isoformat(),
                                            "session_id": session_id,
                                            "steps_taken": step + 1
                                        }
                                        
                                        try:
                                            sheets_link = await store_result_in_sheets(result_data)
                                            return f"Your result has been stored in Google Sheets. You can view it here: {sheets_link}"
                                        except Exception as e:
                                            log_with_timestamp(f"Error storing in sheets: {str(e)}", "ERROR")
                                            return f"Final answer: {final_answer}\n(Note: Could not store in Google Sheets: {str(e)})"

                                    try:
                                        result = await retry_with_backoff(execute_tool, session, tools, plan)
                                        log_with_timestamp(f"{result.tool_name} returned: {result.result}")

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
                                        log_with_timestamp(f"Tool execution failed: {e}", "ERROR")
                                        return f"Error executing tool: {str(e)}"

                                    step += 1
                                
                                return "Maximum steps reached without finding a final answer."
                            except Exception as e:
                                log_with_timestamp(f"Session initialization error: {str(e)}", "ERROR")
                                return f"Session initialization error: {str(e)}"
                    except Exception as e:
                        log_with_timestamp(f"Session creation error: {str(e)}", "ERROR")
                        return f"Session creation error: {str(e)}"
            except Exception as e:
                log_with_timestamp(f"Connection error: {str(e)}", "ERROR")
                return f"Connection error: {str(e)}"
        except Exception as e:
            log_with_timestamp(f"Overall error: {str(e)}", "ERROR")
            return f"Overall error: {str(e)}"

        log_with_timestamp("Agent session complete.")
        return "Agent session completed without a result."

# Remove the standalone main function since it's now part of the Agent class
if __name__ == "__main__":
    query = input("🧑 What do you want to solve today? → ")
    agent = Agent()
    asyncio.run(agent.main(query))


# Find the ASCII values of characters in INDIA and then return sum of exponentials of those values.
# How much Anmol singh paid for his DLF apartment via Capbridge? 
# What do you know about Don Tapscott and Anthony Williams?
# What is the relationship between Gensol and Go-Auto?