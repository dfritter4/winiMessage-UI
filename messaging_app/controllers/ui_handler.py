# controllers/ui_handler.py
import logging
from messaging_app.domain import Event
from messaging_app.utils.timestamp_utils import safe_timestamp_sort
from messaging_app.services import MessageDisplayManager, ThreadManager, ErrorHandler
from .interfaces import IUIEventHandler

class UIEventHandler(IUIEventHandler):
    def __init__(
        self,
        message_display: MessageDisplayManager,
        thread_manager: ThreadManager,
        error_handler: ErrorHandler
    ):
        self.message_display = message_display
        self.thread_manager = thread_manager
        self.error_handler = error_handler
        self.logger = logging.getLogger(__name__)
        self._current_thread = None

    def set_current_thread(self, thread):
        self._current_thread = thread

    async def handle_ui_refresh(self, event: Event) -> None:
        """Handle UI refresh requests."""
        try:
            thread_guid = event.data.get("thread_guid")
            if thread_guid and self._current_thread and self._current_thread.guid == thread_guid:
                self.message_display.clear_display()
                thread = await self.thread_manager.get_thread(thread_guid)
                if thread:
                    for message in safe_timestamp_sort(thread.messages):
                        self.message_display.display_message(message)
                    self.message_display.scroll_to_bottom()
                    
        except Exception as e:
            self.error_handler.handle_error(e, "ui_refresh")

    def handle_error(self, event: Event) -> None:
        """Handle error events."""
        error_data = event.data
        self.logger.error(
            f"Error in {error_data.get('context', 'unknown')}: {error_data.get('error')}"
        )