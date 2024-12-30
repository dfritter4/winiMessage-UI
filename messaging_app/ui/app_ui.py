# messaging_app/ui/app_ui.py
import tkinter as tk
from tkinter import ttk
from datetime import datetime

from messaging_app.services.ui_manager import UIManager
from ..config import AppConfig
from ..domain import Event, EventType
from ..services import EventBus
from .components import (
    ModernFrame,
    ModernEntry,
    ModernListbox,
    ModernButton,
    ModernScrolledText
)

class MessageAppUI:
    """Handles all UI-related concerns"""
    
    def __init__(self, root: tk.Tk, config: AppConfig, event_bus: EventBus, ui_manager: UIManager):
        self.root = root
        self.config = config
        self.event_bus = event_bus
        self.ui_manager = ui_manager  # Add UIManager reference
        
        # UI components
        self.main_container = None
        self.sidebar = None
        self.chat_container = None
        self.message_display_widget = None
        self.chat_listbox = None
        self.message_entry = None
        self.send_button = None
        
        self._setup_styles()
        self._create_ui()
        self._setup_ui_bindings()
        
        # Set the listbox reference in UIManager
        self.ui_manager.set_chat_listbox(self.chat_listbox)
    
    def _setup_styles(self) -> None:
        """Configure ttk styles for the application."""
        style = ttk.Style()
        style.configure("Chat.TFrame", background="white")
        style.configure("Sidebar.TFrame", background="#F5F5F7")

    def _create_ui(self) -> None:
        """Create all UI components."""
        self._create_main_container()
        self._create_sidebar()
        self._create_chat_area()
    
    def _create_main_container(self) -> None:
        self.main_container = ModernFrame(self.root)
        self.main_container.pack(fill="both", expand=True)
        
        self.paned_window = tk.PanedWindow(
            self.main_container,
            orient=tk.HORIZONTAL,
            sashrelief="raised"
        )
        self.paned_window.pack(fill="both", expand=True)

    def _create_sidebar(self) -> None:
        self.sidebar = ModernFrame(
            self.paned_window,
            style="Sidebar.TFrame",
            width=250
        )
        self.paned_window.add(self.sidebar, minsize=200)

        # Search Entry
        self.search_entry = ModernEntry(
            self.sidebar,
            placeholder="Search Messages",
            font=("SF Pro", 12)
        )
        self.search_entry.pack(fill="x", padx=10, pady=10)

        # Chat Listbox
        self.chat_listbox = ModernListbox(self.sidebar, height=20)
        self.chat_listbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # New Chat Button
        self.new_chat_btn = ModernButton(
            self.sidebar,
            text="New Message"
        )
        self.new_chat_btn.pack(fill="x", padx=10, pady=(0, 10))

    def _create_chat_area(self) -> None:
        self.chat_container = ModernFrame(self.paned_window, style="Chat.TFrame")
        self.paned_window.add(self.chat_container, minsize=400)

        # Message Display
        self.message_display_widget = ModernScrolledText(self.chat_container)
        self.message_display_widget.pack(fill="both", expand=True, padx=10, pady=10)

        # Message Input Area
        self._create_input_area()

    def _create_input_area(self) -> None:
        self.input_frame = ModernFrame(self.chat_container)
        self.input_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.message_entry = tk.Text(
            self.input_frame,
            height=3,
            font=("SF Pro", 12),
            wrap="word",
            bd=1,
            relief="solid"
        )
        self.message_entry.pack(fill="x", side="left", expand=True, padx=(0, 10))

        self.send_button = ModernButton(
            self.input_frame,
            text="Send"
        )
        self.send_button.pack(side="right")

    def _setup_ui_bindings(self) -> None:
        """Set up all UI event bindings."""
        self.search_entry.bind("<Return>", 
            lambda e: self.event_bus.publish(Event(
                EventType.MESSAGE_SEARCH_REQUESTED,
                {"search_term": self.search_entry.get().strip()}
            )))
            
        self.chat_listbox.bind("<<ListboxSelect>>", 
            lambda e: self._on_thread_selected())
            
        self.message_entry.bind("<Return>", 
            lambda e: self._handle_return_key(e))
            
        self.message_entry.bind("<KeyRelease>",
            lambda e: self._handle_typing(e))
            
        self.send_button.configure(
            command=lambda: self._handle_send_message())

    def _on_thread_selected(self) -> None:
        selection = self.chat_listbox.curselection()
        if selection:
            thread_name = self.chat_listbox.get(selection[0])
            self.event_bus.publish(Event(
                EventType.THREAD_SELECTED,
                {"thread_name": thread_name}
            ))

    def _handle_return_key(self, event) -> str:
        if not event.state & 0x1:  # Shift key is not pressed
            self._handle_send_message()
            return 'break'
        return None

    def _handle_typing(self, event) -> None:
        if event.keysym not in ('Return', 'Shift_L', 'Shift_R'):
            self.event_bus.publish(Event(
                EventType.STATE_CHANGED,
                {"is_typing": True}
            ))

    def _handle_send_message(self) -> None:
        message = self.message_entry.get("1.0", "end-1c").strip()
        if message:
            self.event_bus.publish(Event(
                EventType.SEND_MESSAGE_REQUESTED,
                {
                    "message": message,
                    "timestamp": datetime.now().timestamp()
                }
            ))
            self.message_entry.delete("1.0", tk.END)