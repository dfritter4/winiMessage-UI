import React, { useState, useEffect } from 'react';
import styled from 'styled-components';

const LinkPreviewContainer = styled.div`
  margin-top: 8px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  max-width: 300px;
  background-color: #ffffff;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    border-color: #007AFF;
    box-shadow: 0 2px 8px rgba(0, 122, 255, 0.1);
  }
`;

const LinkPreviewImage = styled.img`
  width: 100%;
  height: 150px;
  object-fit: cover;
  display: block;
`;

const LinkPreviewContent = styled.div`
  padding: 12px;
`;

const LinkPreviewTitle = styled.div`
  font-weight: 600;
  font-size: 14px;
  color: #333;
  margin-bottom: 4px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
`;

const LinkPreviewDescription = styled.div`
  font-size: 12px;
  color: #666;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 6px;
`;

const LinkPreviewUrl = styled.div`
  font-size: 11px;
  color: #007AFF;
  text-transform: lowercase;
`;

const LoadingPreview = styled.div`
  padding: 12px;
  text-align: center;
  color: #666;
  font-size: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  margin-top: 8px;
  max-width: 300px;
`;

const ErrorPreview = styled.a`
  display: inline-block;
  color: #007AFF;
  text-decoration: underline;
  margin-top: 4px;
  font-size: 14px;
  
  &:hover {
    text-decoration: none;
  }
`;

function LinkPreview({ url, isOutgoing }) {
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    fetchLinkPreview(url);
  }, [url]);

  const fetchLinkPreview = async (url) => {
    try {
      setLoading(true);
      setError(false);

      // Create enhanced preview based on domain
      const domain = extractDomainFromUrl(url);
      const preview = createEnhancedPreview(url, domain);
      
      setPreview(preview);
    } catch (err) {
      console.log('Link preview failed:', err);
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  const createEnhancedPreview = (url, domain) => {
    // Enhanced previews for popular sites
    const siteConfig = {
      'youtube.com': {
        title: 'YouTube Video',
        description: 'Watch on YouTube',
        icon: '🎥'
      },
      'youtu.be': {
        title: 'YouTube Video', 
        description: 'Watch on YouTube',
        icon: '🎥'
      },
      'twitter.com': {
        title: 'Twitter Post',
        description: 'View on Twitter',
        icon: '🐦'
      },
      'x.com': {
        title: 'X Post',
        description: 'View on X',
        icon: '🐦'
      },
      'github.com': {
        title: 'GitHub Repository',
        description: 'View on GitHub',
        icon: '💻'
      },
      'reddit.com': {
        title: 'Reddit Post',
        description: 'View on Reddit',
        icon: '🤖'
      },
      'instagram.com': {
        title: 'Instagram Post',
        description: 'View on Instagram',
        icon: '📸'
      },
      'tiktok.com': {
        title: 'TikTok Video',
        description: 'Watch on TikTok',
        icon: '🎵'
      },
      'spotify.com': {
        title: 'Spotify Track',
        description: 'Listen on Spotify',
        icon: '🎵'
      },
      'news.ycombinator.com': {
        title: 'Hacker News',
        description: 'View on Hacker News',
        icon: '📰'
      }
    };

    const config = siteConfig[domain] || {
      title: domain.charAt(0).toUpperCase() + domain.slice(1),
      description: 'Open link',
      icon: '🔗'
    };

    return {
      title: `${config.icon} ${config.title}`,
      description: config.description,
      image: null,
      url: url
    };
  };

  const extractDomainFromUrl = (url) => {
    try {
      const domain = new URL(url).hostname;
      return domain.replace('www.', '');
    } catch {
      return url;
    }
  };

  const handleClick = () => {
    // Open link in external browser
    if (window.electron) {
      window.electron.shell.openExternal(url);
    } else {
      window.open(url, '_blank', 'noopener,noreferrer');
    }
  };

  if (loading) {
    return (
      <LoadingPreview>
        Loading link preview...
      </LoadingPreview>
    );
  }

  if (error || !preview) {
    return (
      <ErrorPreview 
        href={url} 
        target="_blank" 
        rel="noopener noreferrer"
        onClick={(e) => {
          e.preventDefault();
          handleClick();
        }}
      >
        {url}
      </ErrorPreview>
    );
  }

  return (
    <LinkPreviewContainer onClick={handleClick}>
      {preview.image && (
        <LinkPreviewImage 
          src={preview.image} 
          alt={preview.title}
          onError={(e) => {
            e.target.style.display = 'none';
          }}
        />
      )}
      <LinkPreviewContent>
        <LinkPreviewTitle>{preview.title}</LinkPreviewTitle>
        {preview.description && (
          <LinkPreviewDescription>{preview.description}</LinkPreviewDescription>
        )}
        <LinkPreviewUrl>{extractDomainFromUrl(preview.url)}</LinkPreviewUrl>
      </LinkPreviewContent>
    </LinkPreviewContainer>
  );
}

export default LinkPreview;