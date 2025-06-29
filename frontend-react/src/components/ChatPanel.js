import * as React from 'react';
const { useRef, useEffect } = React;
import { Maximize2, Minimize2 } from 'lucide-react';
const roleLabel = {
    user: 'You',
    ai: 'AI',
};
const roleBubble = {
    user: 'bg-nord7 text-background self-end',
    ai: 'bg-nord3 text-foreground self-start',
};
const ChatPanel = ({ messages, input, onInputChange, onSend, loading, expanded, onToggleExpand }) => {
    const inputRef = useRef(null);
    const bottomRef = useRef(null);
    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, loading]);
    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (input.trim() && !loading)
                onSend();
        }
    };
    return (React.createElement("aside", { className: `flex flex-col h-full bg-nord0 dark:bg-nord0 rounded-2xl shadow-lg p-4 mt-2 ml-2 transition-all duration-300 ${expanded ? 'w-[90vw] max-w-[700px]' : 'w-[380px] min-w-[320px] max-w-[420px]'}`, style: { zIndex: 20 } },
        React.createElement("div", { className: "flex items-center justify-between mb-2" },
            React.createElement("div", { className: "font-bold text-lg text-nord8" }, "AI Chat"),
            React.createElement("button", { className: "p-2 rounded-full hover:bg-nord2 transition-colors", onClick: onToggleExpand, "aria-label": expanded ? 'Collapse chat panel' : 'Expand chat panel' }, expanded ? React.createElement(Minimize2, { className: "w-5 h-5" }) : React.createElement(Maximize2, { className: "w-5 h-5" }))),
        React.createElement("div", { className: "flex-1 overflow-y-auto flex flex-col gap-3 pb-2 max-h-[60vh]" },
            messages.map((msg) => (React.createElement("div", { key: msg.id, className: `flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}` },
                React.createElement("span", { className: `text-xs font-semibold mb-1 ${msg.role === 'user' ? 'text-nord7' : 'text-nord4'}` }, roleLabel[msg.role]),
                React.createElement("div", { className: `rounded-xl px-4 py-2 max-w-[90%] whitespace-pre-wrap break-words shadow ${roleBubble[msg.role]}`, style: { fontSize: '0.98rem', lineHeight: 1.5 } }, msg.content)))),
            loading && (React.createElement("div", { className: "flex items-center gap-2 text-nord7 text-sm animate-pulse" },
                React.createElement("span", { className: "w-2 h-2 rounded-full bg-nord7 inline-block" }),
                " AI is typing...")),
            React.createElement("div", { ref: bottomRef })),
        React.createElement("form", { className: "flex gap-2 mt-2", onSubmit: e => {
                e.preventDefault();
                if (input.trim() && !loading)
                    onSend();
            } },
            React.createElement("input", { ref: inputRef, className: "flex-1 rounded-xl px-3 py-2 bg-nord2 text-foreground focus:outline-none focus:ring-2 focus:ring-nord8 text-base shadow", placeholder: "Type your message...", value: input, onChange: e => onInputChange(e.target.value), onKeyDown: handleKeyDown, disabled: loading }),
            React.createElement("button", { type: "submit", className: "px-4 py-2 rounded-xl bg-nord7 text-background font-semibold shadow hover:bg-nord8 transition-colors disabled:opacity-60", disabled: loading || !input.trim() }, "Send"))));
};
export default ChatPanel;
