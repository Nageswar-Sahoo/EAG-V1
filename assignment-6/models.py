from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field, validator
from mcp.types import TextContent

# Base Input Model
class BaseInputModel(BaseModel):
    class Config:
        arbitrary_types_allowed = True

# Tool Input/Output Models
class AddInput(BaseInputModel):
    a: Union[int, float] = Field(..., description="First number to add")
    b: Union[int, float] = Field(..., description="Second number to add")

class AddListInput(BaseInputModel):
    l: List[Union[int, float]] = Field(..., description="List of numbers to add")

class SubtractInput(BaseInputModel):
    a: Union[int, float] = Field(..., description="Number to subtract from")
    b: Union[int, float] = Field(..., description="Number to subtract")

class MultiplyInput(BaseInputModel):
    a: Union[int, float] = Field(..., description="First number to multiply")
    b: Union[int, float] = Field(..., description="Second number to multiply")

class DivideInput(BaseInputModel):
    a: Union[int, float] = Field(..., description="Numerator")
    b: Union[int, float] = Field(..., description="Denominator")

    @validator('b')
    def check_denominator(cls, v):
        if v == 0:
            raise ValueError("Denominator cannot be zero")
        return v

class PowerInput(BaseInputModel):
    a: Union[int, float] = Field(..., description="Base number")
    b: Union[int, float] = Field(..., description="Exponent")

class SqrtInput(BaseInputModel):
    a: Union[int, float] = Field(..., description="Number to calculate square root of")

    @validator('a')
    def check_negative(cls, v):
        if v < 0:
            raise ValueError("Cannot calculate square root of negative number")
        return v

class CbrtInput(BaseInputModel):
    a: Union[int, float] = Field(..., description="Number to calculate cube root of")

class FactorialInput(BaseInputModel):
    a: int = Field(..., description="Number to calculate factorial of")

    @validator('a')
    def check_negative(cls, v):
        if v < 0:
            raise ValueError("Cannot calculate factorial of negative number")
        return v

class LogInput(BaseInputModel):
    a: Union[int, float] = Field(..., description="Number to calculate logarithm of")

    @validator('a')
    def check_positive(cls, v):
        if v <= 0:
            raise ValueError("Cannot calculate logarithm of non-positive number")
        return v

class RemainderInput(BaseInputModel):
    a: Union[int, float] = Field(..., description="Dividend")
    b: Union[int, float] = Field(..., description="Divisor")

    @validator('b')
    def check_denominator(cls, v):
        if v == 0:
            raise ValueError("Divisor cannot be zero")
        return v

class FloorDivideInput(BaseInputModel):
    a: Union[int, float] = Field(..., description="Dividend")
    b: Union[int, float] = Field(..., description="Divisor")

    @validator('b')
    def check_denominator(cls, v):
        if v == 0:
            raise ValueError("Divisor cannot be zero")
        return v

class SinInput(BaseInputModel):
    a: Union[int, float] = Field(..., description="Angle in radians")

class CosInput(BaseInputModel):
    a: Union[int, float] = Field(..., description="Angle in radians")

class TanInput(BaseInputModel):
    a: Union[int, float] = Field(..., description="Angle in radians")

class MineInput(BaseInputModel):
    a: Union[int, float] = Field(..., description="First number")
    b: Union[int, float] = Field(..., description="Second number")

class CreateThumbnailInput(BaseInputModel):
    image_path: str = Field(..., description="Path to the image file")

class StringsToCharsToIntInput(BaseInputModel):
    string: str = Field(..., description="String to convert to ASCII values")

class IntListToExponentialSumInput(BaseInputModel):
    int_list: List[Union[int, float]] = Field(..., description="List of integers to calculate exponential sum")

class FibonacciNumbersInput(BaseInputModel):
    n: int = Field(..., description="Number of Fibonacci numbers to generate")

    @validator('n')
    def check_positive(cls, v):
        if v < 0:
            raise ValueError("Cannot generate negative number of Fibonacci numbers")
        return v

class DrawRectangleInput(BaseInputModel):
    x1: int = Field(..., description="Starting x-coordinate")
    y1: int = Field(..., description="Starting y-coordinate")
    x2: int = Field(..., description="Ending x-coordinate")
    y2: int = Field(..., description="Ending y-coordinate")

class AddTextInPaintInput(BaseInputModel):
    text: str = Field(..., description="Text to add in Paint")

# LLM Response Models
class LLMResponse(BaseInputModel):
    type: str = Field(..., description="Type of response (FUNCTION_CALL, FINAL_ANSWER, ERROR)")
    name: Optional[str] = Field(None, description="Function name if type is FUNCTION_CALL")
    args: Optional[Dict[str, Any]] = Field(None, description="Function arguments if type is FUNCTION_CALL")
    value: Optional[Any] = Field(None, description="Value if type is FINAL_ANSWER")
    message: Optional[str] = Field(None, description="Error message if type is ERROR")

# Memory Layer Models
class ComputationStep(BaseInputModel):
    operation: str = Field(..., description="Operation performed")
    result: Any = Field(..., description="Result of the operation")
    args: Dict[str, Any] = Field(default_factory=dict, description="Arguments used in the operation")
    iteration: int = Field(..., description="Iteration number")

class MemoryState(BaseInputModel):
    iteration: int = Field(..., description="Current iteration number")
    current_expression: str = Field(..., description="Current mathematical expression")
    last_response: Optional[Any] = Field(None, description="Last response received")
    computation_history: List[ComputationStep] = Field(default_factory=list, description="History of computation steps")
    iteration_responses: List[str] = Field(default_factory=list, description="Responses from each iteration") 