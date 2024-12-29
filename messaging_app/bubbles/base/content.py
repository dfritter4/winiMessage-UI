import tkinter as tk
from typing import Tuple
from ..interfaces import IBubbleContent

class BaseContent(IBubbleContent):
    """Base class for bubble content implementations."""
    
    def create_content(self, canvas: tk.Canvas, x: int, y: int, width: int, **kwargs) -> Tuple[int, int]:
        """
        Create the content on the canvas.
        
        Args:
            canvas: The canvas to draw on
            x: The x coordinate to start drawing
            y: The y coordinate to start drawing
            width: The maximum width allowed
            **kwargs: Additional arguments including:
                - style: The bubble style
                - is_outgoing: Whether this is an outgoing message
                - font_family: The font family to use
                - font_size: The font size to use
        
        Returns:
            Tuple[int, int]: The (width, height) of the created content
        """
        return (0, 0)  # Base implementation creates no content