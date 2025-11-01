"""
Error recovery and auto-fix tools
"""

from google.adk.tools import ToolContext
from typing import Dict, Any, List
import re


def auto_fix_common_errors(
    code: str,
    errors: List[Dict],
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Automatically fixes common errors without AI
    
    Args:
        code: The code with errors
        errors: List of error dictionaries
        tool_context: ADK tool context
    
    Returns:
        dict: {
            'status': 'success' or 'no_fixes',
            'fixed_code': corrected code,
            'fixes_applied': list of fixes
        }
    """
    fixed_code = code
    fixes_applied = []
    
    for error in errors:
        error_type = error.get('type', '')
        
        # Fix className typo
        if 'react_error' in error_type and 'className' in error.get('message', ''):
            if 'class=' in fixed_code:
                fixed_code = fixed_code.replace('class=', 'className=')
                fixes_applied.append("Fixed 'class' to 'className'")
        
        # Fix mismatched brackets
        if 'syntax' in error_type and 'bracket' in error.get('message', '').lower():
            open_count = fixed_code.count('{')
            close_count = fixed_code.count('}')
            if open_count > close_count:
                # Add missing closing brackets
                fixed_code += '\n' + '}' * (open_count - close_count)
                fixes_applied.append(f"Added {open_count - close_count} closing bracket(s)")
        
        # Fix missing semicolons (for specific cases)
        if 'semicolon' in error.get('message', '').lower():
            # Add semicolons to import statements
            lines = fixed_code.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith('import') and not line.strip().endswith(';'):
                    lines[i] = line.rstrip() + ';'
            fixed_code = '\n'.join(lines)
            fixes_applied.append("Added missing semicolons")
    
    # Store fixes in state
    if fixes_applied:
        current_fixes = tool_context.state.get('fixes_applied', 0)
        tool_context.state['fixes_applied'] = current_fixes + len(fixes_applied)
    
    return {
        "status": "success" if fixes_applied else "no_fixes",
        "fixed_code": fixed_code,
        "fixes_applied": fixes_applied,
        "original_error_count": len(errors)
    }


def suggest_error_fix(
    error: Dict[str, Any],
    code: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Suggests intelligent fixes for errors
    
    Args:
        error: Error dictionary
        code: The code with error
        tool_context: ADK tool context
    
    Returns:
        dict: Fix suggestion
    """
    suggestions = []
    
    error_message = error.get('message', '').lower()
    
    # Suggest fixes based on error type
    if 'undefined' in error_message:
        suggestions.append("Ensure the variable is declared before use")
        suggestions.append("Check for typos in variable names")
    
    if 'import' in error_message:
        suggestions.append("Verify the import path is correct")
        suggestions.append("Ensure the package is installed")
    
    if 'bracket' in error_message or 'brace' in error_message:
        suggestions.append("Check for missing opening or closing brackets")
        suggestions.append("Ensure proper nesting of code blocks")
    
    return {
        "status": "success",
        "error": error,
        "suggestions": suggestions,
        "auto_fixable": len(suggestions) > 0
    }
