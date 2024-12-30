# controllers/message_handler.py
import logging
from datetime import datetime
from messaging_app.domain import Event, EventType, Message
from messaging_app.utils.timestamp_utils import normalize_timestamp
from messaging_app.services import MessageService, MessageDisplayManager, ThreadManager, ErrorHandler
from .interfaces import IMessageHandler

class MessageHandler(IMessageHandler):
    def __init__(
        self,
        message_service: MessageService,
        message_display: MessageDisplayManager,
        thread_manager: ThreadManager,
        error_handler: ErrorHandler,
        event_bus
    ):
        self.message_service = message_service
        self.message_display = message_display
        self.thread_manager = thread_manager
        self.error_handler = error_handler
        self.event_bus = event_bus
        self.logger = logging.getLogger(__name__)
        self._current_thread = None

    def set_current_thread(self, thread):
        self._current_thread = thread

    async def send_message(self, thread_guid: str, message_text: str) -> bool:
        try:
            if not thread_guid:
                self.event_bus.publish(Event(
                    EventType.DISPLAY_ERROR,
                    {"message": "Please select a chat first."}
                ))
                return False

            success = await self.message_service.send_message(thread_guid, message_text)

            if success:
                timestamp = normalize_timestamp(datetime.now().timestamp())
                if timestamp is None:
                    self.logger.error("Failed to generate valid timestamp")
                    return False
                    
                message = Message(
                    text=message_text,
                    sender_name="Me",
                    timestamp=timestamp,
                    direction="outgoing",
                    thread_name=self._current_thread.name if self._current_thread else None,
                    guid=f"outgoing_{timestamp}"  # Add a unique guid for immediate display
                )

                # First update the UI immediately
                if self._current_thread and self._current_thread.guid == thread_guid:
                    self.message_display.display_message(message, thread_guid)
                    self.message_display.scroll_to_bottom()

                # Then update the thread data
                await self.thread_manager.update_thread(thread_guid, [message])
                
                # Publish event for any other components that need to know
                self.event_bus.publish(Event(
                    EventType.MESSAGE_SENT,
                    {
                        "thread_guid": thread_guid,
                        "message": message
                    }
                ))
                return True

            return False

        except Exception as e:
            self.error_handler.handle_error(e, "send_message")
            return False
        
    async def handle_message_received(self, event: Event) -> None:
        try:
            thread_guid = event.data.get("thread_guid")
            message = event.data.get("message")

            self.logger.info(f"Received message for thread {thread_guid}")
            
            if not thread_guid or not message:
                return

            if (self._current_thread and 
                self._current_thread.guid == thread_guid):
                self.message_display.display_message(message)
                self.message_display.scroll_to_bottom()
                
        except Exception as e:
            self.error_handler.handle_error(e, "message_received")