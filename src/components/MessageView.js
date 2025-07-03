import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import Reactions from './Reaction';
import LinkPreview from './LinkPreview';
import ClickableText from './ClickableText';
import CachedImage from './CachedImage';
import { extractFirstUrl } from '../utils/linkUtils';

const MessageViewContainer = styled.div`
  height: 100%;
  display: flex;
  flex-direction: column;
`;

const MessageHeader = styled.div`
  padding: 16px;
  border-bottom: 1px solid #e0e0e0;
  background-color: #fafafa;
  text-align: center;
`;

const ContactName = styled.h3`
  font-size: 16px;
  font-weight: 600;
  color: #333;
`;

const MessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background-color: #ffffff;
`;

const MessageGroup = styled.div`
  display: flex;
  flex-direction: column;
  max-width: 70%;
  margin: 8px 0;
  align-self: ${props => props.isOutgoing ? 'flex-end' : 'flex-start'};
  margin-left: ${props => props.isOutgoing ? 'auto' : '0'};
  margin-right: ${props => props.isOutgoing ? '0' : 'auto'};
`;

const MessageBubble = styled.div`
  padding: 12px 16px;
  border-radius: 18px;
  word-wrap: break-word;
  position: relative;
  background-color: ${props => props.isOutgoing ? '#007AFF' : '#E5E5EA'};
  color: ${props => props.isOutgoing ? 'white' : '#000'};
  margin-bottom: ${props => props.hasReactions ? '4px' : '0'};
`;

const MessageText = styled.div`
  font-size: 14px;
  line-height: 1.4;
`;

const AttachmentContainer = styled.div`
  margin-top: 8px;
`;

const AttachmentImage = styled.img`
  max-width: 300px;
  max-height: 200px;
  border-radius: 8px;
  cursor: pointer;
`;

const MessageTime = styled.div`
  font-size: 11px;
  color: ${props => props.isOutgoing ? 'rgba(255,255,255,0.7)' : '#666'};
  margin-top: 4px;
  text-align: ${props => props.isOutgoing ? 'right' : 'left'};
`;

const SenderName = styled.div`
  font-size: 11px;
  color: #666;
  margin-bottom: 4px;
  margin-left: ${props => props.isOutgoing ? 'auto' : '0'};
  margin-right: ${props => props.isOutgoing ? '0' : 'auto'};
  text-align: ${props => props.isOutgoing ? 'right' : 'left'};
`;

const InputContainer = styled.div`
  padding: 16px;
  border-top: 1px solid #e0e0e0;
  background-color: #fafafa;
  display: flex;
  align-items: center;
  gap: 12px;
`;

const MessageInput = styled.input`
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #d0d0d0;
  border-radius: 20px;
  font-size: 14px;
  outline: none;
  
  &:focus {
    border-color: #007AFF;
  }
`;

const SendButton = styled.button`
  background-color: #007AFF;
  color: white;
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  transition: background-color 0.2s ease;
  
  &:hover {
    background-color: #0056b3;
  }
  
  &:disabled {
    background-color: #ccc;
    cursor: not-allowed;
  }
`;

const EmptyState = styled.div`
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  font-size: 16px;
`;

const ErrorBanner = styled.div`
  padding: 12px 16px;
  background-color: #f8d7da;
  color: #721c24;
  border-bottom: 1px solid #f5c6cb;
  text-align: center;
  font-size: 14px;
`;

const ImageButton = styled.button`
  background-color: #f0f0f0;
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  transition: background-color 0.2s ease;
  
  &:hover {
    background-color: #e0e0e0;
  }
`;

const HiddenFileInput = styled.input`
  display: none;
`;

const ImagePreview = styled.div`
  position: relative;
  margin-bottom: 8px;
  border-radius: 8px;
  overflow: hidden;
  max-width: 200px;
`;

const PreviewImage = styled.img`
  width: 100%;
  height: auto;
  display: block;
`;

const RemoveImageButton = styled.button`
  position: absolute;
  top: 4px;
  right: 4px;
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  
  &:hover {
    background-color: rgba(0, 0, 0, 0.9);
  }
