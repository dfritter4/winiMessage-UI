import tkinter as tk
from typing import Optional
from ..base.bubble import BaseBubble
from ..interfaces import IBubbleStyle
from .content import EnhancedTextContent

class EnhancedTextBubble(BaseBubble):
    """A text bubble with clickable links."""
    
    def __init__(self,
                 parent: tk.Widget,
                 content: EnhancedTextContent,
                 style: IBubbleStyle,
                 is_outgoing: bool = False,
                 timestamp: Optional[float] = None,
                 sender_name: Optional[str] = None,
                 **kwargs):
        super().__init__(
            parent=parent,
            content=content,
            style=style,
            is_outgoing=is_outgoing,
            timestamp=timestamp,
            sender_name=sender_name,
            **kwargs
        )
        
        # Set up event bindings for link interaction
        self.bind("<Motion>", self._on_motion)
        self.bind("<Button-1>", self._on_click)
    
    def _on_motion(self, event) -> None:
        """Handle mouse motion to update cursor for links."""
        x, y = event.x, event.y
        for region in self.content._link_regions:
            if (region['x1'] <= x <= region['x2'] and 
                region['y1'] <= y <= region['y2']):
                self.configure(cursor="hand2")
                return
        self.configure(cursor="")
    
    def _on_click(self, event) -> None:
        """Handle click events to open links."""
        self.content.handle_click(event.x, event.y)