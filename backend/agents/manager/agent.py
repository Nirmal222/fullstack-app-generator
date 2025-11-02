"""
Manager Agent - Orchestrates the multi-agent workflow
"""

from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from utils.config import Config
from utils.file_utils import read_instruction_file, read_description_file

# Import sub-agents first
from agents.planning.agent import planning_agent
from agents.code_generator.agent import code_generator_agent
from agents.review.agent import review_agent

# Create Manager Agent with sub-agents as tools
# Note: skip_summarization=True prevents the manager from trying to summarize structured output
manager_agent = LlmAgent(
    model=Config.GEMINI_MODEL,
    name="manager_agent",
    instruction=read_instruction_file(__file__),
    description=read_description_file(__file__),
    tools=[
        AgentTool(agent=planning_agent),
        AgentTool(agent=code_generator_agent),
        AgentTool(agent=review_agent)
    ]
)

# Export for use in orchestration
__all__ = ['manager_agent', 'planning_agent', 'code_generator_agent', 'review_agent']
