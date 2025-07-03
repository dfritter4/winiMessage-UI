import React, { useState, useEffect, useCallback } from 'react';
import styled from 'styled-components';
import ChatList from './components/ChatList';
import MessageView from './components/MessageView';
import Settings from './components/Settings';
import apiClient from './services/apiClient';
import { mockThreads, mockMessages } from './mockData';

const AppContainer = styled.div`
  height: 100vh;
  display: flex;
  background-color: #f5f5f5;
`;

const Sidebar = styled.div`
  width: 300px;
  min-width: 250px;
  max-width: 400px;
  background-color: #ffffff;
  border-right: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
`;

const MainContent = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #ffffff;
`;

const SidebarHeader = styled.div`
  padding: 16px;
  border-bottom: 1px solid #e0e0e0;
  background-color: #fafafa;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const SidebarTitle = styled.h2`
  font-size: 18px;
  font-weight: 600;
  color: #333;
`;

const SettingsButton = styled.button`
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  color: #666;
  padding: 4px;
  border-radius: 4px;
  
  &:hover {
    background-color: #e0e0e0;
  }
`;

const LoadingSpinner = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
  color: #666;
`;

const ErrorMessage = styled.div`
  padding: 16px;
  margin: 16px;
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
  text-align: center;
`;

const OfflineIndicator = styled.div`
  padding: 8px 16px;
  background-color: #f8d7da;
  color: #721c24;
  text-align: center;
  font-size: 14px;
  border-bottom: 1px solid #f5c6cb;
`;

