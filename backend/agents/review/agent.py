"""
Review Agent - Validates and reviews code quality
"""

from google.adk import Agent
from google.genai import types
from utils.config import Config
from utils.file_utils import read_instruction_file, read_description_file
from tools.validation_tools import (
    validate_jsx_syntax,
    validate_css_syntax,
    check_react_best_practices
)
from tools.dependency_tools import (
    extract_npm_dependencies,
    check_package_compatibility
)
from tools.error_recovery_tools import (
    auto_fix_common_errors,
    suggest_error_fix
)


# Create Review Agent with validation tools
review_agent = Agent(
    model=Config.GEMINI_MODEL,
    name="review_agent",
    instruction=read_instruction_file(__file__),
    description=read_description_file(__file__),
    tools=[
        validate_jsx_syntax,
        validate_css_syntax,
        check_react_best_practices,
        extract_npm_dependencies,
        check_package_compatibility,
        auto_fix_common_errors,
        suggest_error_fix
    ],
    generation_config=types.GenerationConfig(
        temperature=0.3,
        top_p=0.9,
        max_output_tokens=2048
    )
)
