import React, { useState, useEffect, useRef, useCallback } from 'react';
import Editor from '@monaco-editor/react';
import { SandpackProvider, SandpackPreview, useSandpack } from '@codesandbox/sandpack-react';
import './V0CloneAdvanced.css';

// Preview Error Monitor Component
const PreviewErrorMonitor = ({ onErrorDetected }) => {
  const { sandpack } = useSandpack();

  useEffect(() => {
    // Monitor for any error state
    if (sandpack.error) {
      onErrorDetected(sandpack.error);
    }
    
    // Monitor status changes
    if (sandpack.status === 'error') {
      const errorMsg = sandpack.error?.message || 'Build error occurred';
      onErrorDetected({ message: errorMsg });
    }
  }, [sandpack.error, sandpack.status, onErrorDetected]);

  return null; // This component doesn't render anything
};

// Custom Editor Component with Monaco
const MonacoEditor = ({ files, activeFile, onFileChange, onErrorDetected }) => {
  const { sandpack } = useSandpack();
  const editorRef = useRef(null);

  // Listen for all types of errors from Sandpack
  useEffect(() => {
    // Runtime errors
    if (sandpack.error) {
      onErrorDetected(sandpack.error);
    }
    
    // Build/compilation errors
    if (sandpack.status === 'error') {
      const errorMessage = sandpack.error?.message || 'Build error occurred';
      onErrorDetected({ message: errorMessage });
    }
  }, [sandpack.error, sandpack.status, onErrorDetected]);

  // Listen to console logs for additional errors
  useEffect(() => {
    const consoleListener = (logs) => {
      logs.forEach(log => {
        if (log.level === 'error') {
          onErrorDetected({ 
            message: log.data.join(' '),
            source: 'console'
          });
        }
      });
    };

    // If Sandpack has console logs, listen to them
    if (sandpack.listen) {
      const unsubscribe = sandpack.listen((message) => {
        if (message.type === 'console' && message.log?.level === 'error') {
          onErrorDetected({
            message: message.log.data.join(' '),
            source: 'console'
          });
        }
      });
      
      return () => {
        if (unsubscribe) unsubscribe();
      };
    }
  }, [sandpack, onErrorDetected]);

  const handleEditorDidMount = (editor) => {
    editorRef.current = editor;
    
    editor.addCommand(window.monaco.KeyMod.CtrlCmd | window.monaco.KeyCode.KeyS, () => {
      console.log('File saved!');
    });
  };

  const handleEditorChange = (value) => {
    onFileChange(activeFile, value || '');
    sandpack.updateFile(activeFile, value || '');
  };

  const getLanguage = (filename) => {
    const ext = filename.split('.').pop();
    const languageMap = {
      'js': 'javascript',
      'jsx': 'javascript',
      'ts': 'typescript',
      'tsx': 'typescript',
      'css': 'css',
      'html': 'html',
      'json': 'json',
      'md': 'markdown'
    };
    return languageMap[ext] || 'javascript';
  };

  return (
    <Editor
      height="100%"
      language={getLanguage(activeFile)}
      value={files[activeFile] || ''}
      theme="vs-dark"
      onChange={handleEditorChange}
      onMount={handleEditorDidMount}
      options={{
        minimap: { enabled: true },
        fontSize: 14,
        lineNumbers: 'on',
        roundedSelection: false,
        scrollBeyondLastLine: false,
        automaticLayout: true,
        tabSize: 2,
        formatOnPaste: true,
        formatOnType: true,
        suggestOnTriggerCharacters: true,
        quickSuggestions: true,
        wordWrap: 'on',
      }}
    />
  );
};

