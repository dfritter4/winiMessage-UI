# domain/event_types.py

from enum import Enum, auto

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