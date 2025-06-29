import React from 'react';
import './Toolbar.css';

interface ToolbarProps {
  language: string;
  onLanguageChange: (e: React.ChangeEvent<HTMLSelectElement>) => void;
  onUndo: () => void;
  onRedo: () => void;
  canUndo: boolean;
  canRedo: boolean;
  showInput: boolean;
  setShowInput: (show: boolean) => void;
  onAnalyze: () => void;
  onOptimize: () => void;
  onHint: () => void;
  onFix: () => void;
  onExecute: () => void;
  onApplyOptimized?: () => void;
  onApplyFixed?: () => void;
}

const Toolbar: React.FC<ToolbarProps> = ({
  language,
  onLanguageChange,
  onUndo,
  onRedo,
  canUndo,
  canRedo,
  showInput,
  setShowInput,
  onAnalyze,
  onOptimize,
  onHint,
  onFix,
  onExecute,
  onApplyOptimized,
  onApplyFixed
}) => {
  return (
    <nav className="toolbar d-flex flex-wrap align-items-center mb-3 gap-2" aria-label="Toolbar">
      <div className="toolbar-btn-group">
        <div className="toolbar-btn" title="Analyze Code">
          <button className="btn btn-outline-primary" aria-label="Analyze code" onClick={onAnalyze}>
            <i className="bi bi-search" aria-hidden="true"></i>
          </button>
          <div className="toolbar-label">Analyze</div>
        </div>
        <div className="toolbar-btn" title="Optimize Code">
          <button className="btn btn-outline-success" aria-label="Optimize code" onClick={onOptimize}>
            <i className="bi bi-lightbulb" aria-hidden="true"></i>
          </button>
          <div className="toolbar-label">Optimize</div>
        </div>
        <div className="toolbar-btn" title="Apply Optimized Code">
          <button className="btn btn-outline-secondary" aria-label="Apply Optimized Code" onClick={onApplyOptimized}>
            <i className="bi bi-arrow-down-circle" aria-hidden="true"></i>
          </button>
          <div className="toolbar-label">Apply Opt.</div>
        </div>
        <div className="toolbar-btn" title="Get Hints">
          <button className="btn btn-outline-info" aria-label="Get hints" onClick={onHint}>
            <i className="bi bi-question-circle" aria-hidden="true"></i>
          </button>
          <div className="toolbar-label">Hint</div>
        </div>
        <div className="toolbar-btn" title="Fix Code">
          <button className="btn btn-outline-warning" aria-label="Fix code" onClick={onFix}>
            <i className="bi bi-tools" aria-hidden="true"></i>
          </button>
          <div className="toolbar-label">Fix</div>
        </div>
        <div className="toolbar-btn" title="Apply Fixed Code">
          <button className="btn btn-outline-secondary" aria-label="Apply Fixed Code" onClick={onApplyFixed}>
            <i className="bi bi-arrow-down-circle" aria-hidden="true"></i>
          </button>
          <div className="toolbar-label">Apply Fix</div>
        </div>
        <div className="toolbar-btn" title="Execute Code (Ctrl+Enter)">
          <button className="btn btn-primary" aria-label="Execute code" onClick={onExecute}>
            <i className="bi bi-play-fill" aria-hidden="true"></i>
          </button>
          <div className="toolbar-label">Execute</div>
        </div>
        <div className="toolbar-btn" title="Show Evaluation Report">
          <button className="btn btn-outline-secondary" aria-label="Show Evaluation Report">
            <i className="bi bi-file-earmark-text" aria-hidden="true"></i>
          </button>
          <div className="toolbar-label">Report</div>
        </div>
        <div className="toolbar-btn" title="Show/Hide Input Section">
          <label className="input-toggle ms-2">
            <input type="checkbox" checked={showInput} onChange={e => setShowInput(e.target.checked)} aria-label="Show input section" />
            <i className="bi bi-terminal" aria-hidden="true"></i>
          </label>
          <div className="toolbar-label">Input</div>
        </div>
        <div className="toolbar-btn" title="Undo (Ctrl+Z)">
          <button className="btn btn-sm btn-secondary ms-2" aria-label="Undo" onClick={onUndo} disabled={!canUndo}>
            <i className="bi bi-arrow-counterclockwise" aria-hidden="true"></i>
          </button>
          <div className="toolbar-label">Undo</div>
        </div>
        <div className="toolbar-btn" title="Redo (Ctrl+Y)">
          <button className="btn btn-sm btn-secondary" aria-label="Redo" onClick={onRedo} disabled={!canRedo}>
            <i className="bi bi-arrow-clockwise" aria-hidden="true"></i>
          </button>
          <div className="toolbar-label">Redo</div>
        </div>
        <div className="toolbar-btn" title="Reset Editor and State">
          <button className="btn btn-sm btn-danger ms-2" aria-label="Reset editor and state">
            <i className="bi bi-x-circle" aria-hidden="true"></i>
          </button>
          <div className="toolbar-label">Reset</div>
        </div>
      </div>
      <select className="form-select form-select-sm w-auto" title="Select language" aria-label="Select programming language" value={language} onChange={onLanguageChange} style={{marginLeft: 8}}>
        <option value="python">Python</option>
        <option value="javascript">JavaScript</option>
        <option value="java">Java</option>
        <option value="cpp">C++</option>
      </select>
    </nav>
  );
};

export default Toolbar; 