`;

const UploadingOverlay = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 12px;
`;

const formatMessageTime = (timestamp) => {
  const date = new Date(timestamp);
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

const isReactionMessage = (message) => {
  if (!message.text) return false;
  
  // Common patterns for iMessage reaction messages
  const reactionPatterns = [
    /^Reacted .+ to ".+"/,
    /^(Reacted|Loved|Liked|Disliked|Laughed at|Emphasized|Questioned) .+ to ["""].+["""]/,
    /^.+ reacted .+ to ["""].+["""]/i,
    /^.+ loved ["""].+["""]/i,
    /^.+ liked ["""].+["""]/i,
    /^.+ laughed at ["""].+["""]/i,
    /^.+ emphasized ["""].+["""]/i,
    /^.+ questioned ["""].+["""]/i,
    /^.+ disliked ["""].+["""]/i,
    /^Loved ["""].+["""]/i,
    /^Liked ["""].+["""]/i,
    /^Disliked ["""].+["""]/i,
    /^Laughed at ["""].+["""]/i,
    /^Emphasized ["""].+["""]/i,
    /^Questioned ["""].+["""]/i
  ];
  
  return reactionPatterns.some(pattern => pattern.test(message.text));
};

function MessageView({ selectedThread, messages, onSendMessage, error, loading }) {
  const [inputValue, setInputValue] = useState('');
  const [selectedImage, setSelectedImage] = useState(null);
  const [uploading, setUploading] = useState(false);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if ((!inputValue.trim() && !selectedImage) || !selectedThread) return;
    
    try {
      setUploading(true);
      
      let attachment = null;
      
      // Upload image if selected
      if (selectedImage) {
        attachment = await uploadImage(selectedImage);
      }
      
      // Send message
      onSendMessage({
        text: inputValue.trim() || undefined,
        thread_guid: selectedThread.thread_guid,
        attachment: attachment
      });
      
      // Clear inputs
      setInputValue('');
      setSelectedImage(null);
      
    } catch (error) {
      console.error('Failed to send message:', error);
      alert('Failed to send message: ' + error.message);
    } finally {
      setUploading(false);
    }
  };

  const uploadImage = async (file) => {
    const currentServerUrl = localStorage.getItem('winiMessage_serverUrl') || 'http://192.168.1.73:5001';
    
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${currentServerUrl}/attachments/upload`, {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
      throw new Error(`Upload failed: ${response.status}`);
    }
    
    const result = await response.json();
    return result.filename;
  };

  const handleImageSelect = (event) => {
    const file = event.target.files[0];
    if (file && file.type.startsWith('image/')) {
      setSelectedImage(file);
    }
    // Reset input to allow selecting same file again
    event.target.value = '';
  };

  const removeSelectedImage = () => {
    setSelectedImage(null);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSend();
    }
  };

  if (!selectedThread) {
    return (
      <MessageViewContainer>
        <EmptyState>
          Select a conversation to start messaging
        </EmptyState>
      </MessageViewContainer>
    );
  }

  return (
    <MessageViewContainer>
      <MessageHeader>
        <ContactName>{selectedThread.thread_name}</ContactName>
      </MessageHeader>
      
      {error && (
        <ErrorBanner>{error}</ErrorBanner>
      )}
      
      <MessagesContainer>
        {loading && (
          <div style={{ 
            display: 'flex', 
            justifyContent: 'center', 
            padding: '20px',
            color: '#666'
          }}>
            Loading messages...
          </div>
        )}
        
        {!loading && messages.length === 0 && (
          <div style={{ 
            display: 'flex', 
            justifyContent: 'center', 
            padding: '20px',
            color: '#666'
          }}>
            No messages in this conversation
          </div>
        )}
        
        {messages.filter(message => !isReactionMessage(message)).map((message, index) => {
          const isOutgoing = message.direction === 'outgoing';
          const showSender = !isOutgoing && selectedThread.participants.length > 2;
          const hasReactions = message.reactions && message.reactions.length > 0;
          
          return (
            <div key={message.guid || index}>
              {showSender && (
                <SenderName isOutgoing={isOutgoing}>
                  {message.sender_name}
                </SenderName>
              )}
              <MessageGroup isOutgoing={isOutgoing}>
                <MessageBubble isOutgoing={isOutgoing} hasReactions={hasReactions}>
                  {message.text && (
                    <MessageText>
                      <ClickableText 
                        text={message.text}
                        isOutgoing={isOutgoing}
                      />
                    </MessageText>
                  )}
                  {message.attachments && message.attachments.length > 0 && (
                    <AttachmentContainer>
                      {message.attachments.map((attachment, attachIndex) => {
                        if (attachment.mime_type?.startsWith('image/')) {
                          // Construct proper attachment URL
                          let imageUrl = attachment.attachment_url;
                          const currentServerUrl = localStorage.getItem('winiMessage_serverUrl') || process.env.REACT_APP_SERVER_URL || 'http://192.168.1.73:5001';
                          
                          // If it's already a full URL but with wrong IP, replace the base URL
                          if (imageUrl.startsWith('http')) {
                            try {
                              const urlObj = new URL(imageUrl);
                              const currentUrlObj = new URL(currentServerUrl);
                              
                              // Replace the hostname and port with current server
                              urlObj.hostname = currentUrlObj.hostname;
                              urlObj.port = currentUrlObj.port;
                              urlObj.protocol = currentUrlObj.protocol;
                              
                              imageUrl = urlObj.toString();
                            } catch (e) {
                              console.error('Failed to parse URL:', imageUrl, e);
                            }
                          } else {
                            // Handle relative URLs
                            if (imageUrl.startsWith('/attachments/')) {
                              imageUrl = currentServerUrl + imageUrl;
                            } else if (!imageUrl.startsWith('/')) {
                              imageUrl = `${currentServerUrl}/attachments/${imageUrl}`;
                            } else {
                              imageUrl = currentServerUrl + imageUrl;
                            }
                          }
                          
                          return (
                            <CachedImage
                              key={attachIndex}
                              src={imageUrl}
                              alt="Attachment"
                              onError={() => {
                                console.error('Failed to load cached image:', imageUrl);
                              }}
                              onLoad={() => {
                                console.log('Successfully loaded cached image:', imageUrl);
                              }}
                            />
                          );
                        }
                        return null;
                      })}
                    </AttachmentContainer>
                  )}
                  <MessageTime isOutgoing={isOutgoing}>
                    {formatMessageTime(message.timestamp)}
                  </MessageTime>
                </MessageBubble>
                
                {/* Link Preview */}
                {message.text && extractFirstUrl(message.text) && (
                  <LinkPreview 
                    url={extractFirstUrl(message.text)}
                    isOutgoing={isOutgoing}
                  />
                )}
                
                {hasReactions && (
                  <Reactions 
                    reactions={message.reactions}
                    isOutgoing={isOutgoing}
                    onReactionClick={(reaction) => {
                      console.log('Reaction clicked:', reaction);
                    }}
                  />
                )}
              </MessageGroup>
            </div>
          );
        })}
        <div ref={messagesEndRef} />
      </MessagesContainer>
      
      <InputContainer>
        {selectedImage && (
          <ImagePreview>
            <PreviewImage 
              src={URL.createObjectURL(selectedImage)} 
              alt="Selected image"
            />
            <RemoveImageButton onClick={removeSelectedImage}>
              ✕
            </RemoveImageButton>
            {uploading && (
              <UploadingOverlay>
                Uploading...
              </UploadingOverlay>
            )}
          </ImagePreview>
        )}
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', width: '100%' }}>
          <HiddenFileInput
            type="file"
            accept="image/*"
            onChange={handleImageSelect}
            ref={fileInputRef}
          />
          
          <ImageButton onClick={() => fileInputRef.current?.click()}>
            📷
          </ImageButton>
          
          <MessageInput
            type="text"
            placeholder="Type a message..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
          />
          
          <SendButton 
            onClick={handleSend}
            disabled={(!inputValue.trim() && !selectedImage) || uploading}
          >
            {uploading ? '⏳' : '▲'}
          </SendButton>
        </div>
      </InputContainer>
    </MessageViewContainer>
  );
}

export default MessageView;