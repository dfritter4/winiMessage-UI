from abc import ABC, abstractmethod
import tkinter as tk
from typing import Optional

class IBubbleDrawer(ABC):
    """Interface for bubble drawing strategies."""
    
    @abstractmethod
    def draw_bubble(self, canvas: tk.Canvas, x: int, y: int, width: int, height: int, **kwargs) -> None:
        """Draw the bubble shape on the canvas."""
        pass

class IBubbleContent(ABC):
    """Interface for bubble content handlers."""
    
    @abstractmethod
    def create_content(self, canvas: tk.Canvas, x: int, y: int, width: int, **kwargs) -> tuple[int, int]:
        """Create the content within the bubble and return content dimensions (width, height)."""
        pass

class IBubbleStyle(ABC):
    """Interface for bubble styling."""
    
    @abstractmethod
    def get_background_color(self, is_outgoing: bool) -> str:
        """Get the bubble background color."""
        pass
    
    @abstractmethod
    def get_text_color(self, is_outgoing: bool) -> str:
        """Get the text color."""
        pass
    
    @abstractmethod
    def get_timestamp_color(self) -> str:
        """Get the timestamp text color."""
        pass
    
    @abstractmethod
    def get_sender_name_color(self) -> str:
        """Get the sender name text color."""
        pass

class IBubbleFactory(ABC):
    """Interface for creating message bubbles."""
    
    @abstractmethod
    def create_bubble(self, 
                     parent: tk.Widget,
                     message: str,
                     is_outgoing: bool = False,
                     timestamp: Optional[float] = None,
                     sender_name: Optional[str] = None,
                     **kwargs) -> tk.Widget:
        """Create a message bubble widget."""
        pass