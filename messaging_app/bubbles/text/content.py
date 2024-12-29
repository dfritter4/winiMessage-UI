import tkinter as tk
from typing import Dict, Any, Tuple
from ..interfaces import IBubbleContent

class TextContent(IBubbleContent):
    """Handles basic text content for message bubbles."""
    
    def __init__(self, text: str):
        self.text = text

    def create_content(self, canvas: tk.Canvas, x: int, y: int, width: int, **kwargs) -> Tuple[int, int]:
        """Create the text content and return its dimensions."""
        style = kwargs.get('style')
        is_outgoing = kwargs.get('is_outgoing', False)
        
        if not style:
            return (0, 0)
        
        # Create text element
        text_item = canvas.create_text(
            x, y,
            text=self.text,
            anchor="nw",
            fill=style.get_text_color(is_outgoing),
            width=width,
            font=(kwargs.get('font_family', "SF Pro"),
                  kwargs.get('font_size', 13))
        )
        
        # Get dimensions
        bbox = canvas.bbox(text_item)
        if not bbox:
            return (0, 0)
        
        return (bbox[2] - bbox[0], bbox[3] - bbox[1])