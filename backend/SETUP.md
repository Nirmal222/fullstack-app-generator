# Setup Guide - V0 Clone Backend with Google ADK

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Google Cloud account (for Gemini API)
- Anthropic account (for Claude API)

## Installation Steps

### 1. Navigate to Backend Directory

```bash
cd backend
```

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI and Uvicorn (web framework)
- Google ADK and GenAI (agent framework)
- Anthropic SDK (Claude API)
- Database drivers (SQLite for dev)
- Code analysis tools
- Other utilities

### 4. Configure Environment Variables

Edit the `.env` file in the backend directory:

```bash
# Required API Keys
GOOGLE_API_KEY=your_actual_gemini_api_key_here
ANTHROPIC_API_KEY=your_actual_claude_api_key_here

# Database (default is fine for development)
DATABASE_URL=sqlite:///./v0clone.db

# App Configuration (optional)
APP_NAME=v0-clone
DEFAULT_SESSION_TTL=3600
```

#### Getting API Keys

**Google Gemini API Key:**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and paste it in `.env`

**Anthropic Claude API Key:**
1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Sign up or sign in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key and paste it in `.env`

### 5. Verify Installation

Check if all dependencies are installed correctly:

```bash
python -c "import google.adk; import anthropic; import fastapi; print('✓ All dependencies installed')"
```

### 6. Initialize Database

The database will be automatically initialized on first run, but you can test it manually:

```bash
python -c "import asyncio; from db import init_database; asyncio.run(init_database())"
```

Expected output:
```
✓ Database initialized successfully
```

## Running the Server

### Development Mode

```bash
# Using Python directly
python main.py

# Or using Uvicorn with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Expected output:
```
🚀 Starting V0-Clone Backend with ADK...
✓ Database initialized
✓ Configuration validated
✓ ADK Manager Agent ready
✓ Server starting on http://0.0.0.0:8000
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Production Mode

```bash
# Use Gunicorn with Uvicorn workers
pip install gunicorn

gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

## Testing the Installation

### 1. Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
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

### 2. Test Code Generation

```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a simple counter button in React",
    "framework": "react"
  }'
```

You should see a stream of events showing:
- Session creation
- Planning phase
- Code generation
- Review phase
- Generated files

### 3. Using the Frontend

If you have the frontend running:
1. Navigate to `http://localhost:3000`
2. Enter a prompt
3. Click "Generate"
4. Watch the multi-agent system work!

## Troubleshooting

### Issue: "API key not configured"

**Solution:**
- Check that `.env` file exists in the backend directory
- Verify API keys are set correctly (no quotes, no spaces)
- Restart the server after modifying `.env`

### Issue: "Module not found"

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Database initialization failed"

**Solution:**
```bash
# Check write permissions
ls -la  # Should show write permissions for current directory

# Try removing existing database
rm v0clone.db
python main.py  # Will recreate database
```

### Issue: "Port 8000 already in use"

**Solution:**
```bash
# Find process using port 8000
lsof -ti:8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows

# Or use a different port
uvicorn main:app --port 8001
```

### Issue: "Import errors with google.adk"

**Solution:**
```bash
# Ensure google-adk is installed
pip install google-adk --upgrade

# Check Python version (must be 3.10+)
python --version
```

## Development Tips

### Hot Reload

For development, use the `--reload` flag:
```bash
uvicorn main:app --reload
```

This automatically restarts the server when you modify code.

### Viewing Logs

All agent activity is logged to console. For better logging:

```bash
# Add logging configuration to main.py
import logging
logging.basicConfig(level=logging.INFO)
```

### Testing Individual Agents

You can test agents individually:

```python
# test_agent.py
import asyncio
from agents.planning.agent import planning_agent
from google.genai import types

async def test():
    content = types.Content(parts=[types.Part(text="Create a todo app")])
    async for response in planning_agent.generate_response(content):
        print(response)

asyncio.run(test())
```

### Database Management

View sessions in SQLite:
```bash
# Install sqlite3 CLI if not available
# macOS: brew install sqlite
# Ubuntu: apt-get install sqlite3

sqlite3 v0clone.db
> .tables
> SELECT * FROM sessions;
> .quit
```

## Production Deployment

### Environment Setup

1. **Use PostgreSQL for production:**
   ```bash
   # Update .env
   DATABASE_URL=postgresql://user:password@localhost/v0clone
   
   # Install PostgreSQL driver
   pip install asyncpg
   ```

2. **Set production environment variables:**
   ```bash
   export ENVIRONMENT=production
   export LOG_LEVEL=WARNING
   ```

3. **Use process manager:**
   ```bash
   # PM2 (Node.js)
   pm2 start "uvicorn main:app --host 0.0.0.0 --port 8000" --name v0-backend
   
   # Or systemd service
   sudo systemctl start v0-backend
   ```

### Security Considerations

1. **API Key Protection:**
   - Never commit `.env` to version control
   - Use secret management service (AWS Secrets, GCP Secret Manager)
   - Rotate keys regularly

2. **Database Security:**
   - Use strong passwords
   - Enable SSL/TLS for connections
   - Regular backups

3. **Rate Limiting:**
   ```python
   # Add to main.py
   from slowapi import Limiter
   limiter = Limiter(key_func=lambda: "global")
   
   @app.post("/api/generate")
   @limiter.limit("10/minute")
   async def generate_code(...):
       ...
   ```

## Next Steps

1. ✅ Backend is now running with ADK
2. Test with various prompts
3. Monitor agent performance
4. Adjust agent instructions as needed
5. Scale to production environment

## Support

For issues or questions:
- Check [ADK_README.md](./ADK_README.md) for architecture details
- Review [Google ADK Documentation](https://google.github.io/adk-docs/)
- Check agent instruction files for customization

## Quick Reference

```bash
# Start server
python main.py

# Test health
curl http://localhost:8000/health

# Stop server
Ctrl+C

# View logs
tail -f logs/app.log  # if logging to file
