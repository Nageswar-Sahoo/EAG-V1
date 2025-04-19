import logging
from typing import List, Dict, Any
from mcp import ClientSession, types
import pyautogui
import json
from models import LLMResponse

class ActionLayer:
    def __init__(self):
        self.logger = logging.getLogger('action')
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        
    async def handle_function_call(self, session: ClientSession, tools: List[types.Tool], func_name: str, args: Dict[str, Any]) -> Any:
        """Handle a function call with proper error handling"""
        try:
            tool = next((t for t in tools if t.name == func_name), None)
            if not tool:
                self.logger.error(f"Unknown tool: {func_name}")
                raise ValueError(f"Unknown tool: {func_name}")

            result = await session.call_tool(func_name, arguments=args)
            
            # Handle different result types
            if isinstance(result, list):
                if len(result) == 1:
                    result = result[0]
                else:
                    result = result
            
            # Convert string results to appropriate type
            if isinstance(result, str):
                try:
                    if '.' in result:
                        return float(result)
                    else:
                        return int(result)
                except (ValueError, TypeError):
                    return result
            
            return result
            
        except Exception as e:
            self.logger.error(f"Tool error: {e}")
            raise
            
    def format_tool_call_details(self, func_name: str, args: Dict[str, Any], result: Any) -> str:
        """Format tool call details for logging"""
        return f"""
🛠️ Tool Call Details:
    Function: {func_name}
    Arguments: {json.dumps(args, indent=4)}
    Result: {result}
"""
        
    async def process_llm_response(self, session: ClientSession, tools: List[types.Tool], parsed_responses: List[LLMResponse]) -> Any:
        """Process the LLM response and execute appropriate actions"""
        self.logger.info("🔍 Processing LLM response...")
        
        for response in parsed_responses:
            self.logger.info(f"📝 Processing response type: {response.type}")
            
            if response.type == "FUNCTION_CALL":
                try:
                    self.logger.info(f"Executing function call: {response.name}")
                    self.logger.info(f"Function arguments: {json.dumps(response.args, indent=2)}")
                    
                    result = await self.handle_function_call(session, tools, response.name, response.args)
                    
                    self.logger.info(f"Function call successful")
                    self.logger.info(f"Result: {result}")
                    return result
                except Exception as e:
                    self.logger.error(f"Function call failed: {str(e)}")
                    return f"Error: {str(e)}"
            elif response.type == "FINAL_ANSWER":
                self.logger.info(f"🎯 Final answer received: {response.value}")
                return response.value
            elif response.type == "ERROR":
                self.logger.error(f"Error response: {response.message}")
                return f"Error: {response.message}"
                
        self.logger.warning("No valid response type found in parsed responses")
        return None 