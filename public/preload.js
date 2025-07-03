const { contextBridge, ipcRenderer, shell } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  fetchLinkPreview: (url) => ipcRenderer.invoke('fetch-link-preview', url),
  downloadImage: (url) => ipcRenderer.invoke('download-image', url),
  openExternal: (url) => shell.openExternal(url)
});