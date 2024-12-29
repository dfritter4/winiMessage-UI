import tkinter as tk
from tkinter import messagebox, simpledialog
import logging
from typing import Optional, Callable, Dict

from ..domain import IEventBus, Event, EventType, AppState, IStateManager
from ..config import AppConfig
from ..modern_ui import (
    ModernScrolledText,
    ModernListbox,
    ModernEntry,
    ModernButton,
    ModernFrame
)

class UIManager:
    def __init__(
        self,
        root: tk.Tk,
        config: AppConfig,
        event_bus: IEventBus,
        state_manager: IStateManager
    ):
        self.root = root
        self.config = config
        self.event_bus = event_bus
        self.state_manager = state_manager
        self.logger = logging.getLogger(__name__)

        # Initialize UI components as None
        self.main_container: Optional[ModernFrame] = None
        self.paned_window: Optional[tk.PanedWindow] = None
        self.sidebar: Optional[ModernFrame] = None
        self.chat_listbox: Optional[ModernListbox] = None
        self.message_display: Optional[ModernScrolledText] = None
        self.message_entry: Optional[tk.Text] = None
        self.send_button: Optional[ModernButton] = None

        # Set up UI
        self._setup_root()
        self._create_ui()
        self._setup_event_handlers()

    def _setup_root(self) -> None:
        """Configure the root window."""
        self.root.title("Messages")
        self.root.geometry("1000x700")
        self.root.configure(bg=self.config.colors.background)

    def _create_ui(self) -> None:
        """Create the main UI components."""
        try:
            # Main container
            self.main_container = ModernFrame(self.root)
            self.main_container.pack(fill="both", expand=True)

            # PanedWindow
            self.paned_window = tk.PanedWindow(
                self.main_container,
                orient=tk.HORIZONTAL,
                sashrelief="raised"
            )
            self.paned_window.pack(fill="both", expand=True)

            self._create_sidebar()
            self._create_chat_area()

        except Exception as e:
            self.logger.error(f"Error creating UI: {e}", exc_info=True)
            self.event_bus.publish(Event(
                EventType.ERROR_OCCURRED,
                {"error": str(e), "context": "ui_creation"}
            ))

    def _create_sidebar(self) -> None:
        """Create the sidebar components."""
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
            font=(self.config.ui.font_family, self.config.ui.font_sizes["normal"])
        )
        self.search_entry.pack(fill="x", padx=10, pady=10)

        # Chat Listbox
        self.chat_listbox = ModernListbox(self.sidebar, height=20)
        self.chat_listbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # New Chat Button
        self.new_chat_btn = ModernButton(
            self.sidebar,
            text="New Message",
            command=self._on_new_chat_clicked
        )
        self.new_chat_btn.pack(fill="x", padx=10, pady=(0, 10))

    def _create_chat_area(self) -> None:
        """Create the chat area components."""
        chat_container = ModernFrame(self.paned_window)
        self.paned_window.add(chat_container, minsize=400)

        # Message Display
        self.message_display = ModernScrolledText(chat_container)
        self.message_display.pack(fill="both", expand=True, padx=10, pady=10)

        # Input Area
        input_frame = ModernFrame(chat_container)
        input_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.message_entry = tk.Text(
            input_frame,
            height=3,
            font=(self.config.ui.font_family, self.config.ui.font_sizes["normal"]),
            wrap="word",
            bd=1,
            relief="solid"
        )
        self.message_entry.pack(fill="x", side="left", expand=True, padx=(0, 10))

        self.send_button = ModernButton(
            input_frame,
            text="Send",
            command=self._on_send_clicked
        )
        self.send_button.pack(side="right")

    def _setup_event_handlers(self) -> None:
        """Set up event handlers for UI components."""
        self.chat_listbox.bind("<<ListboxSelect>>", self._on_chat_selected)
        self.message_entry.bind("<Return>", self._on_return_key)
        self.message_entry.bind("<Shift-Return>", lambda e: 'break')

        # Subscribe to events
        self.event_bus.subscribe(EventType.ERROR_OCCURRED, self._handle_error)
        self.event_bus.subscribe(EventType.STATE_CHANGED, self._handle_state_change)

    def _on_chat_selected(self, event) -> None:
        """Handle chat selection from the listbox."""
        selection = self.chat_listbox.curselection()
        if selection:
            selected_name = self.chat_listbox.get(selection[0])
            self.event_bus.publish(Event(
                EventType.THREAD_SELECTED,
                {"thread_name": selected_name}
            ))

    def _on_send_clicked(self) -> None:
        """Handle send button click."""
        message = self.message_entry.get("1.0", "end-1c").strip()
        if message:
            self.event_bus.publish(Event(
                EventType.SEND_MESSAGE_REQUESTED,
                {"message": message}
            ))
            self.message_entry.delete("1.0", tk.END)

    def _on_return_key(self, event) -> None:
        """Handle return key in message entry."""
        if not event.state & 0x1:  # Shift key is not pressed
            self._on_send_clicked()
            return 'break'
        return None

    def _on_new_chat_clicked(self) -> None:
        """Handle new chat button click."""
        self.event_bus.publish(Event(
            EventType.NEW_CHAT_REQUESTED,
            {}
        ))

    def _handle_error(self, event: Event) -> None:
        """Handle error events."""
        error_data = event.data
        messagebox.showerror(
            "Error",
            error_data.get("error", "An unknown error occurred.")
        )

    def _handle_state_change(self, event: Event) -> None:
        """Handle state change events."""
        new_state: AppState = event.data["new_state"]
        # Update UI based on new state
        pass

    def show_error(self, message: str) -> None:
        """Show an error message to the user."""
        messagebox.showerror("Error", message)

    def show_info(self, message: str) -> None:
        """Show an info message to the user."""
        messagebox.showinfo("Information", message)

    def ask_input(self, prompt: str, title: str = "Input") -> Optional[str]:
        """Ask the user for input."""
        return simpledialog.askstring(title, prompt, parent=self.root)