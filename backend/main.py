"""
V0-Clone Backend with Google ADK Integration
Multi-agent system for React code generation with session management
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import json
import asyncio
from typing import AsyncGenerator
from google.genai import types
from datetime import datetime

# Import enhanced logging
from utils.logger import setup_logging, get_logger

# Setup logging
setup_logging(level="DEBUG", log_file="backend.log")
logger = get_logger(__name__)

from models.schemas import (
    CodeGenerationRequest,
    SessionResponse,
    SessionListResponse,
    ClearSessionRequest
)
from services.agent_service import (
    get_user_session_and_runner,
    run_agent_with_session,
    process_agent_event,
    list_user_sessions
)
from agents.manager.agent import manager_agent
from db import init_database, get_session_service
from utils.config import Config
import re


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    print("🚀 Starting V0-Clone Backend with ADK...")
    
    # Initialize database
    try:
        await init_database()
        print("✓ Database initialized")
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
    
    # Validate configuration
    try:
        Config.validate()
        print("✓ Configuration validated")
    except ValueError as e:
        print(f"⚠️  Configuration warning: {e}")
    
    print("✓ ADK Manager Agent ready")
    print(f"✓ Server starting on http://0.0.0.0:8000")
    
    yield
    
    print("Shutting down V0-Clone Backend...")


app = FastAPI(
    title="V0-Clone Backend with ADK",
    description="AI-powered React code generation with multi-agent system",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def parse_code_from_response(content: str) -> dict:
    """
    Parse generated code from agent response
    Handles both markdown code blocks and plain text
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
    
    return files


