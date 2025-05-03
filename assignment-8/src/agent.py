import asyncio
import time
import os
import datetime
from perception import extract_perception
from memory import MemoryManager, MemoryItem
from decision import generate_plan
from action import execute_tool
from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client
import logging
import random
import aiohttp
import json

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('agent.log')
    ]
)
logger = logging.getLogger(__name__)

# Constants
MAX_STEPS = 3
MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 1  # seconds

# MCP Server URLs
SHEETS_MCP_URL = "http://localhost:8051/sse"
EMAIL_MCP_URL = "http://localhost:8052/sse"

async def retry_with_backoff(func, *args, **kwargs):
    """Retry a function with exponential backoff"""
    retry_delay = INITIAL_RETRY_DELAY
    last_exception = None
    
    for attempt in range(MAX_RETRIES):
        try:
            logger.info(f"Attempt {attempt + 1} of {MAX_RETRIES} for function {func.__name__}")
            result = await func(*args, **kwargs)
            logger.info(f"Success on attempt {attempt + 1}")
            return result
        except Exception as e:
            last_exception = e
            if "503" in str(e) or "overloaded" in str(e).lower():
                if attempt < MAX_RETRIES - 1:
                    jitter = random.uniform(0, 0.1 * retry_delay)
                    wait_time = retry_delay + jitter
                    logger.warning(f"Attempt {attempt + 1} failed. Retrying in {wait_time:.2f} seconds... Error: {str(e)}")
                    await asyncio.sleep(wait_time)
                    retry_delay *= 2
                else:
                    logger.error(f"All {MAX_RETRIES} attempts failed. Last error: {str(e)}")
                    raise last_exception
            else:
                logger.error(f"Non-retryable error: {str(e)}")
                raise e
    
    raise last_exception

