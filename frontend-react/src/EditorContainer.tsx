import React from 'react';
import MonacoEditor from '@monaco-editor/react';

interface EditorContainerProps {
  code: string;
  language: string;
  onChange: (value: string | undefined) => void;
}

const EditorContainer: React.FC<EditorContainerProps> = ({ code, language, onChange }) => {
  return (
    <div className="editor-container mb-0" style={{flex: 1, minHeight: 200, maxHeight: '70vh'}} aria-label="Code Editor">
      <MonacoEditor
        height="100%"
        width="100%"
        value={code}
        language={language}
        theme="vs-dark"
        options={{
          minimap: { enabled: false },
          fontSize: 16,
          automaticLayout: true,
          readOnly: false,
        }}
        onChange={onChange}
      />
    </div>
  );
};

export default EditorContainer; 