async def generate_code_with_adk(
    prompt: str,
    user_id: str = "default_user",
    session_id: str = None
) -> AsyncGenerator[str, None]:
    """
    Generate code using ADK multi-agent system
    
    Args:
        prompt: User's code generation request
        user_id: User identifier
        session_id: Optional session ID for conversation continuity
    
    Yields:
        JSON-formatted events
    """
    logger.info(f"🎯 Starting code generation for user: {user_id}")
    logger.debug(f"Prompt: {prompt[:200]}...")
    
    try:
        # Get session and runner
        logger.info("📦 Initializing session and runner...")
        session, runner = await get_user_session_and_runner(
            user_id=user_id,
            agent=manager_agent,
            session_id=session_id
        )
        
        logger.info(f"✅ Session created: {session.id}")
        yield json.dumps({
            "type": "session_created",
            "session_id": session.id,
            "message": "Session initialized"
        }) + "\n"
        
        # Create user message content
        content = types.Content(
            parts=[types.Part(text=prompt)]
        )
        
        # Track agent responses
        current_phase = "initializing"
        generated_code = None
        event_count = 0
        
        # Run agent and process events
        logger.info("🤖 Running agent workflow...")
        async for event in run_agent_with_session(runner, session, content):
            event_count += 1
            processed = process_agent_event(event)
            
            if processed:
                # Track phases based on agent responses
                old_phase = current_phase
                if "planning" in processed.get("content", "").lower():
                    current_phase = "planning"
                elif "generat" in processed.get("content", "").lower():
                    current_phase = "generating"
                elif "review" in processed.get("content", "").lower():
                    current_phase = "reviewing"
                
                if old_phase != current_phase:
                    logger.info(f"📍 Phase transition: {old_phase} → {current_phase}")
                
                yield json.dumps({
                    "type": "agent_event",
                    "phase": current_phase,
                    "data": processed
                }) + "\n"
        
        logger.info(f"✅ Agent workflow completed. Processed {event_count} events")
        
        # Extract generated code from session state
        logger.info("🔍 Extracting generated code from session state...")
        logger.debug(f"Session state keys: {list(session.state.keys())}")
        
        # The output_schema key is defined in the agent (output_key="generated_code")
        generated_code = session.state.get("generated_code")
        
        if generated_code:
            logger.info(f"📄 Generated code found: {type(generated_code)}")
            
            # Handle both dict and Pydantic model instances
            if hasattr(generated_code, 'model_dump'):
                # It's a Pydantic model, convert to dict
                logger.debug("Converting Pydantic model to dict")
                generated_code = generated_code.model_dump()
            elif hasattr(generated_code, 'dict'):
                # Older Pydantic version
                logger.debug("Converting Pydantic model to dict (legacy)")
                generated_code = generated_code.dict()
            
            if isinstance(generated_code, dict):
                logger.debug(f"Generated code keys: {list(generated_code.keys())}")
            else:
                logger.warning(f"⚠️ Unexpected generated_code type: {type(generated_code)}")
        else:
            logger.warning("⚠️ No generated_code found in session state")
        
        # Stream generated code files
        if generated_code and isinstance(generated_code, dict):
            files_data = generated_code.get("files", [])
            logger.info(f"📁 Found {len(files_data)} files to stream")
            
            if files_data:
                for idx, file_data in enumerate(files_data, 1):
                    file_path = file_data.get("path", "unknown.js")
                    file_content = file_data.get("content", "")
                    logger.info(f"📄 Streaming file {idx}/{len(files_data)}: {file_path} ({len(file_content)} chars)")
                    
                    # Send file start
                    yield json.dumps({
                        "type": "file_start",
                        "file_path": file_path,
                        "metadata": {"size": len(file_content)}
                    }) + "\n"
                    
                    # Stream content in chunks
                    chunk_size = 100
                    for i in range(0, len(file_content), chunk_size):
                        chunk = file_content[i:i + chunk_size]
                        yield json.dumps({
                            "type": "content",
                            "file_path": file_path,
                            "content": chunk
                        }) + "\n"
                    
                    # Send file end
                    yield json.dumps({
                        "type": "file_end",
                        "file_path": file_path
                    }) + "\n"
                
                logger.info(f"✅ Successfully streamed {len(files_data)} files")
                
                # Send completion
                yield json.dumps({
                    "type": "complete",
                    "session_id": session.id,
                    "metadata": {
                        "total_files": len(files_data),
                        "message": f"Generated {len(files_data)} file(s) successfully"
                    }
                }) + "\n"
            else:
                # No files generated
                logger.error("❌ No files in generated_code.files array")
                yield json.dumps({
                    "type": "error",
                    "message": "No files were generated. Please try again.",
                    "session_id": session.id
                }) + "\n"
        else:
            # No generated_code in state
            logger.error(f"❌ Invalid generated_code: type={type(generated_code)}, value={generated_code}")
            yield json.dumps({
                "type": "error",
                "message": "Code generation did not complete. Please try again.",
                "session_id": session.id
            }) + "\n"
        
    except Exception as e:
        logger.error(f"❌ Fatal error in code generation: {str(e)}", exc_info=True)
        yield json.dumps({
            "type": "error",
            "message": f"Error generating code: {str(e)}"
        }) + "\n"


@app.post("/api/generate")
async def generate_code(request: CodeGenerationRequest):
    """
    Generate code using ADK multi-agent system
    Supports session continuity for iterative improvements
    """
    logger.info(f"📥 New generation request - Prompt: {request.prompt[:50]}...")
    logger.info(f"🔐 Session ID: {request.session_id or 'New session'}")
    
    async def event_stream():
        try:
            logger.info("🚀 Starting code generation stream")
            async for chunk in generate_code_with_adk(
                prompt=request.prompt,
                session_id=request.session_id
            ):
                yield f"data: {chunk}\n\n"
            logger.info("✅ Code generation completed successfully")
        except Exception as e:
            logger.error(f"❌ Generation error: {str(e)}", exc_info=True)
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


@app.get("/api/sessions")
async def get_sessions(
    user_id: str = "default_user",
    page: int = 1,
    page_size: int = 10
):
    """List user sessions with pagination"""
    try:
        result = await list_user_sessions(
            user_id=user_id,
            page=page,
            page_size=page_size
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/sessions/clear")
async def clear_session(request: ClearSessionRequest):
    """Clear a specific session"""
    try:
        session_service = get_session_service()
        # ADK session clearing would be implemented here
        # This is a placeholder for the actual implementation
        return {"status": "success", "message": f"Session {request.session_id} cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "v0-clone-backend-adk",
        "version": "2.0.0",
        "features": {
            "adk_enabled": True,
            "multi_agent": True,
            "session_management": True
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
