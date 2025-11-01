"""
Manager Agent - Orchestrates the multi-agent workflow
"""

from google.adk import Agent
from google.genai import types
from utils.config import Config
from utils.file_utils import read_instruction_file, read_description_file
from agents.planning.agent import planning_agent
from agents.code_generator.agent import code_generator_agent
from agents.review.agent import review_agent


# Create Manager Agent with sub-agents
manager_agent = Agent(
    model=Config.GEMINI_MODEL,
    name="manager_agent",
    instruction=read_instruction_file(__file__),
    description=read_description_file(__file__),
    agents=[
        planning_agent,
        code_generator_agent,
        review_agent
    ],
    generation_config=types.GenerationConfig(
        temperature=0.5,
        top_p=0.9,
        max_output_tokens=4096
    )
)
