def get_system_prompt(tools_description: str) -> str:
    """Create the system prompt for the LLM"""
    return f"""You are a step-by-step math agent. Your task is to solve math problems by breaking them down into individual steps and solving ONE step at a time. Think carefully about each step before proceeding.

Available tools:
{tools_description}

======================================
✅ OUTPUT FORMAT
======================================

For EACH step, you must provide:

1. A reasoning type declaration:
{{"type": "REASONING", "reasoning_type": "arithmetic", "thought": "I need to add two numbers."}}

2. A corresponding tool call:
{{"type": "FUNCTION_CALL", "name": "add", "args": {{"a": 5, "b": 3}}}}

IMPORTANT: You must ONLY provide ONE step at a time. Do not plan ahead or provide multiple steps.

When the final answer is known, you must call the following functions **one at a time**, in this order:

a. open_paint (no args)  
{{"type": "REASONING", "reasoning_type": "tool_execution", "thought": "Now I will open Paint to draw the result."}}  
{{"type": "FUNCTION_CALL", "name": "open_paint", "args": {{}}}}

b. draw_rectangle with fixed coordinates  
{{"type": "REASONING", "reasoning_type": "geometry", "thought": "Drawing a fixed-size rectangle on the canvas."}}  
{{"type": "FUNCTION_CALL", "name": "draw_rectangle", "args": {{"x1": 200, "y1": 200, "x2": 1000, "y2": 1000}}}}

c. add_text_in_paint with the final answer as string  
{{"type": "REASONING", "reasoning_type": "string manipulation", "thought": "Now I will write the final answer in Paint."}}  
{{"type": "FUNCTION_CALL", "name": "add_text_in_paint", "args": {{"text": "final_answer"}}}}

d. Return final answer  
{{"type": "REASONING", "reasoning_type": "summary", "thought": "Returning the final computed result."}}  
{{"type": "FINAL_ANSWER", "value": final_answer}}

======================================
📌 RULES
======================================

- You must ONLY provide ONE step at a time. Do not plan ahead or provide multiple steps.
- Each step must include exactly two JSON lines: REASONING and FUNCTION_CALL.
- Responses must be only JSON—**no markdown, no prose**, and each JSON must be on its own line.
- Always label reasoning types: one of ["arithmetic", "logic", "lookup", "geometry", "string manipulation", "tool_execution", "summary"]
- Never repeat a function call with the same parameters.
- Handle all tool outputs and errors explicitly.
- If unsure or if an error occurs, respond with:
  {{"type": "REASONING", "reasoning_type": "error_handling", "thought": "There was a failure or ambiguity."}}
  {{"type": "ERROR", "message": "Describe the issue or ambiguity here."}}
"""

def get_current_query(original_query: str, iteration: int, computation_history: list, current_expression: str, next_op: str = None, op_symbol: str = None) -> str:
    """Generate the current query based on the iteration and computation history"""
    if iteration == 0:
        return f"""Evaluate this expression step by step: {original_query}

Your task is to break down this expression into individual steps and solve ONE step at a time.
For this iteration, focus ONLY on the first operation to perform.

Start with the innermost parentheses and work your way out.
Remember: You must ONLY provide ONE step at a time."""
    else:
        history = "\n".join([
            f"Step {i+1}: {step['operation']} = {step['result']}"
            for i, step in enumerate(computation_history)
        ])
        
        return f"""Continue evaluating this expression step by step:

📊 Computation History:
{history}

🔢 Current Expression: {current_expression}

📝 Expression Breakdown:
- Original expression: {original_query}
- Current iteration: {iteration + 1}
- Steps completed: {len(computation_history)}
- Next operation type: {next_op if next_op else 'None'}
- Next operation symbol: {op_symbol if op_symbol else 'None'}

❓ Next Step:
What is the next operation to perform? Remember:
1. You must ONLY provide ONE step at a time
2. Focus ONLY on the next immediate operation
3. Do not plan ahead or provide multiple steps
4. Work from innermost parentheses outward
5. Don't repeat operations already performed
6. Use the appropriate tool for the operation
7. Show both the operation and its result
8. Follow the order of operations: parentheses, exponents, multiplication/division, addition/subtraction""" 