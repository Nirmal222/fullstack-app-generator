# Google ADK Integration - V0 Clone Backend

## Overview

This backend now uses Google's Agent Development Kit (ADK) to implement a sophisticated multi-agent system for React code generation with:
- **Session Management**: Persistent conversation state across requests
- **Multi-Agent Architecture**: Specialized agents working together
- **Agentic State Management**: Intelligent state tracking and coordination
- **Error Recovery**: Automatic validation and fixing of generated code

## Architecture

### Multi-Agent System

```
┌─────────────────────────────────────────────────────┐
│                  Manager Agent                       │
│         (Orchestrates the workflow)                  │
│  - Coordinates sub-agents                            │
│  - Manages session state                             │
│  - Handles error recovery                            │
└──────────────┬──────────────────────────────────────┘
               │
    ┌──────────┴──────────┬──────────────┬────────────┐
    │                     │               │            │
┌───▼─────┐        ┌──────▼────┐    ┌────▼──────┐    │
│Planning │        │   Code    │    │  Review   │    │
│ Agent   │────────│Generator  │────│  Agent    │    │
│(Gemini) │        │ (Claude)  │    │ (Gemini)  │    │
└─────────┘        └───────────┘    └───┬───────┘    │
                                        │ Issues?     │
                                        └─────────────┘
                                         (Re-generate)
```

### 1. **Planning Agent** (Gemini 2.0 Flash)
- Analyzes user requirements
- Creates technical specifications
- Identifies components and dependencies
- Plans application structure

### 2. **Code Generator Agent** (Claude Sonnet)
- Generates production-ready React code
- Creates multiple files (components, styles)
- Follows React best practices
- Implements the technical plan

### 3. **Review Agent** (Gemini 2.0 Flash)
- Validates syntax and structure
- Checks React best practices
- Identifies errors and issues
- Triggers auto-fixes or re-generation
- Extracts dependencies

**Available Tools:**
- `validate_jsx_syntax`: JSX/JavaScript validation
- `validate_css_syntax`: CSS validation
- `check_react_best_practices`: React patterns check
- `extract_npm_dependencies`: Dependency extraction
- `auto_fix_common_errors`: Automatic error fixing
- `suggest_error_fix`: Intelligent fix suggestions

### 4. **Manager Agent** (Gemini 2.0 Flash)
- Orchestrates the entire workflow
- Manages state across phases
- Coordinates sub-agents
- Handles iterative improvements
- Provides user feedback

## Session Management

### Session Features
- **Persistent State**: Conversations and context maintained across requests
- **Session ID**: Continue previous conversations by passing `session_id`
- **State Tracking**: Each phase (planning, generating, reviewing) tracked
- **Iteration Control**: Automatic retry with maximum iteration limits

### Session State Structure
```json
{
  "current_phase": "planning|generating|reviewing|complete",
  "iteration_count": 0,
  "plan": {...},
  "generated_code": {...},
  "review_results": {...},
  "dependencies": {...}
}
```

## Project Structure

```
backend/
├── main.py                 # New FastAPI app with ADK
├── v0-clone-backend.py    # Legacy backend (for reference)
├── db.py                  # Database configuration
├── requirements.txt       # Dependencies
├── .env                   # Environment variables
│
├── agents/                # ADK Agents
│   ├── manager/
│   │   ├── agent.py
│   │   ├── instruction.txt
│   │   └── description.txt
│   ├── planning/
│   │   ├── agent.py
│   │   ├── instruction.txt
│   │   └── description.txt
│   ├── code_generator/
│   │   ├── agent.py
│   │   ├── instruction.txt
│   │   └── description.txt
│   └── review/
│       ├── agent.py
│       ├── instruction.txt
│       └── description.txt
│
├── tools/                 # ADK Tools
│   ├── validation_tools.py
│   ├── dependency_tools.py
│   └── error_recovery_tools.py
│
├── services/              # Business logic
│   └── agent_service.py
│
├── models/                # Data models
│   └── schemas.py
│
└── utils/                 # Utilities
    ├── config.py
    └── file_utils.py
```

## API Endpoints

### 1. Generate Code (POST `/api/generate`)
```json
{
  "prompt": "Create a todo app with add, delete, and mark complete",
  "framework": "react",
  "session_id": "optional-session-id"
}
```

