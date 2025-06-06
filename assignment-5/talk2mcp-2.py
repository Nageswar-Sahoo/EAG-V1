import os
import json
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
import asyncio
from google import genai
from concurrent.futures import TimeoutError
from functools import partial
import pyautogui
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG to capture all logs
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_execution.log', mode='w'),  # Overwrite existing file
        logging.StreamHandler()  # Keep console output
    ]
)

# Create a custom logger for detailed execution logs
execution_logger = logging.getLogger('execution')
execution_logger.setLevel(logging.DEBUG)

# Create a file handler for execution details
execution_handler = logging.FileHandler('mcp_execution_details.log', mode='w')
execution_handler.setLevel(logging.DEBUG)

# Create a formatter for execution logs
execution_formatter = logging.Formatter('''
%(asctime)s - %(levelname)s
%(message)s
----------------------------------------
''')
execution_handler.setFormatter(execution_formatter)
execution_logger.addHandler(execution_handler)

def log_execution_details(category, details):
    """Log detailed execution information to the execution log file"""
    execution_logger.debug(f"""
🔍 {category}
{json.dumps(details, indent=2)}
""")

# Load environment variables from .env file
load_dotenv()

# Access your API key and initialize Gemini client correctly
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

max_iterations = 20
last_response = None
iteration = 0
iteration_response = []

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

async def generate_with_timeout(client, prompt, timeout=10):
    """Generate content with a timeout"""
    logging.info("Starting LLM generation...")
    try:
        loop = asyncio.get_event_loop()
        response = await asyncio.wait_for(
            loop.run_in_executor(
                None, 
                lambda: client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt
                )
            ),
            timeout=timeout
        )
        logging.info("LLM generation completed successfully")
        return response
    except TimeoutError:
        logging.error("LLM generation timed out!")
        raise
    except Exception as e:
        logging.error(f"Error in LLM generation: {e}")
        raise

def reset_state():
    """Reset all global variables to their initial state"""
    global last_response, iteration, iteration_response
    logging.info("Resetting state variables")
    last_response = None
    iteration = 0
    iteration_response = []

def parse_json_response(response_text):
    """Parse the LLM response into a list of JSON objects"""
    try:
        logging.info("Parsing JSON response")
        # Split response into lines and filter out empty lines
        lines = [line.strip() for line in response_text.split('\n') if line.strip()]
        logging.debug(f"Found {len(lines)} non-empty lines in response")
        
        # Parse each line as JSON
        parsed_responses = []
        for line in lines:
            try:
                parsed = json.loads(line)
                parsed_responses.append(parsed)
                logging.debug(f"Successfully parsed JSON: {parsed}")
            except json.JSONDecodeError:
                logging.warning(f"Could not parse line as JSON: {line}")
                continue
                
        logging.info(f"Successfully parsed {len(parsed_responses)} JSON objects")
        return parsed_responses
    except Exception as e:
        logging.error(f"Error parsing response: {e}")
        return []

async def handle_function_call(session, tools, func_name, args):
    """Handle a function call with proper error handling"""
    try:
        logging.info(f"Handling function call: {func_name} with args: {args}")
        # Find the matching tool
        tool = next((t for t in tools if t.name == func_name), None)
        if not tool:
            logging.error(f"Unknown tool: {func_name}")
            raise ValueError(f"Unknown tool: {func_name}")

        # Call the tool
        logging.info(f"Calling tool: {func_name}")
        result = await session.call_tool(func_name, arguments=args)
        
        # Format the result
        if hasattr(result, 'content'):
            if isinstance(result.content, list):
                formatted_result = [item.text if hasattr(item, 'text') else str(item) for item in result.content]
            else:
                formatted_result = str(result.content)
        else:
            formatted_result = str(result)
            
        logging.info(f"Function call {func_name} completed successfully. Result: {formatted_result}")
        return formatted_result
        
    except Exception as e:
        logging.error(f"Error in function call {func_name}: {e}")
        raise