const V0CloneAdvanced = () => {
  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [files, setFiles] = useState({
    '/App.js': `import React, { useState } from 'react';
import './App.css';

export default function App() {
  const [count, setCount] = useState(0);

  return (
    <div className="app">
      <h1>Welcome to V0 Clone</h1>
      <p>Generate code with AI, then edit with Monaco Editor!</p>
      <div className="counter">
        <button onClick={() => setCount(count - 1)}>-</button>
        <span>{count}</span>
        <button onClick={() => setCount(count + 1)}>+</button>
      </div>
    </div>
  );
}`,
    '/App.css': `.app {
  text-align: center;
  padding: 40px;
  font-family: system-ui, -apple-system, sans-serif;
}

h1 {
  color: #667eea;
  margin-bottom: 10px;
}

.counter {
  display: flex;
  gap: 20px;
  justify-content: center;
  align-items: center;
}

.counter button {
  padding: 10px 20px;
  font-size: 18px;
  border: none;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.2s;
}

.counter button:hover {
  transform: scale(1.05);
}

.counter span {
  font-size: 24px;
  font-weight: bold;
}`,
    '/components/Button.jsx': `import React from 'react';
import './Button.css';

export default function Button({ children, onClick }) {
  return (
    <button className="custom-button" onClick={onClick}>
      {children}
    </button>
  );
}`,
    '/components/Button.css': `.custom-button {
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 600;
  border: none;
  border-radius: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  cursor: pointer;
  transition: all 0.2s;
}

.custom-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}`
  });
  
  const [activeFile, setActiveFile] = useState('/App.js');
  const [expandedFolders, setExpandedFolders] = useState({ 'components': true });
  const [generationLog, setGenerationLog] = useState([]);
  const [viewMode, setViewMode] = useState('code'); // 'code' or 'preview'
  const [showChat, setShowChat] = useState(true);
  const [error, setError] = useState(null);
  const [retryCount, setRetryCount] = useState(0);
  const [runtimeErrors, setRuntimeErrors] = useState([]);
  const [isFixing, setIsFixing] = useState(false);
  
  // ADK Session Management
  const [sessionId, setSessionId] = useState(null);
  const [currentPhase, setCurrentPhase] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [showSessionPanel, setShowSessionPanel] = useState(false);
  
  // Connection status
  const [connectionStatus, setConnectionStatus] = useState('checking'); // 'connected', 'disconnected', 'checking'
  const [backendError, setBackendError] = useState(null);

  // Check backend connection on mount
  useEffect(() => {
    const checkConnection = async () => {
      try {
        const response = await fetch('http://localhost:8000/health');
        if (response.ok) {
          setConnectionStatus('connected');
          setBackendError(null);
        } else {
          setConnectionStatus('disconnected');
          setBackendError(`Server returned ${response.status}`);
        }
      } catch (error) {
        setConnectionStatus('disconnected');
        setBackendError('Cannot connect to backend server');
      }
    };
    
    checkConnection();
    const interval = setInterval(checkConnection, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  // File operations
  const handleFileChange = (filePath, content) => {
    setFiles(prev => ({
      ...prev,
      [filePath]: content
    }));
  };

  // Build file tree structure
  const buildFileTree = (filePaths) => {
    const tree = {};
    
    filePaths.forEach(path => {
      // Remove leading slash if present for tree building
      const cleanPath = path.startsWith('/') ? path.slice(1) : path;
      const parts = cleanPath.split('/').filter(p => p); // Filter empty parts
      let current = tree;
      
      parts.forEach((part, index) => {
        if (index === parts.length - 1) {
          // It's a file
          current[part] = { type: 'file', path };
        } else {
          // It's a folder
          if (!current[part]) {
            current[part] = { type: 'folder', children: {} };
          }
          current = current[part].children;
        }
      });
    });
    
    return tree;
  };

  const toggleFolder = (folderPath) => {
    setExpandedFolders(prev => ({
      ...prev,
      [folderPath]: !prev[folderPath]
    }));
  };

  const addNewFile = () => {
    const fileName = window.prompt('Enter file path (e.g., src/components/Button.js, src/styles.css):');
    if (!fileName) return;
    
    const filePath = fileName.startsWith('/') ? fileName.slice(1) : fileName;
    if (files[filePath]) {
      alert('File already exists!');
      return;
    }

    const extension = filePath.split('.').pop();
    const componentName = filePath.split('/').pop().split('.')[0];
    let defaultContent = '';
    
    if (extension === 'js' || extension === 'jsx') {
      defaultContent = `import React from 'react';\n\nexport default function ${componentName}() {\n  return (\n    <div>\n      <h2>${componentName}</h2>\n    </div>\n  );\n}`;
    } else if (extension === 'css') {
      defaultContent = `/* ${filePath} styles */\n\n`;
    }
    
    // Expand parent folders
    const pathParts = filePath.split('/');
    pathParts.pop(); // Remove file name
    let folderPath = '';
    pathParts.forEach(part => {
      folderPath = folderPath ? `${folderPath}/${part}` : part;
      setExpandedFolders(prev => ({ ...prev, [folderPath]: true }));
    });
    
    setFiles(prev => ({
      ...prev,
      [filePath]: defaultContent
    }));
    setActiveFile(filePath);
    setGenerationLog(prev => [...prev, `✅ Created ${filePath}`]);
  };

  const deleteFile = (filePath) => {
    if (Object.keys(files).length === 1) {
      alert('Cannot delete the last file!');
      return;
    }
    
    const { [filePath]: removed, ...remaining } = files;
    setFiles(remaining);
    
    if (activeFile === filePath) {
      setActiveFile(Object.keys(remaining)[0]);
    }
    setGenerationLog(prev => [...prev, `🗑️ Deleted ${filePath}`]);
  };

  // ADK Session Management Functions
  const loadSessions = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/sessions?user_id=default_user');
      if (response.ok) {
        const data = await response.json();
        setSessions(data.sessions || []);
      }
    } catch (error) {
      console.error('Failed to load sessions:', error);
    }
  };

  const continueWithSession = (sid) => {
    setSessionId(sid);
    setShowSessionPanel(false);
    setGenerationLog(prev => [...prev, `🔄 Continuing session: ${sid}`]);
  };

  const clearSession = async (sid) => {
    try {
      await fetch('http://localhost:8000/api/sessions/clear', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sid })
      });
      loadSessions();
      if (sessionId === sid) {
        setSessionId(null);
      }
    } catch (error) {
      console.error('Failed to clear session:', error);
    }
  };

  // Code generation with ADK support
  const generateCode = async () => {
    if (!prompt.trim()) {
      setError('Please enter a prompt to generate code');
      return;
    }

    setIsGenerating(true);
    setGenerationLog([]);
    setError(null);
    setCurrentPhase('initializing');
    const newFiles = {};
    let hasReceivedData = false;

    try {
      // Call ADK backend
      const response = await fetch('http://localhost:8000/api/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: prompt,
          framework: 'react',
          session_id: sessionId || undefined
        }),
        signal: AbortSignal.timeout(180000) // 3 minute timeout for ADK
      });

      if (!response.ok) {
        throw new Error(`Server responded with status ${response.status}`);
      }

      if (!response.body) {
        throw new Error('Response body is empty');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      let currentFile = null;
      let currentContent = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          if (!hasReceivedData) {
            throw new Error('No data received from server');
          }
          break;
        }

        hasReceivedData = true;
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));

              switch (data.type) {
              // ADK-specific events
              case 'session_created':
                setSessionId(data.session_id);
                setGenerationLog(prev => [...prev, `🔐 Session: ${data.session_id.substring(0, 8)}...`]);
                break;

              case 'agent_event':
                if (data.phase) {
                  setCurrentPhase(data.phase);
                  const phaseEmoji = {
                    'initializing': '🚀',
                    'planning': '📋',
                    'generating': '💻',
                    'reviewing': '✅'
                  };
                  setGenerationLog(prev => [...prev, `${phaseEmoji[data.phase] || '⚙️'} ${data.phase.charAt(0).toUpperCase() + data.phase.slice(1)}...`]);
                }
                if (data.data?.content) {
                  setGenerationLog(prev => [...prev, `  ${data.data.content.substring(0, 100)}...`]);
                }
                break;

              case 'agent_response':
                if (data.content) {
                  setGenerationLog(prev => [...prev, `💬 ${data.content.substring(0, 150)}...`]);
                }
                break;

              // Standard file events
              case 'file_start':
                currentFile = data.file_path;
                currentContent = '';
                setGenerationLog(prev => [...prev, `📄 Creating ${data.file_path}...`]);
                break;

              case 'content':
                currentContent += data.content;
                // Convert backend paths to Sandpack-compatible paths
                // src/App.jsx -> /App.js, src/App.css -> /App.css, etc.
                let sandpackPath = currentFile;
                
                // Remove 'src/' prefix if present
                if (sandpackPath.startsWith('src/')) {
                  sandpackPath = sandpackPath.slice(4);
                }
                
                // Ensure leading slash
                if (!sandpackPath.startsWith('/')) {
                  sandpackPath = '/' + sandpackPath;
                }
                
                // Convert .jsx to .js for compatibility
                sandpackPath = sandpackPath.replace(/\.jsx$/, '.js');
                
                newFiles[sandpackPath] = currentContent;
                setFiles({ ...newFiles });
                break;

              case 'file_end':
                setGenerationLog(prev => [...prev, `✅ Completed ${data.file_path}`]);
                // Use the same path transformation
                let finalPath = data.file_path;
                if (finalPath.startsWith('src/')) {
                  finalPath = finalPath.slice(4);
                }
                if (!finalPath.startsWith('/')) {
                  finalPath = '/' + finalPath;
                }
                finalPath = finalPath.replace(/\.jsx$/, '.js');
                
                if (Object.keys(newFiles).length === 1) {
                  setActiveFile(finalPath);
                }
                break;

              case 'complete':
                setGenerationLog(prev => [...prev, `🎉 ${data.metadata.message}`]);
                setIsGenerating(false);
                break;

              case 'error':
                setGenerationLog(prev => [...prev, `❌ Error: ${data.message}`]);
                setError(data.message);
                setIsGenerating(false);
                break;

              default:
                console.warn('Unknown message type:', data.type);
            }
            } catch (parseError) {
              console.error('Error parsing server message:', parseError);
              setGenerationLog(prev => [...prev, `⚠️ Warning: Could not parse server message`]);
            }
          }
        }
      }
    } catch (error) {
      console.error('Generation error:', error);
      
      let errorMessage = 'An unexpected error occurred';
      
      if (error.name === 'AbortError' || error.message.includes('timeout')) {
        errorMessage = 'Request timed out. The server took too long to respond. Please try a simpler prompt.';
      } else if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
        errorMessage = 'Cannot connect to backend server. Please ensure the server is running at http://localhost:8000';
      } else if (error.message.includes('status')) {
        errorMessage = `Server error: ${error.message}. Please try again.`;
      } else {
        errorMessage = error.message || 'An unexpected error occurred';
      }
      
      setError(errorMessage);
      setGenerationLog(prev => [...prev, `❌ ${errorMessage}`]);
      setIsGenerating(false);
    }
  };

  // Retry generation
  const retryGeneration = () => {
    setRetryCount(prev => prev + 1);
    setError(null);
    generateCode();
  };

  // Clear error
  const clearError = () => {
    setError(null);
    setGenerationLog([]);
  };

  // Handle runtime errors from Sandpack
  const handleRuntimeError = useCallback((error) => {
    if (error) {
      const errorInfo = {
        message: error.message || 'Unknown error',
        line: error.line,
        column: error.column,
        path: error.path
      };
      
      setRuntimeErrors(prev => {
        const isDuplicate = prev.some(e => e.message === errorInfo.message);
        if (!isDuplicate) {
          return [...prev, errorInfo];
        }
        return prev;
      });
    }
  }, []);

  // Fix errors using Claude
  const fixErrors = async () => {
    if (runtimeErrors.length === 0) return;

    setIsFixing(true);
    setGenerationLog([]);

    try {
      // Prepare error context
      const errorContext = runtimeErrors.map(err => 
        `Error: ${err.message}${err.path ? ` in ${err.path}` : ''}${err.line ? ` at line ${err.line}` : ''}`
      ).join('\n');

      // Prepare current code
      const currentCode = Object.entries(files).map(([path, content]) => 
        `File: ${path}\n\`\`\`\n${content}\n\`\`\``
      ).join('\n\n');

      const fixPrompt = `I have the following errors in my React application:\n\n${errorContext}\n\nHere's the current code:\n\n${currentCode}\n\nPlease fix these errors and return the corrected code with the same file structure.`;

      const response = await fetch('http://localhost:8000/api/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: fixPrompt,
          framework: 'react',
          model: 'gpt-4'
        }),
        signal: AbortSignal.timeout(120000)
      });

      if (!response.ok) {
        throw new Error(`Server responded with status ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      const newFiles = {};
      let currentFile = null;
      let currentContent = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));

              switch (data.type) {
                case 'file_start':
                  currentFile = data.file_path;
                  currentContent = '';
                  setGenerationLog(prev => [...prev, `🔧 Fixing ${data.file_path}...`]);
                  break;

                case 'content':
                  currentContent += data.content;
                  let sandpackPath = currentFile;
                  if (sandpackPath.startsWith('src/')) {
                    sandpackPath = sandpackPath.slice(4);
                  }
                  if (!sandpackPath.startsWith('/')) {
                    sandpackPath = '/' + sandpackPath;
                  }
                  sandpackPath = sandpackPath.replace(/\.jsx$/, '.js');
                  newFiles[sandpackPath] = currentContent;
                  setFiles({ ...newFiles });
                  break;

                case 'file_end':
                  setGenerationLog(prev => [...prev, `✅ Fixed ${data.file_path}`]);
                  break;

                case 'complete':
                  setGenerationLog(prev => [...prev, `🎉 Errors fixed successfully!`]);
                  setRuntimeErrors([]);
                  setIsFixing(false);
                  break;

                case 'error':
                  setGenerationLog(prev => [...prev, `❌ Error: ${data.message}`]);
                  setError(data.message);
                  setIsFixing(false);
                  break;
              }
            } catch (parseError) {
              console.error('Error parsing server message:', parseError);
            }
          }
        }
      }
    } catch (error) {
      console.error('Fix error:', error);
      setError('Failed to fix errors. Please try again.');
      setIsFixing(false);
    }
  };

  // Clear runtime errors
  const clearRuntimeErrors = () => {
    setRuntimeErrors([]);
  };

  const getFileIcon = (filename) => {
    if (filename.endsWith('.css')) return '🎨';
    if (filename.endsWith('.tsx') || filename.endsWith('.ts')) return '📘';
    if (filename.endsWith('.jsx') || filename.endsWith('.js')) return '⚛️';
    if (filename.endsWith('.json')) return '📋';
    return '📄';
  };

  const getLineCount = (content) => {
    return content.split('\n').length;
  };

  // Render file tree recursively
  const renderFileTree = (tree, currentPath = '') => {
    return Object.keys(tree).sort().map(key => {
      const node = tree[key];
      const fullPath = currentPath ? `${currentPath}/${key}` : key;
      
      if (node.type === 'folder') {
        const isExpanded = expandedFolders[fullPath];
        return (
          <div key={fullPath}>
            <div 
              className="file-tree-folder"
              onClick={() => toggleFolder(fullPath)}
            >
              <span className="folder-icon">{isExpanded ? '📂' : '📁'}</span>
              <span className="folder-name">{key}</span>
              <span className="folder-toggle">{isExpanded ? '▼' : '▶'}</span>
            </div>
            {isExpanded && (
              <div className="folder-content">
                {renderFileTree(node.children, fullPath)}
              </div>
            )}
          </div>
        );
      } else {
        return (
          <div 
            key={node.path}
            className={`file-tree-item ${activeFile === node.path ? 'active' : ''}`}
            onClick={() => setActiveFile(node.path)}
          >
            <span className="file-icon">{getFileIcon(node.path)}</span>
            <span className="file-name">{key}</span>
            <span className="file-lines">+{getLineCount(files[node.path])}</span>
            {Object.keys(files).length > 1 && (
              <button 
                className="file-delete-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  if (window.confirm(`Delete ${node.path}?`)) {
                    deleteFile(node.path);
                  }
                }}
              >
                ×
              </button>
            )}
          </div>
        );
      }
    });
  };

  return (
    <div className="v0-advanced">
      {/* Top Bar */}
      <div className="top-bar">
        <div className="top-bar-left">
          <div className="logo">Gradientflo</div>
          <div className="project-info">
            <button className="view-project-btn">View Project</button>
          </div>
        </div>
        <div className="top-bar-right">
          <button className="icon-btn" title="Refer">
            <span>🎁</span> Refer
          </button>
          <button className="icon-btn" title="Settings">⚙️</button>
          <button className="icon-btn" title="GitHub">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
              <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>
            </svg>
          </button>
          <button className="share-btn">Share</button>
          <button className="publish-btn">Publish</button>
          <div className="avatar"></div>
        </div>
      </div>

      {/* Main Layout */}
      <div className="main-container">
        {/* Left Sidebar - Chat */}
        {showChat && (
          <div className="chat-sidebar">
            <div className="chat-header">
              <button className="tab active">
                💬 Chat
              </button>
            </div>

            <div className="chat-content">
              <div className="feature-list">
                <h3>✨ Google ADK Powered Features:</h3>
                <ul>
                  <li>🧠 Multi-Agent System (Planning → Generate → Review)</li>
                  <li>💾 Session Management & Continuity</li>
                  <li>🔄 Automatic Error Recovery</li>
                  <li>📝 Monaco Editor with Hot Reload</li>
                  <li>👁️ Live Preview & File Management</li>
                </ul>
                {currentPhase && isGenerating && (
                  <div className="phase-indicator">
                    <h4>🔄 Current Phase:</h4>
                    <div className={`phase-badge phase-${currentPhase}`}>
                      {currentPhase === 'initializing' && '🚀 Initializing...'}
                      {currentPhase === 'planning' && '📋 Planning Architecture...'}
                      {currentPhase === 'generating' && '💻 Generating Code...'}
                      {currentPhase === 'reviewing' && '✅ Reviewing & Validating...'}
                    </div>
                  </div>
                )}
                {sessionId && !isGenerating && (
                  <div className="session-info">
                    <small>🔐 Session: {sessionId.substring(0, 12)}...</small>
                    <button 
                      className="clear-session-btn"
                      onClick={() => {
                        setSessionId(null);
                        setGenerationLog(prev => [...prev, '🗑️ Session cleared']);
                      }}
                      title="Start new session"
                    >
                      New Session
                    </button>
                  </div>
                )}
              </div>

              <div className="prompt-section">
                <label>Generate Code</label>
                {error && (
                  <div className="error-banner">
                    <span className="error-icon">⚠️</span>
                    <span className="error-text">{error}</span>
                    <button className="error-close" onClick={clearError}>×</button>
                  </div>
                )}
                {isGenerating && (
                  <div className="loading-banner">
                    <div className="loading-spinner"></div>
                    <div className="loading-content">
                      <span className="loading-text">AI is generating your code...</span>
                      <span className="loading-subtext">This may take a few seconds</span>
                    </div>
                  </div>
                )}
                <textarea
                  value={prompt}
                  onChange={(e) => {
                    setPrompt(e.target.value);
                    if (error) setError(null);
                  }}
                  placeholder="Describe what you want to build..."
                  rows={4}
                  disabled={isGenerating}
                />
                <div className="button-group">
                  <button 
                    onClick={generateCode}
                    disabled={isGenerating || !prompt.trim()}
                    className="generate-btn"
                  >
                    {isGenerating ? (
                      <>
                        <span className="btn-spinner"></span>
                        <span>Generating...</span>
                      </>
                    ) : (
                      <>
                        <span>✨ Generate</span>
                      </>
                    )}
                  </button>
                  {error && !isGenerating && (
                    <button 
                      onClick={retryGeneration}
                      className="retry-btn"
                      title="Retry generation"
                    >
                      🔄 Retry
                    </button>
                  )}
                </div>
              </div>

              {runtimeErrors.length > 0 && (
                <div className="error-fix-section">
                  <h4>⚠️ Errors Detected ({runtimeErrors.length})</h4>
                  <div className="error-list">
                    {runtimeErrors.map((err, idx) => (
                      <div key={idx} className="error-item">
                        <span className="error-item-icon">❌</span>
                        <div className="error-item-content">
                          <span className="error-item-message">{err.message}</span>
                          {err.path && <span className="error-item-path">in {err.path}</span>}
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="error-actions">
                    <button 
                      onClick={fixErrors}
                      disabled={isFixing}
                      className="fix-btn"
                    >
                      {isFixing ? (
                        <>
                          <span className="btn-spinner"></span>
                          <span>Fixing...</span>
                        </>
                      ) : (
                        <>
                          <span>🔧 Auto-Fix Errors</span>
                        </>
                      )}
                    </button>
                    <button 
                      onClick={clearRuntimeErrors}
                      className="clear-errors-btn"
                      disabled={isFixing}
                    >
                      Clear
                    </button>
                  </div>
                </div>
              )}

              {generationLog.length > 0 && (
                <div className="activity-section">
                  <h4>Activity Log</h4>
                  <div className="log-items">
                    {generationLog.map((log, idx) => (
                      <div key={idx} className="log-entry">{log}</div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="chat-footer">
              <div className="footer-left">
                {connectionStatus === 'connected' && <span className="status-connected">🟢 Connected</span>}
                {connectionStatus === 'disconnected' && <span className="status-disconnected">🔴 Disconnected</span>}
                {connectionStatus === 'checking' && <span className="status-checking">🟡 Checking...</span>}
                {backendError && connectionStatus === 'disconnected' && (
                  <span className="backend-error" title={backendError}>
                    ({backendError})
                  </span>
                )}
              </div>
              <span>⏱️ Ready</span>
            </div>
          </div>
        )}

        {/* Right Side - Editor/Preview */}
        <div className="editor-preview-container">
          {/* View Mode Toggle */}
          <div className="view-toggle-bar">
            <div className="toggle-buttons">
              <button 
                className="toggle-btn"
                onClick={() => setShowChat(!showChat)}
                title="Toggle Chat"
              >
                ←
              </button>
              <button 
                className={`toggle-btn ${viewMode === 'preview' ? 'active' : ''}`}
                onClick={() => setViewMode('preview')}
                title="Preview"
              >
                👁️
              </button>
              <button 
                className={`toggle-btn ${viewMode === 'code' ? 'active' : ''}`}
                onClick={() => setViewMode('code')}
                title="Code"
              >
                &lt;/&gt;
              </button>
            </div>
            <div className="editor-actions">
              <button className="icon-btn-small" title="Fullscreen">⛶</button>
              <button className="icon-btn-small" title="More">⋯</button>
            </div>
          </div>

          <div className="workspace-content">
            {viewMode === 'code' ? (
              <div className="code-view">
                {/* File Tree */}
                <div className="file-tree-panel">
                  <div className="file-tree-header">
                    <button className="tree-toggle">▼</button>
                    <span>app</span>
                  </div>
                  <div className="file-tree-content">
                    {renderFileTree(buildFileTree(Object.keys(files)))}
                    <button className="add-file-btn" onClick={addNewFile}>
                      + New File
                    </button>
                  </div>
                </div>

                {/* Editor */}
                <div className="editor-panel">
                  <div className="editor-tabs">
                    <div className="tab active">
                      <span>{getFileIcon(activeFile)}</span>
                      <span>{activeFile}</span>
                    </div>
                    <div className="tab-actions">
                      <button className="icon-btn-small" title="Copy">📋</button>
                      <button className="icon-btn-small" title="Download">⬇</button>
                    </div>
                  </div>
                  <SandpackProvider
                    template="react"
                    files={files}
                    theme="dark"
                    options={{ activeFile }}
                    customSetup={{ environment: "create-react-app" }}
                  >
                    <div className="monaco-wrapper">
                      <MonacoEditor
                        files={files}
                        activeFile={activeFile}
                        onFileChange={handleFileChange}
                        onErrorDetected={handleRuntimeError}
                      />
                    </div>
                  </SandpackProvider>
                </div>
              </div>
            ) : (
              <div className="preview-view">
                <SandpackProvider
                  template="react"
                  files={files}
                  theme="dark"
                  options={{ activeFile }}
                  customSetup={{ environment: "create-react-app" }}
                >
                  <PreviewErrorMonitor onErrorDetected={handleRuntimeError} />
                  <div className="preview-wrapper">
                    <SandpackPreview
                      showOpenInCodeSandbox={false}
                      showRefreshButton={true}
                    />
                  </div>
                </SandpackProvider>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default V0CloneAdvanced;
