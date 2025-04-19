import logging
from typing import List, Dict, Any
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

from perception import PerceptionLayer
from memory import MemoryLayer
from decision_making import DecisionMakingLayer
from action import ActionLayer
from prompts import get_system_prompt, get_current_query

class CognitiveAgent:
    def __init__(self):
        self.perception = PerceptionLayer()
        self.memory = MemoryLayer()
        self.decision_making = DecisionMakingLayer()
        self.action = ActionLayer()
        self.max_iterations = 15
        
    def reset_state(self):
        """Reset all layers to their initial state"""
        self.memory.reset_state()
        
    def create_system_prompt(self, tools_description: str) -> str:
        """Create the system prompt for the LLM"""
        return get_system_prompt(tools_description)
        
    async def run(self, original_query: str):
        """Run the cognitive agent with the given query"""
        self.reset_state()
        logging.info("Starting execution")
        logging.info(f"Original query: {original_query}")
        
        try:
            server_params = StdioServerParameters(
                command="python",
                args=["mcp_tool.py"]
            )

            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    tools_result = await session.list_tools()
                    tools = tools_result.tools
                    logging.info(f"Available tools: {[tool.name for tool in tools]}")
                    
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
                        except Exception as e:
                            logging.error(f"Tool error: {e}")
                            tools_description.append(f"{i+1}. Error processing tool")
                    
                    tools_description = "\n".join(tools_description)
                    system_prompt = self.create_system_prompt(tools_description)
                    
                    self.memory.update_current_expression(original_query)
                    remaining = original_query  # Initialize remaining with original query
                    
                    while self.memory.iteration < self.max_iterations:
                        logging.info(f"\nIteration {self.memory.iteration + 1}/{self.max_iterations}")
                        logging.info(f"Current expression: {remaining}")
                        
                        if self.memory.iteration == 0:
                            current_query = self.decision_making.generate_current_query(
                                original_query=original_query,
                                iteration=self.memory.iteration,
                                memory=self.memory
                            )
                        else:
                            current_query = self.decision_making.generate_current_query(
                                original_query=original_query,
                                iteration=self.memory.iteration,
                                memory=self.memory
                            )
                        
                        response_text = await self.perception.generate_with_timeout(f"{system_prompt}\n\nQuery: {current_query}")
                        parsed_responses = self.perception.parse_json_response(response_text)
                        logging.info(f"LLM Response: {parsed_responses}")
                        
                        result = await self.action.process_llm_response(session, tools, parsed_responses)
                        logging.info(f"Function call result: {result}")
                        
                        if self.decision_making.process_llm_response(parsed_responses, result, self.memory):
                            break
                                
                        self.memory.increment_iteration()
                        
        except Exception as e:
            logging.error(f"Execution error: {e}")
            import traceback
            logging.error(traceback.format_exc())
        finally:
            self.reset_state() 