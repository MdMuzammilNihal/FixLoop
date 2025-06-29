import * as React from 'react';
const { useRef } = React;
import MonacoEditor from '@monaco-editor/react';
export const Editor = ({ value, language, onChange, onRun }) => {
    const editorRef = useRef(null);
    const handleEditorDidMount = (editor, monaco) => {
        editorRef.current = editor;
        editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => onRun());
    };
    return (React.createElement("div", { className: "flex-1 min-w-0 h-full bg-background rounded-2xl shadow-lg overflow-hidden flex flex-col" },
        React.createElement(MonacoEditor, { height: "80%", defaultLanguage: language, value: value, onChange: onChange, theme: "vs-dark", options: {
                fontSize: 14,
                minimap: { enabled: false },
                fontFamily: 'Fira Mono, Menlo, Monaco, Consolas, monospace',
                scrollBeyondLastLine: false,
                wordWrap: 'on',
            }, onMount: handleEditorDidMount })));
};
export default Editor;
