# domain/models.py

from dataclasses import dataclass
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum, auto

class ConnectionState(Enum):
    """Represents the possible connection states of the application."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"

class EventType(Enum):
    """Defines all possible event types in the application."""
    
    # Message Events
    MESSAGE_RECEIVED = auto()
    MESSAGE_SENT = auto()
    MESSAGE_DELETED = auto()
    MESSAGE_EDITED = auto()
    MESSAGE_SEARCH_REQUESTED = auto()
    SEND_MESSAGE_REQUESTED = auto()
    MESSAGE_DISPLAYED = auto()
    
    # Thread Events
    THREAD_SELECTED = auto()
    THREAD_UPDATED = auto()
    NEW_CHAT_REQUESTED = auto()
    THREAD_DELETED = auto()
    
    # Connection Events
    CONNECTION_CHANGED = auto()
    CONNECTION_ERROR = auto()
    
    # State Events
    STATE_CHANGED = auto()
    ERROR_OCCURRED = auto()
    
    # UI Events
    UI_REFRESH_REQUESTED = auto()
    SCROLL_TO_BOTTOM = auto()
    DISPLAY_ERROR = auto()
    
    # System Events
    INITIALIZATION_COMPLETE = auto()
    SHUTDOWN_REQUESTED = auto()

@dataclass
class Message:
    """Represents a single message in a chat thread."""
    text: str
    sender_name: str
    timestamp: float
    thread_name: Optional[str] = None
    direction: str = "incoming"  # "incoming" or "outgoing"
    attachment_path: Optional[str] = None
    attachment_url: Optional[str] = None
    message_id: Optional[str] = None

    @property
    def formatted_timestamp(self) -> str:
        """Returns a formatted string representation of the timestamp."""
        return datetime.fromtimestamp(self.timestamp).strftime("%I:%M %p")

@dataclass
class Thread:
    """Represents a chat thread with one or more participants."""
    guid: str
    name: str
    messages: List[Message]
    phone_number: Optional[str] = None
    last_read_timestamp: Optional[float] = None
    is_archived: bool = False
    
    def add_message(self, message: Message) -> None:
        """Add a new message to the thread."""
        self.messages.append(message)
        
    def get_latest_message(self) -> Optional[Message]:
        """Get the most recent message in the thread."""
        return self.messages[-1] if self.messages else None
    
    def mark_as_read(self, timestamp: Optional[float] = None) -> None:
        """Mark the thread as read up to a specific timestamp."""
        self.last_read_timestamp = timestamp or datetime.now().timestamp()

@dataclass
class AppState:
    """Represents the complete application state."""
    connection_state: ConnectionState = ConnectionState.DISCONNECTED
    current_thread_guid: Optional[str] = None
    is_polling: bool = False
    error_message: Optional[str] = None
    threads: Dict[str, Thread] = None

    def __post_init__(self):
        """Initialize empty threads dictionary if none provided."""
        if self.threads is None:
            self.threads = {}

@dataclass
class Event:
    """Represents an event in the application."""
    type: EventType
    data: Dict
    timestamp: float = None

    def __post_init__(self):
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now().timestamp()