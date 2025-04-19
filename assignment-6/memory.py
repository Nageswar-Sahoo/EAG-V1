import logging
from typing import List, Dict, Any
from datetime import datetime
from models import ComputationStep, MemoryState


class MemoryLayer:
    def __init__(self):
        self.logger = logging.getLogger('memory')
        self.state = MemoryState(
            iteration=0,
            current_expression="",
            last_response=None,
            computation_history=[],
            iteration_responses=[]
        )
    
    def reset_state(self):
        """Reset all state variables to their initial state"""
        self.state = MemoryState(
            iteration=0,
            current_expression="",
            last_response=None,
            computation_history=[],
            iteration_responses=[]
        )
    
    def add_computation_step(self, step: Dict[str, Any]):
        """Add a computation step to the history"""
        computation_step = ComputationStep(
            operation=step['operation'],
            result=step['result'],
            args=step.get('args', {}),
            iteration=self.state.iteration
        )
        self.state.computation_history.append(computation_step)
    
    def update_current_expression(self, expression: str):
        """Update the current expression being evaluated"""
        self.state.current_expression = expression
    
    def increment_iteration(self):
        """Increment the iteration counter"""
        self.state.iteration += 1
    
    def add_iteration_response(self, response: str):
        """Add a response from the current iteration"""
        self.state.iteration_responses.append(f"Iteration {self.state.iteration} result: {response}")
    
    def get_computation_history(self) -> List[ComputationStep]:
        """Get the complete computation history"""
        return self.state.computation_history
    
    def get_current_state(self) -> MemoryState:
        """Get the current state of the memory layer"""
        return self.state
    
    def format_computation_step(self, step: ComputationStep, step_number: int) -> str:
        """Format a single computation step with detailed information"""
        try:
            formatted = f"""Step {step_number}:
    Operation: {step.operation}
    Parameters: {', '.join(f'{k}={v}' for k, v in step.args.items())}
    Result: {step.result}
    Status: {'Completed' if step.result else ' Failed'}"""
            
            return formatted
        except Exception as e:
            self.logger.error(f"Format error: {e}")
            return str(step) 