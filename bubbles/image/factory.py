import tkinter as tk
from typing import Optional
from ..interfaces import IBubbleStyle
from .content import ImageContent
from .bubble import ImageBubble

class ImageBubbleFactory:
    """Factory for creating image bubbles."""
    
    @staticmethod
    def create(parent: tk.Widget,
              image_url: str,
              text: Optional[str] = None,
              style: Optional[IBubbleStyle] = None,
              **kwargs) -> ImageBubble:
        """Create an ImageBubble instance.
        
        Args:
            parent: The parent widget
            image_url: URL of the image to display
            text: Optional caption text
            style: Bubble style configuration
            **kwargs: Additional arguments passed to ImageBubble
        
        Returns:
            ImageBubble: A configured image bubble instance
        """
        if not style:
            from ..base.style import DefaultBubbleStyle
            style = DefaultBubbleStyle()
        
        content = ImageContent(image_url, text)
        return ImageBubble(parent, content, style, **kwargs)