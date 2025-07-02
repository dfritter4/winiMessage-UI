import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import apiClient from '../services/apiClient';
import ConnectionDebugger from './ConnectionDebugger';

const SettingsOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const SettingsModal = styled.div`
  background-color: white;
  border-radius: 8px;
  padding: 24px;
  width: 500px;
  max-width: 90vw;
  max-height: 80vh;
  overflow-y: auto;
`;

const SettingsTitle = styled.h2`
  margin-bottom: 20px;
  color: #333;
`;

const FormGroup = styled.div`
  margin-bottom: 16px;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 4px;
  font-weight: 500;
  color: #333;
`;

const Input = styled.input`
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
`;

const Button = styled.button`
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
`;

const PrimaryButton = styled(Button)`
  background-color: #007AFF;
  color: white;
  
  &:hover {
    background-color: #0056b3;
  }
`;

const SecondaryButton = styled(Button)`
  background-color: #f0f0f0;
  color: #333;
  
  &:hover {
    background-color: #e0e0e0;
  }
`;

const ConnectionStatus = styled.div`
  padding: 8px 12px;
  border-radius: 4px;
  margin-bottom: 16px;
  font-size: 14px;
  background-color: ${props => props.connected ? '#d4edda' : '#f8d7da'};
  color: ${props => props.connected ? '#155724' : '#721c24'};
  border: 1px solid ${props => props.connected ? '#c3e6cb' : '#f5c6cb'};
`;

const TestButton = styled(SecondaryButton)`
  margin-left: 8px;
`;

const PresetButton = styled.button`
  padding: 6px 12px;
  margin: 4px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: white;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
  
  &:hover {
    background-color: #f0f0f0;
    border-color: #007AFF;
  }
`;

const PresetGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 8px;
  margin-top: 8px;
`;

const SectionTitle = styled.h3`
  margin: 20px 0 12px 0;
  color: #333;
  font-size: 16px;
  border-bottom: 1px solid #eee;
  padding-bottom: 8px;
`;

const ServerStatus = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 16px;
  background-color: ${props => props.status === 'online' ? '#d4edda' : props.status === 'offline' ? '#f8d7da' : '#fff3cd'};
  border: 1px solid ${props => props.status === 'online' ? '#c3e6cb' : props.status === 'offline' ? '#f5c6cb' : '#ffeaa7'};
`;

const StatusDot = styled.div`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: ${props => props.status === 'online' ? '#28a745' : props.status === 'offline' ? '#dc3545' : '#ffc107'};
`;

const ServerInfo = styled.div`
  font-size: 14px;
  color: #333;
`;

const ScanButton = styled(SecondaryButton)`
  margin-left: 8px;
  font-size: 12px;
  padding: 6px 12px;
`;

const ScanResults = styled.div`
  margin-top: 12px;
  max-height: 150px;
  overflow-y: auto;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 8px;
`;

const ScanResult = styled.div`
  padding: 6px;
  margin: 2px 0;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  &:hover {
    background-color: #f0f0f0;
  }
`;

const RecentServers = styled.div`
  margin-top: 12px;
`;

const RecentServer = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  border: 1px solid #eee;
  border-radius: 4px;
  margin-bottom: 4px;
  font-size: 14px;
  
  &:hover {
    background-color: #f8f8f8;
  }
`;

const UseButton = styled.button`
  padding: 4px 8px;
  border: none;
  border-radius: 4px;
  background-color: #007AFF;
  color: white;
  cursor: pointer;
  font-size: 12px;
  
  &:hover {
    background-color: #0056b3;
  }
