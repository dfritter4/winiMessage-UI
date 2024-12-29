import tkinter as tk
import re
import webbrowser
from typing import List, Tuple, Dict, Any
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
        self.text = text
        self._link_regions = []
        
    def create_content(self, canvas: tk.Canvas, x: int, y: int, width: int, **kwargs) -> Tuple[int, int]:
        """Create text content with clickable links and return its dimensions."""
        style = kwargs.get('style')
        is_outgoing = kwargs.get('is_outgoing', False)
        
        if not style:
            return (0, 0)
        
        # Parse text for links
        segments = self._parse_text()
        
        # Create complete text first to get proper wrapping
        text_item = canvas.create_text(
            x, y,
            text=self.text,
            anchor="nw",
            fill=style.get_text_color(is_outgoing),
            width=width,
            font=(kwargs.get('font_family', "SF Pro"),
                  kwargs.get('font_size', 13))
        )
        
        bbox = canvas.bbox(text_item)
        if not bbox:
            return (0, 0)
        
        # Store link regions for click handling
        self._link_regions = []
        for segment in segments:
            if segment.is_link:
                # Get coordinates for this segment
                text_before = self.text[:segment.start_index]
                text_during = self.text[segment.start_index:segment.end_index]
                
                # Create temporary text to measure position
                temp = canvas.create_text(
                    x, y,
                    text=text_before,
                    anchor="nw",
                    width=width,
                    font=(kwargs.get('font_family', "SF Pro"),
                          kwargs.get('font_size', 13))
                )
                temp_bbox = canvas.bbox(temp)
                canvas.delete(temp)
                
                if temp_bbox:
                    link_x = temp_bbox[2]
                    link_y = temp_bbox[1]
                    
                    # Create temporary text for link width
                    temp_link = canvas.create_text(
                        link_x, link_y,
                        text=text_during,
                        anchor="nw",
                        width=width,
                        font=(kwargs.get('font_family', "SF Pro"),
                              kwargs.get('font_size', 13))
                    )
                    link_bbox = canvas.bbox(temp_link)
                    canvas.delete(temp_link)
                    
                    if link_bbox:
                        # Store link region
                        self._link_regions.append({
                            'url': segment.text,
                            'x1': link_bbox[0],
                            'y1': link_bbox[1],
                            'x2': link_bbox[2],
                            'y2': link_bbox[3]
                        })
                        
                        # Draw underline
                        canvas.create_line(
                            link_bbox[0], link_bbox[3],
                            link_bbox[2], link_bbox[3],
                            fill="#0000EE" if not is_outgoing else "#FFFFFF",
                            width=1
                        )
        
        return (bbox[2] - bbox[0], bbox[3] - bbox[1])
    
    def _parse_text(self) -> List[TextSegment]:
        """Parse text and return a list of TextSegments identifying regular text and URLs."""
        if not self.text:
            return []
            
        segments = []
        last_end = 0
        
        for match in re.finditer(self.URL_PATTERN, self.text):
            start, end = match.span()
            
            # Add non-link text before the URL if exists
            if start > last_end:
                segments.append(TextSegment(
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
            
            segments.append(TextSegment(
                text=url_text,
                is_link=True,
                start_index=start,
                end_index=end
            ))
            
            last_end = end
        
        # Add remaining text if exists
        if last_end < len(self.text):
            segments.append(TextSegment(
                text=self.text[last_end:],
                is_link=False,
                start_index=last_end,
                end_index=len(self.text)
            ))
        
        return segments
    
    def handle_click(self, x: int, y: int) -> bool:
        """Handle click events for links."""
        for region in self._link_regions:
            if (region['x1'] <= x <= region['x2'] and 
                region['y1'] <= y <= region['y2']):
                try:
                    webbrowser.open(region['url'])
                    return True
                except Exception as e:
                    print(f"Error opening URL {region['url']}: {e}")
        return False