function App() {
  const [threads, setThreads] = useState([]);
  const [selectedThread, setSelectedThread] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [messagesLoading, setMessagesLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isOnline, setIsOnline] = useState(true);
  const [showSettings, setShowSettings] = useState(false);
  const [serverUrl, setServerUrl] = useState(() => {
    return localStorage.getItem('winiMessage_serverUrl') || 
           process.env.REACT_APP_SERVER_URL || 
           'http://192.168.1.203:5001';
  });
  const [lastMessageCheck, setLastMessageCheck] = useState(null);
  const [deletedThreads, setDeletedThreads] = useState(() => {
    const saved = localStorage.getItem('winiMessage_deletedThreads');
    return saved ? JSON.parse(saved) : [];
  });

  const fetchThreads = useCallback(async () => {
    try {
      setError(null);
      const data = await apiClient.getThreads();
      // Filter out deleted threads and sort by most recent
      const filteredThreads = (data.threads || [])
        .filter(thread => !deletedThreads.includes(thread.thread_guid))
        .sort((a, b) => new Date(b.last_updated) - new Date(a.last_updated));
      setThreads(filteredThreads);
      setIsOnline(true);
    } catch (err) {
      console.error('Failed to fetch threads:', err);
      // Only show offline mode if this is a persistent connection issue
      // Don't set offline for temporary errors like send message failures
      if (threads.length === 0) {
        setError('Failed to connect to server. Using offline mode.');
        setIsOnline(false);
        // Filter mock threads as well and sort them too
        const filteredMockThreads = mockThreads
          .filter(thread => !deletedThreads.includes(thread.thread_guid))
          .sort((a, b) => new Date(b.last_updated) - new Date(a.last_updated));
        setThreads(filteredMockThreads);
      } else {
        // Keep existing threads, just show error
        setError('Connection error occurred');
      }
    } finally {
      setLoading(false);
    }
  }, [deletedThreads, threads.length]);

  const fetchMessages = useCallback(async (threadGuid) => {
    console.log('fetchMessages called with threadGuid:', threadGuid);
    setMessagesLoading(true);
    try {
      setError(null);
      console.log('Making API call to get messages...');
      const data = await apiClient.getMessages(threadGuid);
      console.log('API response received:', data);
      setMessages(data.messages || []);
      setIsOnline(true);
    } catch (err) {
      console.error('Failed to fetch messages:', err);
      setError('Failed to load messages');
      // Don't set offline for message loading failures - keep current online status
      const fallbackMessages = mockMessages[threadGuid] || [];
      console.log('Using fallback messages:', fallbackMessages);
      setMessages(fallbackMessages);
    } finally {
      setMessagesLoading(false);
    }
  }, []);

  const checkForNewMessages = useCallback(async () => {
    if (!isOnline) return;
    
    try {
      const now = new Date().toISOString();
      const since = lastMessageCheck || new Date(Date.now() - 30000).toISOString();
      
      const data = await apiClient.getRecentMessages(20, since);
      
      if (data.messages && data.messages.length > 0) {
        await fetchThreads();
        
        if (selectedThread) {
          await fetchMessages(selectedThread.thread_guid);
        }
      }
      
      setLastMessageCheck(now);
      setIsOnline(true);
    } catch (err) {
      console.error('Failed to check for new messages:', err);
      setIsOnline(false);
    }
  }, [isOnline, lastMessageCheck, fetchThreads, fetchMessages, selectedThread]);

  useEffect(() => {
    console.log('Initializing with server URL:', serverUrl);
    apiClient.baseURL = serverUrl;
    apiClient.client.defaults.baseURL = serverUrl;
    fetchThreads();
  }, [serverUrl, fetchThreads]);

  // Initialize API client with saved URL on app startup
  useEffect(() => {
    const savedUrl = localStorage.getItem('winiMessage_serverUrl');
    if (savedUrl && savedUrl !== serverUrl) {
      console.log('Found saved server URL:', savedUrl);
      setServerUrl(savedUrl);
    }
  }, []);

  useEffect(() => {
    const pollInterval = setInterval(checkForNewMessages, 
      parseInt(process.env.REACT_APP_POLL_INTERVAL) || 5000
    );
    
    return () => clearInterval(pollInterval);
  }, [checkForNewMessages]);

  const handleThreadSelect = async (thread) => {
    console.log('Thread selected:', thread);
    
    // Clear unread count immediately when thread is selected
    const updatedThread = { ...thread, unread_count: 0 };
    setSelectedThread(updatedThread);
    
    // Update the thread in the threads list to clear unread count
    setThreads(prevThreads => 
      prevThreads.map(t => 
        t.thread_guid === thread.thread_guid 
          ? { ...t, unread_count: 0 }
          : t
      )
    );
    
    setMessages([]); // Clear messages while loading
    
    if (isOnline) {
      console.log('Fetching messages for thread:', thread.thread_guid);
      await fetchMessages(thread.thread_guid);
    } else {
      console.log('Offline mode - using mock messages');
      const threadMessages = mockMessages[thread.thread_guid] || [];
      setMessages(threadMessages);
    }
  };

  const handleSendMessage = async (messageData) => {
    if (!selectedThread) return;

    console.log('Sending message:', messageData);
    console.log('Selected thread:', selectedThread);

    try {
      setError(null);
      await apiClient.sendMessage(selectedThread.thread_guid, messageData);
      
      console.log('Message sent successfully, refreshing...');
      await fetchMessages(selectedThread.thread_guid);
      await fetchThreads();
      
      setIsOnline(true);
    } catch (err) {
      console.error('Failed to send message:', err);
      setError(`Failed to send message: ${err.message}`);
      // Don't set offline for send failures - keep current status
    }
  };

  const handleServerUrlChange = (newUrl) => {
    console.log('Changing server URL to:', newUrl);
    setServerUrl(newUrl);
    localStorage.setItem('winiMessage_serverUrl', newUrl);
    
    // Update the API client immediately
    apiClient.baseURL = newUrl;
    apiClient.client.defaults.baseURL = newUrl;
  };

  const handleDeleteThread = (threadGuid) => {
    console.log('Deleting thread:', threadGuid);
    
    // Add to deleted threads list
    const updatedDeletedThreads = [...deletedThreads, threadGuid];
    setDeletedThreads(updatedDeletedThreads);
    
    // Save to localStorage
    localStorage.setItem('winiMessage_deletedThreads', JSON.stringify(updatedDeletedThreads));
    
    // If the deleted thread was selected, clear selection
    if (selectedThread?.thread_guid === threadGuid) {
      setSelectedThread(null);
      setMessages([]);
    }
    
    // Remove from threads list immediately
    setThreads(threads.filter(thread => thread.thread_guid !== threadGuid));
  };

  const handleRestoreAllChats = () => {
    console.log('Restoring all deleted chats');
    setDeletedThreads([]);
    localStorage.setItem('winiMessage_deletedThreads', JSON.stringify([]));
    
    // Refresh the threads to show restored chats
    fetchThreads();
  };

  if (loading) {
    return (
      <AppContainer>
        <LoadingSpinner>Loading conversations...</LoadingSpinner>
      </AppContainer>
    );
  }

  return (
    <AppContainer>
      {!isOnline && (
        <OfflineIndicator>
          Offline mode - Using cached data. Check your connection.
        </OfflineIndicator>
      )}
      
      <Sidebar>
        <SidebarHeader>
          <div>
            <SidebarTitle>Messages</SidebarTitle>
            <div style={{ fontSize: '11px', color: '#666', marginTop: '2px' }}>
              {new URL(serverUrl).host}
            </div>
          </div>
          <SettingsButton onClick={() => setShowSettings(true)}>
            ⚙️
          </SettingsButton>
        </SidebarHeader>
        
        {error && !isOnline && (
          <ErrorMessage>{error}</ErrorMessage>
        )}
        
        <ChatList 
          threads={threads} 
          selectedThread={selectedThread}
          onThreadSelect={handleThreadSelect}
          onDeleteThread={handleDeleteThread}
        />
      </Sidebar>
      
      <MainContent>
        <MessageView 
          selectedThread={selectedThread}
          messages={messages}
          onSendMessage={handleSendMessage}
          error={error && isOnline ? error : null}
          loading={messagesLoading}
        />
      </MainContent>
      
      <Settings
        isOpen={showSettings}
        onClose={() => setShowSettings(false)}
        serverUrl={serverUrl}
        onServerUrlChange={handleServerUrlChange}
        deletedThreadsCount={deletedThreads.length}
        onRestoreAllChats={handleRestoreAllChats}
      />
    </AppContainer>
  );
}

export default App;