import tkinter as tk
from typing import Optional
from datetime import datetime
from ..interfaces import IBubbleStyle
from .content import TextContent

class TextBubble(tk.Canvas):
    """A basic text message bubble."""
    
    def __init__(self,
                 parent: tk.Widget,
                 content: TextContent,
                 style: IBubbleStyle,
                 is_outgoing: bool = False,
                 timestamp: Optional[float] = None,
                 sender_name: Optional[str] = None,
                 **kwargs):
        kwargs.pop('width', None)
        kwargs.pop('height', None)
        super().__init__(parent,
                        highlightthickness=0,
                        bg=style.get_background_color(is_outgoing),
                        **kwargs)
        
        self.content = content
        self.style = style
        self.is_outgoing = is_outgoing
        self.timestamp = timestamp
        self.sender_name = sender_name
        self.padding = 12
        
        self._create_bubble()
    
    def _create_bubble(self) -> None:
        """Create the complete bubble with all components."""
        # Clear canvas
        self.delete("all")
        
        # Calculate sender name height
        sender_height = self._add_sender_name() if self.sender_name else 0
        
        # Create content
        content_width, content_height = self.content.create_content(
            self,
            self.padding,
            sender_height + self.padding,
            300,  # Max width
            style=self.style,
            is_outgoing=self.is_outgoing,
            font_family="SF Pro"
        )
        
        # Calculate total dimensions
        total_width = content_width + (self.padding * 2)
        total_height = (
            sender_height +
            content_height +
            (self.padding * 2) +
            (20 if self.timestamp else 0)  # Extra space for timestamp
        )
        
        # Configure canvas size
        self.configure(
            width=total_width,
            height=total_height
        )
        
        # Draw bubble background
        self._draw_bubble_background(0, 0, total_width, total_height)
        
        # Add timestamp if present
        if self.timestamp:
            self._add_timestamp(0, total_width, total_height - 15)
    
    def _add_sender_name(self) -> int:
        """Add sender name and return its height."""
        if self.sender_name and not self.is_outgoing:
            text_item = self.create_text(
                self.padding,
                2,
                text=self.sender_name,
                anchor="nw",
                fill=self.style.get_sender_name_color(),
                font=("SF Pro", 11, "bold")
            )
            bbox = self.bbox(text_item)
            return (bbox[3] - bbox[1] + 5) if bbox else 20
        return 0
    
    def _draw_bubble_background(self,
                              x: int,
                              y: int,
                              width: int,
                              height: int) -> None:
        """Draw the bubble background with rounded corners."""
        radius = min(15, min(width, height) / 4)
        points = [
            x + radius, y,
            x + width - radius, y,
            x + width, y,
            x + width, y + radius,
            x + width, y + height - radius,
            x + width, y + height,
            x + width - radius, y + height,
            x + radius, y + height,
            x, y + height,
            x, y + height - radius,
            x, y + radius,
            x, y,
            x + radius, y
        ]
        self.create_polygon(
            points,
            smooth=True,
            fill=self.style.get_background_color(self.is_outgoing)
        )
    
    def _add_timestamp(self,
                      x: int,
                      width: int,
                      y_position: int) -> None:
        """Add timestamp to the bubble."""
        if self.timestamp:
            try:
                time_str = datetime.fromtimestamp(self.timestamp).strftime("%I:%M %p")
                if time_str.startswith("0"):
                    time_str = time_str[1:]
                self.create_text(
                    x + width - self.padding,
                    y_position,
                    text=time_str,
                    anchor="se",
                    fill=self.style.get_timestamp_color(),
                    font=("SF Pro", 9)
                )
            except Exception as e:
                print(f"Error formatting timestamp: {e}")