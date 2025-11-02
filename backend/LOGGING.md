# Logging System Documentation

## Overview

The V0-Clone backend now includes a comprehensive logging system based on bytecourse-service patterns. This system provides detailed visibility into the application's behavior, making it easier to debug issues and monitor performance.

## Features

- **Colored Console Output**: Easy-to-read logs with emojis and color coding
- **JSON Logging**: Structured logs for production environments
- **File Logging**: Persistent logs saved to `backend.log`
- **Multiple Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Exception Tracking**: Full stack traces for errors
- **Context Management**: Add contextual information to logs

## Log Levels

- **DEBUG** 🔍: Detailed information for diagnosing problems
- **INFO** ✅: General informational messages
- **WARNING** ⚠️: Warning messages for potentially harmful situations
- **ERROR** ❌: Error messages for serious problems
- **CRITICAL** 🔥: Critical messages for very serious errors

## Configuration

The logging system is configured in `backend/main.py`:

```python
from utils.logger import setup_logging, get_logger

# Setup logging with DEBUG level and file output
setup_logging(level="DEBUG", log_file="backend.log")
logger = get_logger(__name__)
```

### Configuration Options

- `level`: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `log_file`: Optional file path for persistent logging
- `json_format`: Use JSON format for structured logging (default: False)

## Usage Examples

### Basic Logging

```python
from utils.logger import get_logger

logger = get_logger(__name__)

logger.debug("Detailed debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
logger.critical("Critical error")
```

### Logging with Exception Info

```python
try:
    # Some operation
    result = risky_operation()
except Exception as e:
    logger.error(f"Operation failed: {str(e)}", exc_info=True)
```

### Using Log Context

```python
from utils.logger import LogContext

with LogContext(logger, user_id="user123", session_id="session456"):
    logger.info("Processing request")
    # Logs will include user_id and session_id in context
```

## Key Logging Points

### 1. API Endpoints (`main.py`)

- Request received with prompt preview
- Session ID (new or existing)
- Code generation start/completion
- Errors with full stack traces

### 2. Agent Service (`services/agent_service.py`)

- Session creation/retrieval
- Runner initialization
- Agent execution events
- Event processing
- Tool calls and responses

### 3. Code Generation Flow (`main.py`)

- Session initialization
- Agent workflow execution
- Phase transitions (planning → generating → reviewing)
- Generated code extraction
- File streaming
- Completion or error states

## Log Output Examples

### Console Output (Colored)

```
✅ [2025-02-11 17:00:00] INFO - __main__ - 📥 New generation request - Prompt: Create a todo app...
✅ [2025-02-11 17:00:00] INFO - __main__ - 🔐 Session ID: New session
✅ [2025-02-11 17:00:01] INFO - services.agent_service - 🔍 Getting session for user_id=default_user, session_id=None
✅ [2025-02-11 17:00:01] INFO - services.agent_service - 🆕 Creating new session for user: default_user
✅ [2025-02-11 17:00:02] INFO - services.agent_service - ✅ Created new session: abc123
```

### File Output (backend.log)

JSON-formatted logs with full context:

```json
{
  "timestamp": "2025-02-11T17:00:00.123456",
  "level": "INFO",
  "logger": "__main__",
  "message": "📥 New generation request - Prompt: Create a todo app...",
  "module": "main",
  "function": "generate_code",
  "line": 245
}
```

## Debugging Common Issues

### Issue: "Code generation did not complete"

Check logs for:
1. Session state keys: `Session state keys: ['key1', 'key2']`
2. Generated code presence: `Generated code found: <class 'dict'>`
3. Files array: `Found X files to stream`

### Issue: Agent not responding

Look for:
1. Runner creation: `Runner created successfully`
2. Agent execution: `Running agent for session: xyz`
3. Event count: `Agent execution completed. Total events: N`

### Issue: Tool execution failures

Search for:
1. Tool calls: `🔧 Tool call: tool_name`
2. Tool responses: `🔧 Tool response: tool_name`
3. Error messages with stack traces

## Best Practices

1. **Use appropriate log levels**
   - DEBUG: Detailed diagnostic information
   - INFO: Important milestones and state changes
   - WARNING: Recoverable issues
   - ERROR: Serious problems requiring attention

2. **Include context in messages**
   ```python
   logger.info(f"Processing request for user: {user_id}, session: {session_id}")
   ```

3. **Log exceptions with stack traces**
   ```python
   logger.error(f"Failed to process: {str(e)}", exc_info=True)
   ```

4. **Use emojis for visual scanning**
   - 🎯 Starting operations
   - ✅ Successful completions
   - ❌ Errors
   - ⚠️ Warnings
   - 🔍 Searching/finding
   - 📦 Initialization
   - 🚀 Execution

## Monitoring in Production

For production environments:

1. Enable JSON logging:
   ```python
   setup_logging(level="INFO", log_file="backend.log", json_format=True)
   ```

2. Use log aggregation tools (e.g., ELK Stack, Splunk)

3. Set up alerts for ERROR and CRITICAL logs

4. Monitor log file size and implement rotation

## Troubleshooting

### Logs not appearing

1. Check log level configuration
2. Verify logger is initialized: `logger = get_logger(__name__)`
3. Ensure logging is set up before other imports

### Too many logs

1. Increase log level to INFO or WARNING
2. Adjust third-party logger levels in `utils/logger.py`

### File logging not working

1. Check file permissions
2. Verify disk space
3. Check file path is writable

## Related Files

- `backend/utils/logger.py`: Logging configuration and utilities
- `backend/main.py`: Main application with logging
- `backend/services/agent_service.py`: Agent service with logging
- `backend.log`: Log file output
