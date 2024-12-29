import tkinter as tk
from typing import Optional
from ..interfaces import IBubbleStyle
from .content import EnhancedTextContent
from .bubble import EnhancedTextBubble

class EnhancedTextBubbleFactory:
    """Factory for creating enhanced text bubbles with clickable links."""
    
    @staticmethod
    def create(parent: tk.Widget,
              text: str,
              style: Optional[IBubbleStyle] = None,
              **kwargs) -> EnhancedTextBubble:
        """Create an EnhancedTextBubble instance.
        
        Args:
            parent: The parent widget
            text: The text content to display
            style: Bubble style configuration
            **kwargs: Additional arguments passed to EnhancedTextBubble
        
        Returns:
            EnhancedTextBubble: A configured enhanced text bubble instance
        """
        if not style:
            from ..base.style import DefaultBubbleStyle
            style = DefaultBubbleStyle()
        
        content = EnhancedTextContent(text)
        return EnhancedTextBubble(parent, content, style, **kwargs)