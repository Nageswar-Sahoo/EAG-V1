# basic import 
from mcp.server.fastmcp import FastMCP, Image
from mcp.server.fastmcp.prompts import base
from mcp.types import TextContent
from mcp import types
from PIL import Image as PILImage
import math
import sys
import pyautogui
import os
import time
import subprocess
from models import (
    AddInput, AddListInput, SubtractInput, MultiplyInput, DivideInput,
    PowerInput, SqrtInput, CbrtInput, FactorialInput, LogInput,
    RemainderInput, FloorDivideInput, SinInput, CosInput, TanInput,
    MineInput, CreateThumbnailInput, StringsToCharsToIntInput,
    IntListToExponentialSumInput, FibonacciNumbersInput,
    DrawRectangleInput, AddTextInPaintInput
)
from typing import Union

pyautogui.FAILSAFE = False

# instantiate an MCP server client
mcp = FastMCP("Calculator")

# DEFINE TOOLS

#addition tool
@mcp.tool()
def add(input: AddInput) -> Union[int, float]:
    """Add two numbers"""
    print("CALLED: add(a: int, b: int) -> int:")
    return input.a + input.b

@mcp.tool()
def add_list(input: AddListInput) -> Union[int, float]:
    """Add all numbers in a list"""
    print("CALLED: add(l: list) -> int:")
    return sum(input.l)

# subtraction tool
@mcp.tool()
def subtract(input: SubtractInput) -> Union[int, float]:
    """Subtract two numbers"""
    print("CALLED: subtract(a: int, b: int) -> int:")
    return input.a - input.b

# multiplication tool
@mcp.tool()
def multiply(input: MultiplyInput) -> Union[int, float]:
    """Multiply two numbers"""
    print("CALLED: multiply(a: int, b: int) -> int:")
    return input.a * input.b

#  division tool
@mcp.tool() 
def divide(input: DivideInput) -> float:
    """Divide two numbers"""
    print("CALLED: divide(a: int, b: int) -> float:")
    return float(input.a / input.b)

# power tool
@mcp.tool()
def power(input: PowerInput) -> Union[int, float]:
    """Power of two numbers"""
    print("CALLED: power(a: int, b: int) -> int:")
    return input.a ** input.b

# square root tool
@mcp.tool()
def sqrt(input: SqrtInput) -> float:
    """Square root of a number"""
    print("CALLED: sqrt(a: int) -> float:")
    return float(input.a ** 0.5)

# cube root tool
@mcp.tool()
def cbrt(input: CbrtInput) -> float:
    """Cube root of a number"""
    print("CALLED: cbrt(a: int) -> float:")
    return float(input.a ** (1/3))

# factorial tool
@mcp.tool()
def factorial(input: FactorialInput) -> int:
    """factorial of a number"""
    print("CALLED: factorial(a: int) -> int:")
    return int(math.factorial(input.a))

# log tool
@mcp.tool()
def log(input: LogInput) -> float:
    """log of a number"""
    print("CALLED: log(a: int) -> float:")
    return float(math.log(input.a))

# remainder tool
@mcp.tool()
def remainder(input: RemainderInput) -> Union[int, float]:
    """remainder of two numbers divison"""
    print("CALLED: remainder(a: int, b: int) -> int:")
    return input.a % input.b

@mcp.tool()
def floor_divide(input: FloorDivideInput) -> int:
    """Performs floor division of two integers and returns the quotient."""
    print(f"CALLED: floor_divide({input.a}, {input.b})")
    return int(input.a // input.b)

# sin tool
@mcp.tool()
def sin(input: SinInput) -> float:
    """sin of a number"""
    print("CALLED: sin(a: int) -> float:")
    return float(math.sin(input.a))

# cos tool
@mcp.tool()
def cos(input: CosInput) -> float:
    """cos of a number"""
    print("CALLED: cos(a: int) -> float:")
    return float(math.cos(input.a))

# tan tool
@mcp.tool()
def tan(input: TanInput) -> float:
    """tan of a number"""
    print("CALLED: tan(a: int) -> float:")
    return float(math.tan(input.a))

# mine tool
@mcp.tool()
def mine(input: MineInput) -> Union[int, float]:
    """special mining tool"""
    print("CALLED: mine(a: int, b: int) -> int:")
    return input.a - input.b - input.b

@mcp.tool()
def create_thumbnail(input: CreateThumbnailInput) -> Image:
    """Create a thumbnail from an image"""
    print("CALLED: create_thumbnail(image_path: str) -> Image:")
    try:
        img = PILImage.open(input.image_path)
        img.thumbnail((100, 100))
        return Image(data=img.tobytes(), format="png")
    except Exception as e:
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error creating thumbnail: {str(e)}"
                )
            ]
        }

