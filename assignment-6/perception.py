import logging
from typing import List, Dict, Any
from google import genai
import os
from dotenv import load_dotenv
import asyncio
from concurrent.futures import TimeoutError
import json
from models import LLMResponse


class PerceptionLayer:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)
        self.logger = logging.getLogger('perception')
    
    async def generate_with_timeout(self, prompt: str, timeout: int = 10) -> str:
        """Generate content with a timeout"""
        try:
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: self.client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=prompt
                    )
                ),
                timeout=timeout
            )
            return response.text.strip()
        except TimeoutError:
            self.logger.error("LLM generation timed out")
            raise
        except Exception as e:
            self.logger.error(f"LLM error: {e}")
            raise

    def parse_json_response(self, response_text: str) -> List[LLMResponse]:
        """Parse the LLM response into a list of Pydantic LLMResponse objects"""
        try:
            lines = [line.strip() for line in response_text.split('\n') if line.strip()]
            parsed_responses = []
            
            for line in lines:
                try:
                    parsed = json.loads(line)
                    response = LLMResponse(**parsed)
                    parsed_responses.append(response)
                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    self.logger.error(f"Error parsing response: {e}")
                    continue
            
            return parsed_responses
        except Exception as e:
            self.logger.error(f"JSON parse error: {e}")
            return [] 