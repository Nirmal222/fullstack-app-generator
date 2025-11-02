# Timeout Troubleshooting Guide

## Issue: "Request timed out. The server took too long to respond."

This error occurs when the agent workflow takes longer than the frontend's timeout (3 minutes).

## Possible Causes

### 1. **Agent Workflow Taking Too Long**
The multi-agent system (Manager → Planning → Code Generator → Review) can be slow if:
- Complex prompts require extensive planning
- Multiple agent handoffs add latency
- LLM responses are slow
- Network latency to Google AI API

### 2. **No Streaming Updates**
If the backend doesn't send any events for a while, the frontend thinks it's stuck.

### 3. **Backend Not Responding**
The backend might be stuck or crashed.

## Diagnostic Steps

### Step 1: Check Backend Logs

Run the backend and look at `backend.log` or console output:

```bash
cd backend
python main.py
```

Look for:
- `🎯 Starting code generation` - Request received
- `📦 Initializing session` - Session created
- `🤖 Running agent workflow` - Agent started
- `📊 State delta received` - Agent producing output
- `📄 Generated code found` - Code extracted
- `✅ Successfully streamed` - Completion

If you see the workflow stuck at a certain phase, that's your bottleneck.

### Step 2: Test with Simple Prompt

Try a very simple prompt:
```
"Create a button component"
```

If this works but complex prompts timeout, the issue is workflow complexity.

### Step 3: Check Network Connectivity

```bash
curl -X POST http://localhost:8000/health
```

Should return immediately with status "healthy".

## Solutions

### Solution 1: Increase Frontend Timeout

**File**: `frontend/src/components/V0CloneAdvanced.jsx`

Change line with `AbortSignal.timeout(180000)` to:

```javascript
signal: AbortSignal.timeout(300000) // 5 minutes instead of 3
```

### Solution 2: Add Keepalive Events

**File**: `backend/main.py`

Add periodic keepalive events to prevent timeout:

```python
import asyncio

async def generate_code_with_adk(...):
    # ... existing code ...
    
    # Add keepalive task
    async def send_keepalive():
        while True:
            await asyncio.sleep(10)  # Every 10 seconds
            yield json.dumps({
                "type": "keepalive",
                "timestamp": datetime.now().isoformat()
            }) + "\n"
    
    # Merge keepalive with agent events
    # ... rest of code ...
```

### Solution 3: Optimize Agent Workflow

**Option A: Use Faster Model**

Change in agent files to use faster model:
```python
model="gemini-2.0-flash-exp"  # Faster than gemini-2.0-flash
```

**Option B: Simplify Multi-Agent Flow**

Instead of Manager → Planning → Generator → Review, use direct generation:

```python
# In main.py, replace manager_agent with code_generator_agent directly
from agents.code_generator.agent import code_generator_agent

session, runner = await get_user_session_and_runner(
    user_id=user_id,
    agent=code_generator_agent,  # Direct generation, skip planning/review
    session_id=session_id
)
```

**Option C: Make Agents Concurrent**

Use parallel execution instead of sequential (requires ADK configuration).

### Solution 4: Add Progress Updates

Ensure the backend sends frequent updates:

```python
# In run_agent_with_session, yield progress events
async for event in events:
    event_count += 1
    
    # Send progress update every 5 events
    if event_count % 5 == 0:
        yield json.dumps({
            "type": "progress",
            "events_processed": event_count,
            "message": "Processing..."
        }) + "\n"
    
    # ... rest of code ...
```

### Solution 5: Implement Timeout Handling

**File**: `backend/main.py`

Add timeout to agent execution:

```python
import asyncio

async def generate_code_with_adk(...):
    try:
        # Set timeout for agent execution
        async with asyncio.timeout(240):  # 4 minutes
            async for event in run_agent_with_session(runner, session, content):
                # ... process events ...
    except asyncio.TimeoutError:
        logger.error("⏱️ Agent execution timed out")
        yield json.dumps({
            "type": "error",
            "message": "Code generation timed out. Please try a simpler prompt."
        }) + "\n"
```

## Recommended Quick Fix

**Immediate solution** (no code changes needed):

1. **Check backend logs** to see where it's stuck
2. **Try simpler prompts** to verify the system works
3. **Increase frontend timeout** to 5 minutes

**Long-term solution**:

1. **Add keepalive events** to prevent frontend timeout
2. **Optimize agent workflow** by using faster models or direct generation
3. **Add progress indicators** so users know it's working

## Testing

After applying fixes, test with:

1. **Simple prompt**: "Create a button"
2. **Medium prompt**: "Create a todo list app"
3. **Complex prompt**: "Create a full e-commerce dashboard"

Monitor `backend.log` to see timing for each phase.

## Expected Timings

Normal workflow should complete in:
- Simple prompts: 10-30 seconds
- Medium prompts: 30-60 seconds
- Complex prompts: 60-120 seconds

If taking longer than 2 minutes, investigate bottlenecks.
