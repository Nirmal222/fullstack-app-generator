import React, { useState, useEffect, useRef } from 'react';
import Editor from '@monaco-editor/react';
import { SandpackProvider, SandpackPreview, useSandpack } from '@codesandbox/sandpack-react';
import './V0CloneAdvanced.css';

// Custom Editor Component with Monaco
const MonacoEditor = ({ files, activeFile, onFileChange }) => {
  const { sandpack } = useSandpack();
  const editorRef = useRef(null);

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
    'src/App.js': `import React, { useState } from 'react';
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
    'src/App.css': `.app {
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
    'src/components/Button.jsx': `import React from 'react';
import './Button.css';

export default function Button({ children, onClick }) {
  return (
    <button className="custom-button" onClick={onClick}>
      {children}
    </button>
  );
}`,
    'src/components/Button.css': `.custom-button {
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
  
  const [activeFile, setActiveFile] = useState('src/App.js');
  const [expandedFolders, setExpandedFolders] = useState({ 'src': true, 'src/components': true });
  const [generationLog, setGenerationLog] = useState([]);
  const [viewMode, setViewMode] = useState('code'); // 'code' or 'preview'
  const [showChat, setShowChat] = useState(true);

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
      const parts = path.split('/');
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

  // Code generation
  const generateCode = async () => {
    if (!prompt.trim()) return;

    setIsGenerating(true);
    setGenerationLog([]);
    const newFiles = {};

    try {
      const response = await fetch('http://localhost:8000/api/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: prompt,
          framework: 'react',
          model: 'gpt-4'
        })
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      let currentFile = null;
      let currentContent = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6));

            switch (data.type) {
              case 'file_start':
                currentFile = data.file_path;
                currentContent = '';
                setGenerationLog(prev => [...prev, `📄 Creating ${data.file_path}...`]);
                break;

              case 'content':
                currentContent += data.content;
                newFiles[currentFile] = currentContent;
                setFiles({ ...newFiles });
                break;

              case 'file_end':
                setGenerationLog(prev => [...prev, `✅ Completed ${data.file_path}`]);
                if (Object.keys(newFiles).length === 1) {
                  setActiveFile(currentFile);
                }
                break;

              case 'complete':
                setGenerationLog(prev => [...prev, `🎉 ${data.metadata.message}`]);
                setIsGenerating(false);
                break;

              case 'error':
                setGenerationLog(prev => [...prev, `❌ Error: ${data.message}`]);
                setIsGenerating(false);
                break;
            }
          }
        }
      }
    } catch (error) {
      console.error('Generation error:', error);
      setGenerationLog(prev => [...prev, `❌ Connection error: ${error.message}`]);
      setIsGenerating(false);
    }
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
          <div className="logo">V0</div>
          <div className="project-info">
            <h1>Modern React App</h1>
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
                <h3>Current Features:</h3>
                <ul>
                  <li>✨ AI-powered code generation</li>
                  <li>📝 Monaco editor integration</li>
                  <li>👁️ Live preview with hot reload</li>
                  <li>📁 File tree management</li>
                  <li>🎨 Syntax highlighting</li>
                </ul>
              </div>

              <div className="prompt-section">
                <label>Generate Code</label>
                <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="Describe what you want to build..."
                  rows={4}
                  disabled={isGenerating}
                />
                <button 
                  onClick={generateCode}
                  disabled={isGenerating || !prompt.trim()}
                  className="generate-btn"
                >
                  {isGenerating ? '⏳ Generating...' : '✨ Generate'}
                </button>
              </div>

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
              <span>🔧 No issues found</span>
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
