const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const isDev = require('electron-is-dev');

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      preload: path.join(__dirname, 'preload.js')
    },
    titleBarStyle: 'hiddenInset',
    show: false
  });

  mainWindow.loadURL(
    isDev
      ? 'http://localhost:3000'
      : `file://${path.join(__dirname, '../build/index.html')}`
  );

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  if (isDev) {
    mainWindow.webContents.openDevTools();
  }
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// Handle image downloading in main process (bypasses CORS)
ipcMain.handle('download-image', async (event, url) => {
  try {
    const https = require('https');
    const http = require('http');
    
    return new Promise((resolve, reject) => {
      const client = url.startsWith('https:') ? https : http;
      
      const req = client.get(url, {
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
      }, (res) => {
        const chunks = [];
        
        res.on('data', (chunk) => {
          chunks.push(chunk);
        });
        
        res.on('end', () => {
          const buffer = Buffer.concat(chunks);
          resolve({
            success: true,
            data: buffer.toString('base64'),
            contentType: res.headers['content-type'] || 'image/jpeg',
            status: res.statusCode
          });
        });
      });
      
      req.on('error', (err) => {
        resolve({
          success: false,
          error: err.message
        });
      });
      
      req.setTimeout(15000, () => {
        req.destroy();
        resolve({
          success: false,
          error: 'Request timeout'
        });
      });
    });
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
});

// Handle link preview fetching in main process (bypasses CORS)
ipcMain.handle('fetch-link-preview', async (event, url) => {
  try {
    const https = require('https');
    const http = require('http');
    
    return new Promise((resolve, reject) => {
      const client = url.startsWith('https:') ? https : http;
      
      const req = client.get(url, {
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
      }, (res) => {
        let data = '';
        
        res.on('data', (chunk) => {
          data += chunk;
        });
        
        res.on('end', () => {
          resolve({
            success: true,
            html: data,
            status: res.statusCode
          });
        });
      });
      
      req.on('error', (err) => {
        resolve({
          success: false,
          error: err.message
        });
      });
      
      req.setTimeout(10000, () => {
        req.destroy();
        resolve({
          success: false,
          error: 'Request timeout'
        });
      });
    });
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
});