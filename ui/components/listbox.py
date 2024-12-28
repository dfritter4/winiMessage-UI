# ui/components/listbox.py
import tkinter as tk

class ModernListbox(tk.Listbox):
    """A modern styled listbox with improved aesthetics."""
    
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
        
    def _on_enter(self, event):
        self._update_hover(event)
        
    def _on_leave(self, event):
        if self._hover_item is not None:
            self.itemconfig(self._hover_item, background="#F5F5F7")
            self._hover_item = None
            
    def _on_motion(self, event):
        self._update_hover(event)
        
    def _update_hover(self, event):
        item = self.nearest(event.y)
        if self._hover_item != item:
            if self._hover_item is not None:
                self.itemconfig(self._hover_item, background="#F5F5F7")
            self._hover_item = item
            self.itemconfig(item, background="#E5E5EA")