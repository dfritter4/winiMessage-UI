# bubbles/enhanced_text_bubble.py
from .base_bubble import BaseBubble
from .text_parser import TextParser, LinkHandler

class EnhancedTextBubble(BaseBubble):
    """A text bubble that supports clickable links within messages."""

    def __init__(self, parent, message: str, **kwargs):
        super().__init__(parent, **kwargs)
        self.message = message
        self.link_handler = LinkHandler()
        self._text_segments = TextParser.parse_text(self.message)
        self._link_regions = []  # Store coordinates of clickable regions
        self._create_bubble()
        self._setup_bindings()

    def _get_sender_name_height(self):
        """Calculate the height needed for the sender name."""
        if self.sender_name and not self.is_outgoing:
            # Create temporary text to measure sender name height
            temp = self.create_text(
                0, 0,
                text=self.sender_name,
                anchor="nw",
                font=("SF Pro", 11, "bold")
            )
            bbox = self.bbox(temp)
            height = bbox[3] - bbox[1] if bbox else 0
            self.delete(temp)
            return height + 5  # Add small padding
        return 0

    def _create_bubble(self):
        # Clear canvas
        self.delete("all")

        # Calculate sender name height first
        sender_height = self._get_sender_name_height()

        # Calculate initial text dimensions
        max_width = 300
        temp = self.create_text(
            0, 0,
            text=self.message,
            anchor="nw",
            width=max_width,
            font=("SF Pro", 13)  # Consistent font
        )
        bbox = self.bbox(temp)
        text_width = bbox[2] - bbox[0] if bbox else 0
        text_height = bbox[3] - bbox[1] if bbox else 0
        self.delete(temp)

        # Calculate bubble dimensions
        bubble_width = min(max(text_width + 2 * self.padding, 100), max_width)
        bubble_height = text_height + 2 * self.padding + sender_height + 25

        # Configure canvas size
        self.configure(width=bubble_width + (0 if self.is_outgoing else self.padding * 2), 
                      height=bubble_height + self.padding * 2)

        # Calculate bubble position
        bubble_x = 0 if self.is_outgoing else self.padding

        # Draw bubble
        self._draw_bubble_body(bubble_x, sender_height, bubble_width, bubble_height - sender_height)

        # Add sender name if needed
        if sender_height > 0:
            self._add_sender_name()

        # Create text with segments
        y_position = sender_height + self.padding
        x_start = bubble_x + self.padding

        # First, measure each segment to calculate positions
        current_x = x_start
        segment_positions = []
        current_text = ""

        for segment in self._text_segments:
            # Create temporary text to measure
            temp = self.create_text(
                0, 0,
                text=current_text + segment.text,
                anchor="nw",
                width=max_width - 2 * self.padding,
                font=("SF Pro", 13)
            )
            segment_bbox = self.bbox(temp)
            segment_width = segment_bbox[2] - segment_bbox[0] if segment_bbox else 0
            segment_height = segment_bbox[3] - segment_bbox[1] if segment_bbox else 0
            self.delete(temp)

            if segment.is_link:
                segment_positions.append({
                    'text': segment.text,
                    'x': x_start,
                    'y': y_position,
                    'width': segment_width,
                    'height': segment_height
                })

            current_text += segment.text

        # Create the complete text
        text_item = self.create_text(
            x_start,
            y_position,
            text=self.message,
            anchor="nw",
            width=max_width - 2 * self.padding,
            fill=self.text_color,
            font=("SF Pro", 13)
        )

        # Add links and store clickable regions
        for pos in segment_positions:
            # Store link region with proper coordinates
            self._link_regions.append({
                'x1': pos['x'],
                'y1': pos['y'],
                'x2': pos['x'] + pos['width'],
                'y2': pos['y'] + pos['height'],
                'url': pos['text']
            })

            # Draw underline for link
            self.create_line(
                pos['x'], pos['y'] + pos['height'],
                pos['x'] + pos['width'], pos['y'] + pos['height'],
                fill="#0000EE" if not self.is_outgoing else "#FFFFFF",
                width=1
            )

        # Add timestamp
        if self.timestamp:
            self._add_timestamp(bubble_x, bubble_width, bubble_height - 15)

    def _setup_bindings(self):
        """Set up mouse bindings for link interaction."""
        self.bind("<Motion>", self._on_motion)
        self.bind("<Button-1>", self._on_click)

    def _on_motion(self, event):
        """Handle mouse motion to change cursor for links."""
        x, y = event.x, event.y
        for region in self._link_regions:
            if (region['x1'] <= x <= region['x2'] and 
                region['y1'] <= y <= region['y2']):
                self.configure(cursor="hand2")
                return
        self.configure(cursor="")

    def _on_click(self, event):
        """Handle click events to open links."""
        x, y = event.x, event.y
        for region in self._link_regions:
            if (region['x1'] <= x <= region['x2'] and 
                region['y1'] <= y <= region['y2']):
                self.link_handler.open_link(region['url'])
                return