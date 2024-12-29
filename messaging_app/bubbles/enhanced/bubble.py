import tkinter as tk
from typing import Optional
from ..base.bubble import BaseBubble
from ..interfaces import IBubbleStyle
from .content import EnhancedTextContent

class EnhancedTextBubble(BaseBubble):
    """A text bubble with clickable links."""
    
    def __init__(
        self,
        parent: tk.Widget,
        content: str,
        style: Optional[IBubbleStyle] = None,
        is_outgoing: bool = False,
        timestamp: Optional[float] = None,
        sender_name: Optional[str] = None,
        **kwargs
    ):
        # Ensure style is set
        if style is None:
            from messaging_app.bubbles.base.style import DefaultBubbleStyle
            style = DefaultBubbleStyle()
        
        # Create content handler
        content_handler = EnhancedTextContent(content)
        
        super().__init__(
            parent=parent,
            content=content_handler,
            style=style,
            is_outgoing=is_outgoing,
            timestamp=timestamp,
            sender_name=sender_name,
            **kwargs
        )