`;

function Settings({ isOpen, onClose, serverUrl, onServerUrlChange, deletedThreadsCount, onRestoreAllChats }) {
  const [tempUrl, setTempUrl] = useState(serverUrl);
  const [connectionStatus, setConnectionStatus] = useState(null);
  const [testing, setTesting] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [scanResults, setScanResults] = useState([]);
  const [recentServers, setRecentServers] = useState([]);

  const commonPresets = [
    '192.168.1.203:5001',
    '192.168.1.100:5001',
    '192.168.0.100:5001',
    '10.0.0.100:5001',
    '172.16.0.100:5001',
    'localhost:5001'
  ];

  useEffect(() => {
    const saved = localStorage.getItem('winiMessage_recentServers');
    if (saved) {
      setRecentServers(JSON.parse(saved));
    }
  }, []);

  const saveRecentServer = (url) => {
    const updated = [url, ...recentServers.filter(s => s !== url)].slice(0, 5);
    setRecentServers(updated);
    localStorage.setItem('winiMessage_recentServers', JSON.stringify(updated));
  };

  const handleSave = () => {
    const finalUrl = tempUrl.startsWith('http') ? tempUrl : `http://${tempUrl}`;
    onServerUrlChange(finalUrl);
    saveRecentServer(finalUrl);
    onClose();
  };

  const testConnection = async (url = tempUrl) => {
    setTesting(true);
    setConnectionStatus(null);
    
    try {
      const testUrl = url.startsWith('http') ? url : `http://${url}`;
      const originalUrl = apiClient.baseURL;
      
      console.log(`Testing connection to: ${testUrl}`);
      
      apiClient.baseURL = testUrl;
      apiClient.client.defaults.baseURL = testUrl;
      
      const isConnected = await apiClient.testConnection();
      setConnectionStatus({ success: true, message: 'Connection successful!' });
      
      return true;
    } catch (error) {
      console.error('Connection test failed:', error);
      setConnectionStatus({ 
        success: false, 
        message: error.message || 'Connection failed'
      });
      
      // Restore original URL on failure
      const originalUrl = process.env.REACT_APP_SERVER_URL || 'http://192.168.1.203:5001';
      apiClient.baseURL = originalUrl;
      apiClient.client.defaults.baseURL = originalUrl;
      
      return false;
    } finally {
      setTesting(false);
    }
  };

  const scanForServers = async () => {
    setScanning(true);
    setScanResults([]);
    
    const currentIP = await getCurrentIP();
    const baseIP = currentIP.substring(0, currentIP.lastIndexOf('.'));
    const promises = [];
    
    for (let i = 100; i <= 255; i++) {
      const ip = `${baseIP}.${i}`;
      promises.push(testServerAtIP(ip));
    }
    
    try {
      const results = await Promise.allSettled(promises);
      const found = results
        .map((result, index) => ({
          ip: `${baseIP}.${100 + index}`,
          success: result.status === 'fulfilled' && result.value
        }))
        .filter(r => r.success);
      
      setScanResults(found);
    } catch (error) {
      console.error('Scan failed:', error);
    } finally {
      setScanning(false);
    }
  };

  const getCurrentIP = async () => {
    try {
      const response = await fetch('https://api.ipify.org?format=json');
      const data = await response.json();
      return data.ip;
    } catch {
      return '192.168.1.1';
    }
  };

  const testServerAtIP = async (ip) => {
    try {
      const testUrl = `http://${ip}:5001`;
      const response = await fetch(`${testUrl}/threads?limit=1`, {
        method: 'GET',
        timeout: 2000
      });
      return response.ok;
    } catch {
      return false;
    }
  };

  const usePreset = (preset) => {
    const url = preset.startsWith('http') ? preset : `http://${preset}`;
    setTempUrl(url);
  };

  const useServer = (server) => {
    setTempUrl(server);
  };

  if (!isOpen) return null;

  const getServerStatus = () => {
    if (connectionStatus === null) return 'unknown';
    return connectionStatus.success ? 'online' : 'offline';
  };

  return (
    <SettingsOverlay onClick={onClose}>
      <SettingsModal onClick={(e) => e.stopPropagation()}>
        <SettingsTitle>Server Settings</SettingsTitle>
        
        <ServerStatus status={getServerStatus()}>
          <StatusDot status={getServerStatus()} />
          <ServerInfo>
            {connectionStatus === null 
              ? 'Server status unknown' 
              : connectionStatus.success 
                ? `Connected to ${serverUrl}` 
                : connectionStatus.message || 'Not connected to server'}
          </ServerInfo>
        </ServerStatus>
        
        <FormGroup>
          <Label>Server URL</Label>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <Input
              type="text"
              value={tempUrl}
              onChange={(e) => setTempUrl(e.target.value)}
              placeholder="192.168.1.203:5001 or http://192.168.1.203:5001"
            />
            <TestButton onClick={() => testConnection()} disabled={testing}>
              {testing ? 'Testing...' : 'Test'}
            </TestButton>
          </div>
        </FormGroup>

        <SectionTitle>Quick Presets</SectionTitle>
        <PresetGrid>
          {commonPresets.map((preset) => (
            <PresetButton key={preset} onClick={() => usePreset(preset)}>
              {preset}
            </PresetButton>
          ))}
        </PresetGrid>

        <SectionTitle>
          Server Discovery
          <ScanButton onClick={scanForServers} disabled={scanning}>
            {scanning ? 'Scanning...' : 'Scan Network'}
          </ScanButton>
        </SectionTitle>
        
        {scanResults.length > 0 && (
          <ScanResults>
            <div style={{ marginBottom: '8px', fontWeight: 'bold', fontSize: '14px' }}>
              Found {scanResults.length} server(s):
            </div>
            {scanResults.map((result) => (
              <ScanResult key={result.ip} onClick={() => usePreset(`${result.ip}:5001`)}>
                <span>{result.ip}:5001</span>
                <UseButton onClick={(e) => {
                  e.stopPropagation();
                  usePreset(`${result.ip}:5001`);
                }}>
                  Use
                </UseButton>
              </ScanResult>
            ))}
          </ScanResults>
        )}

        {recentServers.length > 0 && (
          <>
            <SectionTitle>Recent Servers</SectionTitle>
            <RecentServers>
              {recentServers.map((server, index) => (
                <RecentServer key={index}>
                  <span>{server}</span>
                  <UseButton onClick={() => useServer(server)}>
                    Use
                  </UseButton>
                </RecentServer>
              ))}
            </RecentServers>
          </>
        )}

        {connectionStatus && !connectionStatus.success && (
          <ConnectionDebugger serverUrl={tempUrl} />
        )}

        {deletedThreadsCount > 0 && (
          <>
            <SectionTitle>Deleted Conversations</SectionTitle>
            <div style={{ padding: '12px', backgroundColor: '#f8f9fa', borderRadius: '4px', marginBottom: '16px' }}>
              <div style={{ marginBottom: '8px', fontSize: '14px' }}>
                You have {deletedThreadsCount} hidden conversation{deletedThreadsCount !== 1 ? 's' : ''}.
              </div>
              <SecondaryButton 
                onClick={() => {
                  onRestoreAllChats();
                  onClose();
                }}
              >
                Restore All Conversations
              </SecondaryButton>
            </div>
          </>
        )}
        
        <ButtonGroup>
          <SecondaryButton onClick={onClose}>Cancel</SecondaryButton>
          <PrimaryButton onClick={handleSave}>Save</PrimaryButton>
        </ButtonGroup>
      </SettingsModal>
    </SettingsOverlay>
  );
}

export default Settings;