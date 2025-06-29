import React from 'react';
import DOMPurify from 'dompurify';
import { marked } from 'marked';

interface ResultsTabsProps {
  output: string;
  errors: string;
  suggestions: string;
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

const safeMarkdown = (md: string) => {
  // Use parseSync if available, else fallback to parse with type assertion
  if ((marked as any).parseSync) {
    return DOMPurify.sanitize((marked as any).parseSync(md));
  }
  return DOMPurify.sanitize(marked.parse(md) as string);
};

const ResultsTabs: React.FC<ResultsTabsProps> = React.memo(({ output, errors, suggestions, activeTab, setActiveTab }) => {
  return (
    <div className="card card-body mt-0" id="results-tabs" style={{flex: 1, minHeight: 120, maxHeight: '40vh', overflowY: 'auto', background: '#23283a', color: '#f8f8f2'}} aria-label="Results Tabs" aria-live="polite">
      <ul className="nav nav-tabs" id="resultsTab" role="tablist" aria-label="Results Tabs">
        <li className="nav-item" role="presentation">
          <button className={`nav-link${activeTab === 'output' ? ' active' : ''}`} id="output-tab" type="button" role="tab" aria-selected={activeTab === 'output'} aria-controls="output-panel" tabIndex={activeTab === 'output' ? 0 : -1} onClick={() => setActiveTab('output')}>Output</button>
        </li>
        <li className="nav-item" role="presentation">
          <button className={`nav-link${activeTab === 'errors' ? ' active' : ''}`} id="errors-tab" type="button" role="tab" aria-selected={activeTab === 'errors'} aria-controls="errors-panel" tabIndex={activeTab === 'errors' ? 0 : -1} onClick={() => setActiveTab('errors')}>Errors</button>
        </li>
        <li className="nav-item" role="presentation">
          <button className={`nav-link${activeTab === 'suggestions' ? ' active' : ''}`} id="suggestions-tab" type="button" role="tab" aria-selected={activeTab === 'suggestions'} aria-controls="suggestions-panel" tabIndex={activeTab === 'suggestions' ? 0 : -1} onClick={() => setActiveTab('suggestions')}>Suggestions</button>
        </li>
      </ul>
      <div className="tab-content" id="resultsTabContent">
        <div className={`tab-pane fade${activeTab === 'output' ? ' show active' : ''}`} id="output-panel" role="tabpanel" aria-labelledby="output-tab">
          <div dangerouslySetInnerHTML={{ __html: safeMarkdown(output || '*No output.*') }} />
        </div>
        <div className={`tab-pane fade${activeTab === 'errors' ? ' show active' : ''}`} id="errors-panel" role="tabpanel" aria-labelledby="errors-tab">
          <pre className="text-danger">{errors || 'No errors.'}</pre>
        </div>
        <div className={`tab-pane fade${activeTab === 'suggestions' ? ' show active' : ''}`} id="suggestions-panel" role="tabpanel" aria-labelledby="suggestions-tab">
          <div dangerouslySetInnerHTML={{ __html: safeMarkdown(suggestions || '*No suggestions.*') }} />
        </div>
      </div>
    </div>
  );
});

export default ResultsTabs; 