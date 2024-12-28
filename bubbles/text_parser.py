# bubbles/text_parser.py
import re
import webbrowser
from dataclasses import dataclass
from typing import List, Tuple, Callable

@dataclass
class TextSegment:
    text: str
    is_link: bool
    start_index: int
    end_index: int

class TextParser:
    """Handles parsing text to identify special segments like URLs."""
    
    # Updated URL pattern to match more complete URLs
    URL_PATTERN = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+(?:[^\s,.!?]*[^\s,.!?:])?'
    
    @classmethod
    def parse_text(cls, text: str) -> List[TextSegment]:
        """Parse text and return a list of TextSegments identifying regular text and URLs."""
        if not text:
            return []
            
        segments = []
        last_end = 0
        
        for match in re.finditer(cls.URL_PATTERN, text):
            start, end = match.span()
            
            # Add non-link text before the URL if exists
            if start > last_end:
                segments.append(TextSegment(
                    text=text[last_end:start],
                    is_link=False,
                    start_index=last_end,
                    end_index=start
                ))
            
            # Add the URL segment - ensure we get the full URL
            url_text = text[start:end]
            # Remove any trailing punctuation that shouldn't be part of the URL
            while url_text and url_text[-1] in '.,!?':
                url_text = url_text[:-1]
                end -= 1
            
            segments.append(TextSegment(
                text=url_text,
                is_link=True,
                start_index=start,
                end_index=end
            ))
            
            last_end = end
        
        # Add remaining text if exists
        if last_end < len(text):
            segments.append(TextSegment(
                text=text[last_end:],
                is_link=False,
                start_index=last_end,
                end_index=len(text)
            ))
        
        return segments

class LinkHandler:
    """Handles operations related to links in text."""
    
    @staticmethod
    def open_link(url: str) -> None:
        """Open a URL in the default web browser."""
        try:
            webbrowser.open(url)
        except Exception as e:
            print(f"Error opening URL {url}: {e}")