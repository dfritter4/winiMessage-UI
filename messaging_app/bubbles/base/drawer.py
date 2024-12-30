import tkinter as tk
from typing import List, Tuple
from ..interfaces import IBubbleDrawer

class DefaultBubbleDrawer(IBubbleDrawer):
    """Default implementation for drawing bubble shapes."""
    
    def draw_bubble(self, canvas: tk.Canvas, x: int, y: int, width: int, height: int, **kwargs) -> None:
        """Draw the bubble shape on the canvas with rounded corners.

        Args:
            canvas: The canvas to draw on
            x: The x coordinate to start drawing
            y: The y coordinate to start drawing
            width: The width of the bubble
            height: The height of the bubble
            **kwargs: Additional drawing arguments including:
                - radius: Corner radius (default: 12)
                - fill: Fill color
                - outline: Outline color
                - tags: Canvas tags to apply
                - is_outgoing: Whether this is an outgoing message
        """
        # Default to 12px radius for modern look
        radius = kwargs.get('radius', 12)

        # Ensure the radius does not exceed half of the bubble's dimensions
        radius = min(radius, width / 2, height / 2)

        # Create points for rounded corners
        points = self._create_rounded_rectangle_points(x, y, width, height, radius)

        # Draw the bubble shape with smooth curves
        bubble = canvas.create_polygon(
            points,
            smooth=True,
            splinesteps=32,  # Increase smoothness
            **{k: v for k, v in kwargs.items() if k not in ['radius', 'is_outgoing']}
        )

        # Optionally, add an outline if specified
        if 'outline' in kwargs:
            canvas.itemconfig(bubble, outline=kwargs['outline'])
    
    def _create_rounded_rectangle_points(self, 
                                      x: int, 
                                      y: int, 
                                      width: int, 
                                      height: int, 
                                      radius: int) -> List[int]:
        """Create points for a rounded rectangle shape with smoother corners.

        Args:
            x: Starting x coordinate
            y: Starting y coordinate
            width: Width of the rectangle
            height: Height of the rectangle
            radius: Corner radius

        Returns:
            List[int]: List of x,y coordinates for the polygon
        """
        import math
        x2 = x + width
        y2 = y + height
        points = []

        # Number of points to use for each corner
        steps = 8

        # Helper function to add arc points
        def add_corner_points(center_x, center_y, start_angle, end_angle):
            for i in range(steps + 1):
                theta = math.radians(start_angle + (i * (end_angle - start_angle) / steps))
                px = center_x + radius * math.cos(theta)
                py = center_y + radius * math.sin(theta)
                points.extend([px, py])

        # Top left corner
        add_corner_points(x + radius, y + radius, 180, 270)

        # Top right corner
        add_corner_points(x2 - radius, y + radius, 270, 360)

        # Bottom right corner
        add_corner_points(x2 - radius, y2 - radius, 0, 90)

        # Bottom left corner
        add_corner_points(x + radius, y2 - radius, 90, 180)

        return points