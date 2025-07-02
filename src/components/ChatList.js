import React, { useState } from 'react';
import styled from 'styled-components';
import ConfirmDialog from './ConfirmDialog';

const ChatListContainer = styled.div`
  flex: 1;
  overflow-y: auto;
`;

const ChatItem = styled.div`
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background-color 0.2s ease;
  background-color: ${props => props.selected ? '#007AFF' : 'transparent'};
  color: ${props => props.selected ? 'white' : '#333'};
  position: relative;
  display: flex;
  align-items: center;

  &:hover {
    background-color: ${props => props.selected ? '#007AFF' : '#f8f8f8'};
  }

  &:hover .delete-button {
    opacity: 1;
  }
`;

const ChatContent = styled.div`
  flex: 1;
  min-width: 0;
`;

const DeleteButton = styled.button`
  opacity: 0;
  transition: opacity 0.2s ease;
  background: ${props => props.selected ? 'rgba(255,255,255,0.2)' : '#ff4444'};
  color: ${props => props.selected ? 'white' : 'white'};
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  cursor: pointer;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: 8px;
  flex-shrink: 0;

  &:hover {
    background: #cc0000;
    transform: scale(1.1);
  }
`;

const ChatHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
`;

const ChatName = styled.div`
  font-weight: 600;
  font-size: 14px;
  color: ${props => props.selected ? 'white' : '#333'};
`;

const ChatTime = styled.div`
  font-size: 12px;
  color: ${props => props.selected ? 'rgba(255,255,255,0.8)' : '#666'};
`;

const ChatPreview = styled.div`
  font-size: 13px;
  color: ${props => props.selected ? 'rgba(255,255,255,0.9)' : '#666'};
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const UnreadBadge = styled.div`
  background-color: ${props => props.selected ? 'rgba(255,255,255,0.3)' : '#007AFF'};
  color: ${props => props.selected ? 'white' : 'white'};
  border-radius: 10px;
  padding: 2px 6px;
  font-size: 11px;
  font-weight: 600;
  min-width: 18px;
  text-align: center;
  margin-left: 8px;
`;

const formatTime = (timestamp) => {
  const date = new Date(timestamp);
  const now = new Date();
  const isToday = date.toDateString() === now.toDateString();
  
  if (isToday) {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  } else {
    return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
  }
};

function ChatList({ threads, selectedThread, onThreadSelect, onDeleteThread }) {
  const [deleteConfirm, setDeleteConfirm] = useState(null);

  const handleDeleteClick = (e, thread) => {
    e.stopPropagation(); // Prevent thread selection
    setDeleteConfirm(thread);
  };

  const handleConfirmDelete = () => {
    if (deleteConfirm && onDeleteThread) {
      onDeleteThread(deleteConfirm.thread_guid);
    }
    setDeleteConfirm(null);
  };

  const handleCancelDelete = () => {
    setDeleteConfirm(null);
  };

  return (
    <>
      <ChatListContainer>
        {threads.map((thread) => {
          const isSelected = selectedThread?.thread_guid === thread.thread_guid;
          
          return (
            <ChatItem
              key={thread.thread_guid}
              selected={isSelected}
              onClick={() => onThreadSelect(thread)}
            >
              <ChatContent>
                <ChatHeader>
                  <ChatName selected={isSelected}>
                    {thread.thread_name}
                  </ChatName>
                  <ChatTime selected={isSelected}>
                    {formatTime(thread.last_updated)}
                  </ChatTime>
                </ChatHeader>
                <ChatPreview selected={isSelected}>
                  <span>{thread.last_message?.text || 'No messages'}</span>
                  {thread.unread_count > 0 && (
                    <UnreadBadge selected={isSelected}>
                      {thread.unread_count}
                    </UnreadBadge>
                  )}
                </ChatPreview>
              </ChatContent>
              
              <DeleteButton
                className="delete-button"
                selected={isSelected}
                onClick={(e) => handleDeleteClick(e, thread)}
                title="Delete conversation"
              >
                ×
              </DeleteButton>
            </ChatItem>
          );
        })}
      </ChatListContainer>

      <ConfirmDialog
        isOpen={!!deleteConfirm}
        title="Delete Conversation"
        message={`Are you sure you want to delete the conversation with "${deleteConfirm?.thread_name}"? This will only remove it from your view, not from the server.`}
        onConfirm={handleConfirmDelete}
        onCancel={handleCancelDelete}
        confirmText="Delete"
        cancelText="Cancel"
      />
    </>
  );
}

export default ChatList;