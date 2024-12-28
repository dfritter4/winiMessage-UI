import tkinter as tk
from typing import List, Tuple
from ..interfaces import IBubbleDrawer

class DefaultBubbleDrawer(IBubbleDrawer):
    """Default implementation for drawing bubble shapes."""
    
    def draw_bubble(self, canvas: tk.Canvas, x: int, y: int, width: int, height: int, **kwargs) -> None:
        """Draw the bubble shape on the canvas.
        
        Args:
            canvas: The canvas to draw on
            x: The x coordinate to start drawing
            y: The y coordinate to start drawing
            width: The width of the bubble
            height: The height of the bubble
            **kwargs: Additional drawing arguments including:
                - radius: Corner radius (default: 15)
                - fill: Fill color
                - outline: Outline color
                - tags: Canvas tags to apply
        """
        radius = kwargs.get('radius', 15)
        
        # Ensure minimum size
        if width < radius * 2:
            radius = width / 2
        if height < radius * 2:
            radius = height / 2
            
        # Create points for rounded corners
        points = self._create_rounded_rectangle_points(x, y, width, height, radius)
        
        # Create the bubble shape
        canvas.create_polygon(
            points,
            smooth=True,
            **{k: v for k, v in kwargs.items() if k not in ['radius']}
        )
    
    def _create_rounded_rectangle_points(self, 
                                      x: int, 
                                      y: int, 
                                      width: int, 
                                      height: int, 
                                      radius: int) -> List[int]:
        """Create points for a rounded rectangle shape.
        
        Args:
            x: Starting x coordinate
            y: Starting y coordinate
            width: Width of the rectangle
            height: Height of the rectangle
            radius: Corner radius
            
        Returns:
            List[int]: List of x,y coordinates for the polygon
        """
        x2 = x + width
        y2 = y + height
        
        return [
            x + radius, y,              # Top edge start
            x2 - radius, y,             # Top edge end
            x2, y,                      # Top-right corner start
            x2, y + radius,             # Top-right corner end
            x2, y2 - radius,            # Bottom-right corner start
            x2, y2,                     # Bottom-right corner end
            x2 - radius, y2,            # Bottom edge start
            x + radius, y2,             # Bottom edge end
            x, y2,                      # Bottom-left corner start
            x, y2 - radius,             # Bottom-left corner end
            x, y + radius,              # Top-left corner start
            x, y,                       # Top-left corner end
            x + radius, y               # Close the shape
        ]