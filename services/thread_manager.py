import logging
from typing import Dict, List, Optional
from ..domain import (
    IThreadManager,
    IEventBus,
    IMessageService,
    Thread,
    Message,
    Event,
    EventType
)

class ThreadManager(IThreadManager):
    def __init__(
        self,
        message_service: IMessageService,
        event_bus: IEventBus
    ):
        self.message_service = message_service
        self.event_bus = event_bus
        self.logger = logging.getLogger(__name__)
        self._threads: Dict[str, Thread] = {}

    def get_thread(self, guid: str) -> Optional[Thread]:
        """Retrieve a thread by its GUID."""
        return self._threads.get(guid)

    def create_thread(self, phone_number: str, name: str = None) -> Thread:
        """Create a new message thread."""
        # Normalize phone number format
        if not phone_number.startswith("+"):
            phone_number = "+" + phone_number
        phone_number = "+" + "".join(filter(str.isdigit, phone_number))

        # Create thread ID and name
        thread_guid = f"thread-{phone_number}"
        thread_name = name or phone_number

        # Create new thread if it doesn't exist
        if thread_guid not in self._threads:
            thread = Thread(
                guid=thread_guid,
                name=thread_name,
                messages=[],
                phone_number=phone_number
            )
            self._threads[thread_guid] = thread
            
            # Publish thread created event
            self.event_bus.publish(Event(
                EventType.THREAD_UPDATED,
                {"thread": thread, "action": "created"}
            ))
            
            return thread
        
        return self._threads[thread_guid]

    def update_thread(self, guid: str, messages: List[Message]) -> None:
        """Update a thread with new messages."""
        thread = self._threads.get(guid)
        if not thread:
            self.logger.warning(f"Attempting to update non-existent thread: {guid}")
            return

        # Add new messages
        for message in messages:
            if message not in thread.messages:  # This requires proper __eq__ implementation in Message
                thread.messages.append(message)

        # Sort messages by timestamp
        thread.messages.sort(key=lambda m: m.timestamp)

        # Publish thread updated event
        self.event_bus.publish(Event(
            EventType.THREAD_UPDATED,
            {"thread": thread, "action": "updated"}
        ))

    def get_all_threads(self) -> Dict[str, Thread]:
        """Get all threads."""
        return self._threads.copy()

    def delete_thread(self, guid: str) -> bool:
        """Delete a thread."""
        if guid in self._threads:
            thread = self._threads.pop(guid)
            self.event_bus.publish(Event(
                EventType.THREAD_UPDATED,
                {"thread": thread, "action": "deleted"}
            ))
            return True
        return False

    async def initialize_threads(self) -> None:
        """Initialize threads from the message service."""
        try:
            threads = await self.message_service.initialize_threads()
            self._threads = threads
            
            # Publish initialization complete event
            self.event_bus.publish(Event(
                EventType.THREAD_UPDATED,
                {"action": "initialized", "thread_count": len(threads)}
            ))
            
        except Exception as e:
            self.logger.error(f"Error initializing threads: {e}", exc_info=True)
            self.event_bus.publish(Event(
                EventType.ERROR_OCCURRED,
                {"error": str(e), "context": "thread_initialization"}
            ))
            raise

    def get_thread_by_name(self, name: str) -> Optional[Thread]:
        """Find a thread by its name."""
        for thread in self._threads.values():
            if thread.name == name:
                return thread
        return None

    def mark_thread_read(self, guid: str) -> None:
        """Mark a thread as read."""
        thread = self._threads.get(guid)
        if thread:
            # In future, implement read status
            self.event_bus.publish(Event(
                EventType.THREAD_UPDATED,
                {"thread": thread, "action": "marked_read"}
            ))