import * as React from 'react';
const { useRef, useState } = React;
import { Upload, Download, FileText, Database, List } from 'lucide-react';
import { Tooltip } from 'react-tooltip';
import PythonTerminal from './PythonTerminal';

interface SidebarProps {
  onFileUpload: (content: string, name: string) => void;
  onDatasetUpload: (content: string, name: string) => void;
  onDownload: () => void;
  onTemplateClick: (template: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ onFileUpload, onDatasetUpload, onDownload, onTemplateClick }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const datasetInputRef = useRef<HTMLInputElement>(null);
  const [showTerminal, setShowTerminal] = useState(false);

  const handleFileUpload = () => fileInputRef.current?.click();
  const handleDatasetUpload = () => datasetInputRef.current?.click();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = evt => onFileUpload(evt.target?.result as string, file.name);
      reader.readAsText(file);
    }
  };
  const handleDatasetChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = evt => onDatasetUpload(evt.target?.result as string, file.name);
      reader.readAsText(file);
    }
  };

  return (
    <aside className="h-full w-64 bg-background dark:bg-nord1 text-foreground flex flex-col p-4 gap-4 shadow-lg rounded-2xl transition-all">
      <div className="text-xl font-bold mb-4">Files</div>
      <div className="flex flex-col gap-4">
        <button
          className="flex items-center gap-2 p-2 rounded-xl hover:bg-nord2 transition-colors"
          onClick={handleFileUpload}
          data-tooltip-id="file-upload-tip"
          data-tooltip-content="Upload Code File"
        >
          <Upload className="w-4 h-4" /> Upload Code
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept=".js,.ts,.py,.java,.cpp,.txt,.md"
          className="hidden"
          onChange={handleFileChange}
        />
        <button
          className="flex items-center gap-2 p-2 rounded-xl hover:bg-nord2 transition-colors"
          onClick={handleDatasetUpload}
          data-tooltip-id="dataset-upload-tip"
          data-tooltip-content="Upload Dataset"
        >
          <Database className="w-4 h-4" /> Upload Dataset
        </button>
        <input
          ref={datasetInputRef}
          type="file"
          accept=".csv,.json,.xlsx,.txt"
          className="hidden"
          onChange={handleDatasetChange}
        />
        <button
          className="flex items-center gap-2 p-2 rounded-xl hover:bg-nord2 transition-colors"
          onClick={onDownload}
          data-tooltip-id="file-download-tip"
          data-tooltip-content="Download Current Code"
        >
          <Download className="w-4 h-4" /> Download Code
        </button>
      </div>
      <div className="mt-8">
        <div className="text-lg font-semibold mb-2 flex items-center gap-2">
          <List className="w-4 h-4" /> Prompt Templates
        </div>
        <ul className="space-y-2">
          <li className="text-accent cursor-pointer hover:underline" onClick={() => onTemplateClick('Explain this code')}>Explain this code</li>
          <li className="text-accent cursor-pointer hover:underline" onClick={() => onTemplateClick('Find bugs')}>Find bugs</li>
          <li className="text-accent cursor-pointer hover:underline" onClick={() => onTemplateClick('Optimize for performance')}>Optimize for performance</li>
        </ul>
      </div>
      <button onClick={() => setShowTerminal((v) => !v)} style={{margin: '10px', padding: '8px', width: '90%'}}>Python Terminal</button>
      {showTerminal && <PythonTerminal />}
      <Tooltip id="file-upload-tip" />
      <Tooltip id="dataset-upload-tip" />
      <Tooltip id="file-download-tip" />
    </aside>
  );
};

export default Sidebar; 