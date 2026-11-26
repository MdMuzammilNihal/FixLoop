const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let backendProcess;

function createWindow () {
  const win = new BrowserWindow({
    title: 'FixLoop',
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    }
  });

  // Load the built React app
  win.loadFile(path.join(__dirname, 'frontend-react', 'dist', 'index.html'));
}

app.whenReady().then(() => {
  // Start the Python backend
  backendProcess = spawn('python', [
    '-m', 'uvicorn', 'backend.main:app', '--port', '8000'
  ], { stdio: 'inherit', cwd: __dirname });

  createWindow();

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') {
    if (backendProcess) backendProcess.kill();
    app.quit();
  }
}); 