def verify_result(expression, result, expected=None):
    """Verify if the result matches the expected value or is mathematically correct"""
    try:
        # If expected value is provided, compare directly
        if expected is not None:
            return abs(float(result) - float(expected)) < 1e-10
        
        # Otherwise, evaluate the expression and compare
        computed = eval(expression)
        return abs(float(result) - float(computed)) < 1e-10
    except Exception as e:
        logging.error(f"Error in verification: {e}")
        return False

def format_verification_result(expression, result, expected=None, is_correct=None):
    """Format the verification result in a structured way"""
    if is_correct is None:
        is_correct = verify_result(expression, result, expected)
    
    verification = {
        "type": "VERIFICATION",
        "expression": expression,
        "result": result,
        "expected": expected,
        "is_correct": is_correct,
        "timestamp": datetime.now().isoformat()
    }
    
    log_execution_details("Verification", verification)
    return verification

def format_llm_input_output(prompt, response_text, parsed_responses):
    """Format LLM input and output for detailed logging"""
    formatted = f"""
📥 LLM Input:
{prompt}

📤 LLM Output:
{response_text}

🔍 Parsed Responses:
{json.dumps(parsed_responses, indent=2)}
"""
    log_execution_details("LLM Interaction", {
        "input": prompt,
        "output": response_text,
        "parsed_responses": parsed_responses
    })
    return formatted

def format_tool_call_details(func_name, args, result):
    """Format tool call details for logging"""
    formatted = f"""
🛠️ Tool Call Details:
- Function: {func_name}
- Arguments: {json.dumps(args, indent=2)}
- Result: {result}
"""
    log_execution_details("Tool Call", {
        "function": func_name,
        "arguments": args,
        "result": result
    })
    return formatted

async def process_llm_response(session, tools, response_text):
    """Process the LLM response and execute appropriate actions"""
    logging.info("Processing LLM response")
    parsed_responses = parse_json_response(response_text)
    
    # Log detailed LLM response information
    log_execution_details("LLM Response Processing", {
        "raw_response": response_text,
        "parsed_responses": parsed_responses
    })
    
    for response in parsed_responses:
        response_type = response.get("type")
        logging.info(f"Processing response type: {response_type}")
        
        if response_type == "FUNCTION_CALL":
            try:
                # Log tool call details
                log_execution_details("Tool Call Initiation", {
                    "function": response["name"],
                    "arguments": response["args"],
                    "status": "pending"
                })
                
                result = await handle_function_call(session, tools, response["name"], response["args"])
                
                # Log tool call result
                log_execution_details("Tool Call Completion", {
                    "function": response["name"],
                    "arguments": response["args"],
                    "result": result,
                    "status": "completed"
                })
                
                # Add verification step for calculate operations
                if response["name"] == "calculate":
                    expression = response["args"].get("expression", "")
                    verification = format_verification_result(expression, result)
                    
                    if not verification["is_correct"]:
                        error_response = {
                            "type": "ERROR",
                            "message": f"Verification failed for expression: {expression}",
                            "verification": verification
                        }
                        log_execution_details("Verification Error", error_response)
                        return error_response
                
                return result
            except Exception as e:
                error_msg = f"Error executing function: {str(e)}"
                log_execution_details("Function Error", {
                    "error": str(e),
                    "function": response["name"],
                    "arguments": response["args"]
                })
                return error_msg
        elif response_type == "FINAL_ANSWER":
            final_answer = response.get("value")
            log_execution_details("Final Answer", {
                "value": final_answer
            })
            return final_answer
        elif response_type == "ERROR":
            error_msg = f"Error: {response.get('message')}"
            log_execution_details("Error Response", response)
            return error_msg
        elif response_type == "VERIFICATION":
            # Handle explicit verification requests
            expression = response.get("expression")
            result = response.get("result")
            expected = response.get("expected")
            
            verification = format_verification_result(expression, result, expected)
            
            if not verification["is_correct"]:
                error_response = {
                    "type": "ERROR",
                    "message": f"Verification failed for expression: {expression}",
                    "verification": verification
                }
                log_execution_details("Verification Error", error_response)
                return error_response
            return verification
    
    logging.warning("No valid response type found in parsed responses")
    return None

