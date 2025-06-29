module.exports = {
  content: [
    './src/**/*.{js,jsx,ts,tsx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: '#1e1e2f',
        foreground: '#e5e5e5',
        accent: '#88c0d0',
        nord0: '#2e3440',
        nord1: '#3b4252',
        nord2: '#434c5e',
        nord3: '#4c566a',
        nord4: '#d8dee9',
        nord5: '#e5e9f0',
        nord6: '#eceff4',
        nord7: '#8fbcbb',
        nord8: '#88c0d0',
        nord9: '#81a1c1',
        nord10: '#5e81ac',
        nord11: '#bf616a',
        nord12: '#d08770',
        nord13: '#ebcb8b',
        nord14: '#a3be8c',
        nord15: '#b48ead',
      },
      fontFamily: {
        mono: ['Fira Mono', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
      },
      borderRadius: {
        xl: '1rem',
        '2xl': '1.5rem',
      },
    },
  },
  plugins: [],
}; 