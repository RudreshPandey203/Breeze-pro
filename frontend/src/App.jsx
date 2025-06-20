import { useState, useEffect } from 'react';
import Editor from '@monaco-editor/react';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';
import { 
  FiCode, 
  FiLayout, 
  FiUploadCloud, 
  FiEdit,
  FiLoader,
  FiCheckCircle,
  FiAlertCircle
} from 'react-icons/fi';
import { useSpeechRecognition } from 'react-speech-recognition';
import './index.css';

const CodeSandbox = () => {
  const [code, setCode] = useState('');
  const [projectDir, setProjectDir] = useState('');
  const [isDeploying, setIsDeploying] = useState(false);
  const [deploymentUrl, setDeploymentUrl] = useState('');
  const [changeRequest, setChangeRequest] = useState('');
  const [status, setStatus] = useState({ type: '', message: '' });
  const { transcript, resetTranscript } = useSpeechRecognition();
  
  const showStatus = (type, duration = 3000) => {
    setStatus({ type, message: type.toUpperCase() });
    if (duration > 0) {
      setTimeout(() => setStatus({ type: '', message: '' }), duration);
    }
  };

  const handleCreateProject = async () => {
    try {
      showStatus('generating', 0);
      const response = await fetch("http://localhost:8000/create-project", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: changeRequest || transcript })
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Creation failed');

      setCode(data.code);
      setProjectDir(data.project_dir);
      resetTranscript();
      showStatus('success');
    } catch (error) {
      showStatus('error');
      console.error("Creation failed:", error);
    }
  };

  const handleDeploy = async () => {
    setIsDeploying(true);
    try {
      showStatus('deploying', 0);
      const response = await fetch('http://localhost:8000/deploy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, project_dir: projectDir })
      });

      const result = await response.json();
      if (!response.ok) throw new Error(result.detail || 'Deployment failed');

      setDeploymentUrl(result.deployment_url);
      showStatus('deployed');
    } catch (error) {
      showStatus('error');
      console.error('Deployment failed:', error);
    } finally {
      setIsDeploying(false);
    }
  };

  const handleChangeRequest = async () => {
    try {
      showStatus('updating', 0);
      const response = await fetch("http://localhost:8000/update-project", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          project_dir: projectDir,
          code,
          message: changeRequest
        })
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Update failed');

      setCode(data.code);
      setChangeRequest('');
      showStatus('updated');
    } catch (error) {
      showStatus('error');
      console.error("Update failed:", error);
    }
  };

  const StatusIndicator = () => (
    <div className={`fixed bottom-6 right-6 p-4 rounded-lg flex items-center gap-3
      ${status.type === 'error' ? 'bg-red-900/80' : 'bg-gray-800/80'}
      backdrop-blur-sm transition-all ${status.message ? 'opacity-100' : 'opacity-0'}`}
    >
      {status.type === 'generating' && <FiLoader className="animate-spin" />}
      {status.type === 'success' && <FiCheckCircle className="text-green-400" />}
      {status.type === 'error' && <FiAlertCircle className="text-red-400" />}
      {status.type === 'deploying' && <FiUploadCloud className="animate-pulse" />}
      <span className="text-sm">{status.message}</span>
    </div>
  );

  return (
    <div className="h-screen flex flex-col bg-gradient-to-br from-gray-900 to-gray-800 text-white">
      <StatusIndicator />
      
      <nav className="px-6 py-4 border-b border-gray-700 flex items-center justify-between">
        <h1 className="text-xl font-bold flex items-center gap-3">
          <FiCode className="text-blue-400" />
          Breeze <p className='text-sm italic'>pro</p>
        </h1>
        {deploymentUrl && (
          <div className="flex items-center gap-3 bg-gray-800/50 rounded-lg px-4 py-2">
            <a
              href={deploymentUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-blue-400 hover:text-blue-300 flex items-center gap-2"
            >
              <FiLayout />
              <span className="max-w-[200px] truncate">Live Preview</span>
            </a>
          </div>
        )}
      </nav>

      <PanelGroup direction="horizontal" className="flex-1">
        <Panel defaultSize={60} minSize={40}>
          <div className="h-full flex flex-col">
            <div className="px-4 py-3 border-b border-gray-700 flex items-center justify-between">
              <h2 className="text-sm font-mono text-gray-400 flex items-center gap-2">
                <FiCode className="text-green-400" />
                CODE EDITOR
              </h2>
              <div className="flex gap-3">
                <button
                  onClick={handleDeploy}
                  disabled={isDeploying}
                  className="px-4 py-2 bg-gradient-to-r from-green-600 to-blue-600 rounded-md text-sm flex items-center gap-2 hover:opacity-90 disabled:opacity-50"
                >
                  <FiUploadCloud />
                  {isDeploying ? 'Deploying...' : 'Deploy'}
                </button>
              </div>
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
                scrollBeyondLastLine: false,
                automaticLayout: true
              }}
            />
            
            <div className="border-t border-gray-700 p-4 bg-gray-800">
              <div className="flex flex-col gap-4">
                <textarea
                  className="w-full p-3 bg-gray-700 rounded-lg text-sm placeholder-gray-400"
                  placeholder="Request changes (e.g., 'Make buttons blue', 'Add mobile menu')"
                  value={changeRequest}
                  onChange={(e) => setChangeRequest(e.target.value)}
                  rows={status.type === 'updating' ? 1 : 2}
                />
                <button
                  onClick={handleChangeRequest}
                  disabled={status.type === 'updating'}
                  className="bg-blue-600 hover:bg-blue-700 px-6 py-2 rounded text-sm flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {status.type === 'updating' ? (
                    <>
                      <FiLoader className="animate-spin" />
                      Updating Code...
                    </>
                  ) : (
                    <>
                      <FiEdit />
                      Request Changes
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </Panel>

        <PanelResizeHandle className="w-1 bg-gray-700 hover:bg-gray-600 transition-colors" />

        <Panel defaultSize={40} minSize={30}>
          <div className="h-full flex flex-col">
            <div className="px-4 py-3 border-b border-gray-700">
              <h2 className="text-sm font-mono text-gray-400 flex items-center gap-2">
                <FiLayout className="text-purple-400" />
                LIVE PREVIEW
              </h2>
            </div>
            
            <iframe 
              srcDoc={code}
              title="preview"
              className="w-full h-full bg-white"
              sandbox="allow-scripts allow-modals allow-same-origin"
            />
          </div>
        </Panel>
      </PanelGroup>

      {!code && (
        <div className="absolute inset-0 bg-gray-900/90 backdrop-blur-sm flex items-center justify-center">
          <div className="max-w-2xl w-full p-6">
            <div className="bg-gray-800/90 rounded-xl p-8 border border-gray-700">
              <h2 className="text-3xl font-bold mb-6">Start New Project</h2>
              <div className="space-y-6">
                <textarea
                  className="w-full h-32 p-4 bg-gray-700/50 text-white placeholder-gray-400 rounded-lg focus:ring-2 focus:ring-blue-500 border-none"
                  placeholder="Describe your project (e.g., 'Create a portfolio with dark mode')"
                  value={changeRequest || transcript}
                  onChange={(e) => setChangeRequest(e.target.value)}
                />
                
                <button
                  onClick={handleCreateProject}
                  disabled={status.type === 'generating'}
                  className="w-full py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium flex items-center justify-center gap-2"
                >
                  {status.type === 'generating' ? (
                    <>
                      <FiLoader className="animate-spin" />
                      Generating Project...
                    </>
                  ) : (
                    'Create New Project'
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CodeSandbox;
