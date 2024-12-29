# services/core.py

import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading
import logging
from typing import Any, Dict, List, Callable, Union
from messaging_app.domain.interfaces import IEventBus, IStateManager
from messaging_app.domain.models import Event, AppState, EventType

class EventBus(IEventBus):
    """
    Event bus implementation for handling application-wide events.
    Thread-safe implementation with support for both sync and async callbacks.
    """
    
    def __init__(self):
        self._subscribers: Dict[EventType, List[Union[Callable[[Event], None], Callable[[Event], Any]]]] = {}
        self._lock = threading.Lock()
        self._logger = logging.getLogger(__name__)
        self._executor = ThreadPoolExecutor(max_workers=5)
        
        # Ensure an event loop exists
        try:
            self._event_loop = asyncio.get_event_loop()
        except RuntimeError:
            self._event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._event_loop)
            # If no event loop is running, create a new one
            self._event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._event_loop)
    
    def subscribe(self, event_type: EventType, callback: Union[Callable[[Event], None], Callable[[Event], Any]]) -> None:
        """Subscribe to a specific event type."""
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append(callback)
            self._logger.debug(f"Added subscriber for {event_type}")
    
    def unsubscribe(self, event_type: EventType, callback: Union[Callable[[Event], None], Callable[[Event], Any]]) -> None:
        """Unsubscribe from a specific event type."""
        with self._lock:
            if event_type in self._subscribers:
                try:
                    self._subscribers[event_type].remove(callback)
                    self._logger.debug(f"Removed subscriber for {event_type}")
                except ValueError:
                    pass  # Callback wasn't registered
    
    def publish(self, event: Event) -> None:
        """Publish an event to all subscribers."""
        subscribers = []
        with self._lock:
            if event.type in self._subscribers:
                subscribers = self._subscribers[event.type].copy()
        
        for callback in subscribers:
            try:
                # Check if the callback is a coroutine function
                if asyncio.iscoroutinefunction(callback):
                    # Run the coroutine in a thread pool
                    self._executor.submit(self._run_async_callback, callback, event)
                else:
                    # Call synchronous callback
                    callback(event)
            except Exception as e:
                self._logger.error(f"Error in event handler: {e}", exc_info=True)
    
    def _run_async_callback(self, callback, event):
        """Run an async callback in a separate thread."""
        try:
            # Create a new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # Run the coroutine to completion
                result = loop.run_until_complete(callback(event))
                return result
            except Exception as e:
                self._logger.error(f"Error running async callback: {e}", exc_info=True)
            finally:
                # Close the loop
                loop.close()
        except Exception as e:
            self._logger.error(f"Unexpected error in async callback execution: {e}", exc_info=True)
            
    def _schedule_coroutine(self, callback, event):
        """Safely schedule a coroutine."""
        def run_callback():
            try:
                # Create a new loop for this thread if needed
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Run the coroutine
                loop.run_until_complete(callback(event))
                
                # Close the loop
                loop.close()
            except Exception as e:
                self._logger.error(f"Error running async callback: {e}", exc_info=True)
        
        # Run in a separate thread to avoid blocking
        threading.Thread(target=run_callback, daemon=True).start()
        """Publish an event to all subscribers."""
        self._logger.info(f"Publishing event: {event.type}")
        subscribers = []
        with self._lock:
            if event.type in self._subscribers:
                subscribers = self._subscribers[event.type].copy()
                self._logger.info(f"Number of subscribers for {event.type}: {len(subscribers)}")
        
        for callback in subscribers:
            try:
                # Check if the callback is a coroutine
                if asyncio.iscoroutinefunction(callback):
                    self._logger.info(f"Scheduling async callback for {event.type}")
                    # Schedule the coroutine to run
                    asyncio.create_task(callback(event))
                else:
                    # Call synchronous callback
                    self._logger.info(f"Calling sync callback for {event.type}")
                    callback(event)
            except Exception as e:
                self._logger.error(f"Error in event handler: {e}", exc_info=True)

class StateManager(IStateManager):
    """
    State manager implementation for handling application state.
    Thread-safe implementation using locks for state updates.
    """
    
    def __init__(self, event_bus: IEventBus):
        self._state = AppState()
        self._observers: List[Callable[[AppState], None]] = []
        self._lock = threading.Lock()
        self._event_bus = event_bus
        self._logger = logging.getLogger(__name__)
        
    def get_state(self) -> AppState:
        """Get the current application state."""
        with self._lock:
            return self._state
    
    def update_state(self, updated_state: AppState) -> None:
        """Update the application state and notify observers."""
        with self._lock:
            old_state = self._state
            self._state = updated_state
            
            # Track what changed
            changes = {
                "connection_changed": old_state.connection_state != updated_state.connection_state,
                "thread_changed": old_state.current_thread_guid != updated_state.current_thread_guid,
                "polling_changed": old_state.is_polling != updated_state.is_polling,
                "threads_changed": old_state.threads != updated_state.threads
            }
        
        # Notify observers
        for observer in self._observers:
            try:
                observer(updated_state)
            except Exception as e:
                self._logger.error(f"Error notifying state observer: {e}", exc_info=True)
        
        # Publish specific change events
        if changes["connection_changed"]:
            self._event_bus.publish(Event(
                EventType.CONNECTION_CHANGED,
                {"state": updated_state.connection_state}
            ))
        
        if changes["thread_changed"]:
            self._event_bus.publish(Event(
                EventType.THREAD_SELECTED,
                {"thread_guid": updated_state.current_thread_guid}
            ))
        
        # Always publish general state change event
        self._event_bus.publish(Event(
            EventType.STATE_CHANGED,
            {
                "old_state": old_state,
                "new_state": updated_state,
                "changes": changes
            }
        ))
    
    def add_observer(self, observer: Callable[[AppState], None]) -> None:
        """Add a state observer."""
        with self._lock:
            self._observers.append(observer)
            
    def remove_observer(self, observer: Callable[[AppState], None]) -> None:
        """Remove a state observer."""
        with self._lock:
            try:
                self._observers.remove(observer)
            except ValueError:
                pass  # Observer wasn't registered
                
    def update_partial_state(self, **kwargs) -> None:
        """Update specific parts of the state while preserving others."""
        with self._lock:
            current_state = self._state
            # Create new state with updated fields
            new_state = AppState(
                connection_state=kwargs.get('connection_state', current_state.connection_state),
                current_thread_guid=kwargs.get('current_thread_guid', current_state.current_thread_guid),
                is_polling=kwargs.get('is_polling', current_state.is_polling),
                threads=kwargs.get('threads', current_state.threads),
                error_message=kwargs.get('error_message', current_state.error_message)
            )
            self.update_state(new_state)