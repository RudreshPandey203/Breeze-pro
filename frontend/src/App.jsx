import { useState } from "react";
import Editor from '@monaco-editor/react';
import { Panel, PanelGroup, PanelResizeHandle } from "react-resizable-panels";
import { useSpeechRecognition } from "react-speech-recognition";
import { FiCopy, FiExternalLink, FiCode, FiLayout, FiUploadCloud, FiDownload } from "react-icons/fi";
import './index.css';

const CodeSandbox = () => {
  const [code, setCode] = useState('');
  const [projectDir, setProjectDir] = useState('');
  const [isDeploying, setIsDeploying] = useState(false);
  const [deploymentUrl, setDeploymentUrl] = useState('');
  const { transcript, resetTranscript } = useSpeechRecognition();
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async () => {
    try {
      setError('');
      const response = await fetch("http://localhost:8000/create-project", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: message || transcript })
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Project creation failed');

      setCode(data.code);
      setProjectDir(data.project_dir);
      resetTranscript();
    } catch (error) {
      setError(error.message);
    }
  };

  const handleDeploy = async () => {
    setIsDeploying(true);
    setError('');
    try {
      const response = await fetch('http://localhost:8000/deploy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, project_dir: projectDir })
      });

      const result = await response.json();
      if (!response.ok) throw new Error(result.detail || 'Deployment failed');

      setDeploymentUrl(result.deployment_url);
    } catch (error) {
      setError(error.message);
    } finally {
      setIsDeploying(false);
    }
  };

  return (
    <div className="h-screen flex flex-col bg-gradient-to-br from-gray-900 to-gray-800 text-white">
      <nav className="px-6 py-4 border-b border-gray-700 flex items-center justify-between">
        <h1 className="text-xl font-bold flex items-center gap-2">
          <FiCode className="text-blue-400" />
          CodeDeploy Studio
        </h1>
        
        {deploymentUrl && (
          <div className="flex items-center gap-3 bg-gray-800 px-4 py-2 rounded-lg">
            <a
              href={deploymentUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-blue-400 hover:text-blue-300 flex items-center gap-2"
            >
              <FiExternalLink />
              <span className="max-w-[200px] truncate">{deploymentUrl}</span>
            </a>
            <button
              onClick={() => navigator.clipboard.writeText(deploymentUrl)}
              className="text-gray-400 hover:text-white"
            >
              <FiCopy />
            </button>
          </div>
        )}
      </nav>

      <PanelGroup direction="horizontal" className="flex-1">
        <Panel defaultSize={50} minSize={30}>
          <div className="h-full flex flex-col">
            <div className="px-4 py-3 border-b border-gray-700 flex items-center justify-between">
              <h2 className="text-sm font-mono text-gray-400 flex items-center gap-2">
                <FiCode className="text-green-400" />
                EDITOR
              </h2>
              <button
                onClick={handleDeploy}
                disabled={isDeploying}
                className="px-4 py-2 bg-gradient-to-r from-green-600 to-blue-600 rounded-md text-sm font-medium hover:opacity-90 disabled:opacity-50 transition-opacity flex items-center gap-2"
              >
                {isDeploying ? (
                  <>
                    <FiUploadCloud className="animate-pulse" />
                    Deploying...
                  </>
                ) : (
                  <>
                    <FiUploadCloud />
                    Deploy Now
                  </>
                )}
              </button>
            </div>
            
            <Editor
              height="100%"
              defaultLanguage="html"
              value={code}
              onChange={setCode}
              theme="vs-dark"
              options={{
                minimap: { enabled: false },
                fontSize: 14,
                lineNumbers: 'on',
                roundedSelection: false,
                scrollBeyondLastLine: false,
                automaticLayout: true
              }}
            />
          </div>
        </Panel>

        <PanelResizeHandle className="w-1 bg-gray-700 hover:bg-gray-600 transition-colors" />

        <Panel defaultSize={50} minSize={30}>
          <div className="h-full flex flex-col">
            <div className="px-4 py-3 border-b border-gray-700">
              <h2 className="text-sm font-mono text-gray-400 flex items-center gap-2">
                <FiLayout className="text-purple-400" />
                PREVIEW
              </h2>
            </div>
            
            <iframe 
              srcDoc={code}
              title="preview"
              className="w-full h-full bg-white"
              sandbox="allow-scripts allow-modals allow-same-origin"
            />
            
            <div className="border-t border-gray-700 p-4 bg-gray-800 flex items-center gap-4">
              <button
                onClick={() => setCode('')}
                className="px-4 py-2 bg-gray-700 rounded-md text-sm hover:bg-gray-600 transition-colors"
              >
                Reset Code
              </button>
              <a
                href={`http://localhost:8000/download-project/${projectDir}`}
                className="px-4 py-2 bg-purple-600 rounded-md text-sm hover:bg-purple-500 transition-colors flex items-center gap-2"
                download
              >
                <FiDownload />
                Download Project
              </a>
            </div>
          </div>
        </Panel>
      </PanelGroup>

      {!code && (
        <div className="absolute inset-0 bg-gray-900/80 backdrop-blur-sm flex items-center justify-center">
          <div className="max-w-2xl w-full p-8">
            <div className="bg-gray-800 rounded-xl p-8 border border-gray-700">
              <h2 className="text-2xl font-bold mb-4">Start New Project</h2>
              <textarea
                className="w-full h-32 p-4 mb-4 bg-gray-700/50 text-white placeholder-gray-400 rounded-lg focus:ring-2 focus:ring-blue-500 border-none"
                placeholder="Describe your project (e.g., 'Create a portfolio site with dark theme')"
                value={message || transcript}
                onChange={(e) => setMessage(e.target.value)}
              />
              
              {error && (
                <div className="mb-4 p-3 bg-red-900/50 text-red-300 rounded-lg">
                  {error}
                </div>
              )}

              <button
                onClick={handleSubmit}
                className="w-full py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
              >
                Generate Project Template
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CodeSandbox;
