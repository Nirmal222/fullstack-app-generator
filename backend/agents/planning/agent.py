"""
Planning Agent - Analyzes requirements and creates technical plans
"""

from google.adk import Agent
from google.genai import types
from utils.config import Config
from utils.file_utils import read_instruction_file, read_description_file


# Create Planning Agent
planning_agent = Agent(
    model=Config.GEMINI_MODEL,
    name="planning_agent",
    instruction=read_instruction_file(__file__),
    description=read_description_file(__file__),
    generation_config=types.GenerationConfig(
        temperature=0.7,
        top_p=0.95,
        max_output_tokens=2048
    )
)
