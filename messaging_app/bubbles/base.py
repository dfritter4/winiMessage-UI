import tkinter as tk
import datetime
import time as py_time
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
        """Draw the bubble shape on the canvas with properly rounded corners.
        
        Args:
            canvas: The canvas to draw on
            x: The x coordinate to start drawing
            y: The y coordinate to start drawing
            width: The width of the bubble
            height: The height of the bubble
            **kwargs: Additional drawing arguments
        """
        radius = kwargs.get('radius', 12)
        fill_color = kwargs.get('fill', '#E9E9EB')
        outline = kwargs.get('outline', '')
        
        # Right side
        canvas.create_arc(width - 2*radius + x, y, width + x, 2*radius + y, 
                         start=270, extent=90, fill=fill_color, outline=outline)  # Top-right corner
        canvas.create_arc(width - 2*radius + x, height - 2*radius + y, width + x, height + y, 
                         start=0, extent=90, fill=fill_color, outline=outline)    # Bottom-right corner
        canvas.create_rectangle(width - radius + x, y, width + x, height + y,
                              fill=fill_color, outline=outline)  # Right edge
        
        # Left side
        canvas.create_arc(x, y, 2*radius + x, 2*radius + y,
                         start=180, extent=90, fill=fill_color, outline=outline)  # Top-left corner
        canvas.create_arc(x, height - 2*radius + y, 2*radius + x, height + y,
                         start=90, extent=90, fill=fill_color, outline=outline)   # Bottom-left corner
        canvas.create_rectangle(x, y, radius + x, height + y,
                              fill=fill_color, outline=outline)  # Left edge
        
        # Center
        canvas.create_rectangle(radius + x, y, width - radius + x, height + y,
                              fill=fill_color, outline=outline)  # Center rectangle

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
            return (bbox[3] - bbox[1] + 5) if bbox else 20  # Add padding
        return 0


    def _parse_timestamp(self, timestamp: Optional[str]) -> Optional[float]:
        try:
            if isinstance(timestamp, (int, float)):
                return float(timestamp)
            if isinstance(timestamp, str):
                # Handle common timestamp formats
                try:
                    return datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").timestamp()
                except ValueError:
                    return datetime.fromisoformat(timestamp.replace('Z', '+00:00')).timestamp()
            return None
        except Exception as e:
            self.logger.error(f"Error parsing timestamp: {timestamp}, {e}")
            return None



    def _add_timestamp(self, x: int, width: int, y_position: int) -> None:
        """Add timestamp to the bubble."""
        if self.timestamp:
            try:
                # Convert timestamp to local time
                # Use time.localtime if timestamp is a float
                if isinstance(self.timestamp, (int, float)):
                    time_struct = py_time.localtime(self.timestamp)
                    time_str = py_time.strftime("%I:%M %p", time_struct).lower()
                else:
                    # Fallback to datetime if it's not a simple float
                    time = datetime.fromtimestamp(float(self.timestamp))
                    time_str = time.strftime("%I:%M %p").lower()
                
                # Remove leading zero from hour
                if time_str.startswith('0'):
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
                # Log the actual timestamp value for debugging
                print(f"Problematic timestamp: {self.timestamp}, Type: {type(self.timestamp)}")

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