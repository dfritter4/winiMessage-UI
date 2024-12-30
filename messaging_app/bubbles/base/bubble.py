import tkinter as tk
from typing import Optional
from datetime import datetime
import time as py_time
from datetime import datetime, timezone, timedelta
from ..interfaces import IBubbleStyle, IBubbleContent, IBubbleDrawer
from .style import DefaultBubbleStyle
from .drawer import DefaultBubbleDrawer

class BaseBubble(tk.Canvas):
    """Base class for message bubbles with improved sender name display."""
    
    def __init__(
        self,
        parent: tk.Widget,
        content: IBubbleContent,
        style: Optional[IBubbleStyle] = None,
        drawer: Optional[IBubbleDrawer] = None,
        is_outgoing: bool = False,
        timestamp: Optional[float] = None,
        sender_name: Optional[str] = None,
        **kwargs
    ):
        # Remove size specs from kwargs
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
        self.padding = 14
        self.corner_radius = 12  # Explicit corner radius

        # Configure background
        self.configure(bg=self.style.get_background_color(is_outgoing))
        
        # Create the bubble
        self._create_bubble()

        self.bind("<Button-1>", self._handle_click)
    
    def _handle_click(self, event):
        # Delegate click to content handler
        if hasattr(self.content, 'handle_click'):
            self.content.handle_click(event.x, event.y)

    def _create_bubble(self) -> None:
        """Create the complete bubble with all components."""
        # Clear the canvas
        self.delete("all")

        # Calculate initial dimensions
        sender_height = 0
        if self.sender_name and not self.is_outgoing:
            sender_height = self._get_sender_name_height()

        # Initial dimensions
        total_width = 300 + (self.padding * 2)
        total_height = sender_height + 20 + (self.padding * 2)

        # Add sender name if present and not outgoing
        if self.sender_name and not self.is_outgoing:
            self._add_sender_name(self.padding, 2)

        # Draw the bubble background
        bubble_y = sender_height + (self.padding / 2)  # Add padding after sender name
        self.drawer.draw_bubble(
            self,
            self.padding if not self.is_outgoing else 0,
            bubble_y,
            total_width - (self.padding if self.is_outgoing else 0),
            total_height - bubble_y,
            fill=self.style.get_background_color(self.is_outgoing)
        )

        # Add content
        content_width, content_height = self.content.create_content(
            self,
            self.padding * 1.5 if not self.is_outgoing else self.padding,
            bubble_y + self.padding,
            300,  # Maximum content width
            style=self.style,
            is_outgoing=self.is_outgoing,
            font_family="SF Pro",
            font_size=13
        )

        # Recalculate total dimensions based on content
        total_width = max(total_width, content_width + (self.padding * 3))
        total_height = bubble_y + content_height + (self.padding * 2)

        # Add timestamp below content with proper spacing
        if self.timestamp:
            timestamp_padding = 8  # Space between content and timestamp
            timestamp_y = total_height + timestamp_padding
            self._add_timestamp(
                self.padding if not self.is_outgoing else 0,
                total_width -5,
                timestamp_y
            )
            total_height = timestamp_y + 5  # Account for timestamp height

        # Configure final canvas size
        self.configure(
            width=total_width,
            height=total_height
        )

    def _get_sender_name_height(self) -> int:
        """Calculate height needed for sender name."""
        if self.sender_name and not self.is_outgoing:
            temp = self.create_text(
                0, 0,
                text=self.sender_name,
                anchor="nw",
                font=("SF Pro", 11, "bold")
            )
            bbox = self.bbox(temp)
            self.delete(temp)
            return (bbox[3] - bbox[1] + 8) if bbox else 20  # Added more padding
        return 0

    def _add_sender_name(self, x: int, y: int) -> None:
        """Add sender name above the bubble."""
        if self.sender_name and not self.is_outgoing:
            self.create_text(
                x, y,
                text=self.sender_name,
                anchor="nw",
                fill=self.style.get_sender_name_color(),
                font=("SF Pro", 11, "bold")
            )
    
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
                # Convert UTC timestamp to local time
                if isinstance(self.timestamp, (int, float)):
                    utc_dt = datetime.fromtimestamp(self.timestamp, tz=timezone.utc)
                    local_dt = utc_dt.astimezone()  # Convert to local timezone
                    time_str = local_dt.strftime("%I:%M %p").lower()
                else:
                    # If it's a string or other format, try to parse it
                    try:
                        timestamp_float = float(self.timestamp)
                        utc_dt = datetime.fromtimestamp(timestamp_float, tz=timezone.utc)
                        local_dt = utc_dt.astimezone()
                        time_str = local_dt.strftime("%I:%M %p").lower()
                    except (ValueError, TypeError):
                        time_str = datetime.now().strftime("%I:%M %p").lower()
                
                # Remove leading zero from hour
                if time_str.startswith('0'):
                    time_str = time_str[1:]
                
                # Create the timestamp text
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