import React from 'react';
import styled from 'styled-components';

const ReactionBubble = styled.div`
  display: inline-flex;
  align-items: center;
  background-color: #ffffff;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 2px 6px;
  margin: 2px;
  font-size: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background-color: #f8f8f8;
    transform: scale(1.05);
  }
`;

const ReactionEmoji = styled.span`
  font-size: 14px;
  margin-right: 2px;
`;

const ReactionCount = styled.span`
  color: #666;
  font-weight: 500;
`;

const ReactionsContainer = styled.div`
  display: flex;
  flex-wrap: wrap;
  margin-top: 4px;
  margin-left: ${props => props.isOutgoing ? 'auto' : '0'};
  margin-right: ${props => props.isOutgoing ? '0' : 'auto'};
  max-width: fit-content;
`;

// Map reaction types to emojis and labels
const REACTION_MAP = {
  'love': { emoji: '❤️', label: 'Love' },
  'like': { emoji: '👍', label: 'Like' },
  'dislike': { emoji: '👎', label: 'Dislike' },
  'laugh': { emoji: '😂', label: 'Ha Ha' },
  'emphasize': { emoji: '!!', label: 'Emphasized' },
  'question': { emoji: '?', label: 'Questioned' },
  // iMessage-specific reactions
  'haha': { emoji: '😂', label: 'Ha Ha' },
  'heart': { emoji: '❤️', label: 'Loved' },
  'thumbs_up': { emoji: '👍', label: 'Liked' },
  'thumbs_down': { emoji: '👎', label: 'Disliked' },
  'exclamation': { emoji: '!!', label: 'Emphasized' },
  'question_mark': { emoji: '?', label: 'Questioned' }
};

function Reaction({ reaction, onClick }) {
  const reactionInfo = REACTION_MAP[reaction.type] || { emoji: '👍', label: 'Reaction' };
  
  return (
    <ReactionBubble 
      onClick={onClick}
      title={`${reactionInfo.label} by ${reaction.reactors?.join(', ') || 'someone'}`}
    >
      <ReactionEmoji>{reactionInfo.emoji}</ReactionEmoji>
      {reaction.count > 1 && <ReactionCount>{reaction.count}</ReactionCount>}
    </ReactionBubble>
  );
}

function Reactions({ reactions, isOutgoing, onReactionClick }) {
  if (!reactions || reactions.length === 0) {
    return null;
  }

  return (
    <ReactionsContainer isOutgoing={isOutgoing}>
      {reactions.map((reaction, index) => (
        <Reaction
          key={`${reaction.type}-${index}`}
          reaction={reaction}
          onClick={() => onReactionClick && onReactionClick(reaction)}
        />
      ))}
    </ReactionsContainer>
  );
}

export default Reactions;