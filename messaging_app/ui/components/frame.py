# ui/components/frame.py
from tkinter import ttk

class ModernFrame(ttk.Frame):
    """A modern styled frame."""
    
    def __init__(self, parent, **kwargs):
        style = ttk.Style()
        style.configure(
            "Modern.TFrame",
            background="white",
            borderwidth=0,
            relief="flat"
        )
        
        style_name = kwargs.pop('style', "Modern.TFrame")
        super().__init__(parent, style=style_name, **kwargs)