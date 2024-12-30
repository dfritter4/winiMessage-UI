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
        """Ensure reliable scrolling to bottom of content."""
        try:
            # Update geometry management
            self.update_idletasks()
            self.canvas.update_idletasks()
            self.scrollable_frame.update_idletasks()
            
            # Force geometry recalculation
            self._on_frame_configure()
            
            # Schedule multiple scroll attempts to ensure it takes effect
            def do_scroll():
                self.canvas.yview_moveto(1.0)
                # Schedule another scroll attempt after a short delay
                self.after(50, lambda: self.canvas.yview_moveto(1.0))
            
            # Initial scroll attempt
            self.after(10, do_scroll)
            
        except tk.TclError as e:
            self.logger.debug(f"Error in scroll_to_bottom: {e}")
            pass