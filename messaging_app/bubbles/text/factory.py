import tkinter as tk
from typing import Optional
from ..interfaces import IBubbleStyle
from .content import TextContent
from .bubble import TextBubble

class TextBubbleFactory:
    """Factory for creating text bubbles."""
    
    @staticmethod
    def create(parent: tk.Widget,
              text: str,
              style: Optional[IBubbleStyle] = None,
              **kwargs) -> TextBubble:
        """Create a TextBubble instance.
        
        Args:
            parent: The parent widget
            text: The text content to display
            style: Bubble style configuration
            **kwargs: Additional arguments passed to TextBubble
        
        Returns:
            TextBubble: A configured text bubble instance
        """
        if not style:
            from ..base.style import DefaultBubbleStyle
            style = DefaultBubbleStyle()
        
        content = TextContent(text)
        return TextBubble(parent, content, style, **kwargs)