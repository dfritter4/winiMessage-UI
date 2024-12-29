import tkinter as tk
from datetime import datetime
from typing import Optional
from ..config import AppConfig
from .interfaces import IBubbleDrawer, IBubbleContent, IBubbleStyle

class DefaultBubbleStyle(IBubbleStyle):
    def __init__(self, config: AppConfig):
        self.config = config
    
    def get_background_color(self, is_outgoing: bool) -> str:
        return (self.config.colors.outgoing_bubble 
                if is_outgoing 
                else self.config.colors.incoming_bubble)
    
    def get_text_color(self, is_outgoing: bool) -> str:
        return (self.config.colors.outgoing_text 
                if is_outgoing 
                else self.config.colors.incoming_text)
    
    def get_timestamp_color(self) -> str:
        return self.config.colors.timestamp
    
    def get_sender_name_color(self) -> str:
        return self.config.colors.sender_name

class DefaultBubbleDrawer(IBubbleDrawer):
    def draw_bubble(self, canvas: tk.Canvas, x: int, y: int, width: int, height: int, **kwargs) -> None:
        is_outgoing = kwargs.get('is_outgoing', False)
        style = kwargs.get('style')
        if not style:
            return
            
        color = style.get_background_color(is_outgoing)
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
        
        canvas.create_polygon(points, smooth=True, fill=color)

class BaseBubble(tk.Canvas):
    """Base class for message bubbles."""
    
    def __init__(
        self,
        parent: tk.Widget,
        config: AppConfig,
        drawer: IBubbleDrawer,
        content_handler: IBubbleContent,
        style: IBubbleStyle,
        is_outgoing: bool = False,
        timestamp: Optional[float] = None,
        sender_name: Optional[str] = None,
        **kwargs
    ):
        # Remove size specs from kwargs
        kwargs.pop('width', None)
        kwargs.pop('height', None)
        
        super().__init__(
            parent,
            highlightthickness=0,
            bg=config.colors.background,
            **kwargs
        )
        
        self.config = config
        self.drawer = drawer
        self.content_handler = content_handler
        self.style = style
        self.is_outgoing = is_outgoing
        self.timestamp = self._parse_timestamp(timestamp)
        self.sender_name = sender_name
        self.padding = config.ui.bubble_padding

    def _parse_timestamp(self, timestamp: Optional[float]) -> Optional[float]:
        """Convert various timestamp formats to float."""
        if not timestamp:
            return None
            
        if isinstance(timestamp, (int, float)):
            return float(timestamp)
            
        if isinstance(timestamp, str):
            try:
                return float(timestamp)
            except ValueError:
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    return dt.timestamp()
                except ValueError:
                    return None
        return None

    def _get_sender_name_height(self) -> int:
        """Calculate height needed for sender name."""
        if self.sender_name and not self.is_outgoing:
            temp = self.create_text(
                0, 0,
                text=self.sender_name,
                anchor="nw",
                font=(self.config.ui.font_family, 
                      self.config.ui.font_sizes["sender"])
            )
            bbox = self.bbox(temp)
            self.delete(temp)
            return (bbox[3] - bbox[1] + 5) if bbox else 0
        return 0

    def _add_sender_name(self, x: int, y: int) -> None:
        """Add sender name if present."""
        if self.sender_name and not self.is_outgoing:
            self.create_text(
                x, y,
                text=self.sender_name,
                anchor="nw",
                fill=self.style.get_sender_name_color(),
                font=(self.config.ui.font_family, 
                      self.config.ui.font_sizes["sender"])
            )

    def _add_timestamp(self, x: int, y: int) -> None:
        """Add timestamp if present."""
        if self.timestamp:
            try:
                time_str = datetime.fromtimestamp(self.timestamp).strftime("%I:%M %p")
                if time_str.startswith("0"):
                    time_str = time_str[1:]
                    
                self.create_text(
                    x, y,
                    text=time_str,
                    anchor="se",
                    fill=self.style.get_timestamp_color(),
                    font=(self.config.ui.font_family, 
                          self.config.ui.font_sizes["timestamp"])
                )
            except Exception:
                pass

    def draw(self) -> None:
        """Draw the complete bubble with content."""
        # Clear canvas
        self.delete("all")
        
        # Calculate sender name height
        sender_height = self._get_sender_name_height()
        
        # Create content and get dimensions
        content_width, content_height = self.content_handler.create_content(
            self,
            self.padding,
            sender_height + self.padding,
            self.config.ui.max_message_width - 2 * self.padding,
            style=self.style,
            is_outgoing=self.is_outgoing
        )
        
        # Calculate total dimensions
        bubble_width = max(content_width + 2 * self.padding, 
                         self.config.ui.min_message_width)
        bubble_height = (sender_height + content_height + 
                        2 * self.padding + 
                        (20 if self.timestamp else 0))  # timestamp space
        
        # Configure canvas size
        self.configure(
            width=bubble_width + (0 if self.is_outgoing else self.padding * 2),
            height=bubble_height + self.padding * 2
        )
        
        # Draw bubble background
        bubble_x = 0 if self.is_outgoing else self.padding
        self.drawer.draw_bubble(
            self,
            bubble_x,
            sender_height,
            bubble_width,
            bubble_height - sender_height,
            is_outgoing=self.is_outgoing,
            style=self.style
        )
        
        # Add sender name
        if sender_height > 0:
            self._add_sender_name(self.padding, 2)
        
        # Add timestamp
        if self.timestamp:
            self._add_timestamp(
                bubble_x + bubble_width - self.padding,
                bubble_height - self.padding / 2
            )