import React from 'react';
import styled from 'styled-components';
import { makeTextClickable } from '../utils/linkUtils';

const TextContainer = styled.span`
  word-wrap: break-word;
`;

const ClickableLink = styled.span`
  color: ${props => props.isOutgoing ? 'rgba(255,255,255,0.9)' : '#007AFF'};
  text-decoration: underline;
  cursor: pointer;
  
  &:hover {
    text-decoration: none;
  }
`;

function ClickableText({ text, isOutgoing, onLinkClick }) {
  const handleLinkClick = (url) => {
    if (onLinkClick) {
      onLinkClick(url);
    } else {
      // Default behavior: open in external browser
      if (window.electron) {
        window.electron.shell.openExternal(url);
      } else {
        window.open(url, '_blank', 'noopener,noreferrer');
      }
    }
  };

  const parts = makeTextClickable(text);
  
  if (typeof parts === 'string') {
    // No links found, return plain text
    return <TextContainer>{text}</TextContainer>;
  }

  return (
    <TextContainer>
      {parts.map((part, index) => {
        if (typeof part === 'string') {
          return part;
        } else if (part.type === 'link') {
          return (
            <ClickableLink
              key={part.key}
              isOutgoing={isOutgoing}
              onClick={() => handleLinkClick(part.url)}
            >
              {part.text}
            </ClickableLink>
          );
        }
        return null;
      })}
    </TextContainer>
  );
}

export default ClickableText;