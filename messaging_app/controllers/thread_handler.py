# controllers/thread_handler.py
import asyncio
import logging
from typing import Optional
from messaging_app.domain import Event, EventType
from messaging_app.utils.timestamp_utils import safe_timestamp_sort
from messaging_app.services import ThreadManager, MessageDisplayManager, ErrorHandler, UIManager
from .interfaces import IThreadHandler

class ThreadHandler(IThreadHandler):
    def __init__(
        self,
        thread_manager: ThreadManager,
        message_display: MessageDisplayManager,
        ui_manager: UIManager,
        error_handler: ErrorHandler,
        event_bus
    ):
        self.thread_manager = thread_manager
        self.message_display = message_display
        self.ui_manager = ui_manager
        self.error_handler = error_handler
        self.event_bus = event_bus
        self.logger = logging.getLogger(__name__)
        self._current_thread = None

    @property
    def current_thread(self):
        return self._current_thread

    async def select_thread(self, thread_name: str) -> None:
        try:
            if not thread_name:
                self.logger.warning("No thread name provided")
                return

            thread = await asyncio.wait_for(
                self.thread_manager.get_thread_by_name(thread_name), 
                timeout=5.0
            )

            if not thread:
                self.logger.warning(f"No thread found with name: {thread_name}")
                return

            # Skip reload if already on this thread
            if self._current_thread and self._current_thread.guid == thread.guid:
                return

            self._current_thread = thread
            
            def update_ui():
                try:
                    self.message_display.clear_display()
                    self.message_display.set_current_thread(thread.guid)
                    
                    messages = safe_timestamp_sort(thread.messages)
                    self.message_display.display_thread_messages(messages, thread.guid)
                    
                except Exception as e:
                    self.logger.error(f"Error updating UI: {e}", exc_info=True)
            
            self.event_bus.publish(Event(
                EventType.UI_REFRESH_REQUESTED,
                {"action": "update_thread", "thread_name": thread_name, "update_func": update_ui}
            ))
                
        except asyncio.TimeoutError:
            self.logger.error(f"Timeout getting thread: {thread_name}")
        except Exception as e:
            self.error_handler.handle_error(e, "thread_selection")

    async def create_thread(self, phone_number: str, display_name: Optional[str]) -> None:
        try:
            thread = await self.thread_manager.create_thread(phone_number, display_name)
            
            self._current_thread = thread
            self.message_display.clear_display()
            self.message_display.set_current_thread(thread.guid)
            
        except Exception as e:
            self.error_handler.handle_error(e, "new_chat_creation")