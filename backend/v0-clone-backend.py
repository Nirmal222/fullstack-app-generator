"""
V0-Clone Backend - AI Code Generation with Streaming
Supports streaming React component generation to frontend
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import json
from typing import AsyncGenerator, Optional
import os
import re
from anthropic import AsyncAnthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="V0 Clone Backend")

# CORS middleware for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeGenerationRequest(BaseModel):
    prompt: str
    framework: str = "react"  # react, vue, html
    model: str = "gpt-4"  # or claude-3-5-sonnet, gemini-pro

class FileChunk(BaseModel):
    type: str  # "file_start", "content", "file_end", "complete"
    file_path: Optional[str] = None
    content: Optional[str] = None
    metadata: Optional[dict] = None

def parse_claude_response(content: str) -> dict:
    """
    Parse Claude's response to extract file paths and content
    Expected format:
    ```filepath
    content
    ```
    """
    files = {}
    
    # Match code blocks with file paths
    pattern = r'```(\w+)?\s*(?:\/\/\s*)?([^\n]*)\n(.*?)```'
    matches = re.finditer(pattern, content, re.DOTALL)
    
    for match in matches:
        language = match.group(1) or ''
        potential_path = match.group(2).strip()
        code_content = match.group(3).strip()
        
        # Determine file path
        if potential_path and ('/' in potential_path or '.' in potential_path):
            file_path = potential_path
        else:
            # Infer from language
            if language in ['javascript', 'jsx', 'js']:
                file_path = f"src/{potential_path or 'App'}.jsx"
            elif language == 'css':
                file_path = f"src/{potential_path or 'App'}.css"
            elif language == 'html':
                file_path = "public/index.html"
            else:
                file_path = f"src/Component.{language or 'jsx'}"
        
        files[file_path] = code_content
    
    # If no code blocks found, try to parse differently
    if not files:
        # Look for explicit file markers
        file_pattern = r'(?:^|\n)(?:File|file):\s*([^\n]+)\n(.*?)(?=(?:\n(?:File|file):|$))'
        file_matches = re.finditer(file_pattern, content, re.DOTALL | re.MULTILINE)
        
        for match in file_matches:
            file_path = match.group(1).strip()
            file_content = match.group(2).strip()
            # Remove code block markers if present
            file_content = re.sub(r'^```\w*\n|```$', '', file_content, flags=re.MULTILINE)
            files[file_path] = file_content
    
    return files

async def generate_code_stream(prompt: str, framework: str) -> AsyncGenerator[str, None]:
    """
    Generate code using Claude API with streaming
    """
    try:
        # Validate API key
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            yield json.dumps({
                "type": "error",
                "message": "API key not configured. Please set ANTHROPIC_API_KEY in .env file"
            }) + "\n"
            return
        
        # Validate prompt
        if not prompt or not prompt.strip():
            yield json.dumps({
                "type": "error",
                "message": "Prompt cannot be empty"
            }) + "\n"
            return
        
        client = AsyncAnthropic(api_key=api_key)
        
        # Construct system prompt
        system_prompt = f"""You are an expert {framework} developer. Generate complete, production-ready code based on the user's request.

IMPORTANT: Format your response with code blocks that include file paths like this:

```jsx src/App.jsx
// code here
```

```css src/App.css
/* styles here */
```

For React components:
- Use functional components with hooks
- Include proper imports
- Follow modern React best practices
- Create separate CSS files for styling
- Use descriptive component and variable names

Generate ALL necessary files (components, styles, etc.) to make the application work.
Make the code clean, well-commented, and production-ready."""

        # Construct user prompt
        user_prompt = f"Create a {framework} application: {prompt}\n\nGenerate all necessary files with proper file paths."
        
        # Stream from Claude
        full_response = ""
        async with client.messages.stream(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            system=system_prompt
        ) as stream:
            async for text in stream.text_stream:
                full_response += text
                # You could yield partial updates here if needed
                await asyncio.sleep(0)
        
        # Validate response
        if not full_response or not full_response.strip():
            yield json.dumps({
                "type": "error",
                "message": "Claude returned an empty response. Please try again."
            }) + "\n"
            return
        
        # Parse the complete response
        files = parse_claude_response(full_response)
        
        if not files:
            # Fallback: create a basic component from the response
            yield json.dumps({
                "type": "error",
                "message": "Could not parse files from Claude's response. The response might not contain properly formatted code blocks."
            }) + "\n"
            return
        
        # Stream files to frontend
        for file_path, content in files.items():
            # Send file start marker
            yield json.dumps({
                "type": "file_start",
                "file_path": file_path,
                "metadata": {"size": len(content)}
            }) + "\n"
            
            await asyncio.sleep(0.05)
            
            # Stream content in chunks
            chunk_size = 100
            for i in range(0, len(content), chunk_size):
                chunk = content[i:i + chunk_size]
                yield json.dumps({
                    "type": "content",
                    "file_path": file_path,
                    "content": chunk
                }) + "\n"
                await asyncio.sleep(0.02)
            
            # Send file end marker
            yield json.dumps({
                "type": "file_end",
                "file_path": file_path
            }) + "\n"
            
            await asyncio.sleep(0.05)
        
        # Send completion signal
        yield json.dumps({
            "type": "complete",
            "metadata": {
                "total_files": len(files),
                "message": f"Generated {len(files)} file(s) successfully"
            }
        }) + "\n"
        
    except asyncio.TimeoutError:
        yield json.dumps({
            "type": "error",
            "message": "Request timed out. The generation took too long. Please try a simpler prompt."
        }) + "\n"
    except Exception as e:
        error_message = str(e)
        
        # Handle specific error types
        if "rate_limit" in error_message.lower():
            yield json.dumps({
                "type": "error",
                "message": "Rate limit exceeded. Please wait a moment and try again."
            }) + "\n"
        elif "authentication" in error_message.lower() or "api_key" in error_message.lower():
            yield json.dumps({
                "type": "error",
                "message": "Invalid API key. Please check your ANTHROPIC_API_KEY in .env file."
            }) + "\n"
        elif "not_found" in error_message.lower():
            yield json.dumps({
                "type": "error",
                "message": "Model not found. The specified Claude model may not be available with your API key."
            }) + "\n"
        elif "overloaded" in error_message.lower():
            yield json.dumps({
                "type": "error",
                "message": "Claude API is currently overloaded. Please try again in a moment."
            }) + "\n"
        else:
            yield json.dumps({
                "type": "error",
                "message": f"Error generating code: {error_message}"
            }) + "\n"

@app.post("/api/generate")
async def generate_code(request: CodeGenerationRequest):
    """
    Streaming endpoint for code generation
    Client receives real-time updates as code is generated
    """
    
    async def event_stream():
        try:
            async for chunk in generate_code_stream(request.prompt, request.framework):
                yield f"data: {chunk}\n\n"
        except Exception as e:
            error_data = json.dumps({
                "type": "error",
                "message": str(e)
            })
            yield f"data: {error_data}\n\n"
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "v0-clone-backend"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
