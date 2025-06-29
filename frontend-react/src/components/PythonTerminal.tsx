import React, { useEffect, useRef } from 'react';
import { Terminal } from 'xterm';
import 'xterm/css/xterm.css';

const WS_URL = 'ws://localhost:8000/ws/terminal';

const PythonTerminal: React.FC = () => {
  const terminalRef = useRef<HTMLDivElement>(null);
  const termObj = useRef<Terminal | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const term = new Terminal({
      cursorBlink: true,
      fontSize: 16,
      theme: {
        background: '#1e1e1e',
        foreground: '#ffffff',
      },
    });
    term.open(terminalRef.current!);
    termObj.current = term;

    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => {
      term.writeln('Connected to Python Terminal!');
      term.write('\r\n>>> ');
    };

    ws.onmessage = (event) => {
      term.write(event.data);
      term.write('\r\n>>> ');
    };

    ws.onclose = () => {
      term.writeln('\r\n[Disconnected from backend]');
    };

    term.onData((data) => {
      ws.send(data);
    });

    return () => {
      ws.close();
      term.dispose();
    };
  }, []);

  return <div ref={terminalRef} style={{ width: '100%', height: '500px', background: '#1e1e1e' }} />;
};

export default PythonTerminal; 