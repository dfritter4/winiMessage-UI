#!/usr/bin/env python3
import asyncio
import logging
import threading
import tkinter as tk
from tkinter import ttk
from datetime import datetime

from messaging_app.bubbles import (
    EnhancedTextContent,  # Add this import
    TextBubbleFactory     # Optional, but might be useful
)

from messaging_app.config import AppConfig, load_config
from messaging_app.domain import Event, EventType, ConnectionState
from messaging_app.ui import (
    ModernScrolledText,
    ModernListbox,
    ModernEntry,
    ModernButton,
    ModernFrame
)
from messaging_app.controllers import ChatController
from messaging_app.services import (
    EventBus,
    StateManager,
    MessageService,
    ThreadManager,
    MessageDisplayManager,
    UIManager,
    ErrorHandler
)
from messaging_app.utils import AsyncApp

class MessagingApp:
    """Main application class for the Messages app."""

    def __init__(self, root: tk.Tk, async_app: AsyncApp):
        self.root = root
        self.async_app = async_app
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
        
        # Initialize UI-dependent services
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
        
        # Set up event listeners
        self._setup_event_listeners()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Start initialization
        self.root.after(100, self._initialize_async)

        self.logger = logging.getLogger(__name__)

    def _setup_event_listeners(self) -> None:
        """Set up listeners for application events."""
        self.event_bus.subscribe(EventType.STATE_CHANGED, self._on_state_changed)
        self.event_bus.subscribe(EventType.DISPLAY_ERROR, self._on_display_error)
        self.event_bus.subscribe(EventType.UI_REFRESH_REQUESTED, self._on_ui_refresh)
        
        # Add this new event listener
        self.event_bus.subscribe(EventType.THREAD_INITIALIZED, self._on_threads_initialized)

    def _on_threads_initialized(self, event: Event) -> None:
        """Populate chat list when threads are initialized."""
        try:
            thread_names = event.data.get("thread_names", [])
            
            # Clear existing items
            self.chat_listbox.delete(0, tk.END)
            
            # Add thread names to listbox
            for name in thread_names:
                self.chat_listbox.insert(tk.END, name)
            
        except Exception as e:
            self.logger.error(f"Error populating chat list: {e}", exc_info=True)

    def _setup_styles(self) -> None:
        """Configure ttk styles for the application."""
        style = ttk.Style()
        style.configure("Chat.TFrame", background="white")
        style.configure("Sidebar.TFrame", background="#F5F5F7")

    def _create_ui(self) -> None:
        """Create the main UI components."""
        # Main container
        self.main_container = ModernFrame(self.root)
        self.main_container.pack(fill="both", expand=True)

        # PanedWindow for sidebar and chat area
        self.paned_window = tk.PanedWindow(
            self.main_container,
            orient=tk.HORIZONTAL,
            sashrelief="raised"
        )
        self.paned_window.pack(fill="both", expand=True)

        self._create_sidebar()
        self._create_chat_area()

    def _create_sidebar(self) -> None:
        """Create the sidebar with search and thread list."""
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
        self.search_entry.bind("<Return>", self._on_search)

        # Chat Listbox
        self.chat_listbox = ModernListbox(self.sidebar, height=20)
        self.chat_listbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.chat_listbox.bind("<<ListboxSelect>>", self._on_thread_selected)
        self.chat_listbox.bind("<Button-3>", self._on_thread_context_menu)

        # New Chat Button
        self.new_chat_btn = ModernButton(
            self.sidebar,
            text="New Message",
            command=self._on_new_chat
        )
        self.new_chat_btn.pack(fill="x", padx=10, pady=(0, 10))

    def _create_chat_area(self) -> None:
        """Create the main chat area."""
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
        self.message_entry.bind("<KeyRelease>", self._on_typing)

        self.send_button = ModernButton(
            self.input_frame,
            text="Send",
            command=self._on_send_message
        )
        self.send_button.pack(side="right")

    def _initialize_async(self) -> None:
        """Initialize the application asynchronously."""
        def init_app():
            try:
                # Run the initialization coroutine
                asyncio.run(self.controller.initialize())
            except Exception as e:
                self.logger.error(f"Initialization error: {e}", exc_info=True)

        # Run initialization in a separate thread
        threading.Thread(target=init_app, daemon=True).start()
        
    def _on_thread_selected(self, event) -> None:
        """Handle thread selection from listbox."""
        selection = self.chat_listbox.curselection()
        if selection:
            thread_name = self.chat_listbox.get(selection[0])
            self.logger.info(f"Selected thread: {thread_name}")
            self.event_bus.publish(Event(
                EventType.THREAD_SELECTED,
                {"thread_name": thread_name}
            ))

    def _on_new_chat(self) -> None:
        """Handle new chat button click."""
        self.event_bus.publish(Event(
            EventType.NEW_CHAT_REQUESTED,
            {}
        ))

    def _on_send_message(self) -> None:
        """Handle send message button click."""
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

    def _on_return_key(self, event) -> None:
        """Handle Return key in message entry."""
        if not event.state & 0x1:  # Shift key is not pressed
            self._on_send_message()
            return 'break'
        return None

    def _on_typing(self, event) -> None:
        """Handle typing in message entry."""
        if event.keysym not in ('Return', 'Shift_L', 'Shift_R'):
            self.event_bus.publish(Event(
                EventType.STATE_CHANGED,
                {"is_typing": True}
            ))

    def _on_search(self, event) -> None:
        """Handle search entry Return key."""
        search_term = self.search_entry.get().strip()
        if search_term:
            self.event_bus.publish(Event(
                EventType.MESSAGE_SEARCH_REQUESTED,
                {"search_term": search_term}
            ))

    def _on_thread_context_menu(self, event) -> None:
        """Handle right-click on thread list."""
        selection = self.chat_listbox.nearest(event.y)
        if selection >= 0:
            thread_name = self.chat_listbox.get(selection)
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(
                label="Delete Thread",
                command=lambda: self._delete_thread(thread_name)
            )
            menu.add_command(
                label="Mark as Read",
                command=lambda: self._mark_thread_read(thread_name)
            )
            menu.post(event.x_root, event.y_root)

    def _delete_thread(self, thread_name: str) -> None:
        """Handle thread deletion."""
        self.event_bus.publish(Event(
            EventType.THREAD_DELETED,
            {"thread_name": thread_name}
        ))

    def _mark_thread_read(self, thread_name: str) -> None:
        """Handle marking thread as read."""
        self.event_bus.publish(Event(
            EventType.THREAD_UPDATED,
            {
                "thread_name": thread_name,
                "thread_data": {"last_read_timestamp": datetime.now().timestamp()}
            }
        ))

    def _on_state_changed(self, event: Event) -> None:
        """Handle application state changes."""
        new_state = event.data.get("state")
        if new_state == ConnectionState.ERROR:
            self.error_handler.handle_error(
                Exception(event.data.get("error", "Unknown error")),
                "connection"
            )

    def _on_display_error(self, event: Event) -> None:
        """Handle error display requests."""
        self.ui_manager.show_error(event.data.get("message", "An error occurred"))

    def _on_ui_refresh(self, event: Event) -> None:
        """Handle UI refresh requests."""
        try:
            action = event.data.get("action")
            
            if action == "update_thread":
                # Get and run the update function
                update_func = event.data.get("update_func")
                if update_func:
                    update_func()
            else:
                # Existing refresh logic
                self.message_display_widget.update_idletasks()
        except Exception as e:
            self.logger.error(f"Error in UI refresh: {e}", exc_info=True)

    def _on_close(self) -> None:
        """Handle application window close."""
        self.event_bus.publish(Event(
            EventType.SHUTDOWN_REQUESTED,
            {}
        ))
        self.root.destroy()

def main():
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    try:
        root = tk.Tk()
        app_wrapper = AsyncApp(root)
        app = MessagingApp(root, app_wrapper)
        app_wrapper.start()
    except Exception as e:
        logger.error(f"Error starting application: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()