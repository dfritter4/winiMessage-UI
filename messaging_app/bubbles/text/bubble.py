from typing import Optional
from ..base.bubble import BaseBubble
from ..interfaces import IBubbleStyle
from .content import TextContent
import tkinter as tk

class TextBubble(BaseBubble):
    """A basic text message bubble."""
    
    def __init__(self,
                 parent: tk.Widget,
                 content: TextContent,
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