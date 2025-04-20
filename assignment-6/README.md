# Mathematical Computation Agent

A cognitive agent that can solve complex mathematical expressions using a multi-layer architecture. The agent uses Pydantic models for type safety and validation, and implements a step-by-step approach to solve mathematical problems.

## Project Structure

```
.
├── README.md
├── requirements.txt
├── .env
├── main.py
├── cognitive_agent.py
├── models.py
├── mcp_tool.py
├── perception.py
├── memory.py
├── decision_making.py
├── action.py
└── prompts.py
```

## Components

### 1. Core Components

- **Cognitive Agent** (`cognitive_agent.py`): The main orchestrator that coordinates between different layers
- **Models** (`models.py`): Pydantic models for type safety and validation
- **MCP Tools** (`mcp_tool.py`): Mathematical computation tools and operations

### 2. Layer Architecture

- **Perception Layer** (`perception.py`): Handles LLM interactions and response parsing
- **Memory Layer** (`memory.py`): Maintains computation history and state
- **Decision Making Layer** (`decision_making.py`): Determines next operations and evaluates expressions
- **Action Layer** (`action.py`): Executes mathematical operations

### 3. Support Files

- **Prompts** (`prompts.py`): Contains system prompts and query templates
- **Main** (`main.py`): Entry point for the application
- **Environment** (`.env`): Configuration and API keys
- **Requirements** (`requirements.txt`): Project dependencies

## Features

1. **Mathematical Operations**
   - Basic operations: addition, subtraction, multiplication, division
   - Advanced operations: power, remainder, floor division
   - Support for parentheses and operator precedence

2. **Step-by-Step Evaluation**
   - Breaks down complex expressions into simpler operations
   - Maintains computation history
   - Handles operator precedence correctly

3. **Type Safety**
   - Uses Pydantic models for input validation
   - Proper handling of numeric types (int/float)
   - Error handling and validation

4. **Memory Management**
   - Tracks computation history
   - Maintains state between iterations
   - Handles expression updates

## Usage

1. **Setup**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configuration**
   - Create a `.env` file with your API keys
   - Configure the maximum iterations in `cognitive_agent.py`

3. **Running**
   ```bash
   python main.py
   ```

## Example

The agent can solve complex expressions like:
```python
((15 + 5) * 3 - (18 / 2)) + (27 % 4) - (2 ** 3) + (100 // 9)
```

It will:
1. Break down the expression into simpler operations
2. Solve each operation in the correct order
3. Maintain a history of computations
4. Return the final result

## Dependencies

- Python 3.8+
- Pydantic
- MCP (Mathematical Computation Protocol)
- Google Generative AI
- Other dependencies listed in `requirements.txt`

## Error Handling

The system includes comprehensive error handling for:
- Invalid mathematical expressions
- Type mismatches
- Operation failures
- API errors
- Timeout handling

## Future Improvements

1. Support for more mathematical operations
2. Enhanced error recovery
3. Improved expression parsing
4. Better handling of complex expressions
5. Support for symbolic mathematics

## Contributing

Feel free to submit issues and enhancement requests.
