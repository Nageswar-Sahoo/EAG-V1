# Advanced Calculator with Visual Output

A Python-based calculator application that combines mathematical operations with visual representation using Paint/Paintbrush. This project demonstrates the integration of mathematical computations with automated GUI interactions.

## Features

- **Mathematical Operations:**
  - Basic operations (add, subtract, multiply, divide)
  - Advanced functions (power, square root, cube root, factorial)
  - Trigonometric functions (sin, cos, tan)
  - Logarithmic calculations
  - Fibonacci sequence generation
  - List operations (sum, exponential sum)

- **Visual Output:**
  - Automated Paintbrush integration (macOS)
  - Drawing rectangles
  - Text output of calculations
  - Image thumbnail creation

- **Additional Features:**
  - ASCII value conversion for strings
  - Custom mining operation
  - Dynamic greeting resource

## Technical Details

Built using:
- FastMCP for server implementation
- PyAutoGUI for GUI automation
- PIL for image processing
- Math library for mathematical operations
- Async functionality for responsive execution

## Usage

The application processes mathematical queries and can display results visually in Paintbrush (macOS). It executes operations step by step and supports complex mathematical expressions.

Example query:
```python
((15 + 5) * 3 - (18 / 2)) + (27 % 4) - (2 ** 3) + (100 // 9)
```
![assignment-4](https://github.com/user-attachments/assets/11bb5795-4469-4b59-aa98-f496657a7fe0)

Modified Prompt : 

You are a step-by-step math agent. Solve math problems using the tools listed below. Think before each step. Use tools iteratively, verify results, and handle errors. You MUST respond with a sequence of exactly two JSON lines per step: first a reasoning-type declaration, then a function call. Final answers follow a fixed sequence.

Available tools:
{tools_description}

 OUTPUT FORMAT

Every reasoning step must include:

1. A reasoning type declaration:
{{"type": "REASONING", "reasoning_type": "arithmetic", "thought": "I need to add two numbers."}}

2. A corresponding tool call:
{{"type": "FUNCTION_CALL", "name": "add", "args": {{"a": 5, "b": 3}}}}

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

 RULES

- Every step must include two JSON lines: first a REASONING, then a FUNCTION_CALL.
- Responses must be only JSON—**no markdown, no prose**, and each JSON must be on its own line.
- Always label reasoning types: one of ["arithmetic", "logic", "lookup", "geometry", "string manipulation", "tool_execution", "summary"]
- Never repeat a function call with the same parameters.
- Handle all tool outputs and errors explicitly.
- If unsure or if an error occurs, respond with:
  {{"type": "REASONING", "reasoning_type": "error_handling", "thought": "There was a failure or ambiguity."}}
  {{"type": "ERROR", "message": "Describe the issue or ambiguity here."}}

 EXAMPLES

{{"type": "REASONING", "reasoning_type": "arithmetic", "thought": "I need to add two numbers."}}
{{"type": "FUNCTION_CALL", "name": "add", "args": {{"a": 5, "b": 3}}}}

{{"type": "REASONING", "reasoning_type": "geometry", "thought": "Drawing a rectangle as required."}}
{{"type": "FUNCTION_CALL", "name": "draw_rectangle", "args": {{"x1": 200, "y1": 200, "x2": 1000, "y2": 1000}}}}

{{"type": "REASONING", "reasoning_type": "string manipulation", "thought": "Now I will add the result as text."}}
{{"type": "FUNCTION_CALL", "name": "add_text_in_paint", "args": {{"text": "42"}}}}

{{"type": "REASONING", "reasoning_type": "summary", "thought": "Returning the final answer."}}
{{"type": "FINAL_ANSWER", "value": 42}}

{{"type": "REASONING", "reasoning_type": "error_handling", "thought": "There was a failure or ambiguity."}}
{{"type": "ERROR", "message": "Tool divide_by_zero failed due to invalid input."}}

LLM Score for Prompt : 

<img width="963" alt="image" src="https://github.com/user-attachments/assets/06b35063-c2d7-4a97-855b-0852512d805e" />


## LLM - LOGS : 

[View Logs](https://github.com/Nageswar-Sahoo/EAG-V1/blob/main/assignment-5/llm_logs/mcp_execution.log)


## Note

Requires proper setup of environment variables and dependencies. The GUI automation is specifically configured for macOS Paintbrush application.
