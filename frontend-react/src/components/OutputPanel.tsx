import * as React from 'react';
import { useState, useEffect } from 'react';
import * as Diff2Html from 'diff2html';
import { createTwoFilesPatch } from 'diff';
import { marked } from 'marked';
// @ts-ignore
import DOMPurify from 'dompurify';
// @ts-ignore
const purify = DOMPurify as typeof DOMPurify;

interface OutputPanelProps {
  originalCode?: string;
  aiCode?: string;
  aiMarkdown?: string;
  runOutput?: string;
  runLoading?: boolean;
  errors?: string;
  suggestions?: string;
  requestedTab?: string;
}

function parseSections(markdown: string) {
  // Parse sections like ### Explanation, ### Processed Code, etc.
  const sections: Record<string, string> = {};
  if (!markdown) return sections;
  const regex = /### ([A-Za-z ]+)\n+([\s\S]*?)(?=\n### |$)/g;
  let match;
  while ((match = regex.exec(markdown)) !== null) {
    sections[match[1].trim()] = match[2].trim();
  }
  return sections;
}

function parseMetrics(section: string) {
  // Try to extract metrics from a section (lines, chars, complexity, functions)
  if (!section) return null;
  const metrics: Record<string, any> = {};
  // Simple regexes for common metrics
  const lineMatch = section.match(/line[s]?[:=]?\s*(\d+)/i);
  if (lineMatch) metrics['Lines'] = lineMatch[1];
  const charMatch = section.match(/char[s]?[:=]?\s*(\d+)/i);
  if (charMatch) metrics['Characters'] = charMatch[1];
  const complexityMatch = section.match(/complexity[:=]?\s*(\d+)/i);
  if (complexityMatch) metrics['Complexity'] = complexityMatch[1];
  const funcMatch = section.match(/function[s]?[:=]?\s*(\d+)/i);
  if (funcMatch) metrics['Functions'] = funcMatch[1];
  // Try to parse percent changes
  const percentMatch = section.match(/percent[_ ]?change[:=]?\s*([\d.\-%]+)/i);
  if (percentMatch) metrics['Percent Change'] = percentMatch[1];
  return Object.keys(metrics).length ? metrics : null;
}

const TABS = [
  { key: 'Output', label: 'Output' },
  { key: 'Errors', label: 'Errors' },
  { key: 'Suggestions', label: 'Suggestions' },
  { key: 'Hints', label: 'Hints' },
  { key: 'Explanation', label: 'Explanation' },
  { key: 'Advanced', label: 'Advanced' },
];

