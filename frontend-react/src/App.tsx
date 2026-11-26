import React, { useState, useRef, useCallback, useMemo, useEffect } from 'react';
import './index.css';
import Toolbar from './Toolbar';
import InputSection from './InputSection';
import './AppLayout.css';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Editor from './components/Editor';
import ChatPanel from './components/ChatPanel';
import OutputPanel from './components/OutputPanel';
import ToastProvider from './components/ToastProvider';
import toast from 'react-hot-toast';
import { v4 as uuidv4 } from 'uuid';
import { motion, AnimatePresence } from 'framer-motion';
import Terminal from './components/Terminal';

const DEFAULT_CODE: { [key: string]: string } = {
  python: '# Write your Python code here\ndef hello_world():\n    print("Hello, World!")\n\nhello_world()',
  javascript: '// Write your JavaScript code here\nfunction helloWorld() {\n    console.log("Hello, World!");\n}\n\nhelloWorld();',
  java: 'public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello, World!");\n    }\n}',
  cpp: '#include <iostream>\n\nint main() {\n    std::cout << "Hello, World!" << std::endl;\n    return 0;\n}'
};

interface OpenFile {
  name: string;
  content: string;
}

// --- Custom hooks for file management, undo/redo, and chat logic ---
function useFileTabs(initialFiles: OpenFile[]) {
  const [openFiles, setOpenFiles] = useState<OpenFile[]>(initialFiles);
  const [activeFileIdx, setActiveFileIdx] = useState<number>(0);
  const [fileName, setFileName] = useState<string>(initialFiles[0]?.name || 'code.py');

  const code = useMemo(() => openFiles[activeFileIdx]?.content || '', [openFiles, activeFileIdx]);
  const setCode = useCallback((newCode: string) => {
    setOpenFiles((files: OpenFile[]) => files.map((f: OpenFile, i: number) => i === activeFileIdx ? { ...f, content: newCode } : f));
  }, [activeFileIdx]);

  const handleTabClick = useCallback((idx: number) => {
    setActiveFileIdx(idx);
    setFileName(openFiles[idx]?.name || 'code.py');
  }, [openFiles]);

  const handleTabClose = useCallback(
    (idx: number, e: React.MouseEvent<any, MouseEvent>): void => {
      e.stopPropagation();
      setOpenFiles((files: OpenFile[]) => {
        const newFiles = files.filter((_, i: number) => i !== idx);
        if (activeFileIdx >= newFiles.length) setActiveFileIdx(Math.max(0, newFiles.length - 1));
        return newFiles.length ? newFiles : [{ name: 'code.py', content: '' }];
      });
    },
    [activeFileIdx]
  );

  return { openFiles, setOpenFiles, activeFileIdx, setActiveFileIdx, fileName, setFileName, code, setCode, handleTabClick, handleTabClose };
}

function useUndoRedo(initialCode: string) {
  const [undoStack, setUndoStack] = useState<string[]>([initialCode]);
  const [redoStack, setRedoStack] = useState<string[]>([]);
  const canUndo = useMemo(() => undoStack.length > 1, [undoStack]);
  const canRedo = useMemo(() => redoStack.length > 0, [redoStack]);

  const handleUndo = useCallback((setCode: (code: string) => void) => {
    if (undoStack.length > 1) {
      setRedoStack((prev: string[]) => [undoStack[undoStack.length - 1], ...prev]);
      const newUndo = undoStack.slice(0, -1);
      setUndoStack(newUndo);
      setCode(newUndo[newUndo.length - 1]);
    }
  }, [undoStack]);

  const handleRedo = useCallback((setCode: (code: string) => void) => {
    if (redoStack.length > 0) {
      const [redoCode, ...rest] = redoStack;
      setUndoStack((prev: string[]) => [...prev, redoCode]);
      setCode(redoCode);
      setRedoStack(rest);
    }
  }, [redoStack]);

  const handleCodeChange = useCallback((value: string | undefined, setCode: (code: string) => void) => {
    setCode(value || '');
    setUndoStack((prev: string[]) => [...prev, value || '']);
    setRedoStack([]);
  }, []);

  return { undoStack, redoStack, canUndo, canRedo, handleUndo, handleRedo, handleCodeChange, setUndoStack, setRedoStack };
}

