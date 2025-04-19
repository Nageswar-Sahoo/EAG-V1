import logging
from typing import List, Dict, Any
from mcp import ClientSession, types
import pyautogui
import json

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
            
            if hasattr(result, 'content'):
                if isinstance(result.content, list):
                    formatted_result = [item.text if hasattr(item, 'text') else str(item) for item in result.content]
                else:
                    formatted_result = str(result.content)
            else:
                formatted_result = str(result)
                
            return formatted_result
            
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
        
    async def process_llm_response(self, session: ClientSession, tools: List[types.Tool], parsed_responses: List[Dict[str, Any]]) -> Any:
        """Process the LLM response and execute appropriate actions"""
        self.logger.info("🔍 Processing LLM response...")
        
        for response in parsed_responses:
            response_type = response.get("type")
            self.logger.info(f"📝 Processing response type: {response_type}")
            
            if response_type == "FUNCTION_CALL":
                try:
                    self.logger.info(f"Executing function call: {response['name']}")
                    self.logger.info(f"Function arguments: {json.dumps(response['args'], indent=2)}")
                    
                    result = await self.handle_function_call(session, tools, response["name"], response["args"])
                    
                    self.logger.info(f"Function call successful")
                    self.logger.info(f"Result: {result}")
                    return result
                except Exception as e:
                    self.logger.error(f"Function call failed: {str(e)}")
                    return f"Error: {str(e)}"
            elif response_type == "FINAL_ANSWER":
                self.logger.info(f"🎯 Final answer received: {response.get('value')}")
                return response.get("value")
            elif response_type == "ERROR":
                self.logger.error(f"Error response: {response.get('message')}")
                return f"Error: {response.get('message')}"
            elif response_type == "VERIFICATION":
                self.logger.info(f"✓ Verification step: {response}")
                return response
                
        self.logger.warning("No valid response type found in parsed responses")
        return None 