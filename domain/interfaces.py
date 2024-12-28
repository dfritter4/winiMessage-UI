from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Callable
from .models import Message, Thread, AppState

class IMessageService(ABC):
    @abstractmethod
    async def initialize_threads(self) -> Dict[str, Thread]:
        pass
    
    @abstractmethod
    async def poll_messages(self) -> Dict[str, List[Message]]:
        pass
    
    @abstractmethod
    async def send_message(self, thread_guid: str, message: str) -> bool:
        pass

class IMessageDisplay(ABC):
    @abstractmethod
    def display_message(self, message: Message) -> None:
        pass
    
    @abstractmethod
    def clear_display(self) -> None:
        pass
    
    @abstractmethod
    def scroll_to_bottom(self) -> None:
        pass

class IThreadManager(ABC):
    @abstractmethod
    def get_thread(self, guid: str) -> Optional[Thread]:
        pass
    
    @abstractmethod
    def create_thread(self, phone_number: str, name: str) -> Thread:
        pass
    
    @abstractmethod
    def update_thread(self, guid: str, messages: List[Message]) -> None:
        pass

class IStateManager(ABC):
    @abstractmethod
    def get_state(self) -> AppState:
        pass
    
    @abstractmethod
    def update_state(self, updated_state: AppState) -> None:
        pass
    
    @abstractmethod
    def add_observer(self, observer: Callable[[AppState], None]) -> None:
        pass

class IErrorHandler(ABC):
    @abstractmethod
    def handle_error(self, error: Exception, context: str = None) -> None:
        pass

class EventType:
    MESSAGE_RECEIVED = "message_received"
    MESSAGE_SENT = "message_sent"
    THREAD_UPDATED = "thread_updated"
    ERROR_OCCURRED = "error_occurred"
    STATE_CHANGED = "state_changed"
    CONNECTION_CHANGED = "connection_changed"

class Event:
    def __init__(self, event_type: str, data: Any):
        self.type = event_type
        self.data = data
        self.timestamp = time.time()

class IEventBus(ABC):
    @abstractmethod
    def subscribe(self, event_type: str, callback: Callable[[Event], None]) -> None:
        pass
    
    @abstractmethod
    def publish(self, event: Event) -> None:
        pass