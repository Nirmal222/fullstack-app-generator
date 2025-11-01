"""
Validation tools for code syntax and quality checking
"""

from google.adk.tools import ToolContext
from typing import Dict, Any, List
import re


def validate_jsx_syntax(code: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Validates JSX/JavaScript syntax
    
    Args:
        code: The JSX/JavaScript code to validate
        tool_context: ADK tool context
    
    Returns:
        dict: {
            'status': 'success' or 'error',
            'errors': list of error dictionaries,
            'warnings': list of warning messages
        }
    """
    errors = []
    warnings = []
    
    # Basic syntax checks
    # Check for unclosed brackets
    open_brackets = code.count('{')
    close_brackets = code.count('}')
    if open_brackets != close_brackets:
        errors.append({
            "type": "syntax",
            "message": f"Mismatched brackets: {open_brackets} open, {close_brackets} close",
            "severity": "error"
        })
    
    # Check for unclosed JSX tags
    jsx_tags = re.findall(r'<(\w+)[^>]*>', code)
    closing_tags = re.findall(r'</(\w+)>', code)
    self_closing = re.findall(r'<\w+[^>]*/>', code)
    
    # Check for common React errors
    if 'class=' in code:
        errors.append({
            "type": "react_error",
            "message": "Use 'className' instead of 'class' in JSX",
            "severity": "error",
            "fix": "Replace 'class=' with 'className='"
        })
    
    # Check for missing key prop in lists
    if '.map(' in code and 'key=' not in code:
        warnings.append("Consider adding 'key' prop when rendering lists")
    
    # Store validation result in state
    tool_context.state['last_validation'] = {
        "file_type": "jsx",
        "errors": len(errors),
        "warnings": len(warnings)
    }
    
    return {
        "status": "error" if errors else "success",
        "errors": errors,
        "warnings": warnings,
        "total_issues": len(errors) + len(warnings)
    }


def validate_css_syntax(code: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Validates CSS syntax
    
    Args:
        code: The CSS code to validate
        tool_context: ADK tool context
    
    Returns:
        dict: Validation results
    """
    errors = []
    warnings = []
    
    # Check for unclosed braces
    open_braces = code.count('{')
    close_braces = code.count('}')
    if open_braces != close_braces:
        errors.append({
            "type": "syntax",
            "message": f"Mismatched braces: {open_braces} open, {close_braces} close",
            "severity": "error"
        })
    
    # Check for missing semicolons (optional but good practice)
    lines = code.split('\n')
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if line and ':' in line and not line.endswith((';', '{', '}')):
            if not line.startswith(('/*', '//', '*')):  # Ignore comments
                warnings.append(f"Line {i}: Consider adding semicolon")
    
    return {
        "status": "error" if errors else "success",
        "errors": errors,
        "warnings": warnings[:5],  # Limit warnings
        "total_issues": len(errors) + len(warnings)
    }


def check_react_best_practices(code: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Checks React code for best practices
    
    Args:
        code: The React code to check
        tool_context: ADK tool context
    
    Returns:
        dict: Best practice suggestions
    """
    suggestions = []
    
    # Check for useState
    if 'useState' in code and 'import' in code and 'useState' not in code[:code.find('export')]:
        suggestions.append("Ensure useState is imported from React")
    
    # Check for useEffect
    if 'useEffect' in code:
        # Check for dependency array
        effect_pattern = r'useEffect\([^)]+\)'
        effects = re.findall(effect_pattern, code)
        for effect in effects:
            if ']' not in effect:
                suggestions.append("useEffect should have dependency array")
    
    # Check for prop-types
    if 'props' in code and 'PropTypes' not in code:
        suggestions.append("Consider adding PropTypes for better type safety")
    
    return {
        "status": "success",
        "suggestions": suggestions,
        "best_practices_checked": 3
    }
