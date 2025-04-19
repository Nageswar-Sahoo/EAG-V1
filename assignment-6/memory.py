import logging
from typing import List, Dict, Any
from datetime import datetime


class MemoryLayer:
    def __init__(self):
        self.logger = logging.getLogger('memory')
        self.computation_history: List[Dict[str, Any]] = []
        self.current_expression: str = ""
        self.iteration: int = 0
        self.last_response: Any = None
        self.iteration_responses: List[str] = []
    
    def reset_state(self):
        """Reset all state variables to their initial state"""
        self.last_response = None
        self.iteration = 0
        self.iteration_responses = []
        self.computation_history = []
        self.current_expression = ""
    
    def add_computation_step(self, step: Dict[str, Any]):
        """Add a computation step to the history"""
        self.computation_history.append(step)
    
    def update_current_expression(self, expression: str):
        """Update the current expression being evaluated"""
        self.current_expression = expression
    
    def increment_iteration(self):
        """Increment the iteration counter"""
        self.iteration += 1
    
    def add_iteration_response(self, response: str):
        """Add a response from the current iteration"""
        self.iteration_responses.append(f"Iteration {self.iteration} result: {response}")
    
    def get_computation_history(self) -> List[Dict[str, Any]]:
        """Get the complete computation history"""
        return self.computation_history
    
    def get_current_state(self) -> Dict[str, Any]:
        """Get the current state of the memory layer"""
        return {
            "iteration": self.iteration,
            "current_expression": self.current_expression,
            "last_response": self.last_response,
            "computation_history": self.computation_history,
            "iteration_responses": self.iteration_responses
        }
    
    def format_computation_step(self, step: Dict[str, Any], step_number: int) -> str:
        """Format a single computation step with detailed information"""
        try:
            operation = step['operation']
            result = step['result']
            args = step.get('args', {})
            
            formatted = f"""Step {step_number}:
    Operation: {operation}
    Parameters: {', '.join(f'{k}={v}' for k, v in args.items())}
    Result: {result}
    Status: {'Completed' if result else ' Failed'}"""
            
            return formatted
        except Exception as e:
            self.logger.error(f"Format error: {e}")
            return str(step) 