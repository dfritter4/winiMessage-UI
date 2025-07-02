import React, { useState } from 'react';
import styled from 'styled-components';

const DebugContainer = styled.div`
  margin-top: 20px;
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
`;

const DebugTitle = styled.h4`
  margin-bottom: 12px;
  color: #333;
`;

const DebugButton = styled.button`
  background-color: #6c757d;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 8px;
  font-size: 14px;
  
  &:hover {
    background-color: #5a6268;
  }
`;

const DebugResults = styled.div`
  margin-top: 12px;
  padding: 12px;
  background-color: #1e1e1e;
  color: #f8f8f8;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  max-height: 200px;
  overflow-y: auto;
  white-space: pre-wrap;
`;

function ConnectionDebugger({ serverUrl }) {
  const [debugResults, setDebugResults] = useState('');
  const [isDebugging, setIsDebugging] = useState(false);

  const runBasicTests = async () => {
    setIsDebugging(true);
    setDebugResults('Starting connection diagnostics...\n\n');

    // Parse URL
    const url = serverUrl.startsWith('http') ? serverUrl : `http://${serverUrl}`;
    const urlObj = new URL(url);
    
    setDebugResults(prev => prev + `Target Server: ${url}\n`);
    setDebugResults(prev => prev + `Host: ${urlObj.hostname}\n`);
    setDebugResults(prev => prev + `Port: ${urlObj.port}\n\n`);

    // Test 1: Basic fetch with timeout
    setDebugResults(prev => prev + '1. Testing basic HTTP connection...\n');
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3000);
      
      const response = await fetch(url + '/threads?limit=1', {
        method: 'GET',
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      clearTimeout(timeoutId);
      
      setDebugResults(prev => prev + `   ✓ HTTP Response: ${response.status} ${response.statusText}\n`);
      setDebugResults(prev => prev + `   ✓ Headers: ${JSON.stringify(Object.fromEntries(response.headers.entries()), null, 2)}\n`);
      
    } catch (error) {
      setDebugResults(prev => prev + `   ✗ HTTP Error: ${error.name} - ${error.message}\n`);
    }

    // Test 2: CORS check
    setDebugResults(prev => prev + '\n2. Testing CORS headers...\n');
    try {
      const response = await fetch(url, { 
        method: 'OPTIONS',
        headers: {
          'Origin': window.location.origin,
          'Access-Control-Request-Method': 'GET'
        }
      });
      setDebugResults(prev => prev + `   ✓ OPTIONS Response: ${response.status}\n`);
    } catch (error) {
      setDebugResults(prev => prev + `   ✗ CORS Error: ${error.message}\n`);
    }

    // Test 3: Network connectivity
    setDebugResults(prev => prev + '\n3. Testing network connectivity...\n');
    try {
      const pingResponse = await fetch(`http://${urlObj.hostname}:${urlObj.port || 80}`, {
        method: 'HEAD',
        mode: 'no-cors'
      });
      setDebugResults(prev => prev + `   ✓ Network reachable\n`);
    } catch (error) {
      setDebugResults(prev => prev + `   ✗ Network Error: ${error.message}\n`);
    }

    setDebugResults(prev => prev + '\n4. Common issues to check:\n');
    setDebugResults(prev => prev + '   • Is your iMessage server running on the MacBook?\n');
    setDebugResults(prev => prev + '   • Is the server listening on all interfaces (0.0.0.0) not just localhost?\n');
    setDebugResults(prev => prev + '   • Is port 5001 open in macOS firewall?\n');
    setDebugResults(prev => prev + '   • Are both devices on the same network?\n');
    setDebugResults(prev => prev + '   • Is the MacBook IP address correct?\n\n');

    setIsDebugging(false);
  };

  const testSpecificEndpoints = async () => {
    setIsDebugging(true);
    setDebugResults('Testing specific API endpoints...\n\n');

    const endpoints = [
      { path: '/', description: 'Root endpoint' },
      { path: '/threads', description: 'Threads endpoint' },
      { path: '/threads?limit=1', description: 'Threads with limit' },
      { path: '/messages/recent', description: 'Recent messages' },
    ];

    for (const endpoint of endpoints) {
      setDebugResults(prev => prev + `Testing ${endpoint.description} (${endpoint.path})...\n`);
      
      try {
        const response = await fetch(serverUrl + endpoint.path, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' }
        });
        
        setDebugResults(prev => prev + `   ✓ Status: ${response.status}\n`);
        
        if (response.ok) {
          const text = await response.text();
          setDebugResults(prev => prev + `   ✓ Response preview: ${text.substring(0, 100)}...\n`);
        }
      } catch (error) {
        setDebugResults(prev => prev + `   ✗ Error: ${error.message}\n`);
      }
      
      setDebugResults(prev => prev + '\n');
    }

    setIsDebugging(false);
  };

  return (
    <DebugContainer>
      <DebugTitle>Connection Diagnostics</DebugTitle>
      <div>
        <DebugButton onClick={runBasicTests} disabled={isDebugging}>
          {isDebugging ? 'Testing...' : 'Run Basic Tests'}
        </DebugButton>
        <DebugButton onClick={testSpecificEndpoints} disabled={isDebugging}>
          Test Endpoints
        </DebugButton>
      </div>
      
      {debugResults && (
        <DebugResults>{debugResults}</DebugResults>
      )}
    </DebugContainer>
  );
}

export default ConnectionDebugger;