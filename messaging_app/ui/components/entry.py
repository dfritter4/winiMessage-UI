# ui/components/entry.py
import tkinter as tk
from tkinter import ttk

class ModernEntry(ttk.Entry):
    """A modern styled entry widget with placeholder text support."""
    
    def __init__(self, parent, **kwargs):
        self.placeholder = kwargs.pop('placeholder', '')
        self.placeholder_color = kwargs.pop('placeholder_color', 'grey')
        
        style = ttk.Style()
        style.configure(
            "Modern.TEntry",
            fieldbackground="white",
            borderwidth=1,
            relief="flat",
            padding=5
        )
        
        super().__init__(parent, style="Modern.TEntry", **kwargs)
        
        self._is_placeholder = False
        
        if self.placeholder:
            self.bind("<FocusIn>", self._clear_placeholder)
            self.bind("<FocusOut>", self._add_placeholder)
            self._add_placeholder()

    def _clear_placeholder(self, event=None):
        if self._is_placeholder:
            self.delete(0, tk.END)
            self.configure(foreground='black')
            self._is_placeholder = False

    def _add_placeholder(self, event=None):
        if not self.get():
            self.insert(0, self.placeholder)
            self.configure(foreground=self.placeholder_color)
            self._is_placeholder = True

    def get(self):
        if self._is_placeholder:
            return ''
        return super().get()