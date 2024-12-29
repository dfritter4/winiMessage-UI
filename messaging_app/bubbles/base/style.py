from typing import Optional
from messaging_app.config.settings import AppConfig
from ..interfaces import IBubbleStyle

class DefaultBubbleStyle(IBubbleStyle):
    def __init__(self, config: Optional[AppConfig] = None):
        self.config = config
    
    def get_background_color(self, is_outgoing: bool) -> str:
        if self.config:
            return (self.config.colors.outgoing_bubble 
                    if is_outgoing 
                    else self.config.colors.incoming_bubble)
        return "#007AFF" if is_outgoing else "#E9E9EB"
    
    def get_text_color(self, is_outgoing: bool) -> str:
        if self.config:
            return (self.config.colors.outgoing_text 
                    if is_outgoing 
                    else self.config.colors.incoming_text)
        return "white" if is_outgoing else "black"
    
    def get_timestamp_color(self) -> str:
        return self.config.colors.timestamp if self.config else "#8E8E93"
    
    def get_sender_name_color(self) -> str:
        return self.config.colors.sender_name if self.config else "#65656A"