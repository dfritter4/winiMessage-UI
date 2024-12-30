import tkinter as tk
import re
import webbrowser
from typing import List, Optional, Tuple
from dataclasses import dataclass
from .interfaces import IBubbleContent

@dataclass
class TextSegment:
    """Represents a segment of text that may be a link."""
    text: str
    is_link: bool
    start_index: int
    end_index: int

class TextParser:
    """Parses text to identify special segments like URLs."""
    
    URL_PATTERN = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+(?:[^\s,.!?]*[^\s,.!?:])?'
    
    @classmethod
    def parse_text(cls, text: str) -> List[TextSegment]:
        """Parse text and return a list of TextSegments."""
        if not text:
            return []
            
        segments = []
        last_end = 0
        
        for match in re.finditer(cls.URL_PATTERN, text):
            start, end = match.span()
            
            # Add non-link text before the URL if it exists
            if start > last_end:
                segments.append(TextSegment(
                    text=text[last_end:start],
                    is_link=False,
                    start_index=last_end,
                    end_index=start
                ))
            
            # Add the URL segment
            url_text = text[start:end]
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

class BasicTextContent(IBubbleContent):
    """Handles basic text content without link parsing."""
    
    def __init__(self, text: str):
        self.text = text

    def create_content(self, canvas: tk.Canvas, x: int, y: int, width: int, **kwargs) -> Tuple[int, int]:
        """Create basic text content and return its dimensions."""
        style = kwargs.get('style')
        is_outgoing = kwargs.get('is_outgoing', False)
        
        if not style:
            return (0, 0)
            
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
            
        return (bbox[2] - bbox[0], bbox[3] - bbox[1])

class EnhancedTextContent(IBubbleContent):
    """Handles text content with clickable links."""
    
    def __init__(self, text: str, parser: Optional[TextParser] = None):
        # Ensure text is a string
        self.text = str(text).strip() if text is not None else ""
        self.parser = parser or TextParser()
        self._link_regions = []
        
    def create_content(self, canvas: tk.Canvas, x: int, y: int, width: int, **kwargs) -> Tuple[int, int]:
        """Create text content with clickable links and return its dimensions."""
        style = kwargs.get('style')
        is_outgoing = kwargs.get('is_outgoing', False)
        
        if not style:
            return (0, 0)
            
        # Parse text for links
        segments = self.parser.parse_text(self.text)
        
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
    
    def handle_click(self, x: int, y: int) -> bool:
        """Handle click events for links."""
        for region in self._link_regions:
            if (region['x1'] <= x <= region['x2'] and 
                region['y1'] <= y <= region['y2']):
                webbrowser.open(region['url'])
                return True
        return False
    
    def get_link_at(self, x: int, y: int) -> Optional[str]:
        """Get the URL at the given coordinates, if any."""
        for region in self._link_regions:
            if (region['x1'] <= x <= region['x2'] and 
                region['y1'] <= y <= region['y2']):
                return region['url']
        return None