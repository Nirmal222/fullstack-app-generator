# State Delta Flow Documentation

## Overview

The state_delta handling in the backend is **completely transparent to the frontend**. The frontend continues to work exactly as before, receiving the same event stream format.

## How It Works

### Backend Flow (with state_delta)

```
1. Frontend sends request → Backend receives prompt
2. Backend creates session and runner
3. Runner executes agent workflow
4. Agent generates structured output using output_schema
5. ADK emits events with state_delta containing structured data
6. Backend captures state_delta and updates session.state
7. Backend extracts generated_code from session.state
8. Backend converts Pydantic model to dict (if needed)
9. Backend streams files to frontend in standard format
```

### Key Backend Changes

#### 1. State Delta Capture (`agent_service.py`)

```python
async for event in events:
    # Handle state_delta for structured output_schema responses
    if hasattr(event, 'state_delta') and event.state_delta:
        logger.info(f"📊 State delta received: {list(event.state_delta.keys())}")
        for key, value in event.state_delta.items():
            # Update session state with delta
            session.state[key] = value
    
    yield event
```

**What this does:**
- Detects when an event contains `state_delta`
- Extracts structured data (e.g., `generated_code`)
- Updates the session state automatically
- Logs the keys for debugging

#### 2. Pydantic Model Handling (`main.py`)

```python
generated_code = session.state.get("generated_code")

if generated_code:
    # Handle both dict and Pydantic model instances
    if hasattr(generated_code, 'model_dump'):
        # It's a Pydantic model, convert to dict
        generated_code = generated_code.model_dump()
    elif hasattr(generated_code, 'dict'):
        # Older Pydantic version
        generated_code = generated_code.dict()
```

**What this does:**
- Retrieves `generated_code` from session state
- Checks if it's a Pydantic model
- Converts to dict for JSON serialization
- Handles both Pydantic v1 and v2

### Frontend Compatibility

The frontend **receives the exact same event stream** as before:

```javascript
// Frontend receives these events (unchanged):
{
  "type": "session_created",
  "session_id": "abc123",
  "message": "Session initialized"
}

{
  "type": "agent_event",
  "phase": "generating",
  "data": { ... }
}

{
  "type": "file_start",
  "file_path": "src/App.jsx",
  "metadata": { "size": 1234 }
}

{
  "type": "content",
  "file_path": "src/App.jsx",
  "content": "import React..."
}

{
  "type": "file_end",
  "file_path": "src/App.jsx"
}

{
  "type": "complete",
  "session_id": "abc123",
  "metadata": {
    "total_files": 2,
    "message": "Generated 2 file(s) successfully"
  }
}
```

## Why No Frontend Changes Are Needed

### 1. **Transparent State Management**
- State delta is captured and processed entirely in the backend
- Frontend never sees the raw state_delta events
- Frontend only receives the final processed file events

### 2. **Same Event Format**
- The event stream format remains unchanged
- File streaming works exactly the same way
- No new event types introduced

### 3. **Backward Compatible**
- Works with both structured (output_schema) and unstructured responses
- Handles Pydantic models and plain dicts
- Gracefully falls back if state_delta is not present

## Agent Output Schema

The code generator agent uses this output schema:

```python
class GeneratedFile(BaseModel):
    path: str = Field(description="File path")
    content: str = Field(description="Complete file content")
    language: str = Field(description="Programming language")

class CodeGenerationOutput(BaseModel):
    files: List[GeneratedFile] = Field(description="List of generated files")
    dependencies: List[str] = Field(default=[], description="Required packages")
    setup_instructions: str = Field(default="", description="Setup instructions")
```

When the agent completes, ADK automatically:
1. Validates the output against the schema
2. Creates a `CodeGenerationOutput` Pydantic model instance
3. Emits an event with `state_delta = {"generated_code": <model_instance>}`
4. Our backend captures this and updates `session.state["generated_code"]`

## Logging Output

With the new logging, you'll see:

```
✅ [timestamp] INFO - 🚀 Running agent for session: abc123
📊 [timestamp] INFO - State delta received: ['generated_code']
🔍 [timestamp] DEBUG -   - generated_code: CodeGenerationOutput
📄 [timestamp] INFO - Generated code found: <class 'CodeGenerationOutput'>
🔍 [timestamp] DEBUG - Converting Pydantic model to dict
📁 [timestamp] INFO - Found 2 files to stream
📄 [timestamp] INFO - Streaming file 1/2: src/App.jsx (1234 chars)
✅ [timestamp] INFO - Successfully streamed 2 files
```

## Benefits

### 1. **Type Safety**
- Structured output ensures consistent format
- Pydantic validation catches errors early
- No need to parse unstructured text

### 2. **Better Error Handling**
- If agent doesn't follow schema, ADK catches it
- Clear error messages about what's missing
- Automatic retry logic can be implemented

### 3. **Easier Debugging**
- Logs show exactly what data is received
- State keys are visible at each step
- Type information helps identify issues

### 4. **Session Continuity**
- State persists across requests
- Can reference previous generations
- Enables iterative improvements

## Example Flow

### Request:
```json
{
  "prompt": "Create a todo app",
  "session_id": null
}
```

### Backend Processing:
1. Creates new session
2. Runs manager_agent → planning_agent → code_generator_agent
3. Code generator produces `CodeGenerationOutput` model
4. ADK emits event with `state_delta = {"generated_code": <model>}`
5. Backend captures state_delta
6. Backend converts model to dict
7. Backend extracts files array
8. Backend streams each file to frontend

### Frontend Receives:
```javascript
// Standard event stream (no changes needed)
data: {"type":"session_created","session_id":"abc123"}
data: {"type":"agent_event","phase":"planning"}
data: {"type":"agent_event","phase":"generating"}
data: {"type":"file_start","file_path":"src/App.jsx"}
data: {"type":"content","file_path":"src/App.jsx","content":"import..."}
data: {"type":"file_end","file_path":"src/App.jsx"}
data: {"type":"complete","session_id":"abc123"}
```

## Summary

**Frontend developers don't need to know about state_delta!**

The backend handles all the complexity:
- ✅ Captures state deltas automatically
- ✅ Converts Pydantic models to dicts
- ✅ Maintains session state
- ✅ Streams files in the expected format
- ✅ Logs everything for debugging

The frontend continues to work exactly as before, consuming the same event stream format.
