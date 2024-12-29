import tkinter as tk

class ModernListbox(tk.Listbox):
    """A modern styled listbox with improved aesthetics and hover effects."""
    
    def __init__(self, parent, **kwargs):
        defaults = {
            'bg': "#F5F5F7",
            'fg': "#000000",
            'font': ("SF Pro", 13),
            'selectmode': "single",
            'activestyle': "none",
            'highlightthickness': 0,
            'bd': 0,
            'relief': "flat",
            'selectbackground': "#007AFF",
            'selectforeground': "#FFFFFF"
        }
        
        defaults.update(kwargs)
        super().__init__(parent, **defaults)
        
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Motion>", self._on_motion)
        
        self._hover_item = None
    
    def _is_valid_index(self, index) -> bool:
        """Check if an index is valid for the current listbox state."""
        try:
            # Get the number of items in the listbox
            size = self.size()
            # Convert index to int and check if it's in valid range
            return 0 <= int(index) < size
        except (ValueError, TypeError):
            return False
    
    def _clear_hover_state(self) -> None:
        """Safely clear the hover state of the previously hovered item."""
        if self._hover_item is not None and self._is_valid_index(self._hover_item):
            try:
                self.itemconfig(self._hover_item, background="#F5F5F7")
            except tk.TclError:
                pass  # Ignore errors if item no longer exists
        self._hover_item = None
    
    def _on_enter(self, event) -> None:
        """Handle mouse enter event."""
        self._update_hover(event)
    
    def _on_leave(self, event) -> None:
        """Handle mouse leave event."""
        self._clear_hover_state()
    
    def _on_motion(self, event) -> None:
        """Handle mouse motion event."""
        self._update_hover(event)
    
    def _update_hover(self, event) -> None:
        """Update the hover effect based on mouse position."""
        try:
            # Get the item index at the current mouse position
            item = self.nearest(event.y)
            
            # Only proceed if we have a valid item and it's different from current hover
            if self._is_valid_index(item) and self._hover_item != item:
                # Clear previous hover state
                self._clear_hover_state()
                
                # Set new hover state
                self._hover_item = item
                self.itemconfig(item, background="#E5E5EA")
        except tk.TclError:
            # If any Tcl/Tk error occurs, clear the hover state
            self._clear_hover_state()
    
    def delete(self, first, last=None) -> None:
        """Override delete to properly handle hover state."""
        self._clear_hover_state()
        super().delete(first, last)
    
    def delete_all(self) -> None:
        """Helper method to clear all items."""
        self._clear_hover_state()
        self.delete(0, tk.END)