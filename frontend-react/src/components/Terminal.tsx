import React, { useEffect, useRef, useImperativeHandle, forwardRef } from 'react';
import { Terminal as XTerm } from 'xterm';
import 'xterm/css/xterm.css';

export interface TerminalHandle {
  clear: () => void;
}

interface TerminalProps {
  output: string;
}

const Terminal = forwardRef<TerminalHandle, TerminalProps>(({ output }, ref) => {
  const terminalRef = useRef<HTMLDivElement>(null);
  const xtermRef = useRef<XTerm | null>(null);
  const lastOutputRef = useRef('');

  useImperativeHandle(ref, () => ({
    clear: () => xtermRef.current?.clear(),
  }));

  useEffect(() => {
    if (!xtermRef.current && terminalRef.current) {
      xtermRef.current = new XTerm({
        fontSize: 14,
        theme: {
          background: '#2e3440',
          foreground: '#eceff4',
        },
        rows: 16,
        cols: 80,
        cursorBlink: true,
      });
      xtermRef.current.open(terminalRef.current);
    }
    // Only append new output
    if (xtermRef.current && output !== lastOutputRef.current) {
      const newOutput = output.replace(lastOutputRef.current, '');
      xtermRef.current.write(newOutput.replace(/\n/g, '\r\n'));
      xtermRef.current.scrollToBottom();
      lastOutputRef.current = output;
    }
  }, [output]);

  return (
    <div style={{ position: 'relative' }}>
      <button
        style={{ position: 'absolute', right: 10, top: 10, zIndex: 2 }}
        onClick={() => xtermRef.current?.clear()}
      >
        Clear
      </button>
      <div ref={terminalRef} style={{ width: '100%', height: '300px', background: '#2e3440', borderRadius: '8px', overflow: 'hidden' }} />
    </div>
  );
});

export default Terminal; 