"""
File utility functions for ADK integration
"""

import os
from pathlib import Path


def read_instruction_file(agent_file_path: str) -> str:
    """
    Read instruction.txt file from the same directory as the agent file
    
    Args:
        agent_file_path: Path to the agent.py file (use __file__)
    
    Returns:
        Content of instruction.txt
    """
    agent_dir = Path(agent_file_path).parent
    instruction_file = agent_dir / "instruction.txt"
    
    if instruction_file.exists():
        return instruction_file.read_text()
    
    return "You are a helpful AI assistant."


def read_description_file(agent_file_path: str) -> str:
    """
    Read description.txt file from the same directory as the agent file
    
    Args:
        agent_file_path: Path to the agent.py file (use __file__)
    
    Returns:
        Content of description.txt
    """
    agent_dir = Path(agent_file_path).parent
    description_file = agent_dir / "description.txt"
    
    if description_file.exists():
        return description_file.read_text()
    
    return "AI Assistant"
