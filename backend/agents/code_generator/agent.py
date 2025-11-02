"""
Code Generator Agent - Generates React code using Claude AI
"""

from google.adk.agents import LlmAgent
from utils.config import Config
from utils.file_utils import read_instruction_file, read_description_file
from pydantic import BaseModel, Field
from typing import List, Dict


class GeneratedFile(BaseModel):
    """Represents a single generated code file"""
    path: str = Field(description="File path (e.g., 'src/App.jsx', 'src/App.css')")
    content: str = Field(description="Complete file content")
    language: str = Field(description="Programming language (jsx, css, js, etc.)")


class CodeGenerationOutput(BaseModel):
    """Output schema for code generation"""
    files: List[GeneratedFile] = Field(description="List of generated code files")
    dependencies: List[str] = Field(default=[], description="Required npm packages")
    setup_instructions: str = Field(default="", description="Setup instructions for the generated code")


# Create Code Generator Agent using Claude with output schema
code_generator_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="code_generator_agent",
    instruction=read_instruction_file(__file__),
    description=read_description_file(__file__),
    output_schema=CodeGenerationOutput,
    output_key="generated_code"
)
