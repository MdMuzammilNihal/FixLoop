import * as React from 'react';
import { Sun, Moon } from 'lucide-react';

interface HeaderProps {
  darkMode: boolean;
  onToggleTheme: () => void;
}

export const Header: React.FC<HeaderProps> = ({ darkMode, onToggleTheme }) => {
  return (
    <header className="w-full flex items-center justify-between px-6 py-4 bg-nord0 dark:bg-background text-foreground shadow rounded-2xl mb-4">
      <div className="text-2xl font-bold tracking-tight">DeepSeek Code Assistant</div>
      <button
        className="p-2 rounded-full hover:bg-nord2 transition-colors"
        onClick={onToggleTheme}
        aria-label="Toggle theme"
      >
        {darkMode ? <Sun className="w-6 h-6" /> : <Moon className="w-6 h-6" />}
      </button>
    </header>
  );
};

export default Header; 