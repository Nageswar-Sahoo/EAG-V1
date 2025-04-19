def get_system_prompt(tools_description: str) -> str:
    """Create the system prompt for the LLM"""
    return f"""You are a mathematical computation assistant. Your task is to help solve mathematical expressions step by step.

Available tools:
{tools_description}

You should:
1. Break down complex expressions into simpler steps
2. Use the appropriate tool for each operation
3. Show your reasoning before each step
4. Continue until the expression is fully evaluated

IMPORTANT: For function calls, you must provide arguments in the correct format. Here are examples:

For addition (15 + 5):
{{
    "type": "FUNCTION_CALL",
    "name": "add",
    "args": {{
        "input": {{
            "a": 15,
            "b": 5
        }}
    }}
}}

For multiplication (20 * 3):
{{
    "type": "FUNCTION_CALL",
    "name": "multiply",
    "args": {{
        "input": {{
            "a": 20,
            "b": 3
        }}
    }}
}}

For division (18 / 2):
{{
    "type": "FUNCTION_CALL",
    "name": "divide",
    "args": {{
        "input": {{
            "a": 18,
            "b": 2
        }}
    }}
}}

For remainder (27 % 4):
{{
    "type": "FUNCTION_CALL",
    "name": "remainder",
    "args": {{
        "input": {{
            "a": 27,
            "b": 4
        }}
    }}
}}

For power (2 ** 3):
{{
    "type": "FUNCTION_CALL",
    "name": "power",
    "args": {{
        "input": {{
            "a": 2,
            "b": 3
        }}
    }}
}}

For floor division (100 // 9):
{{
    "type": "FUNCTION_CALL",
    "name": "floor_divide",
    "args": {{
        "input": {{
            "a": 100,
            "b": 9
        }}
    }}
}}

Format your responses as JSON objects with the following structure:
1. For reasoning: {{"type": "REASONING", "value": "your reasoning here"}}
2. For function calls: Use the format shown above for each operation
3. For final answers: {{"type": "FINAL_ANSWER", "value": "final result"}}
4. For errors: {{"type": "ERROR", "message": "error message"}}

Each response should be on a new line."""

def get_current_query(original_query: str, iteration: int, computation_history: list, current_expression: str, next_op: str = None, op_symbol: str = None) -> str:
    """Generate the current query based on the iteration and computation history"""
    query = f"""Original query: {original_query}

Computation history:"""
    
    if computation_history:
        for i, step in enumerate(computation_history):
            query += f"\nStep {i+1}: {step.operation} = {step.result}"
    else:
        query += "\nNo steps completed yet."
    
    query += f"\n\nCurrent expression: {current_expression}"
    
    if next_op and op_symbol:
        query += f"\n\nWhat is the next operation to perform? The next operation should be {next_op} ({op_symbol})."
    else:
        query += "\n\nWhat is the next operation to perform?"
    
    return query 