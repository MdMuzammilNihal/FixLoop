import * as React from 'react';
import { Sun, Moon } from 'lucide-react';
export const Header = ({ darkMode, onToggleTheme }) => {
    return (React.createElement("header", { className: "w-full flex items-center justify-between px-6 py-4 bg-nord0 dark:bg-background text-foreground shadow rounded-2xl mb-4" },
        React.createElement("div", { className: "text-2xl font-bold tracking-tight" }, "DeepSeek Code Assistant"),
        React.createElement("button", { className: "p-2 rounded-full hover:bg-nord2 transition-colors", onClick: onToggleTheme, "aria-label": "Toggle theme" }, darkMode ? React.createElement(Sun, { className: "w-6 h-6" }) : React.createElement(Moon, { className: "w-6 h-6" }))));
};
export default Header;
