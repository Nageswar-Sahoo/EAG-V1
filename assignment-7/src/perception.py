from pydantic import BaseModel
from typing import Optional, List
import os
from dotenv import load_dotenv
from google import genai
import re

# Optional: import log from agent if shared, else define locally
try:
    from agent import log
except ImportError:
    import datetime
    def log(stage: str, msg: str):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] [{stage}] {msg}")

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


class PerceptionResult(BaseModel):
    user_input: str
    intent: Optional[str]
    entities: List[str] = []
    tool_hint: Optional[str] = None
    content_type: Optional[str] = None
    time_relevance: Optional[str] = None
    specificity: Optional[str] = None


def extract_perception(user_input: str) -> PerceptionResult:
    """Extracts intent, entities, and tool hints using LLM"""

    prompt = f"""
You are an AI that analyzes search queries to understand the user's intent and find the most relevant content.

Input: "{user_input}"

Return the response as a Python dictionary with keys:
- intent: (detailed description of what the user is looking for, including context and specific requirements)
- entities: a list of strings representing key concepts, topics, or specific items to find (e.g., ["Python", "web scraping", "tutorial"])
- tool_hint: (name of the MCP tool that might be useful, if any)
- content_type: (type of content being searched for, e.g., "tutorial", "documentation", "article", "code example")
- time_relevance: (how recent the content should be, e.g., "latest", "recent", "any")
- specificity: (how specific the content should be, e.g., "detailed", "overview", "quick reference")

Output only the dictionary on a single line. Do NOT wrap it in ```json or other formatting. Ensure `entities` is a list of strings, not a dictionary.

Example outputs:
1. For "how to use python requests library":
{{
    "intent": "Looking for a tutorial or guide on using the Python requests library for HTTP requests",
    "entities": ["Python", "requests library", "HTTP requests"],
    "tool_hint": "search_documents",
    "content_type": "tutorial",
    "time_relevance": "any",
    "specificity": "detailed"
}}

2. For "latest react hooks tutorial":
{{
    "intent": "Searching for recent tutorials about React Hooks, preferably with practical examples",
    "entities": ["React", "Hooks", "tutorial"],
    "tool_hint": "search_documents",
    "content_type": "tutorial",
    "time_relevance": "latest",
    "specificity": "detailed"
}}

3. For "quick overview of machine learning":
{{
    "intent": "Looking for a high-level introduction to machine learning concepts",
    "entities": ["machine learning", "overview", "introduction"],
    "tool_hint": "search_documents",
    "content_type": "article",
    "time_relevance": "any",
    "specificity": "overview"
}}
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        raw = response.text.strip()
        log("perception", f"LLM output: {raw}")

        # Strip Markdown backticks if present
        clean = re.sub(r"^```json|```$", "", raw.strip(), flags=re.MULTILINE).strip()

        try:
            parsed = eval(clean)
        except Exception as e:
            log("perception", f"⚠️ Failed to parse cleaned output: {e}")
            raise

        # Fix common issues
        if isinstance(parsed.get("entities"), dict):
            parsed["entities"] = list(parsed["entities"].values())

        return PerceptionResult(user_input=user_input, **parsed)

    except Exception as e:
        log("perception", f"⚠️ Extraction failed: {e}")
        return PerceptionResult(user_input=user_input)
