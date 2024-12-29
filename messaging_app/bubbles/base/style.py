from ..interfaces import IBubbleStyle

class DefaultBubbleStyle(IBubbleStyle):
    """Default implementation of bubble styling."""
    
    def get_background_color(self, is_outgoing: bool) -> str:
        """Get the bubble background color."""
        return "#007AFF" if is_outgoing else "#E9E9EB"  # iMessage blue / Light gray
    
    def get_text_color(self, is_outgoing: bool) -> str:
        """Get the text color."""
        return "white" if is_outgoing else "black"
    
    def get_timestamp_color(self) -> str:
        """Get the timestamp text color."""
        return "#8E8E93"  # Subtle gray for timestamp
    
    def get_sender_name_color(self) -> str:
        """Get the sender name text color."""
        return "#65656A"  # Dark gray for sender name