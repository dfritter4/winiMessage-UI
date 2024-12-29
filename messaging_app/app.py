# messaging_app/app.py
import asyncio
import threading
import tkinter as tk
from .config import load_config
from .domain import Event, EventType
from .services import (
    EventBus,
    StateManager,
    MessageService,
    ThreadManager,
    MessageDisplayManager,
    UIManager,
    ErrorHandler
)
from .controllers import ChatController
from .utils import AsyncApp
from .ui.app_ui import MessageAppUI
from .event_handling import MessageAppEventHandler
from .app_lifecycle import MessageAppLifecycle

class MessagingApp:
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
        self.ui_manager = UIManager(self.root, self.event_bus)
        
        # Initialize UI
        self.ui = MessageAppUI(
            root=self.root,
            config=self.config,
            event_bus=self.event_bus,
            ui_manager=self.ui_manager
        )
        
        # Initialize event handler
        self.event_handler = MessageAppEventHandler(
            self.event_bus,
            self.ui_manager,
            self.error_handler
        )
        
        # Initialize other components
        self.message_display = MessageDisplayManager(
            self.ui.message_display_widget,
            self.config,
            self.event_bus
        )
        
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
        
        # Initialize lifecycle manager with all required parameters
        self.lifecycle = MessageAppLifecycle(
            root=self.root,
            controller=self.controller,
            event_bus=self.event_bus,
            error_handler=self.error_handler,
            async_app=self.async_app  # Pass the async_app instance
        )
        
        # Start initialization
        self.async_app.run_async(self.lifecycle.initialize())