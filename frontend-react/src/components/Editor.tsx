import * as React from 'react';
const { useRef } = React;
import MonacoEditor, { type OnMount } from '@monaco-editor/react';
import { Play } from 'lucide-react';
import { Tooltip } from 'react-tooltip';

interface EditorProps {
  value: string;
  language: string;
  onChange: (value: string | undefined) => void;
  onRun: () => void;
}

export const Editor: React.FC<EditorProps> = ({ value, language, onChange, onRun }) => {
  const editorRef = useRef<any>(null);

  const handleEditorDidMount: OnMount = (editor, monaco) => {
    editorRef.current = editor;
    editor.addCommand(
      monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter,
      () => onRun()
    );
  };

  return (
    <div className="flex-1 min-w-0 h-full bg-background rounded-2xl shadow-lg overflow-hidden flex flex-col">
      <MonacoEditor
        height="80%"
        defaultLanguage={language}
        value={value}
        onChange={onChange}
        theme="vs-dark"
        options={{
          fontSize: 14,
          minimap: { enabled: false },
          fontFamily: 'Fira Mono, Menlo, Monaco, Consolas, monospace',
          scrollBeyondLastLine: false,
          wordWrap: 'on',
        }}
        onMount={handleEditorDidMount}
      />
    </div>
  );
};

export default Editor; 