def is_final_result(result):
    """Check if the result is a final answer or error"""
    if isinstance(result, (int, float)):
        return True
    if isinstance(result, str):
        return result.startswith("Error")
    if isinstance(result, list):
        # If it's a list with a single number, treat it as final
        if len(result) == 1 and isinstance(result[0], (int, float, str)):
            try:
                float(result[0])  # Try to convert to number
                return True
            except (ValueError, TypeError):
                return False
    return False

def format_query_for_logging(query):
    """Format the query for logging in a readable way"""
    try:
        # Split the query into sections
        sections = query.split('\n\n')
        formatted = []
        
        for section in sections:
            if section.startswith('Computation history:'):
                # Format computation history
                history_lines = section.split('\n')
                formatted.append("📊 Computation History:")
                for line in history_lines[1:]:
                    if line.strip():
                        formatted.append(f"   {line.strip()}")
            elif section.startswith('Current expression:'):
                # Format current expression
                expr = section.split(':', 1)[1].strip()
                formatted.append(f"🔢 Current Expression: {expr}")
            elif section.startswith('What is the next operation'):
                # Format the question
                formatted.append("❓ Next Step:")
                formatted.append(f"   {section.strip()}")
            else:
                # Format other sections
                formatted.append(section.strip())
        
        return '\n'.join(formatted)
    except Exception as e:
        logging.error(f"Error formatting query: {e}")
        return query

def format_computation_step(step, iteration):
    """Format a single computation step with detailed information"""
    try:
        # Extract operation details
        operation = step['operation']
        result = step['result']
        args = step.get('args', {})
        
        # Format the step with iteration number and details
        formatted = f"""Step {iteration}:
   Operation: {operation}
   Parameters: {', '.join(f'{k}={v}' for k, v in args.items())}
   Result: {result}
   Status: {'✅ Completed' if result else '❌ Failed'}"""
        
        return formatted
    except Exception as e:
        logging.error(f"Error formatting computation step: {e}")
        return str(step)

def get_next_operation(expression, completed_steps):
    """Determine the next operation to perform based on the current state"""
    # Create a list of operations in order of precedence
    operations = [
        ('power', '**'),
        ('multiply', '*'),
        ('divide', '/'),
        ('remainder', '%'),
        ('add', '+'),
        ('subtract', '-')
    ]
    
    # Find the next operation to perform
    for op_name, op_symbol in operations:
        if op_symbol in expression:
            return op_name, op_symbol
    return None, None