**Response**: Server-Sent Events (SSE) stream with:
- Session creation events
- Agent phase updates
- Code generation progress
- File streaming
- Completion status

### 2. List Sessions (GET `/api/sessions`)
```
GET /api/sessions?user_id=default_user&page=1&page_size=10
```

### 3. Clear Session (POST `/api/sessions/clear`)
```json
{
  "session_id": "session-to-clear"
}
```

### 4. Health Check (GET `/health`)
```json
{
  "status": "healthy",
  "service": "v0-clone-backend-adk",
  "version": "2.0.0",
  "features": {
    "adk_enabled": true,
    "multi_agent": true,
    "session_management": true
  }
}
```

## Workflow

1. **User Request** → Manager Agent receives prompt
2. **Planning Phase** → Planning Agent analyzes requirements
3. **Code Generation** → Code Generator (Claude) creates code
4. **Review Phase** → Review Agent validates code
5. **Auto-Fix** → Minor issues fixed automatically
6. **Iteration** → If needed, regenerate with feedback (max 2-3 times)
7. **Completion** → Return validated code to user

## Benefits of ADK Integration

### 1. **Session Persistence**
- Resume conversations across requests
- Context maintained between iterations
- No need to repeat requirements

### 2. **Intelligent State Management**
- Automatic state tracking
- Phase management
- Iteration control

### 3. **Multi-Agent Collaboration**
- Specialized agents for specific tasks
- Better code quality through review process
- Automatic error recovery

### 4. **Scalability**
- Database-backed sessions (SQLite/PostgreSQL)
- Efficient state storage
- Production-ready architecture

## Configuration

### Required Environment Variables (.env)
```bash
# API Keys
GOOGLE_API_KEY=your_gemini_api_key
ANTHROPIC_API_KEY=your_claude_api_key

# Database
DATABASE_URL=sqlite:///./v0clone.db

# App Settings
APP_NAME=v0-clone
DEFAULT_SESSION_TTL=3600
```

## Database

### Development
- SQLite (default)
- File: `v0clone.db`
- Auto-created on startup

### Production
- PostgreSQL recommended
- Update `DATABASE_URL` in .env
- Uncomment `asyncpg` in requirements.txt

## Error Handling

### Automatic Recovery
1. **Syntax Errors**: Auto-fix common issues (className, brackets, etc.)
2. **Missing Dependencies**: Extracted and reported automatically
3. **Validation Failures**: Review agent identifies and suggests fixes
4. **Generation Issues**: Automatic retry with feedback

### Manual Recovery
- Manager agent coordinates fixes
- Maximum iteration limits prevent infinite loops
- Clear error messages for user intervention

## Monitoring

### Session Metrics
- Track in session state:
  - Iteration count
  - Fixes applied
  - Validation results
  - Dependencies extracted

### Agent Performance
- Phase tracking
- Tool usage statistics
- Error rates

## Extending the System

### Adding New Agents
1. Create agent directory under `agents/`
2. Add `instruction.txt` and `description.txt`
3. Create `agent.py` with Agent definition
4. Register with Manager Agent

### Adding New Tools
1. Create tool function in `tools/`
2. Follow ADK tool signature
3. Register with appropriate agent
4. Update agent instructions

## Comparison: Legacy vs ADK

| Feature | Legacy Backend | ADK Backend |
|---------|---------------|-------------|
| Session Management | ❌ None | ✅ Full support |
| State Persistence | ❌ No | ✅ Database-backed |
| Multi-Agent | ❌ Single model | ✅ Specialized agents |
| Error Recovery | ❌ Manual | ✅ Automatic |
| Code Review | ❌ No | ✅ Dedicated agent |
| Iteration | ❌ No | ✅ Intelligent retry |
| Tool Usage | ❌ No | ✅ Validation tools |

## Next Steps

1. **Testing**: Test with various prompts
2. **Monitoring**: Add metrics and logging
3. **Optimization**: Fine-tune agent instructions
4. **Scaling**: Move to PostgreSQL for production
5. **Features**: Add more tools and capabilities

## Resources

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [Bytecourse Service Reference](../bytecourse-service/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Claude API](https://docs.anthropic.com/)
- [Gemini API](https://ai.google.dev/)
