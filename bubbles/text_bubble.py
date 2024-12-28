from .base_bubble import BaseBubble

class TextBubble(BaseBubble):
    def __init__(self, parent, message: str, **kwargs):
        super().__init__(parent, **kwargs)
        self.message = message
        self._create_bubble()

    def _create_bubble(self):
        # Clear canvas
        self.delete("all")

        # Calculate sender name height first
        sender_height = self._get_sender_name_height()

        # Calculate text dimensions with specified font
        max_width = 300  # Maximum bubble width
        min_width = 60   # Minimum bubble width
        
        # Create temporary text for measurement with proper font
        temp = self.create_text(
            0, 0,
            text=self.message,
            anchor="nw",
            width=max_width,
            font=("SF Pro", 13)  # Specify consistent font
        )
        bbox = self.bbox(temp)
        
        if not bbox:
            # Handle empty or invalid text
            text_width = min_width
            text_height = 0
        else:
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        
        self.delete(temp)

        # Calculate bubble dimensions
        # Add extra padding for timestamp area
        timestamp_height = 20 if self.timestamp else 0
        horizontal_padding = self.padding * 2
        vertical_padding = self.padding * 2
        
        # Calculate bubble width ensuring it's within bounds
        bubble_width = min(
            max(
                text_width + horizontal_padding,
                min_width
            ),
            max_width
        )

        # Calculate total height including all elements
        bubble_height = (
            sender_height +         # Sender name
            text_height +           # Message text
            vertical_padding +      # Padding
            timestamp_height        # Timestamp area
        )

        # Configure canvas size
        # Add extra padding to ensure nothing is cut off
        self.configure(
            width=bubble_width + (0 if self.is_outgoing else self.padding * 2),
            height=bubble_height + vertical_padding
        )

        # Calculate bubble position
        bubble_x = 0 if self.is_outgoing else self.padding

        # Draw the background bubble
        self._draw_bubble_body(
            bubble_x,
            sender_height,
            bubble_width,
            bubble_height - sender_height
        )

        # Add sender name if present
        if sender_height > 0:
            self._add_sender_name()

        # Add message text
        if self.message:
            self.create_text(
                bubble_x + self.padding,
                sender_height + self.padding,
                text=self.message,
                anchor="nw",
                fill=self.text_color,
                width=max_width - horizontal_padding,
                font=("SF Pro", 13)  # Consistent font
            )

        # Add timestamp
        self._add_timestamp(
            bubble_x,
            bubble_width,
            bubble_height - (self.padding / 2)
        )

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