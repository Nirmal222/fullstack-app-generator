"""
Dependency management tools for NPM packages
"""

from google.adk.tools import ToolContext
from typing import Dict, Any, List
import re


def extract_npm_dependencies(code: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Extracts required npm packages from import statements
    
    Args:
        code: The JavaScript/JSX code
        tool_context: ADK tool context
    
    Returns:
        dict: {
            'status': 'success',
            'dependencies': dict of package names and versions,
            'imports': list of imported items
        }
    """
    dependencies = {}
    imports = []
    
    # Find all import statements
    import_pattern = r"import\s+(?:{[^}]+}|[\w]+|\*\s+as\s+\w+)\s+from\s+['\"]([^'\"]+)['\"]"
    matches = re.findall(import_pattern, code)
    
    for package in matches:
        # Skip relative imports
        if package.startswith('.'):
            continue
        
        # Extract package name (handle scoped packages)
        if package.startswith('@'):
            # Scoped package like @testing-library/react
            package_name = '/'.join(package.split('/')[:2])
        else:
            # Regular package
            package_name = package.split('/')[0]
        
        imports.append(package_name)
        
        # Assign common package versions
        version = get_default_version(package_name)
        dependencies[package_name] = version
    
    # Store in state
    tool_context.state['dependencies'] = dependencies
    
    return {
        "status": "success",
        "dependencies": dependencies,
        "imports": list(set(imports)),
        "total_packages": len(dependencies)
    }


def get_default_version(package_name: str) -> str:
    """
    Get default version for common packages
    
    Args:
        package_name: NPM package name
    
    Returns:
        Version string
    """
    common_versions = {
        "react": "^18.2.0",
        "react-dom": "^18.2.0",
        "react-router-dom": "^6.20.0",
        "axios": "^1.6.0",
        "@testing-library/react": "^14.0.0",
        "@testing-library/jest-dom": "^6.1.0",
        "styled-components": "^6.1.0",
        "tailwindcss": "^3.3.0",
        "typescript": "^5.3.0",
        "@types/react": "^18.2.0",
        "@types/react-dom": "^18.2.0"
    }
    
    return common_versions.get(package_name, "latest")


def generate_package_json(
    dependencies: Dict[str, str],
    project_name: str = "generated-app",
    tool_context: ToolContext = None
) -> Dict[str, Any]:
    """
    Generates a complete package.json file
    
    Args:
        dependencies: Dictionary of dependencies
        project_name: Project name
        tool_context: ADK tool context
    
    Returns:
        dict: package.json content
    """
    package_json = {
        "name": project_name,
        "version": "0.1.0",
        "private": True,
        "dependencies": dependencies,
        "scripts": {
            "start": "react-scripts start",
            "build": "react-scripts build",
            "test": "react-scripts test",
            "eject": "react-scripts eject"
        },
        "eslintConfig": {
            "extends": ["react-app"]
        },
        "browserslist": {
            "production": [">0.2%", "not dead", "not op_mini all"],
            "development": [
                "last 1 chrome version",
                "last 1 firefox version",
                "last 1 safari version"
            ]
        }
    }
    
    return {
        "status": "success",
        "package_json": package_json,
        "install_command": generate_install_command(dependencies)
    }


def generate_install_command(dependencies: Dict[str, str]) -> str:
    """
    Generates npm install command
    
    Args:
        dependencies: Dictionary of dependencies with versions
    
    Returns:
        Installation command string
    """
    if not dependencies:
        return "# No dependencies to install"
    
    packages = [f"{name}@{version}" for name, version in dependencies.items()]
    return f"npm install {' '.join(packages)}"


def check_package_compatibility(
    packages: List[str],
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Checks if packages are compatible with each other
    
    Args:
        packages: List of package names
        tool_context: ADK tool context
    
    Returns:
        dict: Compatibility information
    """
    warnings = []
    
    # Check for common incompatibilities
    if "react" in packages:
        if "react-dom" not in packages:
            warnings.append("react-dom is required when using react")
    
    # Add more compatibility checks as needed
    
    return {
        "status": "success",
        "warnings": warnings,
        "compatible": len(warnings) == 0
    }
