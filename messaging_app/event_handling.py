import logging
import tkinter as tk
from .domain import Event, EventType, ConnectionState
from .services import EventBus, UIManager, ErrorHandler

# messaging_app/event_handling.py
class MessageAppEventHandler:
    """Handles all event-related concerns"""
    
    def __init__(self, 
                 event_bus: EventBus,
                 ui_manager: UIManager,
                 error_handler: ErrorHandler):
        self.event_bus = event_bus
        self.ui_manager = ui_manager
        self.error_handler = error_handler
        self.logger = logging.getLogger(__name__)
        
        self._setup_event_listeners()
    
    def _setup_event_listeners(self) -> None:
        """Set up all event listeners."""
        self.event_bus.subscribe(EventType.STATE_CHANGED, self._on_state_changed)
        self.event_bus.subscribe(EventType.DISPLAY_ERROR, self._on_display_error)
        self.event_bus.subscribe(EventType.UI_REFRESH_REQUESTED, self._on_ui_refresh)
        self.event_bus.subscribe(EventType.THREAD_INITIALIZED, self._on_threads_initialized)
    
    def _on_state_changed(self, event: Event) -> None:
        new_state = event.data.get("state")
        if new_state == ConnectionState.ERROR:
            self.error_handler.handle_error(
                Exception(event.data.get("error", "Unknown error")),
                "connection"
            )

    def _on_display_error(self, event: Event) -> None:
        self.ui_manager.show_error(
            event.data.get("message", "An error occurred")
        )

    def _on_ui_refresh(self, event: Event) -> None:
        try:
            action = event.data.get("action")
            if action == "update_thread":
                update_func = event.data.get("update_func")
                if update_func:
                    update_func()
        except Exception as e:
            self.logger.error(f"Error in UI refresh: {e}", exc_info=True)

    def _on_threads_initialized(self, event: Event) -> None:
        try:
            thread_names = event.data.get("thread_names", [])
            self.ui_manager.update_thread_list(thread_names)
        except Exception as e:
            self.logger.error(f"Error handling thread initialization: {e}", exc_info=True)