import React, { useState, useRef, useCallback, useMemo } from 'react';
import './index.css';
import Toolbar from './Toolbar';
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
const DEFAULT_CODE = {
    python: '# Write your Python code here\ndef hello_world():\n    print("Hello, World!")\n\nhello_world()',
    javascript: '// Write your JavaScript code here\nfunction helloWorld() {\n    console.log("Hello, World!");\n}\n\nhelloWorld();',
    java: 'public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello, World!");\n    }\n}',
    cpp: '#include <iostream>\n\nint main() {\n    std::cout << "Hello, World!" << std::endl;\n    return 0;\n}'
};
// --- Custom hooks for file management, undo/redo, and chat logic ---
function useFileTabs(initialFiles) {
    const [openFiles, setOpenFiles] = useState(initialFiles);
    const [activeFileIdx, setActiveFileIdx] = useState(0);
    const [fileName, setFileName] = useState(initialFiles[0]?.name || 'code.py');
    const code = useMemo(() => openFiles[activeFileIdx]?.content || '', [openFiles, activeFileIdx]);
    const setCode = useCallback((newCode) => {
        setOpenFiles((files) => files.map((f, i) => i === activeFileIdx ? { ...f, content: newCode } : f));
    }, [activeFileIdx]);
    const handleTabClick = useCallback((idx) => {
        setActiveFileIdx(idx);
        setFileName(openFiles[idx]?.name || 'code.py');
    }, [openFiles]);
    const handleTabClose = useCallback((idx, e) => {
        e.stopPropagation();
        setOpenFiles((files) => {
            const newFiles = files.filter((_, i) => i !== idx);
            if (activeFileIdx >= newFiles.length)
                setActiveFileIdx(Math.max(0, newFiles.length - 1));
            return newFiles.length ? newFiles : [{ name: 'code.py', content: '' }];
        });
    }, [activeFileIdx]);
    return { openFiles, setOpenFiles, activeFileIdx, setActiveFileIdx, fileName, setFileName, code, setCode, handleTabClick, handleTabClose };
}
function useUndoRedo(initialCode) {
    const [undoStack, setUndoStack] = useState([initialCode]);
    const [redoStack, setRedoStack] = useState([]);
    const canUndo = useMemo(() => undoStack.length > 1, [undoStack]);
    const canRedo = useMemo(() => redoStack.length > 0, [redoStack]);
    const handleUndo = useCallback((setCode) => {
        if (undoStack.length > 1) {
            setRedoStack((prev) => [undoStack[undoStack.length - 1], ...prev]);
            const newUndo = undoStack.slice(0, -1);
            setUndoStack(newUndo);
            setCode(newUndo[newUndo.length - 1]);
        }
    }, [undoStack]);
    const handleRedo = useCallback((setCode) => {
        if (redoStack.length > 0) {
            const [redoCode, ...rest] = redoStack;
            setUndoStack((prev) => [...prev, redoCode]);
            setCode(redoCode);
            setRedoStack(rest);
        }
    }, [redoStack]);
    const handleCodeChange = useCallback((value, setCode) => {
        setCode(value || '');
        setUndoStack((prev) => [...prev, value || '']);
        setRedoStack([]);
    }, []);
    return { undoStack, redoStack, canUndo, canRedo, handleUndo, handleRedo, handleCodeChange, setUndoStack, setRedoStack };
}
function useChat() {
    const [chatMessages, setChatMessages] = useState([]);
    const [chatInput, setChatInput] = useState('');
    const [chatLoading, setChatLoading] = useState(false);
    const [chatExpanded, setChatExpanded] = useState(false);
    return { chatMessages, setChatMessages, chatInput, setChatInput, chatLoading, setChatLoading, chatExpanded, setChatExpanded };
}
const App = () => {
    // --- File Tabs ---
    const { openFiles, setOpenFiles, activeFileIdx, setActiveFileIdx, fileName, setFileName, code, setCode, handleTabClick, handleTabClose } = useFileTabs([{ name: 'code.py', content: DEFAULT_CODE.python }]);
    // --- Undo/Redo ---
    const { undoStack, redoStack, canUndo, canRedo, handleUndo, handleRedo, handleCodeChange, setUndoStack, setRedoStack } = useUndoRedo(DEFAULT_CODE.python);
    // --- Chat ---
    const { chatMessages, setChatMessages, chatInput, setChatInput, chatLoading, setChatLoading, chatExpanded, setChatExpanded } = useChat();
    // --- Other State ---
    const [darkMode, setDarkMode] = useState(true);
    const [language, setLanguage] = useState('typescript');
    const [showInput, setShowInput] = useState(false);
    const [inputValue, setInputValue] = useState('');
    const [output, setOutput] = useState('');
    const [errors, setErrors] = useState('');
    const [suggestions, setSuggestions] = useState('');
    const [activeTab, setActiveTab] = useState('output');
    const [loading, setLoading] = useState(false);
    const [datasetPreview, setDatasetPreview] = useState('');
    const [pyodide, setPyodide] = useState(null);
    const [runOutput, setRunOutput] = useState('');
    const [runLoading, setRunLoading] = useState(false);
    const fileInputRef = useRef(null);
    const datasetInputRef = useRef(null);
    const downloadAnchorRef = useRef(null);
    // --- Memoized Handlers ---
    const getLanguageFromFileName = useCallback((name) => {
        const ext = name.split('.').pop();
        switch (ext) {
            case 'py': return 'python';
            case 'js': return 'javascript';
            case 'java': return 'java';
            case 'cpp': return 'cpp';
            default: return 'python';
        }
    }, []);
    const handleLanguageChange = useCallback((e) => {
        const lang = e.target.value;
        setCode(DEFAULT_CODE[lang]);
        setUndoStack([DEFAULT_CODE[lang]]);
        setRedoStack([]);
        setLanguage(lang);
    }, [setCode, setUndoStack, setRedoStack]);
    const handleAction = useCallback(async (action) => {
        setLoading(true);
        setOutput('');
        setErrors('');
        setSuggestions('');
        setRunOutput('');
        setActiveTab('output');
        try {
            const extToLang = { py: 'python', js: 'javascript', java: 'java', cpp: 'cpp' };
            let fileExt = openFiles[activeFileIdx]?.name.split('.').pop();
            if (!fileExt)
                fileExt = 'py';
            const language = extToLang[fileExt] || 'python';
            const response = await fetch('/api/code', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    code,
                    language,
                    action,
                    inputs: showInput ? inputValue.split('\n').filter(line => line.trim()) : []
                })
            });
            const data = await response.json();
            let outputText = '';
            if (data.explanation)
                outputText += `### Explanation\n\n${data.explanation}\n`;
            if (data.processed_code)
                outputText += `### Processed Code\n\n${data.processed_code}\n`;
            if (data.optimized_code)
                outputText += `### Optimized Code\n\n${data.optimized_code}\n`;
            if (data.fixed_code)
                outputText += `### Fixed Code\n\n${data.fixed_code}\n`;
            if (data.hints && Array.isArray(data.hints))
                outputText += `### Hints\n\n${data.hints.join('\n')}\n`;
            if (data.suggestions && Array.isArray(data.suggestions))
                outputText += `### Suggestions\n\n${data.suggestions.join('\n')}\n`;
            if (data.warnings && Array.isArray(data.warnings))
                outputText += `### Warnings\n\n${data.warnings.join('\n')}\n`;
            if (data.errors && Array.isArray(data.errors))
                outputText += `### Errors\n\n${data.errors.join('\n')}\n`;
            setOutput(outputText.trim() || '*No output.*');
            let errorText = '';
            if (data.errors && Array.isArray(data.errors))
                errorText += data.errors.join('\n');
            if (data.execution_result?.stderr)
                errorText += (errorText ? '\n' : '') + data.execution_result.stderr;
            setErrors(errorText.trim());
            let suggestionText = '';
            if (data.suggestions && Array.isArray(data.suggestions))
                suggestionText += data.suggestions.join('\n');
            if (data.hints && Array.isArray(data.hints))
                suggestionText += (suggestionText ? '\n' : '') + data.hints.join('\n');
            setSuggestions(suggestionText.trim());
            if (errorText)
                setActiveTab('errors');
            else if (suggestionText)
                setActiveTab('suggestions');
            else
                setActiveTab('output');
        }
        catch (err) {
            setErrors('Error: ' + (err.message || 'Unknown error'));
            setActiveTab('errors');
        }
        finally {
            setLoading(false);
        }
    }, [openFiles, activeFileIdx, code, showInput, inputValue]);
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
        }
        else {
            setRunOutput('No optimized code found in output.');
        }
    }, [extractProcessedCode, setCode, setUndoStack, setRedoStack]);
    const handleApplyFixed = useCallback(() => {
        const processed = extractProcessedCode();
        if (processed) {
            setCode(processed);
            setUndoStack(prev => [...prev, processed]);
            setRedoStack([]);
        }
        else {
            setRunOutput('No fixed code found in output.');
        }
    }, [extractProcessedCode, setCode, setUndoStack, setRedoStack]);
    const handleOpenFile = useCallback(async (e) => {
        const files = e instanceof FileList ? e : e.target.files;
        if (files && files[0]) {
            const file = files[0];
            const reader = new FileReader();
            reader.onload = (evt) => {
                const content = typeof evt.target?.result === 'string' ? evt.target.result : '';
                setOpenFiles((prev) => [...prev, { name: file.name, content }]);
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
            downloadAnchorRef.current.href = url;
            downloadAnchorRef.current.download = fileName || openFiles[activeFileIdx]?.name || 'code.py';
            downloadAnchorRef.current.click();
            setTimeout(() => URL.revokeObjectURL(url), 1000);
        }
    }, [code, fileName, openFiles, activeFileIdx]);
    const handleOpenDataset = useCallback(async (e) => {
        const files = e instanceof FileList ? e : e.target.files;
        if (files && files[0]) {
            const file = files[0];
            const reader = new FileReader();
            reader.onload = (evt) => {
                const content = typeof evt.target?.result === 'string' ? evt.target.result : '';
                setOutput(content);
                setActiveTab('output');
            };
            reader.readAsText(file);
        }
    }, []);
    const handleDrop = useCallback((e) => {
        e.preventDefault();
        const files = e.dataTransfer.files;
        if (files.length) {
            const file = files[0];
            if (file.name.match(/\.(py|js|java|cpp|txt|md)$/i)) {
                handleOpenFile(files);
            }
            else if (file.name.match(/\.(csv|xlsx|json|txt)$/i)) {
                handleOpenDataset(files);
            }
        }
    }, [handleOpenFile, handleOpenDataset]);
    const handleDragOver = useCallback((e) => {
        e.preventDefault();
    }, []);
    const handleToggleTheme = useCallback(() => setDarkMode((d) => !d), []);
    const handleToggleChatWidth = useCallback(() => setChatExpanded(e => !e), [setChatExpanded]);
    // --- Chat/AI logic ---
    const sendPromptToAI = useCallback(async (prompt) => {
        setChatLoading(true);
        const userMsg = { id: uuidv4(), role: 'user', content: prompt };
        setChatMessages((msgs) => [...msgs, userMsg]);
        setChatInput('');
        const toastId = toast.loading('Generating...');
        try {
            const fullPrompt = `${prompt}\n\nHere is the code to analyze:\n\n${code}`;
            const response = await fetch('http://localhost:11434/api/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: fullPrompt, model: 'deepseek-coder-v2:16b', stream: true })
            });
            if (!response.body)
                throw new Error('No response body');
            let aiMsg = { id: uuidv4(), role: 'ai', content: '' };
            setChatMessages((msgs) => [...msgs, aiMsg]);
            const reader = response.body.getReader();
            let done = false;
            while (!done) {
                const { value, done: doneReading } = await reader.read();
                done = doneReading;
                if (value) {
                    const chunk = new TextDecoder().decode(value);
                    for (const line of chunk.split('\n')) {
                        if (!line.trim())
                            continue;
                        try {
                            const data = JSON.parse(line);
                            if (data.response) {
                                aiMsg = { ...aiMsg, content: aiMsg.content + data.response };
                                setChatMessages((msgs) => msgs.map((m) => m.id === aiMsg.id ? aiMsg : m));
                            }
                        }
                        catch (e) { }
                    }
                }
            }
            toast.success('Done!', { id: toastId });
            setChatLoading(false);
        }
        catch (err) {
            toast.error('Failed!', { id: toastId });
            setChatLoading(false);
        }
    }, [setChatLoading, setChatMessages, setChatInput, code]);
    const handleRun = useCallback(() => {
        if (code.trim()) {
            sendPromptToAI(code);
        }
    }, [code, sendPromptToAI]);
    const handleFileUpload = useCallback((content, name) => {
        setCode(content);
        setLanguage(getLanguageFromFileName(name));
    }, [setCode, setLanguage, getLanguageFromFileName]);
    const handleDatasetUpload = useCallback((content, name) => {
        setDatasetPreview(content.slice(0, 1000));
        setOutput(`Dataset Preview (${name}):\n\n${content.slice(0, 1000)}`);
        setActiveTab('output');
    }, []);
    const handleDownload = useCallback(() => {
        const blob = new Blob([code], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'code.txt';
        document.body.appendChild(a);
        a.click();
        setTimeout(() => {
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }, 100);
    }, [code]);
    const handleTemplateClick = useCallback((template) => {
        setChatInput(template);
    }, [setChatInput]);
    // Unified backend code execution handler
    const handleRunCode = useCallback(async () => {
        setRunOutput('');
        setRunLoading(true);
        try {
            const response = await fetch('/api/code', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    code,
                    language: 'python',
                    action: 'execute',
                }),
            });
            const data = await response.json();
            setRunOutput(
                (data.execution_result?.stdout || '') +
                (data.execution_result?.stderr ? '\n' + data.execution_result.stderr : '')
            );
        } catch (e) {
            setRunOutput('Error: ' + (e.message || String(e)));
        } finally {
            setRunLoading(false);
        }
    }, [code]);
    // --- Render ---
    return (
        <div>
            <h1 style={{color: 'white', background: 'red', zIndex: 9999}}>TEST - If you see this, React is rendering</h1>
            <div className={darkMode ? 'dark' : ''}>
                <div className="min-h-screen bg-background dark:bg-background text-foreground flex flex-col font-mono">
                    <Header darkMode={darkMode} onToggleTheme={handleToggleTheme} />
                    <main className="flex-1 flex flex-row gap-4 px-4 pb-4">
                        <Sidebar onFileUpload={handleFileUpload} onDatasetUpload={handleDatasetUpload} onDownload={handleDownload} onTemplateClick={handleTemplateClick} />
                        <div className="flex-1 flex flex-col gap-4 min-w-0">
                            <Toolbar language={language} onLanguageChange={handleLanguageChange} onUndo={() => handleUndo(setCode)} onRedo={() => handleRedo(setCode)} canUndo={canUndo} canRedo={canRedo} showInput={showInput} setShowInput={setShowInput} onAnalyze={() => handleAction('analyze')} onOptimize={() => handleAction('optimize')} onHint={() => handleAction('hint')} onFix={() => handleAction('fix')} onExecute={handleRunCode} onApplyOptimized={handleApplyOptimized} onApplyFixed={handleApplyFixed} />
                            <Editor value={code} language={language} onChange={v => handleCodeChange(v, setCode)} onRun={handleRunCode} />
                            <AnimatePresence>
                                <motion.div key="output-panel" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 10 }} transition={{ duration: 0.2 }}>
                                    <OutputPanel originalCode='' aiCode='' aiMarkdown={output} runOutput={runOutput} runLoading={runLoading} errors={errors} suggestions={suggestions} />
                                </motion.div>
                            </AnimatePresence>
                        </div>
                        <ChatPanel messages={chatMessages} input={chatInput} onInputChange={setChatInput} onSend={() => chatInput.trim() && sendPromptToAI(chatInput)} loading={chatLoading} expanded={chatExpanded} onToggleExpand={handleToggleChatWidth} />
                    </main>
                    <ToastProvider />
                </div>
            </div>
        </div>
    );
};
export default App;
