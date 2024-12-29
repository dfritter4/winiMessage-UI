import tkinter as tk
from typing import Optional

from ..config import AppConfig
from .base import BaseBubble, DefaultBubbleDrawer, DefaultBubbleStyle
from .text_handlers import BasicTextContent, EnhancedTextContent
from .interfaces import IBubbleFactory

class TextBubble(BaseBubble):
    """Basic text message bubble."""
    
    def __init__(
        self,
        parent: tk.Widget,
        config: AppConfig,
        message: str,
        is_outgoing: bool = False,
        timestamp: Optional[float] = None,
        sender_name: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            parent,
            config,
            DefaultBubbleDrawer(),
            BasicTextContent(message),
            DefaultBubbleStyle(config),
            is_outgoing,
            timestamp,
            sender_name,
            **kwargs
        )
        self.draw()

class EnhancedTextBubble(BaseBubble):
    """Text message bubble with clickable links."""
    
    def __init__(
        self,
        parent: tk.Widget,
        config: AppConfig,
        message: str,
        is_outgoing: bool = False,
        timestamp: Optional[float] = None,
        sender_name: Optional[str] = None,
        **kwargs
    ):
        self.content_handler = EnhancedTextContent(message)
        super().__init__(
            parent,
            config,
            DefaultBubbleDrawer(),
            self.content_handler,
            DefaultBubbleStyle(config),
            is_outgoing,
            timestamp,
            sender_name,
            **kwargs
        )
        self.draw()
        self._setup_bindings()
        
    def _setup_bindings(self):
        """Set up mouse bindings for link interaction."""
        self.bind("<Motion>", self._on_motion)
        self.bind("<Button-1>", self._on_click)
        
    def _on_motion(self, event):
        """Handle mouse motion to change cursor for links."""
        if self.content_handler.get_link_at(event.x, event.y):
            self.configure(cursor="hand2")
        else:
            self.configure(cursor="")
            
    def _on_click(self, event):
        """Handle click events to open links."""
        self.content_handler.handle_click(event.x, event.y)

class TextBubbleFactory(IBubbleFactory):
    """Factory for creating text message bubbles."""
    
    def __init__(self, config: AppConfig, enhanced: bool = True):
        self.config = config
        self.enhanced = enhanced
    
    def create_bubble(
        self,
        parent: tk.Widget,
        message: str,
        is_outgoing: bool = False,
        timestamp: Optional[float] = None,
        sender_name: Optional[str] = None,
        **kwargs
    ) -> tk.Widget:
        """Create either a basic or enhanced text bubble based on configuration."""
        bubble_class = EnhancedTextBubble if self.enhanced else TextBubble
        return bubble_class(
            parent,
            self.config,
            message,
            is_outgoing,
            timestamp,
            sender_name,
            **kwargs
        )