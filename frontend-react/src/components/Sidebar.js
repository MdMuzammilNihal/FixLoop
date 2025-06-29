import * as React from 'react';
const { useRef, useState } = React;
import { Upload, Download, Database, List } from 'lucide-react';
import { Tooltip } from 'react-tooltip';
import PythonTerminal from './PythonTerminal';
export const Sidebar = ({ onFileUpload, onDatasetUpload, onDownload, onTemplateClick }) => {
    const fileInputRef = useRef(null);
    const datasetInputRef = useRef(null);
    const [showTerminal, setShowTerminal] = useState(false);
    const handleFileUpload = () => fileInputRef.current?.click();
    const handleDatasetUpload = () => datasetInputRef.current?.click();
    const handleFileChange = (e) => {
        const file = e.target.files?.[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = evt => onFileUpload(evt.target?.result, file.name);
            reader.readAsText(file);
        }
    };
    const handleDatasetChange = (e) => {
        const file = e.target.files?.[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = evt => onDatasetUpload(evt.target?.result, file.name);
            reader.readAsText(file);
        }
    };
    return (React.createElement("aside", { className: "h-full w-64 bg-background dark:bg-nord1 text-foreground flex flex-col p-4 gap-4 shadow-lg rounded-2xl transition-all" },
        React.createElement("div", { className: "text-xl font-bold mb-4" }, "Files"),
        React.createElement("div", { className: "flex flex-col gap-4" },
            React.createElement("button", { className: "flex items-center gap-2 p-2 rounded-xl hover:bg-nord2 transition-colors", onClick: handleFileUpload, "data-tooltip-id": "file-upload-tip", "data-tooltip-content": "Upload Code File" },
                React.createElement(Upload, { className: "w-4 h-4" }),
                " Upload Code"),
            React.createElement("input", { ref: fileInputRef, type: "file", accept: ".js,.ts,.py,.java,.cpp,.txt,.md", className: "hidden", onChange: handleFileChange }),
            React.createElement("button", { className: "flex items-center gap-2 p-2 rounded-xl hover:bg-nord2 transition-colors", onClick: handleDatasetUpload, "data-tooltip-id": "dataset-upload-tip", "data-tooltip-content": "Upload Dataset" },
                React.createElement(Database, { className: "w-4 h-4" }),
                " Upload Dataset"),
            React.createElement("input", { ref: datasetInputRef, type: "file", accept: ".csv,.json,.xlsx,.txt", className: "hidden", onChange: handleDatasetChange }),
            React.createElement("button", { className: "flex items-center gap-2 p-2 rounded-xl hover:bg-nord2 transition-colors", onClick: onDownload, "data-tooltip-id": "file-download-tip", "data-tooltip-content": "Download Current Code" },
                React.createElement(Download, { className: "w-4 h-4" }),
                " Download Code")),
        React.createElement("div", { className: "mt-8" },
            React.createElement("div", { className: "text-lg font-semibold mb-2 flex items-center gap-2" },
                React.createElement(List, { className: "w-4 h-4" }),
                " Prompt Templates"),
            React.createElement("ul", { className: "space-y-2" },
                React.createElement("li", { className: "text-accent cursor-pointer hover:underline", onClick: () => onTemplateClick('Explain this code') }, "Explain this code"),
                React.createElement("li", { className: "text-accent cursor-pointer hover:underline", onClick: () => onTemplateClick('Find bugs') }, "Find bugs"),
                React.createElement("li", { className: "text-accent cursor-pointer hover:underline", onClick: () => onTemplateClick('Optimize for performance') }, "Optimize for performance"))),
        React.createElement("button", { onClick: () => setShowTerminal((v) => !v), style: { margin: '10px', padding: '8px', width: '90%' } }, "Python Terminal"),
        showTerminal && React.createElement(PythonTerminal, null),
        React.createElement(Tooltip, { id: "file-upload-tip" }),
        React.createElement(Tooltip, { id: "dataset-upload-tip" }),
        React.createElement(Tooltip, { id: "file-download-tip" })));
};
export default Sidebar;
