# modern_ui.py

import tkinter as tk
from tkinter import ttk

class ModernScrolledText(tk.Frame):
    """A modern scrolled text widget with smooth scrolling."""
    
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent)
        
        # Create canvas and scrollbar
        self.canvas = tk.Canvas(self, bg="white", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="white")
        
        # Configure canvas
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Bind events
        self.scrollable_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Layout
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def _on_frame_configure(self, event=None):
        """Reset the scroll region to encompass the inner frame."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """Update the inner frame's width to fill the canvas."""
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_frame, width=canvas_width)

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def clear(self):
        """Remove all widgets from the scrollable frame."""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

    def scroll_to_bottom(self):
        """Scroll to the bottom of the content."""
        try:
            self.update_idletasks()  # Ensure geometry is updated
            self.canvas.update_idletasks()
            self.canvas.yview_moveto(1.0)
            # Double-check scroll position after brief delay
            self.after(50, lambda: self.canvas.yview_moveto(1.0))
        except tk.TclError:
            pass  # Handle case where widget might be destroyed

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
        
        # Update defaults with any provided kwargs
        defaults.update(kwargs)
        super().__init__(parent, **defaults)
        
        # Bind hover events
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Motion>", self._on_motion)
        
        self._hover_item = None
        
    def _on_enter(self, event):
        """Handle mouse enter event."""
        self._update_hover(event)
        
    def _on_leave(self, event):
        """Handle mouse leave event."""
        if self._hover_item is not None:
            self.itemconfig(self._hover_item, background="#F5F5F7")
            self._hover_item = None
            
    def _on_motion(self, event):
        """Handle mouse motion event."""
        self._update_hover(event)
        
    def _update_hover(self, event):
        """Update the hover effect."""
        item = self.nearest(event.y)
        if self._hover_item != item:
            if self._hover_item is not None:
                self.itemconfig(self._hover_item, background="#F5F5F7")
            self._hover_item = item
            self.itemconfig(item, background="#E5E5EA")

class ModernEntry(ttk.Entry):
    """A modern styled entry widget with placeholder text support."""
    
    def __init__(self, parent, **kwargs):
        # Extract custom parameters
        self.placeholder = kwargs.pop('placeholder', '')
        self.placeholder_color = kwargs.pop('placeholder_color', 'grey')
        
        # Configure style
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
        """Clear placeholder text on focus."""
        if self._is_placeholder:
            self.delete(0, tk.END)
            self.configure(foreground='black')
            self._is_placeholder = False

    def _add_placeholder(self, event=None):
        """Add placeholder text if entry is empty."""
        if not self.get():
            self.insert(0, self.placeholder)
            self.configure(foreground=self.placeholder_color)
            self._is_placeholder = True

    def get(self):
        """Override get method to handle placeholder text."""
        if self._is_placeholder:
            return ''
        return super().get()

class ModernButton(ttk.Button):
    """A modern styled button with hover effects."""
    
    def __init__(self, parent, **kwargs):
        style = ttk.Style()
        
        # Create a unique style name for debugging
        style_name = "CustomModern.TButton"
        
        # Configure base style with explicit text color
        style.configure(
            style_name,
            background="#007AFF",
            foreground="white",  # Set text color
            padding=(10, 5),
            relief="flat",
            borderwidth=0,
            font=("SF Pro", 12),
        )
        
        # Map state-specific colors
        style.map(
            style_name,
            background=[
                ("pressed", "#005AC7"),
                ("active", "#0051A8"),
                ("!disabled", "#007AFF")
            ],
            # Explicitly map text color for all states
            foreground=[
                ("pressed", "white"),
                ("active", "white"),
                ("!disabled", "white"),
                ("disabled", "gray")
            ]
        )
        
        # Initialize layout to ensure text is rendered
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
        
        # Remove unsupported direct styling options from kwargs
        if "foreground" in kwargs:
            del kwargs["foreground"]
        if "background" in kwargs:
            del kwargs["background"]
            
        # Create button with our custom style
        super().__init__(parent, style=style_name, **kwargs)

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
        
        # Remove style from kwargs if it exists
        style_name = kwargs.pop('style', "Modern.TFrame")
        super().__init__(parent, style=style_name, **kwargs)
