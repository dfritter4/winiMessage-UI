import tkinter as tk
from datetime import datetime
from typing import Optional

class BaseBubble(tk.Canvas):
    COLORS = {
        'outgoing': "#007AFF",  # iMessage blue
        'incoming': "#E9E9EB",  # Light gray
        'timestamp': "#8E8E93",  # Subtle gray for timestamp
        'sender_name': "#65656A"  # Dark gray for sender name
    }

    def __init__(self, parent, is_outgoing: bool = False, timestamp=None, sender_name: str = None, **kwargs):
        kwargs.pop('width', None)
        kwargs.pop('height', None)
        super().__init__(parent, highlightthickness=0, bg="white", **kwargs)
        
        self.text_color = "white" if is_outgoing else "black"
        self.timestamp = self._parse_timestamp(timestamp)
        self.sender_name = sender_name
        self.padding = 12
        self.is_outgoing = is_outgoing

    def _parse_timestamp(self, timestamp) -> Optional[float]:
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

    def _add_sender_name(self):
        """Add sender name if present and message is incoming."""
        if self.sender_name and not self.is_outgoing:
            self.create_text(
                self.padding,
                2,
                text=self.sender_name,
                anchor="nw",
                fill=self.COLORS['sender_name'],
                font=("SF Pro", 11, "bold")
            )
            return 20  # Sender name height
        return 0

    def _add_timestamp(self, bubble_x: int, bubble_width: int, y_position: int):
        """Add timestamp below the message."""
        if self.timestamp:
            try:
                time_str = datetime.fromtimestamp(self.timestamp).strftime("%I:%M %p")
                self.create_text(
                    bubble_x + bubble_width - self.padding,
                    y_position,
                    text=time_str,
                    anchor="se",
                    fill=self.COLORS['timestamp'],
                    font=("SF Pro", 9)
                )
            except (ValueError, TypeError, OverflowError):
                pass

    def _draw_bubble_body(self, x: int, y: int, width: int, height: int):
        """Draw the bubble background."""
        color = self.COLORS['outgoing' if self.is_outgoing else 'incoming']
        self.create_rounded_rectangle(x, y, x + width, y + height, radius=15, fill=color)

    def create_rounded_rectangle(self, x1: int, y1: int, x2: int, y2: int, radius: int = 25, **kwargs):
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1,
            x1 + radius, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)