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

# Simulated LLM streaming (replace with actual API calls)
async def generate_code_stream(prompt: str, framework: str) -> AsyncGenerator[str, None]:
    """
    Simulates streaming code generation from LLM
    Replace this with actual OpenAI/Anthropic/Gemini API calls
    """
    
    # Example: Generating a React component
    files = {
        "App.js": '''import React, { useState } from 'react';
import './App.css';

function App() {
  const [count, setCount] = useState(0);

  return (
    <div className="App">
      <h1>Counter Application</h1>
      <p>Current count: {count}</p>
      <button onClick={() => setCount(count + 1)}>
        Increment
      </button>
      <button onClick={() => setCount(count - 1)}>
        Decrement
      </button>
    </div>
  );
}

export default App;''',
        
        "App.css": '''.App {
  text-align: center;
  padding: 50px;
  font-family: Arial, sans-serif;
}

h1 {
  color: #333;
  margin-bottom: 20px;
}

button {
  margin: 10px;
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
}

button:hover {
  background-color: #0056b3;
}'''
    }
    
    # Stream file by file
    for file_path, content in files.items():
        # Send file start marker
        yield json.dumps({
            "type": "file_start",
            "file_path": file_path,
            "metadata": {"size": len(content)}
        }) + "\n"
        
        await asyncio.sleep(0.1)
        
        # Stream content in chunks (simulating token-by-token generation)
        chunk_size = 50
        for i in range(0, len(content), chunk_size):
            chunk = content[i:i + chunk_size]
            yield json.dumps({
                "type": "content",
                "file_path": file_path,
                "content": chunk
            }) + "\n"
            await asyncio.sleep(0.05)  # Simulate streaming delay
        
        # Send file end marker
        yield json.dumps({
            "type": "file_end",
            "file_path": file_path
        }) + "\n"
        
        await asyncio.sleep(0.1)
    
    # Send completion signal
    yield json.dumps({
        "type": "complete",
        "metadata": {
            "total_files": len(files),
            "message": "Code generation complete"
        }
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

# Example: Integrate with actual LLM APIs
async def call_openai_streaming(prompt: str, model: str = "gpt-4"):
    """
    Example integration with OpenAI API (requires openai package)
    """
    # import openai
    # 
    # response = await openai.ChatCompletion.acreate(
    #     model=model,
    #     messages=[
    #         {"role": "system", "content": "You are a code generation assistant..."},
    #         {"role": "user", "content": prompt}
    #     ],
    #     stream=True
    # )
    # 
    # async for chunk in response:
    #     content = chunk.choices[0].delta.get("content", "")
    #     if content:
    #         yield content
    pass

async def call_anthropic_streaming(prompt: str):
    """
    Example integration with Anthropic Claude API
    """
    # import anthropic
    # 
    # async with anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY")) as client:
    #     async with client.messages.stream(
    #         model="claude-3-5-sonnet-20241022",
    #         max_tokens=4096,
    #         messages=[{"role": "user", "content": prompt}]
    #     ) as stream:
    #         async for text in stream.text_stream:
    #             yield text
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)