function useChat() {
  const [chatMessages, setChatMessages] = useState<{ id: string; role: 'user' | 'ai'; content: string }[]>([]);
  const [chatInput, setChatInput] = useState<string>('');
  const [chatLoading, setChatLoading] = useState<boolean>(false);
  const [chatExpanded, setChatExpanded] = useState<boolean>(false);
  return { chatMessages, setChatMessages, chatInput, setChatInput, chatLoading, setChatLoading, chatExpanded, setChatExpanded };
}

const App: React.FC = () => {
  // --- File Tabs ---
  const {
    openFiles, setOpenFiles, activeFileIdx, setActiveFileIdx, fileName, setFileName, code, setCode, handleTabClick, handleTabClose
  } = useFileTabs([{ name: 'code.py', content: DEFAULT_CODE.python }]);
  // --- Undo/Redo ---
  const {
    undoStack, redoStack, canUndo, canRedo, handleUndo, handleRedo, handleCodeChange, setUndoStack, setRedoStack
  } = useUndoRedo(DEFAULT_CODE.python);
  // --- Chat ---
  const {
    chatMessages, setChatMessages, chatInput, setChatInput, chatLoading, setChatLoading, chatExpanded, setChatExpanded
  } = useChat();
  // --- Other State ---
  const [darkMode, setDarkMode] = useState(true);
  const [language, setLanguage] = useState('python');
  useEffect(() => {
    document.documentElement.classList.toggle('theme-light', !darkMode);
  }, [darkMode]);
  const [showInput, setShowInput] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [output, setOutput] = useState('');
  const [errors, setErrors] = useState('');
  const [suggestions, setSuggestions] = useState('');
  const [activeTab, setActiveTab] = useState('output');
  const [loading, setLoading] = useState(false);
  const [datasetPreview, setDatasetPreview] = useState('');
  const [runOutput, setRunOutput] = useState('');
  const [runLoading, setRunLoading] = useState(false);
  const fileInputRef = useRef(null);
  const datasetInputRef = useRef(null);
  const downloadAnchorRef = useRef(null);

  // --- Memoized Handlers ---
  const getLanguageFromFileName = useCallback((name: string): string => {
    const ext = name.split('.').pop();
    switch (ext) {
      case 'py': return 'python';
      case 'js': return 'javascript';
      case 'java': return 'java';
      case 'cpp': return 'cpp';
      default: return 'python';
    }
  }, []);

  const handleLanguageChange = useCallback((e: React.ChangeEvent<HTMLSelectElement>) => {
    const lang = e.target.value;
    setCode(DEFAULT_CODE[lang]);
    setUndoStack([DEFAULT_CODE[lang]]);
    setRedoStack([]);
    setLanguage(lang);
  }, [setCode, setUndoStack, setRedoStack]);

  const handleAction = useCallback(async (action: string) => {
    setLoading(true);
    setOutput('');
    setErrors('');
    setSuggestions('');
    setRunOutput('');
    setActiveTab('output');
    if (action === 'execute' && language !== 'python') {
      setRunOutput('Execution is only supported for Python. Switch the language to Python to run code.');
      setLoading(false);
      return;
    }
    try {
      // Always use Python for execution
      const langToSend = language;
      const response = await fetch('/api/code', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code,
          language: langToSend,
          action,
          inputs: showInput ? inputValue.split('\n').filter(line => line.trim()) : []
        })
      });
      const data = await response.json();
      if (!response.ok || data.error) {
        const message = Array.isArray(data.error) ? data.error.join('\n') : (data.error || data.detail || `Request failed (${response.status})`);
        setErrors(String(message));
        setActiveTab('errors');
        if (action === 'execute') setRunOutput(String(message));
      } else if (action === 'execute' && data.execution_result) {
        const { stdout = '', stderr = '' } = data.execution_result;
        // the backend copies known tracebacks into stdout, so do not print them twice
        setRunOutput(stderr && !stdout.includes(stderr) ? `${stdout}${stdout ? '\n' : ''}${stderr}` : stdout || stderr || '[No output]');
      } else {
        let outputText = '';
        if (data.explanation) outputText += `### Explanation\n\n${data.explanation}\n`;
        if (data.processed_code) outputText += `### Processed Code\n\n${data.processed_code}\n`;
        if (data.optimized_code) outputText += `### Optimized Code\n\n${data.optimized_code}\n`;
        if (data.fixed_code) outputText += `### Fixed Code\n\n${data.fixed_code}\n`;
        if (data.hints && Array.isArray(data.hints)) outputText += `### Hints\n\n${data.hints.join('\n')}\n`;
        if (data.suggestions && Array.isArray(data.suggestions)) outputText += `### Suggestions\n\n${data.suggestions.join('\n')}\n`;
        if (data.warnings && Array.isArray(data.warnings)) outputText += `### Warnings\n\n${data.warnings.join('\n')}\n`;
        if (data.errors && Array.isArray(data.errors)) outputText += `### Errors\n\n${data.errors.join('\n')}\n`;
        setOutput(outputText.trim() || '*No output.*');
        let errorText = '';
        if (data.errors && Array.isArray(data.errors)) errorText += data.errors.join('\n');
        if (data.execution_result?.stderr) errorText += (errorText ? '\n' : '') + data.execution_result.stderr;
        setErrors(errorText.trim());
        let suggestionText = '';
        if (data.suggestions && Array.isArray(data.suggestions)) suggestionText += data.suggestions.join('\n');
        if (data.hints && Array.isArray(data.hints)) suggestionText += (suggestionText ? '\n' : '') + data.hints.join('\n');
        setSuggestions(suggestionText.trim());
        if (errorText) setActiveTab('errors');
        else if (suggestionText) setActiveTab('suggestions');
        else setActiveTab('output');
      }
    } catch (err: any) {
      setErrors('Error: ' + (err.message || 'Unknown error'));
      setActiveTab('errors');
    } finally {
      setLoading(false);
    }
  }, [code, showInput, inputValue, language]);

  const extractProcessedCode = useCallback(() => {
    const match = output.match(/### Processed Code\n\n([\s\S]*?)(?=\n###|$)/);
    return match ? match[1].trim() : '';
  }, [output]);

  const handleApplyOptimized = useCallback(() => {
    const processed = extractProcessedCode();
    if (processed) {
      setCode(processed);
      setUndoStack(prev => [...prev, processed]);
      setRedoStack([]);
    } else {
      setRunOutput('No optimized code found in output.');
    }
  }, [extractProcessedCode, setCode, setUndoStack, setRedoStack]);

  const handleApplyFixed = useCallback(() => {
    const processed = extractProcessedCode();
    if (processed) {
      setCode(processed);
      setUndoStack(prev => [...prev, processed]);
      setRedoStack([]);
    } else {
      setRunOutput('No fixed code found in output.');
    }
  }, [extractProcessedCode, setCode, setUndoStack, setRedoStack]);

  const handleOpenFile = useCallback(async (e: React.ChangeEvent<HTMLInputElement> | FileList) => {
    const files = e instanceof FileList ? e : (e as React.ChangeEvent<HTMLInputElement>).target.files;
    if (files && files[0]) {
      const file = files[0];
      const reader = new FileReader();
      reader.onload = (evt) => {
        const content = typeof evt.target?.result === 'string' ? evt.target.result : '';
        setOpenFiles((prev: OpenFile[]) => [...prev, { name: file.name, content }]);
        setActiveFileIdx(openFiles.length);
        setFileName(file.name);
        setLanguage(getLanguageFromFileName(file.name));
      };
      reader.readAsText(file);
    }
  }, [setOpenFiles, setActiveFileIdx, openFiles.length, setFileName, setLanguage, getLanguageFromFileName]);

  const handleSaveFile = useCallback(() => {
    const blob = new Blob([code], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    if (downloadAnchorRef.current) {
      (downloadAnchorRef.current as HTMLAnchorElement).href = url;
      (downloadAnchorRef.current as HTMLAnchorElement).download = fileName || openFiles[activeFileIdx]?.name || 'code.py';
      (downloadAnchorRef.current as HTMLAnchorElement).click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    }
  }, [code, fileName, openFiles, activeFileIdx]);

  const handleOpenDataset = useCallback(async (e: React.ChangeEvent<HTMLInputElement> | FileList) => {
    const files = e instanceof FileList ? e : (e as React.ChangeEvent<HTMLInputElement>).target.files;
    if (files && files[0]) {
      const file = files[0];
      const reader = new FileReader();
      reader.onload = (evt) => {
        const content = typeof evt.target?.result === 'string' ? evt.target.result : '';
        setRunOutput(`Dataset Preview (${file.name}):\n\n${content.slice(0, 1000)}`);
      };
      reader.readAsText(file);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    const files = e.dataTransfer.files;
    if (files.length) {
      const file = files[0];
      if (file.name.match(/\.(py|js|java|cpp|txt|md)$/i)) {
        handleOpenFile(files);
      } else if (file.name.match(/\.(csv|xlsx|json|txt)$/i)) {
        handleOpenDataset(files);
      }
    }
  }, [handleOpenFile, handleOpenDataset]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
  }, []);

  const handleToggleTheme = useCallback(() => setDarkMode((d) => !d), []);
  const handleToggleChatWidth = useCallback(() => setChatExpanded(e => !e), [setChatExpanded]);

  // --- Chat/AI logic ---
  const sendPromptToAI = useCallback(async (prompt: string) => {
    setChatLoading(true);
    const userMsg = { id: uuidv4(), role: 'user' as 'user', content: prompt };
    setChatMessages((msgs) => [...msgs, userMsg]);
    setChatInput('');
    const toastId = toast.loading('Generating...');
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: prompt, code })
      });
      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.error || data.detail || `Chat failed (${response.status})`);
      }
      if (!response.body) throw new Error('No response body');
      let aiMsg = { id: uuidv4(), role: 'ai' as 'ai', content: '' };
      setChatMessages((msgs) => [...msgs, aiMsg]);
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let done = false;
      while (!done) {
        const { value, done: doneReading } = await reader.read();
        done = doneReading;
        if (value) {
          aiMsg = { ...aiMsg, content: aiMsg.content + decoder.decode(value, { stream: true }) };
          setChatMessages((msgs) => msgs.map((m) => m.id === aiMsg.id ? aiMsg : m));
        }
      }
      toast.success('Done!', { id: toastId });
      setChatLoading(false);
    } catch (err: any) {
      toast.error(err.message || 'Failed!', { id: toastId });
      setChatMessages((msgs) => [...msgs, { id: uuidv4(), role: 'ai' as 'ai', content: `Error: ${err.message || 'chat failed'}` }]);
      setChatLoading(false);
    }
  }, [setChatLoading, setChatMessages, setChatInput, code]);

  const handleRun = useCallback(() => {
    if (code.trim()) handleAction('execute');
  }, [code, handleAction]);

  const handleReset = useCallback(() => {
    const fresh = DEFAULT_CODE[language];
    setCode(fresh);
    setUndoStack([fresh]);
    setRedoStack([]);
    setOutput('');
    setErrors('');
    setSuggestions('');
    setRunOutput('');
    setInputValue('');
    setActiveTab('output');
  }, [language, setCode, setUndoStack, setRedoStack]);

  const handleReport = useCallback(async () => {
    try {
      const res = await fetch('/api/cache/stats');
      const s = await res.json();
      const c = s.cache_summary || {};
      setRunOutput(
        ['FixLoop report', '--------------',
          `Cache entries: ${c.total_entries}`, `Cache hit ratio: ${c.hit_ratio}`, `Cache memory: ${c.memory_usage}`,
          `Last cache save: ${c.last_save}`, `Server uptime: ${c.uptime}`].join('\n')
      );
    } catch (err: any) {
      setRunOutput('Could not load report: ' + (err.message || 'unknown error'));
    }
  }, []);

  const handleFileUpload = useCallback((content: string, name: string) => {
    setCode(content);
    setLanguage(getLanguageFromFileName(name));
  }, [setCode, setLanguage, getLanguageFromFileName]);

  const handleDatasetUpload = useCallback((content: string, name: string) => {
    setDatasetPreview(content.slice(0, 1000));
    setRunOutput(`Dataset Preview (${name}):\n\n${content.slice(0, 1000)}`);
  }, []);

  const handleDownload = useCallback(() => {
    const blob = new Blob([code], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `code.${{ python: 'py', javascript: 'js', java: 'java', cpp: 'cpp' }[language] || 'txt'}`;
    document.body.appendChild(a);
    a.click();
    setTimeout(() => {
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }, 100);
  }, [code, language]);

  const handleTemplateClick = useCallback((template: string) => {
    setChatInput(template);
  }, [setChatInput]);

  // --- Render ---
  return (
    <div className={darkMode ? 'dark' : ''}>
      <div className="min-h-screen bg-background dark:bg-background text-foreground flex flex-col font-mono">
        <Header darkMode={darkMode} onToggleTheme={handleToggleTheme} />
        <main className="flex-1 flex flex-row gap-4 px-4 pb-4">
          <Sidebar
            onFileUpload={handleFileUpload}
            onDatasetUpload={handleDatasetUpload}
            onDownload={handleDownload}
            onTemplateClick={handleTemplateClick}
          />
          <div className="flex-1 flex flex-col gap-4 min-w-0">
            <Toolbar
              language={language}
              onLanguageChange={handleLanguageChange}
              onUndo={() => handleUndo(setCode)}
              onRedo={() => handleRedo(setCode)}
              canUndo={canUndo}
              canRedo={canRedo}
              showInput={showInput}
              setShowInput={setShowInput}
              onAnalyze={() => handleAction('analyze')}
              onOptimize={() => handleAction('optimize')}
              onHint={() => handleAction('hint')}
              onFix={() => handleAction('fix')}
              onExecute={handleRun}
              onReport={handleReport}
              onReset={handleReset}
              onApplyOptimized={handleApplyOptimized}
              onApplyFixed={handleApplyFixed}
            />
            {showInput && <InputSection value={inputValue} onChange={setInputValue} />}
            <Editor
              value={code}
              language={language}
              onChange={v => handleCodeChange(v, setCode)}
              onRun={handleRun}
            />
            <Terminal output={runOutput} />
            <AnimatePresence>
              <motion.div
                key="output-panel"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 10 }}
                transition={{ duration: 0.2 }}
              >
                <OutputPanel
                  originalCode={''}
                  aiCode={''}
                  aiMarkdown={output}
                  errors={errors}
                  suggestions={suggestions}
                  requestedTab={activeTab}
                />
              </motion.div>
            </AnimatePresence>
          </div>
          <ChatPanel
            messages={chatMessages}
            input={chatInput}
            onInputChange={setChatInput}
            onSend={() => chatInput.trim() && sendPromptToAI(chatInput)}
            loading={chatLoading}
            expanded={chatExpanded}
            onToggleExpand={handleToggleChatWidth}
          />
        </main>
        <ToastProvider />
      </div>
    </div>
  );
};

export default App;
