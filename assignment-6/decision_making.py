import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from prompts import get_current_query


class DecisionMakingLayer:
    def __init__(self):
        self.logger = logging.getLogger('decision_making')
    
    def get_next_operation(self, expression: str, completed_steps: List[Dict[str, Any]]) -> Tuple[Optional[str], Optional[str]]:
        """Determine the next operation to perform based on the current state"""
        operations = [
            ('power', '**'),
            ('multiply', '*'),
            ('divide', '/'),
            ('remainder', '%'),
            ('add', '+'),
            ('subtract', '-')
        ]
        
        for op_name, op_symbol in operations:
            if op_symbol in expression:
                return op_name, op_symbol
        return None, None
    
    def is_final_result(self, result: Any) -> bool:
        """Check if the result is a final answer or error"""
        if isinstance(result, (int, float)):
            return True
        if isinstance(result, str):
            return result.startswith("Error")
        if isinstance(result, list):
            if len(result) == 1 and isinstance(result[0], (int, float, str)):
                try:
                    float(result[0])
                    return True
                except (ValueError, TypeError):
                    return False
        return False
    
    def format_query_for_logging(self, query: str) -> str:
        """Format the query for logging in a readable way"""
        try:
            sections = query.split('\n\n')
            formatted = []
            
            for section in sections:
                if section.startswith('Computation history:'):
                    history_lines = section.split('\n')
                    formatted.append("📊 Computation History:")
                    for line in history_lines[1:]:
                        if line.strip():
                            formatted.append(f"    {line.strip()}")
                elif section.startswith('Current expression:'):
                    expr = section.split(':', 1)[1].strip()
                    formatted.append(f"🔢 Current Expression: {expr}")
                elif section.startswith('What is the next operation'):
                    formatted.append("❓ Next Step:")
                    formatted.append(f"    {section.strip()}")
                else:
                    formatted.append(section.strip())
            
            return '\n'.join(formatted)
        except Exception as e:
            self.logger.error(f"Query format error: {e}")
            return query

    def generate_current_query(self, original_query: str, iteration: int, memory) -> str:
        """Generate the current query for the LLM based on the current state"""
        if iteration == 0:
            return get_current_query(
                original_query=original_query,
                iteration=iteration,
                computation_history=[],
                current_expression=original_query
            )
        else:
            history = memory.get_computation_history()
            remaining = memory.current_expression
            for step in history:
                remaining = remaining.replace(step['operation'], str(step['result']))
                
            next_op, op_symbol = self.get_next_operation(remaining, history)
            self.logger.info(f"Next operation: {next_op} ({op_symbol})")
            
            return get_current_query(
                original_query=original_query,
                iteration=iteration,
                computation_history=history,
                current_expression=remaining,
                next_op=next_op,
                op_symbol=op_symbol
            )

    def process_llm_response(self, parsed_responses: List[Dict[str, Any]], result: Any, memory) -> bool:
        """Process the LLM response and update memory with computation steps"""
        if result is not None and len(parsed_responses) >= 2:
            reasoning = parsed_responses[0]
            function_call = parsed_responses[1]
            
            if function_call.get("type") == "FUNCTION_CALL":
                operation = f"{function_call['name']}({', '.join(f'{k}={v}' for k, v in function_call['args'].items())})"
                self.logger.info(f"Executing operation: {operation}")
                memory.add_computation_step({
                    'operation': operation,
                    'result': result,
                    'iteration': memory.iteration + 1,
                    'args': function_call['args']
                })
            
            memory.last_response = result
            memory.add_iteration_response(str(result))
            
            try:
                final_result = eval(memory.current_expression)
                if len(memory.get_computation_history()) > 0 and all(
                    str(step['result']) in memory.current_expression 
                    for step in memory.get_computation_history()
                ):
                    self.logger.info(f"Final result computed: {final_result}")
                    return True
            except Exception as e:
                self.logger.error(f"Error evaluating final result: {e}")
        
        return False 