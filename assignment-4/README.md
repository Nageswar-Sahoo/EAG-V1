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

The result is both calculated and displayed visually in Paintbrush.

## Note

Requires proper setup of environment variables and dependencies. The GUI automation is specifically configured for macOS Paintbrush application.
