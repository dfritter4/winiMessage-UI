import tkinter as tk
from typing import Optional
from datetime import datetime

import dateutil
from ..interfaces import IBubbleStyle, IBubbleContent, IBubbleDrawer
from .style import DefaultBubbleStyle
from .drawer import DefaultBubbleDrawer

class BaseBubble(tk.Canvas):
    """Base class for message bubbles.
    
    Provides common functionality for all bubble types including:
    - Basic layout and sizing
    - Sender name display
    - Timestamp display
    - Background drawing
    """
    
    def __init__(self,
                 parent: tk.Widget,
                 content: IBubbleContent,
                 style: Optional[IBubbleStyle] = None,
                 drawer: Optional[IBubbleDrawer] = None,
                 is_outgoing: bool = False,
                 timestamp: Optional[float] = None,
                 sender_name: Optional[str] = None,
                 **kwargs):
        # Remove size specifications from kwargs
        kwargs.pop('width', None)
        kwargs.pop('height', None)
        
        # Initialize canvas
        super().__init__(
            parent,
            highlightthickness=0,
            **kwargs
        )
        
        # Store components and properties
        self.content = content
        self.style = style or DefaultBubbleStyle()
        self.drawer = drawer or DefaultBubbleDrawer()
        self.is_outgoing = is_outgoing
        self.timestamp = timestamp
        self.sender_name = sender_name
        self.padding = 12
        
        # Configure background
        self.configure(bg=self.style.get_background_color(is_outgoing))
        
        # Create the bubble
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
        self.drawer.draw_bubble(
            self,
            0, 0,
            total_width,
            total_height,
            fill=self.style.get_background_color(self.is_outgoing)
        )
        
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
    
    def _add_timestamp(self,
                   x: int,
                   width: int,
                   y_position: int) -> None:
        """Add timestamp to the bubble."""
        if self.timestamp:
            try:
                # Try parsing the timestamp string
                if isinstance(self.timestamp, str):
                    # Use dateutil to parse various timestamp formats
                    parsed_timestamp = dateutil.parser.parse(self.timestamp)
                    timestamp = parsed_timestamp.timestamp()
                else:
                    # Ensure it's a float
                    timestamp = float(self.timestamp)
                
                time_str = datetime.fromtimestamp(timestamp).strftime("%I:%M %p")
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
    
    def update(self) -> None:
        """Update the bubble display."""
        self._create_bubble()