export const OutputPanel: React.FC<OutputPanelProps> = ({ originalCode, aiCode, aiMarkdown, runOutput, runLoading, errors, suggestions, requestedTab }) => {
  const [activeTab, setActiveTab] = useState('Output');
  // the app asks for a tab (e.g. Errors after a failed request); the user can still click any tab
  useEffect(() => {
    const match = TABS.find(t => t.key.toLowerCase() === (requestedTab || '').toLowerCase());
    if (match) setActiveTab(match.key);
  }, [requestedTab, errors, suggestions, aiMarkdown]);
  // Parse sections from aiMarkdown
  const sections = parseSections(aiMarkdown || '');
  // Try to get optimized or fixed code for diff
  const optimizedCode = sections['Optimized Code'] || sections['Fixed Code'] || '';
  // Generate diff if both codes are present
  let diffHtml = '';
  if (originalCode && (aiCode || optimizedCode)) {
    const diffLinesStr = createTwoFilesPatch('Original', 'AI Suggestion', originalCode, aiCode || optimizedCode);
    diffHtml = Diff2Html.html(diffLinesStr, { drawFileList: false, matching: 'lines', outputFormat: 'side-by-side' });
  }
  // Parse metrics from aiMarkdown
  let metrics: Record<string, any> | null = null;
  if (sections['Performance Impact']) {
    metrics = parseMetrics(sections['Performance Impact']);
  }
  if (!metrics && sections['code_metrics']) {
    metrics = parseMetrics(sections['code_metrics']);
  }
  // Render markdown for each section
  const renderMarkdown = (md: string) => {
    const parsed = marked.parse(md || '');
    return <div className="prose prose-invert max-w-none" dangerouslySetInnerHTML={{ __html: purify.sanitize(typeof parsed === 'string' ? parsed : '') }} />;
  };
  // Ensure errors and suggestions are arrays
  const errorsArray = Array.isArray(errors) ? errors : errors ? [errors] : [];
  const suggestionsArray = Array.isArray(suggestions) ? suggestions : suggestions ? [suggestions] : [];
  // Tab content logic
  let tabContent: React.ReactNode = null;
  if (activeTab === 'Output') {
    tabContent = (
      <>
        {runLoading && <div className="text-accent mb-2 font-semibold">Running code...</div>}
        {runOutput && (
          <div>
            <div className="font-bold text-nord8 mb-1">Execution Output</div>
            <pre className="bg-nord2 text-foreground p-2 rounded whitespace-pre-wrap max-h-32 overflow-y-auto text-sm">{runOutput}</pre>
          </div>
        )}
        {sections['Processed Code'] && (
          <div>
            <div className="font-bold text-nord8 mb-1">Processed Code</div>
            <pre className="bg-nord2 text-foreground p-2 rounded whitespace-pre-wrap max-h-32 overflow-y-auto text-sm">{sections['Processed Code']}</pre>
          </div>
        )}
        {sections['Optimized Code'] && (
          <div>
            <div className="font-bold text-nord8 mb-1">Optimized Code</div>
            <pre className="bg-nord2 text-foreground p-2 rounded whitespace-pre-wrap max-h-32 overflow-y-auto text-sm">{sections['Optimized Code']}</pre>
          </div>
        )}
        {sections['Fixed Code'] && (
          <div>
            <div className="font-bold text-nord8 mb-1">Fixed Code</div>
            <pre className="bg-nord2 text-foreground p-2 rounded whitespace-pre-wrap max-h-32 overflow-y-auto text-sm">{sections['Fixed Code']}</pre>
          </div>
        )}
        {!runOutput && !sections['Processed Code'] && !sections['Optimized Code'] && !sections['Fixed Code'] && <div className="text-nord4">[No output]</div>}
      </>
    );
  } else if (activeTab === 'Errors') {
    tabContent = (
      <>
        {errorsArray.length > 0 ? (
          <ul className="list-disc pl-6">
            {errorsArray.map((err: string, idx: number) => (
              <li key={idx}>{err}</li>
            ))}
          </ul>
        ) : <div className="text-nord4">[No errors]</div>}
      </>
    );
  } else if (activeTab === 'Suggestions') {
    tabContent = (
      <>
        {suggestionsArray.length > 0 ? (
          <ul className="list-disc pl-6">
            {suggestionsArray.map((sugg: string, idx: number) => (
              <li key={idx}>{sugg}</li>
            ))}
          </ul>
        ) : <div className="text-nord4">[No suggestions]</div>}
      </>
    );
  } else if (activeTab === 'Hints') {
    tabContent = (
      <>
        {sections['Hints'] ? renderMarkdown(sections['Hints']) : <div className="text-nord4">No hints.</div>}
      </>
    );
  } else if (activeTab === 'Explanation') {
    tabContent = (
      <>
        {sections['Explanation'] ? renderMarkdown(sections['Explanation']) : <div className="text-nord4">No explanation.</div>}
      </>
    );
  } else if (activeTab === 'Advanced') {
    tabContent = (
      <div className="flex flex-col gap-4">
        {diffHtml && (
          <div>
            <div className="font-bold text-nord8 mb-2">Side-by-Side Diff</div>
            <div className="diff2html-container" dangerouslySetInnerHTML={{ __html: diffHtml }} />
          </div>
        )}
        {metrics && (
          <div>
            <div className="font-bold text-nord8 mb-2">Code Metrics</div>
            <table className="table-auto bg-nord2 rounded w-full text-sm mb-2">
              <tbody>
                {Object.entries(metrics).map(([k, v]) => (
                  <tr key={k}>
                    <td className="font-semibold px-2 py-1 text-nord7">{k}</td>
                    <td className="px-2 py-1">{v}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {!diffHtml && !metrics && <div className="text-nord4">No advanced diff or metrics available.</div>}
      </div>
    );
  }
  return (
    <section className="w-full flex justify-center">
      <div className="bg-nord1 dark:bg-background text-foreground p-6 rounded-2xl shadow-lg w-full max-w-3xl h-80 overflow-y-auto mt-4 flex flex-col gap-4">
        <div className="flex gap-2 mb-2 border-b border-nord3">
          {TABS.map(tab => (
            <button
              key={tab.key}
              className={`px-3 py-1 rounded-t-md font-semibold transition-colors ${activeTab === tab.key ? 'bg-nord3 text-nord8' : 'bg-transparent text-nord4 hover:bg-nord2'}`}
              onClick={() => setActiveTab(tab.key)}
            >
              {tab.label}
            </button>
          ))}
        </div>
        <div className="flex-1 overflow-y-auto">{tabContent}</div>
      </div>
    </section>
  );
};

export default OutputPanel; 