import React from 'react';
import MonacoEditor from '@monaco-editor/react';
const EditorContainer = ({ code, language, onChange }) => {
    return (React.createElement("div", { className: "editor-container mb-0", style: { flex: 1, minHeight: 200, maxHeight: '70vh' }, "aria-label": "Code Editor" },
        React.createElement(MonacoEditor, { height: "100%", width: "100%", value: code, language: language, theme: "vs-dark", options: {
                minimap: { enabled: false },
                fontSize: 16,
                automaticLayout: true,
                readOnly: false,
            }, onChange: onChange })));
};
export default EditorContainer;
