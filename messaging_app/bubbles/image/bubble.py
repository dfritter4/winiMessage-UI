import tkinter as tk
from typing import Optional
from ..base.bubble import BaseBubble
from ..interfaces import IBubbleStyle
from .content import ImageContent

class ImageBubble(BaseBubble):
    """A bubble for displaying images with optional text captions."""
    
    def __init__(self,
                 parent: tk.Widget,
                 content: ImageContent,
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
        
        # Set up event binding for image preview
        self.tag_bind("image", "<Button-1>", lambda e: self.content._show_image_preview(self))