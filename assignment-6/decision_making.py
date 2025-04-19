import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from prompts import get_current_query
from models import LLMResponse, ComputationStep


class DecisionMakingLayer:
    def __init__(self):
        self.logger = logging.getLogger('decision_making')
    
    def get_next_operation(self, expression: str, completed_steps: List[ComputationStep]) -> Tuple[Optional[str], Optional[str]]:
        """Determine the next operation to perform based on the current state"""
        # Define operations in order of precedence
        operations = [
            ('power', '**'),
            ('multiply', '*'),
            ('divide', '/'),
            ('remainder', '%'),
            ('floor_divide', '//'),
            ('add', '+'),
            ('subtract', '-')
        ]
        
        # First check for parentheses
        if '(' in expression:
            # Find the innermost parentheses
            start = expression.rfind('(')
            end = expression.find(')', start)
            if start != -1 and end != -1:
                inner_expr = expression[start+1:end]
                # Check operations in the inner expression
                for op_name, op_symbol in operations:
                    if op_symbol in inner_expr:
                        return op_name, op_symbol
                # If no operations in inner expression, it's just a number
                return None, None
        
        # If no parentheses, check operations in order of precedence
        for op_name, op_symbol in operations:
            if op_symbol in expression:
                # For power operation, make sure it's not part of a larger number
                if op_symbol == '**':
                    # Find all occurrences of **
                    indices = [i for i, c in enumerate(expression) if expression[i:i+2] == '**']
                    for idx in indices:
                        # Check if it's a valid power operation (not part of a number)
                        if idx > 0 and idx < len(expression)-2:
                            prev_char = expression[idx-1]
                            next_char = expression[idx+2]
                            if prev_char.isdigit() and next_char.isdigit():
                                return op_name, op_symbol
                else:
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
            remaining = memory.state.current_expression
            for step in history:
                remaining = remaining.replace(step.operation, str(step.result))
                
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

    def process_llm_response(self, parsed_responses: List[LLMResponse], result: Any, memory) -> bool:
        """Process the LLM response and update memory with computation steps"""
        if result is not None and len(parsed_responses) >= 2:
            reasoning = parsed_responses[0]
            function_call = parsed_responses[1]
            
            if function_call.type == "FUNCTION_CALL":
                # Extract the operation and arguments
                operation = function_call.name
                args = function_call.args.get('input', {})
                
                # Format the operation string
                if operation in ['add', 'subtract', 'multiply', 'divide', 'power', 'remainder', 'floor_divide']:
                    op_symbol = {
                        'add': '+',
                        'subtract': '-',
                        'multiply': '*',
                        'divide': '/',
                        'power': '**',
                        'remainder': '%',
                        'floor_divide': '//'
                    }[operation]
                    operation_str = f"{args['a']} {op_symbol} {args['b']}"
                else:
                    operation_str = f"{operation}({', '.join(f'{k}={v}' for k, v in args.items())})"
                
                self.logger.info(f"Executing operation: {operation_str}")
                
                # Extract the actual result value from the TextContent
                if hasattr(result, 'content') and isinstance(result.content, list):
                    for content in result.content:
                        if hasattr(content, 'text'):
                            result_value = content.text
                            try:
                                # Try to convert to float first, then int if possible
                                result_value = float(result_value)
                                if result_value.is_integer():
                                    result_value = int(result_value)
                            except (ValueError, TypeError):
                                pass
                            break
                    else:
                        result_value = result
                else:
                    result_value = result
                
                memory.add_computation_step({
                    'operation': operation_str,
                    'result': result_value,
                    'args': args
                })
            
            memory.state.last_response = result
            memory.add_iteration_response(str(result))
            
            try:
                # Build the expression by replacing operations with their results
                expression = memory.state.current_expression
                
                # First, replace all completed operations with their results
                for step in memory.get_computation_history():
                    # Replace the operation with its result, handling parentheses
                    operation = step.operation
                    result = str(step.result)
                    
                    # Handle operations in parentheses
                    if f"({operation})" in expression:
                        expression = expression.replace(f"({operation})", result)
                    else:
                        expression = expression.replace(operation, result)
                
                # Clean up the expression
                expression = ' '.join(expression.split())
                expression = expression.replace('* *', '**')  # Fix power operator
                
                # Remove any non-numeric characters from the start/end
                expression = expression.strip('Find the result of ')
                
                # Check if there are any remaining operations
                remaining_ops = any(op in expression for op in ['+', '-', '*', '/', '**', '%', '//'])
                
                if not remaining_ops:
                    # If no remaining operations, try to evaluate the final result
                    try:
                        final_result = eval(expression)
                        self.logger.info(f"Final result computed: {final_result}")
                        return True
                    except Exception as e:
                        self.logger.error(f"Error evaluating final result: {e}")
                        return False
                else:
                    # If there are remaining operations, continue the iteration
                    self.logger.info(f"Remaining expression: {expression}")
                    return False
                    
            except Exception as e:
                self.logger.error(f"Error evaluating expression: {e}")
                return False
        
        return False 