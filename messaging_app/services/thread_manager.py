# services/thread_manager.py

import logging
from typing import Optional, Dict, List
from datetime import datetime

import aiohttp

from messaging_app.domain import (
    IThreadManager,
    IStateManager,
    IEventBus,
    Thread,
    Message,
    Event,
    EventType,
    AppState
)
from messaging_app.services import MessageService

class ThreadManager(IThreadManager):
    """
    Manages chat threads and their messages.
    Handles thread creation, updates, and state management.
    """
    
    def __init__(
        self,
        message_service: MessageService,
        event_bus: IEventBus,
        state_manager: IStateManager
    ):
        self._message_service = message_service
        self._event_bus = event_bus
        self._state_manager = state_manager
        self._logger = logging.getLogger(__name__)
        self._threads: Dict[str, Thread] = {}
        self._thread_names: Dict[str, str] = {}

    async def initialize_threads(self) -> Dict[str, Thread]:
        """Initialize and return all message threads."""
        try:
            self._logger.info(f"Initializing threads from message service")
            
            # Get threads from message service
            threads = await self._message_service.initialize_threads()
            
            # Update local thread cache
            self._threads = threads
            self._thread_names = {
                guid: thread.name 
                for guid, thread in threads.items()
            }
            
            # Populate chat list
            # If you have a method to update the chat list, call it here
            self._event_bus.publish(Event(
                EventType.THREAD_INITIALIZED,
                {
                    "threads": list(threads.keys()),
                    "thread_names": list(self._thread_names.values())
                }
            ))
            
            # Update application state
            current_state = self._state_manager.get_state()
            self._state_manager.update_state(AppState(
                connection_state=current_state.connection_state,
                current_thread_guid=current_state.current_thread_guid,
                is_polling=current_state.is_polling,
                threads=self._threads
            ))
            
            # Publish initialization event
            self._event_bus.publish(Event(
                EventType.INITIALIZATION_COMPLETE,
                {"thread_count": len(threads)}
            ))
            
            self._logger.info(f"Successfully initialized {len(threads)} threads")
            return threads
            
        except Exception as e:
            self._logger.error(f"Error initializing threads: {e}", exc_info=True)
            self._event_bus.publish(Event(
                EventType.ERROR_OCCURRED,
                {
                    "error": str(e),
                    "context": "thread_initialization"
                }
            ))
            raise

    async def get_thread(self, guid: str) -> Optional[Thread]:
        """Get a thread by its GUID."""
        try:
            return self._threads.get(guid)
        except Exception as e:
            self._logger.error(f"Error getting thread {guid}: {e}", exc_info=True)
            return None

    async def get_thread_by_name(self, name: str) -> Optional[Thread]:
        """Get a thread by its name."""
        try:
            # Find thread with matching name
            for thread in self._threads.values():
                if thread.name == name:
                    return thread
            
            # If not found, log and return None
            self._logger.warning(f"No thread found with name: {name}")
            return None
        except Exception as e:
            self._logger.error(f"Error getting thread by name {name}: {e}", exc_info=True)
            return None

    async def create_thread(self, phone_number: str, name: Optional[str] = None) -> Thread:
        """Create a new thread."""
        try:
            self._logger.info(f"Creating new thread for {phone_number}")
            
            # Generate thread GUID
            thread_guid = f"thread_{phone_number}_{int(datetime.now().timestamp())}"
            
            # Create thread object
            thread = Thread(
                guid=thread_guid,
                name=name or phone_number,
                messages=[],
                phone_number=phone_number
            )
            
            # Update local caches
            self._threads[thread_guid] = thread
            self._thread_names[thread_guid] = thread.name
            
            # Update application state
            current_state = self._state_manager.get_state()
            self._state_manager.update_state(AppState(
                connection_state=current_state.connection_state,
                current_thread_guid=thread_guid,
                is_polling=current_state.is_polling,
                threads=self._threads
            ))
            
            # Publish thread creation event
            self._event_bus.publish(Event(
                EventType.THREAD_UPDATED,
                {
                    "thread_guid": thread_guid,
                    "action": "created"
                }
            ))
            
            self._logger.info(f"Successfully created thread {thread_guid}")
            return thread
            
        except Exception as e:
            self._logger.error(f"Error creating thread: {e}", exc_info=True)
            self._event_bus.publish(Event(
                EventType.ERROR_OCCURRED,
                {
                    "error": str(e),
                    "context": "thread_creation"
                }
            ))
            raise

    async def update_thread(self, guid: str, messages: List[Message]) -> None:
        """Update a thread with new messages."""
        try:
            self._logger.debug(f"Updating thread {guid} with {len(messages)} messages")
            
            # Create thread if it doesn't exist
            if guid not in self._threads:
                self._threads[guid] = Thread(
                    guid=guid,
                    name=self._thread_names.get(guid, "Unknown"),
                    messages=[]
                )
            
            thread = self._threads[guid]
            
            # Add new messages
            for message in messages:
                thread.add_message(message)
            
            # Update application state
            current_state = self._state_manager.get_state()
            self._state_manager.update_state(AppState(
                connection_state=current_state.connection_state,
                current_thread_guid=current_state.current_thread_guid,
                is_polling=current_state.is_polling,
                threads=self._threads
            ))
            
            # Publish thread update event
            self._event_bus.publish(Event(
                EventType.THREAD_UPDATED,
                {
                    "thread_guid": guid,
                    "action": "updated",
                    "message_count": len(messages)
                }
            ))
            
        except Exception as e:
            self._logger.error(f"Error updating thread {guid}: {e}", exc_info=True)
            self._event_bus.publish(Event(
                EventType.ERROR_OCCURRED,
                {
                    "error": str(e),
                    "context": "thread_update"
                }
            ))
            raise

    async def delete_thread(self, guid: str) -> None:
        """Delete a thread."""
        try:
            self._logger.info(f"Deleting thread {guid}")
            
            if guid in self._threads:
                del self._threads[guid]
                if guid in self._thread_names:
                    del self._thread_names[guid]
                
                # Update application state
                current_state = self._state_manager.get_state()
                new_current_thread = None if current_state.current_thread_guid == guid else current_state.current_thread_guid
                
                self._state_manager.update_state(AppState(
                    connection_state=current_state.connection_state,
                    current_thread_guid=new_current_thread,
                    is_polling=current_state.is_polling,
                    threads=self._threads
                ))
                
                # Publish thread deletion event
                self._event_bus.publish(Event(
                    EventType.THREAD_DELETED,
                    {
                        "thread_guid": guid,
                        "action": "deleted"
                    }
                ))
                
                self._logger.info(f"Successfully deleted thread {guid}")
                
        except Exception as e:
            self._logger.error(f"Error deleting thread {guid}: {e}", exc_info=True)
            self._event_bus.publish(Event(
                EventType.ERROR_OCCURRED,
                {
                    "error": str(e),
                    "context": "thread_deletion"
                }
            ))
            raise

    async def update_thread_data(self, guid: str, data: Dict) -> None:
        """Update thread metadata."""
        try:
            self._logger.debug(f"Updating thread {guid} metadata: {data}")
            
            if guid in self._threads:
                thread = self._threads[guid]
                
                # Update thread properties
                if "name" in data:
                    thread.name = data["name"]
                    self._thread_names[guid] = data["name"]
                if "last_read_timestamp" in data:
                    thread.mark_as_read(data["last_read_timestamp"])
                
                # Update application state
                current_state = self._state_manager.get_state()
                self._state_manager.update_state(AppState(
                    connection_state=current_state.connection_state,
                    current_thread_guid=current_state.current_thread_guid,
                    is_polling=current_state.is_polling,
                    threads=self._threads
                ))
                
                # Publish thread update event
                self._event_bus.publish(Event(
                    EventType.THREAD_UPDATED,
                    {
                        "thread_guid": guid,
                        "action": "metadata_updated",
                        "updated_fields": list(data.keys())
                    }
                ))
                
        except Exception as e:
            self._logger.error(f"Error updating thread data for {guid}: {e}", exc_info=True)
            self._event_bus.publish(Event(
                EventType.ERROR_OCCURRED,
                {
                    "error": str(e),
                    "context": "thread_data_update"
                }
            ))
            raise