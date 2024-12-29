# ui/components/button.py
import tkinter as tk
from tkinter import ttk

class ModernButton(ttk.Button):
    """A modern styled button with hover effects."""
    
    def __init__(self, parent, **kwargs):
        style = ttk.Style()
        style_name = "CustomModern.TButton"
        
        style.configure(
            style_name,
            background="#007AFF",
            foreground="white",
            padding=(10, 5),
            relief="flat",
            borderwidth=0,
            font=("SF Pro", 12),
        )
        
        style.map(
            style_name,
            background=[
                ("pressed", "#005AC7"),
                ("active", "#0051A8"),
                ("!disabled", "#007AFF")
            ],
            foreground=[
                ("pressed", "white"),
                ("active", "white"),
                ("!disabled", "white"),
                ("disabled", "gray")
            ]
        )
        
        style.layout(style_name, [
            ('Button.padding', {
                'sticky': 'nswe',
                'children': [
                    ('Button.label', {
                        'sticky': 'nswe'
                    })
                ]
            })
        ])
        
        # Remove unsupported direct styling options
        kwargs.pop("foreground", None)
        kwargs.pop("background", None)
            
        super().__init__(parent, style=style_name, **kwargs)