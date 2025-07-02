// URL detection regex
const URL_REGEX = /(https?:\/\/[^\s]+)/g;

// More comprehensive URL detection including www. and common TLDs
const COMPREHENSIVE_URL_REGEX = /(https?:\/\/[^\s]+|www\.[^\s]+\.[a-zA-Z]{2,}|[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]*\.([a-zA-Z]{2,})\b[^\s]*)/g;

export const detectUrls = (text) => {
  if (!text) return [];
  
  const urls = [];
  let match;
  
  // Reset regex lastIndex
  COMPREHENSIVE_URL_REGEX.lastIndex = 0;
  
  while ((match = COMPREHENSIVE_URL_REGEX.exec(text)) !== null) {
    let url = match[0];
    
    // Add protocol if missing
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      url = 'https://' + url;
    }
    
    // Remove trailing punctuation
    url = url.replace(/[.,;:!?]+$/, '');
    
    urls.push({
      original: match[0],
      normalized: url,
      startIndex: match.index,
      endIndex: match.index + match[0].length
    });
  }
  
  return urls;
};

export const hasUrls = (text) => {
  return detectUrls(text).length > 0;
};

export const extractFirstUrl = (text) => {
  const urls = detectUrls(text);
  return urls.length > 0 ? urls[0].normalized : null;
};

export const makeTextClickable = (text, onLinkClick) => {
  if (!text) return text;
  
  const urls = detectUrls(text);
  if (urls.length === 0) return text;
  
  const parts = [];
  let lastIndex = 0;
  
  urls.forEach((urlInfo, index) => {
    // Add text before the URL
    if (urlInfo.startIndex > lastIndex) {
      parts.push(text.slice(lastIndex, urlInfo.startIndex));
    }
    
    // Add the clickable URL
    parts.push({
      type: 'link',
      text: urlInfo.original,
      url: urlInfo.normalized,
      key: `link-${index}`
    });
    
    lastIndex = urlInfo.endIndex;
  });
  
  // Add remaining text after last URL
  if (lastIndex < text.length) {
    parts.push(text.slice(lastIndex));
  }
  
  return parts;
};

// Simple link preview fetcher (fallback)
export const getSimpleLinkPreview = async (url) => {
  try {
    const domain = new URL(url).hostname.replace('www.', '');
    
    // Return a basic preview
    return {
      title: domain,
      description: url,
      image: null,
      url: url
    };
  } catch (error) {
    return {
      title: url,
      description: '',
      image: null,
      url: url
    };
  }
};