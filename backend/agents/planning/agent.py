"""
Planning Agent - Analyzes requirements and creates technical plans
"""

from google.adk.agents import LlmAgent
from utils.config import Config
from utils.file_utils import read_instruction_file, read_description_file
from pydantic import BaseModel, Field
from typing import List


class ComponentPlan(BaseModel):
    """Plan for a single component"""
    name: str = Field(description="Component name")
    description: str = Field(description="Component description")
    props: List[str] = Field(default=[], description="Component props")


class TechnicalPlan(BaseModel):
    """Output schema for technical planning (avoid additionalProperties for Gemini API)"""
    summary: str = Field(description="Brief summary of the application")
    components: List[ComponentPlan] = Field(description="List of components to create")
    features: List[str] = Field(description="Key features to implement")
    dependencies: List[str] = Field(description="Required npm packages")
    file_paths: List[str] = Field(default=[], description="Flat list of desired file paths (e.g. ['src/App.jsx','src/App.css','src/components/Button.jsx'])")


# Create Planning Agent with output schema
planning_agent = LlmAgent(
    model=Config.GEMINI_MODEL,
    name="planning_agent",
    instruction=read_instruction_file(__file__),
    description=read_description_file(__file__),
    output_schema=TechnicalPlan,
    output_key="technical_plan",
)
