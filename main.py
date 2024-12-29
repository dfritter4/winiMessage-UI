#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox, simpledialog

from config import AppConfig, load_config
from domain import Event, EventType
from ui import (
    ModernScrolledText,
    ModernListbox,
    ModernEntry,
    ModernButton,
    ModernFrame
)
from controllers import ChatController
from services import (
    EventBus,
    StateManager,
    MessageService,
    ThreadManager,
    MessageDisplayManager,
    UIManager,
    ErrorHandler
)

class MessagingApp:
    """Main application class for the Messages app."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Messages")
        self.root.geometry("1000x700")
        self.root.configure(bg="white")
        
        # Initialize core components
        self.config = load_config()
        self.event_bus = EventBus()
        self.state_manager = StateManager(self.event_bus)
        
        # Initialize services
        self.message_service = MessageService(self.config, self.event_bus)
        self.error_handler = ErrorHandler(self.event_bus)
        
        # Create UI
        self._setup_styles()
        self._create_ui()
        
        # Initialize remaining services that depend on UI
        self.message_display = MessageDisplayManager(
            self.message_display_widget,
            self.config,
            self.event_bus
        )
        self.ui_manager = UIManager(self.root, self.event_bus)
        self.thread_manager = ThreadManager(
            self.message_service,
            self.event_bus,
            self.state_manager
        )
        
        # Initialize controller
        self.controller = ChatController(
            self.config,
            self.event_bus,
            self.state_manager,
            self.message_service,
            self.thread_manager,
            self.message_display,
            self.ui_manager,
            self.error_handler
        )
        
        # Start initialization after GUI is shown
        self.root.after(100, self._initialize_async)

    def _setup_styles(self):
        """Configure ttk styles for the application."""
        style = ttk.Style()
        style.configure("Chat.TFrame", background="white")
        style.configure("Sidebar.TFrame", background="#F5F5F7")

    def _create_ui(self):
        """Create the main UI components."""
        # Main container
        self.main_container = ModernFrame(self.root)
        self.main_container.pack(fill="both", expand=True)

        # PanedWindow to separate sidebar and chat area
        self.paned_window = tk.PanedWindow(
            self.main_container,
            orient=tk.HORIZONTAL,
            sashrelief="raised"
        )
        self.paned_window.pack(fill="both", expand=True)

        self._create_sidebar()
        self._create_chat_area()

    def _create_sidebar(self):
        """Create the sidebar with search, chat list, and new chat button."""
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
        self.chat_listbox.bind("<<ListboxSelect>>", self._on_chat_selected)

        # New Chat Button
        self.new_chat_btn = ModernButton(
            self.sidebar,
            text="New Message",
            command=self._on_new_chat_requested
        )
        self.new_chat_btn.pack(fill="x", padx=10, pady=(0, 10))

    def _create_chat_area(self):
        """Create the main chat area with message display and input."""
        self.chat_container = ModernFrame(self.paned_window, style="Chat.TFrame")
        self.paned_window.add(self.chat_container, minsize=400)

        # Message Display
        self.message_display_widget = ModernScrolledText(self.chat_container)
        self.message_display_widget.pack(fill="both", expand=True, padx=10, pady=10)

        # Message Input Area
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
        self.message_entry.bind("<Return>", self._on_return_key)
        self.message_entry.bind("<Shift-Return>", lambda e: 'break')

        self.send_button = ModernButton(
            self.input_frame,
            text="Send",
            command=self._on_send_message
        )
        self.send_button.pack(side="right")

    def _initialize_async(self):
        """Initialize the application asynchronously."""
        self.controller.initialize()

    def _on_chat_selected(self, event):
        """Handle chat selection from the listbox."""
        selection = self.chat_listbox.curselection()
        if selection:
            thread_name = self.chat_listbox.get(selection[0])
            self.event_bus.publish(Event(
                EventType.THREAD_SELECTED,
                {"thread_name": thread_name}
            ))

    def _on_new_chat_requested(self):
        """Handle new chat button click."""
        self.event_bus.publish(Event(
            EventType.NEW_CHAT_REQUESTED,
            {}
        ))

    def _on_send_message(self):
        """Handle send message button click."""
        message = self.message_entry.get("1.0", "end-1c").strip()
        if message:
            self.event_bus.publish(Event(
                EventType.SEND_MESSAGE_REQUESTED,
                {"message": message}
            ))
            self.message_entry.delete("1.0", tk.END)

    def _on_return_key(self, event):
        """Handle Return key in message entry."""
        if not event.state & 0x1:  # Shift key is not pressed
            self._on_send_message()
            return 'break'
        return None

def main():
    root = tk.Tk()
    app = MessagingApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()