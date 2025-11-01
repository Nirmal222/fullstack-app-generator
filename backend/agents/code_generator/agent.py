"""
Code Generator Agent - Generates React code using Claude AI
"""

from google.adk import Agent
from google.genai import types
from utils.config import Config
from utils.file_utils import read_instruction_file, read_description_file


# Create Code Generator Agent using Claude
code_generator_agent = Agent(
    model=Config.CLAUDE_MODEL,
    name="code_generator_agent",
    instruction=read_instruction_file(__file__),
    description=read_description_file(__file__),
    generation_config=types.GenerationConfig(
        temperature=0.8,
        top_p=0.95,
        max_output_tokens=4096
    )
)