@mcp.tool()
def strings_to_chars_to_int(input: StringsToCharsToIntInput) -> list[int]:
    """Return the ASCII values of the characters in a word"""
    print("CALLED: strings_to_chars_to_int(string: str) -> list[int]:")
    return [int(ord(char)) for char in input.string]

@mcp.tool()
def int_list_to_exponential_sum(input: IntListToExponentialSumInput) -> float:
    """Return sum of exponentials of numbers in a list"""
    print("CALLED: int_list_to_exponential_sum(int_list: list) -> float:")
    return sum(math.exp(i) for i in input.int_list)

@mcp.tool()
def fibonacci_numbers(input: FibonacciNumbersInput) -> list:
    """Return the first n Fibonacci Numbers"""
    print("CALLED: fibonacci_numbers(n: int) -> list:")
    if input.n <= 0:
        return []
    fib_sequence = [0, 1]
    for _ in range(2, input.n):
        fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])
    return fib_sequence[:input.n]

@mcp.tool()
async def draw_rectangle(input: DrawRectangleInput) -> dict:
    """Draw a rectangle in Paint from (x1,y1) to (x2,y2)"""
    try:
        print(f"Moving to start position ({input.x1}, {input.y1})")
        pyautogui.moveTo(input.x1, input.y1, duration=0.7)

        print("Click and drag to draw rectangle...")
        pyautogui.mouseDown()
        pyautogui.dragTo(input.x2, input.y2, duration=0.9, button='left')
        pyautogui.mouseUp()

        return {
            "content": [
                TextContent(
                    type="text", 
                    text=f"Rectangle drawn from ({input.x1},{input.y1}) to ({input.x2},{input.y2})"
                )
            ]
        }
    except Exception as e:
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error drawing rectangle: {str(e)}"
                )
            ]
        }

@mcp.tool()
async def add_text_in_paint(input: AddTextInPaintInput) -> dict:
    """Add text in Paint"""
    try:
        time.sleep(10)

        # Click text tool (adjust coordinates for your Paint app on macOS)
        pyautogui.click(x=528, y=92)
        time.sleep(0.5)
  
        # Click where to add text
        pyautogui.click(x=810, y=533)
        time.sleep(0.5)
        
        # Type the text
        pyautogui.write("Mathematical Query : ((15 + 5) * 3 - (18 / 2)) + (27 % 4) - (2 ** 3) + (100 // 9) \n\n Final Answer is : ")
        pyautogui.write(input.text)
        time.sleep(0.5)
        
        # Click to exit text mode
        pyautogui.click(x=1050, y=800)
        
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Text:'{input.text}' added successfully"
                )
            ]
        }
    except Exception as e:
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error opening Paint: {str(e)}"
                )
            ]
        }

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    print("CALLED: get_greeting(name: str) -> str:")
    return f"Hello, {name}!"

# DEFINE AVAILABLE PROMPTS
@mcp.prompt()
def review_code(code: str) -> str:
    return f"Please review this code:\n\n{code}"

@mcp.prompt()
def debug_error(error: str) -> list[base.Message]:
    return [
        base.Message(
            role="system",
            content=f"Debug this error:\n\n{error}"
        )
    ]

if __name__ == "__main__":
    # Check if running with mcp dev command
    print("STARTING")
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        mcp.run()  # Run without transport for dev server
    else:
        mcp.run(transport="stdio")  # Run with stdio for direct execution