class Agent:
    def __init__(self):
        logger.info("Initializing Agent...")
        self.memory = MemoryManager()
        self.sheets_session = None
        self.email_session = None
        self.stdio_session = None
        self.tools = []  # Initialize tools list
        
    async def connect_to_mcp_servers(self):
        """Connect to MCP servers"""
        try:
            logger.info("Starting connection to MCP servers...")
            
            # Connect to Stdio MCP
            logger.info("Setting up Stdio MCP server parameters...")
            server_params = StdioServerParameters(
                command="python",
                args=["example3.py"],
                cwd="/Users/nageswar.sahoo/Desktop/ERAG/EAG-V1/assignment-8/src/"
            )
            
            logger.info("Connecting to Stdio MCP server...")
            async with stdio_client(server_params) as (stdio_read, stdio_write):
                logger.info("Stdio client connection established")
                async with ClientSession(stdio_read, stdio_write) as session:
                    logger.info("ClientSession for Stdio MCP created")
                    await session.initialize()
                    self.stdio_session = session
                    logger.info("Stdio MCP session initialized")
                    
                    # List available tools
                    logger.info("Fetching available Stdio tools...")
                    tools_result = await session.list_tools()
                    logger.info("Available Stdio tools:")
                    for tool in tools_result.tools:
                        logger.info(f"  - {tool.name}: {tool.description}")
                        self.tools.append(tool)  # Add tools to agent's tools list
            
            logger.info("Successfully connected to all MCP servers")
            
        except Exception as e:
            logger.error(f"Error connecting to MCP servers: {str(e)}")
            raise
            
    async def close_mcp_connections(self):
        """Close MCP connections"""
        try:
            logger.info("Closing MCP connections...")
            sessions = [self.sheets_session, self.email_session, self.stdio_session]
            for session in sessions:
                if session:
                    try:
                        session_name = session.__class__.__name__
                        logger.info(f"Closing {session_name} session...")
                        await session.__aexit__(None, None, None)
                        logger.info(f"{session_name} session closed")
                    except Exception as e:
                        logger.error(f"Error closing {session_name} session: {str(e)}")
            logger.info("All MCP connections closed")
        except Exception as e:
            logger.error(f"Error closing MCP connections: {str(e)}")
            raise
    
    async def store_result_in_sheets(self, result_data: dict) -> str:
        """Store result in Google Sheets via MCP server"""
        try:
            # Connect to Sheets MCP
            logger.info(f"Connecting to Sheets MCP at {SHEETS_MCP_URL}")
            async with sse_client(SHEETS_MCP_URL) as (sheets_read, sheets_write):
                logger.info("SSE client for Sheets MCP established")
                async with ClientSession(sheets_read, sheets_write) as session:
                    logger.info("ClientSession for Sheets MCP created")
                    await session.initialize()
                    logger.info("Sheets MCP session initialized")
                    
                    # List available tools
                    logger.info("Fetching available Sheets tools...")
                    tools_result = await session.list_tools()
                    logger.info("Available Sheets tools:")
                    for tool in tools_result.tools:
                        logger.info(f"  - {tool.name}: {tool.description}")
                    
                    # Store result
                    logger.info("Storing result in Sheets...")
                    logger.debug(f"Result data: {json.dumps(result_data, indent=2)}")
                    
                    # Prepare request data with result field
                    request_data = {
                        "result": {
                            "query": result_data.get("query", ""),
                            "answer": result_data.get("answer", ""),
                            "timestamp": result_data.get("timestamp", datetime.datetime.now().isoformat()),
                            "session_id": result_data.get("session_id", ""),
                            "steps_taken": result_data.get("steps_taken", 0)
                        }
                    }
                    
                    # Call the process_result tool
                    result = await session.call_tool(
                        "process_result",
                        arguments=request_data
                    )
                    
                    logger.info(f"Sheets storage result: {result}")
                    
                    # Handle different response formats
                    if isinstance(result, dict):
                        return result.get('spreadsheet_link', '')
                    elif hasattr(result, 'content') and len(result.content) > 0:
                        if isinstance(result.content[0].text, dict):
                            return result.content[0].text.get('spreadsheet_link', '')
                        elif isinstance(result.content[0].text, str):
                            try:
                                response_data = json.loads(result.content[0].text)
                                return response_data.get('spreadsheet_link', '')
                            except json.JSONDecodeError:
                                return result.content[0].text
                    else:
                        raise Exception("Invalid response format from Sheets MCP")
                    
        except Exception as e:
            error_msg = f"Error storing result in sheets: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    async def send_email_notification(self, result_data: dict, sheets_link: str) -> dict:
        """Send email notification with results"""
        try:
            # Connect to Email MCP
            logger.info(f"Connecting to Email MCP at {EMAIL_MCP_URL}")
            async with sse_client(EMAIL_MCP_URL) as (email_read, email_write):
                logger.info("SSE client for Email MCP established")
                async with ClientSession(email_read, email_write) as session:
                    logger.info("ClientSession for Email MCP created")
                    await session.initialize()
                    logger.info("Email MCP session initialized")
                    
                    # List available tools
                    logger.info("Fetching available Email tools...")
                    tools_result = await session.list_tools()
                    logger.info("Available Email tools:")
                    for tool in tools_result.tools:
                        logger.info(f"  - {tool.name}: {tool.description}")
                    
                    # Prepare email data
                    logger.info("Preparing email notification...")
                    email_data = {
                        "recipient_email": "tech.nageswar@gmail.com",  # Default recipient
                        "subject": "AI Assistant Results",
                        "content": {
                            "query": result_data.get("query", ""),
                            "answer": result_data.get("answer", ""),
                            "spreadsheet_link": sheets_link,
                            "session_id": result_data.get("session_id", ""),
                            "timestamp": result_data.get("timestamp", datetime.datetime.now().isoformat()),
                            "steps_taken": result_data.get("steps_taken", 0)
                        }
                    }
                    
                    logger.debug(f"Email data: {json.dumps(email_data, indent=2)}")
                    
                    # Call the send_email tool
                    result = await session.call_tool(
                        "send_email",
                        arguments=email_data
                    )
                    
                    logger.info(f"Email notification result: {result}")
                    
                    # Handle different response formats
                    if isinstance(result, dict):
                        return result
                    elif hasattr(result, 'content') and len(result.content) > 0:
                        if isinstance(result.content[0].text, dict):
                            return result.content[0].text
                        elif isinstance(result.content[0].text, str):
                            try:
                                return json.loads(result.content[0].text)
                            except json.JSONDecodeError:
                                return {"status": "success", "message": result.content[0].text}
                    else:
                        raise Exception("Invalid response format from Email MCP")
                    
        except Exception as e:
            error_msg = f"Error sending email notification: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    async def process_input(self, user_input: str) -> str:
        """Process user input through the agent's pipeline"""
        try:
            logger.info(f"Processing input: {user_input}")
            
            # 1. Perception
            logger.info("Extracting perception...")
            perception = extract_perception(user_input)
            logger.info(f"Perception extracted - Intent: {perception.intent}, Tool hint: {perception.tool_hint}")
            
            # 2. Memory
            logger.info("Retrieving relevant memories...")
            relevant_memories = self.memory.retrieve(
                query=user_input,
                top_k=3
            )
            logger.info(f"Found {len(relevant_memories)} relevant memories")
            
            # 3. Decision
            logger.info("Generating plan...")
            plan = generate_plan(
                perception=perception,
                memory_items=relevant_memories,
                tool_descriptions=str([t.__doc__ for t in self.tools])
            )
            logger.info(f"Plan generated: {plan}")
            
            # 4. Action
            logger.info("Executing plan...")
            if plan.startswith("FUNCTION_CALL:"):
                logger.info("Executing function call...")
                try:
                    # Extract tool name and arguments from the plan
                    tool_call = plan.replace("FUNCTION_CALL:", "").strip()
                    tool_name, *args = tool_call.split("|")
                    tool_args = {}
                    for arg in args:
                        key, value = arg.split("=", 1)
                        tool_args[key] = value
                    
                    logger.info(f"Calling tool {tool_name} with args: {tool_args}")
                    
                    # Try each session for tool execution
                    sessions = [self.stdio_session]
                    last_error = None
                    
                    for session in sessions:
                        if session:
                            try:
                                logger.info(f"Attempting to execute tool using {session.__class__.__name__}")
                                result = await session.call_tool(tool_name, arguments=tool_args)
                                logger.info(f"Tool execution successful with {session.__class__.__name__}")
                                return str(result.content[0].text)
                            except Exception as e:
                                last_error = e
                                logger.warning(f"Tool execution failed with {session.__class__.__name__}: {str(e)}")
                                continue
                    
                    if last_error:
                        raise last_error
                    else:
                        raise Exception("No available session for tool execution")
                        
                except Exception as e:
                    logger.error(f"Error executing tool: {str(e)}")
                    return f"Error executing tool: {str(e)}"
                    
            elif plan.startswith("FINAL_ANSWER:"):
                final_answer = plan.replace("FINAL_ANSWER:", "").strip()
                logger.info(f"Returning final answer: {final_answer}")
                return final_answer
            else:
                logger.warning("No valid action found in plan")
                return "I'm not sure how to handle that request."
                
        except Exception as e:
            logger.error(f"Error processing input: {str(e)}")
            return f"An error occurred: {str(e)}"

    async def main(self, user_input: str):
        try:
            logger.info("Starting agent...")
            logger.info(f"Current working directory: {os.getcwd()}")
            
            server_params = StdioServerParameters(
                command="python",
                args=["example3.py"],
                cwd="/Users/nageswar.sahoo/Desktop/ERAG/EAG-V1/assignment-8/src/"
            )

            try:
                logger.info("Connecting to MCP server...")
                async with stdio_client(server_params) as (read, write):
                    logger.info("Connection established, creating session...")
                    try:
                        async with ClientSession(read, write) as session:
                            logger.info("Session created, initializing...")
 
                            try:
                                await session.initialize()
                                logger.info("MCP session initialized")

                                # Get available tools
                                logger.info("Requesting tool list...")
                                tools_result = await retry_with_backoff(session.list_tools)
                                tools = tools_result.tools
                                logger.info("tool list received...")

                                print(tools)
                                tool_descriptions = "\n".join(
                                    f"- {tool.name}: {getattr(tool, 'description', 'No description')}" 
                                    for tool in tools
                                )

                                logger.info(f"{len(tools)} tools loaded")
                                logger.info("Available tools:\n" + tool_descriptions)

                                memory = MemoryManager()
                                session_id = f"session-{int(time.time())}"
                                query = user_input  # Store original intent
                                step = 0

                                while step < MAX_STEPS:
                                    logger.info(f"Step {step + 1} started")

                                    perception = extract_perception(user_input)
                                    logger.info(f"Intent: {perception.intent}, Tool hint: {perception.tool_hint}")

                                    retrieved = memory.retrieve(query=user_input, top_k=3, session_filter=session_id)
                                    logger.info(f"Retrieved {len(retrieved)} relevant memories")

                                    plan = generate_plan(
                                        perception=perception,
                                        memory_items=retrieved,
                                        tool_descriptions=tool_descriptions
                                    )
                                    logger.info(f"Plan generated: {plan}")

                                    if plan.startswith("FINAL_ANSWER:"):
                                        final_answer = plan.replace("FINAL_ANSWER:", "").strip()
                                        logger.info(f"✅ FINAL RESULT: {final_answer}")
                                        
                                        # Store result in Google Sheets
                                        result_data = {
                                            "query": query,
                                            "answer": final_answer,
                                            "timestamp": datetime.datetime.now().isoformat(),
                                            "session_id": session_id,
                                            "steps_taken": step + 1
                                        }
                                        
                                        try:
                                            # Store in sheets
                                            sheets_link = await self.store_result_in_sheets(result_data)
                                            
                                            # Send email notification
                                            email_result = await self.send_email_notification(result_data, sheets_link)
                                            
                                            return (
                                                f"Your result has been stored in Google Sheets and "
                                                f"an email notification has been sent.\n"
                                                f"Sheets Link: {sheets_link}\n"
                                                f"Email Status: {email_result['message']}"
                                            )
                                        except Exception as e:
                                            if "store_result_in_sheets" in str(e):
                                                return f"Final answer: {final_answer}\n(Note: Could not store in Google Sheets: {str(e)})"
                                            else:
                                                return (
                                                    f"Final answer: {final_answer}\n"
                                                    f"Sheets Link: {sheets_link}\n"
                                                    f"(Note: Could not send email: {str(e)})"
                                                )

                                    try:
                                        result = await retry_with_backoff(execute_tool, session, tools, plan)
                                        logger.info(f"{result.tool_name} returned: {result.result}")

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
                                        logger.info(f"Tool execution failed: {e}", "ERROR")
                                        return f"Error executing tool: {str(e)}"

                                    step += 1
                                
                                return "Maximum steps reached without finding a final answer."
                            except Exception as e:
                                logger.info(f"Session initialization error: {str(e)}", "ERROR")
                                return f"Session initialization error: {str(e)}"
                    except Exception as e:
                        logger.info(f"Session creation error: {str(e)}", "ERROR")
                        return f"Session creation error: {str(e)}"
            except Exception as e:
                logger.info(f"Connection error: {str(e)}", "ERROR")
                return f"Connection error: {str(e)}"
        except Exception as e:
            logger.info(f"Overall error: {str(e)}", "ERROR")
            return f"Overall error: {str(e)}"

        log_with_timestamp("Agent session complete.")
        return "Agent session completed without a result."
    

if __name__ == "__main__":
    query = input("🧑 What do you want to solve today? → ")
    agent = Agent()
    asyncio.run(agent.main(query))


# Find the ASCII values of characters in INDIA and then return sum of exponentials of those values.
# How much Anmol singh paid for his DLF apartment via Capbridge? 
# What do you know about Don Tapscott and Anthony Williams?
# What is the relationship between Gensol and Go-Auto?