async def main():
    global iteration, last_response, iteration_response
    reset_state()
    logging.info("Starting main execution...")
    log_execution_details("Execution Start", {
        "timestamp": datetime.now().isoformat(),
        "iteration": iteration
    })
    
    try:
        server_params = StdioServerParameters(
            command="python",
            args=["example2-3.py"]
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                logging.info("Initializing session...")
                await session.initialize()
                
                # Get available tools
                logging.info("Fetching available tools...")
                tools_result = await session.list_tools()
                tools = tools_result.tools
                logging.info(f"Successfully retrieved {len(tools)} tools")

                # Create tools description
                tools_description = []
                for i, tool in enumerate(tools):
                    try:
                        params = tool.inputSchema
                        desc = getattr(tool, 'description', 'No description available')
                        name = getattr(tool, 'name', f'tool_{i}')
                        
                        if 'properties' in params:
                            param_details = []
                            for param_name, param_info in params['properties'].items():
                                param_type = param_info.get('type', 'unknown')
                                param_details.append(f"{param_name}: {param_type}")
                            params_str = ', '.join(param_details)
                        else:
                            params_str = 'no parameters'

                        tool_desc = f"{i+1}. {name}({params_str}) - {desc}"
                        tools_description.append(tool_desc)
                        logging.debug(f"Processed tool: {tool_desc}")
                    except Exception as e:
                        logging.error(f"Error processing tool {i}: {e}")
                        tools_description.append(f"{i+1}. Error processing tool")
                
                tools_description = "\n".join(tools_description)
                logging.info("Tools description created successfully")
                
                # Create system prompt with mandatory verification
                logging.info("Creating system prompt...")
                system_prompt = f"""You are a step-by-step math agent. Solve math problems using the tools listed below. Think before each step. Use tools iteratively, verify results, and handle errors. You MUST respond with a sequence of exactly three JSON lines per step: first a reasoning-type declaration, then a function call, and finally a verification step.

Available tools:
{tools_description}

======================================
✅ OUTPUT FORMAT
======================================

Every reasoning step must include:

1. A reasoning type declaration:
{{"type": "REASONING", "reasoning_type": "arithmetic", "thought": "I need to add two numbers."}}

2. A corresponding tool call:
{{"type": "FUNCTION_CALL", "name": "add", "args": {{"a": 5, "b": 3}}}}

3. A mandatory verification step:
{{"type": "VERIFICATION", "expression": "5 + 3", "result": 8, "expected": 8}}

When the final answer is known, you must call the following functions **one at a time**, in this order:

a. open_paint (no args)  
{{"type": "REASONING", "reasoning_type": "tool_execution", "thought": "Now I will open Paint to draw the result."}}  
{{"type": "FUNCTION_CALL", "name": "open_paint", "args": {{}}}}  
{{"type": "VERIFICATION", "expression": "open_paint()", "result": "success", "expected": "success"}}

b. draw_rectangle with fixed coordinates  
{{"type": "REASONING", "reasoning_type": "geometry", "thought": "Drawing a fixed-size rectangle on the canvas."}}  
{{"type": "FUNCTION_CALL", "name": "draw_rectangle", "args": {{"x1": 200, "y1": 200, "x2": 1000, "y2": 1000}}}}  
{{"type": "VERIFICATION", "expression": "draw_rectangle(200,200,1000,1000)", "result": "success", "expected": "success"}}

c. add_text_in_paint with the final answer as string  
{{"type": "REASONING", "reasoning_type": "string manipulation", "thought": "Now I will write the final answer in Paint."}}  
{{"type": "FUNCTION_CALL", "name": "add_text_in_paint", "args": {{"text": "final_answer"}}}}  
{{"type": "VERIFICATION", "expression": "add_text_in_paint(final_answer)", "result": "success", "expected": "success"}}

d. Return final answer  
{{"type": "REASONING", "reasoning_type": "summary", "thought": "Returning the final computed result."}}  
{{"type": "FINAL_ANSWER", "value": final_answer}}  
{{"type": "VERIFICATION", "expression": "final_answer", "result": final_answer, "expected": final_answer}}

======================================
📌 RULES
======================================

- Every step must include three JSON lines: REASONING, FUNCTION_CALL, and VERIFICATION.
- Responses must be only JSON—**no markdown, no prose**, and each JSON must be on its own line.
- Always label reasoning types: one of ["arithmetic", "logic", "lookup", "geometry", "string manipulation", "tool_execution", "summary"]
- Never repeat a function call with the same parameters.
- Handle all tool outputs and errors explicitly.
- Verification is MANDATORY for every step.
- If unsure or if an error occurs, respond with:
  {{"type": "REASONING", "reasoning_type": "error_handling", "thought": "There was a failure or ambiguity."}}
  {{"type": "ERROR", "message": "Describe the issue or ambiguity here."}}
  {{"type": "VERIFICATION", "expression": "error", "result": "error", "expected": "error"}}
"""

                original_query = """Find the result of ((15 + 5) * 3 - (18 / 2)) + (27 % 4) - (2 ** 3) + (100 // 9) """
                logging.info(f"Starting execution with query: {original_query}")
                
                # Track the current expression being evaluated
                current_expression = original_query
                computation_steps = []
                
                while iteration < max_iterations:
                    log_execution_details("Iteration Start", {
                        "iteration": iteration + 1,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    logging.info(f"\n--- Starting Iteration {iteration + 1} ---")
                    
                    # Build the current query with context
                    if iteration == 0:
                        current_query = f"""Evaluate this expression step by step: {current_expression}

Break down the expression into smaller parts and solve them one at a time. For each step:
1. Identify the next operation to perform
2. Use the appropriate tool to compute it
3. Show the result

Start with the innermost parentheses and work your way out."""
                    else:
                        # Show computation history with detailed information
                        history = "\n".join([
                            format_computation_step(step, i+1)
                            for i, step in enumerate(computation_steps)
                        ])
                        
                        # Build remaining expression
                        remaining = current_expression
                        for step in computation_steps:
                            remaining = remaining.replace(step['operation'], str(step['result']))
                            
                        # Get the next operation to perform
                        next_op, op_symbol = get_next_operation(remaining, computation_steps)
                        
                        current_query = f"""Continue evaluating this expression step by step:

📊 Computation History:
{history}

🔢 Current Expression: {remaining}

📝 Expression Breakdown:
- Original expression: {original_query}
- Current iteration: {iteration + 1}
- Steps completed: {len(computation_steps)}
- Next operation type: {next_op if next_op else 'None'}
- Next operation symbol: {op_symbol if op_symbol else 'None'}

❓ Next Step:
What is the next operation to perform? Break it down into the smallest possible step.
Remember:
1. Work from innermost parentheses outward
2. Don't repeat operations already performed
3. Use the appropriate tool for each operation
4. Show both the operation and its result
5. Follow the order of operations: parentheses, exponents, multiplication/division, addition/subtraction"""
                    
                    # Log the formatted query
                    formatted_query = format_query_for_logging(current_query)
                    logging.info(f"\n📝 Query to LLM:\n{formatted_query}\n")

                    try:
                        logging.info("Generating LLM response...")
                        response = await generate_with_timeout(client, f"{system_prompt}\n\nQuery: {current_query}")
                        response_text = response.text.strip()
                        logging.debug(f"Raw LLM response: {response_text}")
                        
                        logging.info("Processing LLM response...")
                        result = await process_llm_response(session, tools, response_text)
                        if result is not None:
                            # Parse the response to get the operation and result
                            try:
                                parsed_responses = parse_json_response(response_text)
                                if len(parsed_responses) >= 2:
                                    reasoning = parsed_responses[0]
                                    function_call = parsed_responses[1]
                                    
                                    if function_call.get("type") == "FUNCTION_CALL":
                                        operation = f"{function_call['name']}({', '.join(f'{k}={v}' for k, v in function_call['args'].items())})"
                                        computation_steps.append({
                                            'operation': operation,
                                            'result': result,
                                            'iteration': iteration + 1,
                                            'args': function_call['args']
                                        })
                            except Exception as e:
                                logging.error(f"Error parsing response: {e}")
                                
                            last_response = result
                            iteration_response.append(f"Iteration {iteration + 1} result: {result}")
                            logging.info(f"Iteration {iteration + 1} completed with result: {result}")
                            
                            # Check if we've evaluated the entire expression
                            try:
                                final_result = eval(current_expression)
                                if len(computation_steps) > 0 and all(
                                    str(step['result']) in current_expression 
                                    for step in computation_steps
                                ):
                                    logging.info("Final result computed, ending execution")
                                    break
                            except:
                                pass
                                
                    except Exception as e:
                        logging.error(f"Error in iteration {iteration + 1}: {e}")
                        break
                        
                    log_execution_details("Iteration End", {
                        "iteration": iteration + 1,
                        "result": result,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    iteration += 1

    except Exception as e:
        log_execution_details("Execution Error", {
            "error": str(e),
            "traceback": traceback.format_exc(),
            "timestamp": datetime.now().isoformat()
        })
        logging.error(f"Error in main execution: {e}")
        import traceback
        logging.error(traceback.format_exc())
    finally:
        log_execution_details("Execution End", {
            "timestamp": datetime.now().isoformat(),
            "total_iterations": iteration
        })
        logging.info("Resetting state...")
        reset_state()

if __name__ == "__main__":
    asyncio.run(main())
    
    
