import tkinter as tk
import re
import webbrowser
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass

from ..interfaces import IBubbleContent

@dataclass
class TextSegment:
    """Represents a segment of text that may be a link."""
    text: str
    is_link: bool
    start_index: int
    end_index: int

class EnhancedTextContent(IBubbleContent):
    """Handles text content with clickable links."""
    
    # URL pattern for link detection
    URL_PATTERN = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+(?:[^\s,.!?]*[^\s,.!?:])?'
    
    def __init__(self, text: str):
        # Ensure text is a string and strip whitespace
        self.text = str(text).strip() if text is not None else ""
        self._link_regions: List[Dict[str, Any]] = []
        self._segments: List[TextSegment] = []
        self._parse_text()  # Parse text segments once during initialization
        
    def create_content(self, canvas: tk.Canvas, x: int, y: int, width: int, **kwargs) -> Tuple[int, int]:
        """Create text content with clickable links and return its dimensions."""
        style = kwargs.get('style')
        is_outgoing = kwargs.get('is_outgoing', False)
        
        if not style:
            return (0, 0)
        
        font_family = kwargs.get('font_family', "SF Pro")
        font_size = kwargs.get('font_size', 13)
        text_font = (font_family, font_size)
        
        # Clear previous link regions
        self._link_regions = []
        
        # Track current y position
        current_y = y
        max_width = 0
        
        for segment in self._segments:
            # Create text item for this segment
            text_item = canvas.create_text(
                x, current_y,
                text=segment.text,
                anchor="nw",
                fill=style.get_text_color(is_outgoing),
                width=width,
                font=text_font
            )
            
            bbox = canvas.bbox(text_item)
            if not bbox:
                continue
                
            # Track maximum width
            max_width = max(max_width, bbox[2] - bbox[0])
            
            # If this is a link, store the region and add underline
            if segment.is_link:
                link_color = "#FFFFFF" if is_outgoing else "#0000EE"
                canvas.create_line(
                    bbox[0], bbox[3],
                    bbox[2], bbox[3],
                    fill=link_color,
                    width=1
                )
                
                self._link_regions.append({
                    'url': segment.text,
                    'x1': bbox[0],
                    'y1': bbox[1],
                    'x2': bbox[2],
                    'y2': bbox[3]
                })
                
                # Bind click events to the canvas
                canvas.tag_bind(text_item, '<Button-1>', 
                              lambda e, url=segment.text: self._handle_link_click(url))
                canvas.tag_bind(text_item, '<Enter>', 
                              lambda e: canvas.config(cursor='hand2'))
                canvas.tag_bind(text_item, '<Leave>', 
                              lambda e: canvas.config(cursor=''))
            
            # Update y position for next segment
            current_y = bbox[3] + 2  # Small spacing between segments
        
        total_height = current_y - y
        return (max_width, total_height)
    
    def _parse_text(self) -> None:
        """Parse text into segments of regular text and URLs."""
        self._segments = []
        last_end = 0
        
        # Find all URLs in the text
        for match in re.finditer(self.URL_PATTERN, self.text):
            start, end = match.span()
            
            # Add non-link text before the URL if exists
            if start > last_end:
                self._segments.append(TextSegment(
                    text=self.text[last_end:start],
                    is_link=False,
                    start_index=last_end,
                    end_index=start
                ))
            
            # Add the URL segment
            url_text = self.text[start:end]
            while url_text and url_text[-1] in '.,!?':
                url_text = url_text[:-1]
                end -= 1
            
            self._segments.append(TextSegment(
                text=url_text,
                is_link=True,
                start_index=start,
                end_index=end
            ))
            
            last_end = end
        
        # Add remaining text if exists
        if last_end < len(self.text):
            self._segments.append(TextSegment(
                text=self.text[last_end:],
                is_link=False,
                start_index=last_end,
                end_index=len(self.text)
            ))
    
    def _handle_link_click(self, url: str) -> None:
        """Handle click event on a link."""
        try:
            webbrowser.open(url)
        except Exception as e:
            print(f"Error opening URL {url}: {e}")
    
    def handle_click(self, x: int, y: int) -> bool:
        """Handle click events for links."""
        for region in self._link_regions:
            if (region['x1'] <= x <= region['x2'] and 
                region['y1'] <= y <= region['y2']):
                self._handle_link_click(region['url'])
                return True
        return False

    def get_link_at(self, x: int, y: int) -> Optional[str]:
        """Get the URL at the given coordinates, if any."""
        for region in self._link_regions:
            if (region['x1'] <= x <= region['x2'] and 
                region['y1'] <= y <= region['y2']):
                return region['url']
        return None