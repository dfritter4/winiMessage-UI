# ui/components/scrolled_text.py
import tkinter as tk
from tkinter import ttk

class ModernScrolledText(tk.Frame):
    """A modern scrolled text widget with smooth scrolling."""
    
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent)
        
        self.canvas = tk.Canvas(self, bg="white", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="white")
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        self.scrollable_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def _on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_frame, width=canvas_width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def clear(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

    def scroll_to_bottom(self):
        """Ensure immediate scroll to bottom without animation."""
        try:
            # Force complete geometry update
            self.update_idletasks()
            self.canvas.update_idletasks()
            self.scrollable_frame.update_idletasks()
            
            # Force geometry recalculation
            self._on_frame_configure()
            
            # Set view directly to bottom
            self.canvas.yview_moveto(1.0)
            
            # Force immediate update
            self.canvas.update_idletasks()
        except tk.TclError:
            pass