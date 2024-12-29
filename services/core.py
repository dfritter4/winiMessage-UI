from typing import Dict, List, Callable
from ..domain.interfaces import IEventBus, IStateManager, Event
from ..domain.models import AppState
import threading
import logging

class EventBus(IEventBus):
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._lock = threading.Lock()
        self._logger = logging.getLogger(__name__)
    
    def subscribe(self, event_type: str, callback: Callable[[Event], None]) -> None:
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append(callback)
    
    def publish(self, event: Event) -> None:
        with self._lock:
            subscribers = self._subscribers.get(event.type, []).copy()
        
        for callback in subscribers:
            try:
                callback(event)
            except Exception as e:
                self._logger.error(f"Error in event handler: {e}", exc_info=True)

class StateManager(IStateManager):
    def __init__(self, event_bus: IEventBus):
        self._state = AppState()
        self._observers: List[Callable[[AppState], None]] = []
        self._lock = threading.Lock()
        self._event_bus = event_bus
        
    def get_state(self) -> AppState:
        with self._lock:
            return self._state
    
    def update_state(self, updated_state: AppState) -> None:
        with self._lock:
            old_state = self._state
            self._state = updated_state
            
        # Notify observers
        for observer in self._observers:
            try:
                observer(updated_state)
            except Exception as e:
                logging.error(f"Error notifying state observer: {e}", exc_info=True)
        
        # Publish state change event
        self._event_bus.publish(Event(EventType.STATE_CHANGED, {
            'old_state': old_state,
            'new_state': updated_state
        }))
    
    def add_observer(self, observer: Callable[[AppState], None]) -> None:
        with self._lock:
            self._observers.append(observer)