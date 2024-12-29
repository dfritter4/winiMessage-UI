import logging
from typing import Optional, Callable
from ..domain import IErrorHandler, IEventBus, Event, EventType

class ErrorCategory:
    NETWORK = "network"
    THREAD = "thread"
    UI = "ui"
    MESSAGE = "message"
    UNKNOWN = "unknown"

class ApplicationError(Exception):
    """Base exception class for application-specific errors."""
    def __init__(self, message: str, category: str = ErrorCategory.UNKNOWN):
        super().__init__(message)
        self.category = category

class NetworkError(ApplicationError):
    def __init__(self, message: str):
        super().__init__(message, ErrorCategory.NETWORK)

class ThreadError(ApplicationError):
    def __init__(self, message: str):
        super().__init__(message, ErrorCategory.THREAD)

class MessageError(ApplicationError):
    def __init__(self, message: str):
        super().__init__(message, ErrorCategory.MESSAGE)

class ErrorHandler(IErrorHandler):
    def __init__(self, event_bus: IEventBus):
        self.event_bus = event_bus
        self.logger = logging.getLogger(__name__)
        self._error_callbacks: dict[str, list[Callable]] = {}

    def handle_error(self, error: Exception, context: str = None) -> None:
        """Handle an error by logging it and notifying observers."""
        # Determine error category
        if isinstance(error, ApplicationError):
            category = error.category
        elif isinstance(error, (ConnectionError, TimeoutError)):
            category = ErrorCategory.NETWORK
        else:
            category = ErrorCategory.UNKNOWN

        # Log the error
        self.logger.error(
            f"Error in {context or 'unknown context'} ({category}): {str(error)}",
            exc_info=True
        )

        # Create error event data
        error_data = {
            "error": str(error),
            "category": category,
            "context": context
        }

        # Publish error event
        self.event_bus.publish(Event(
            EventType.ERROR_OCCURRED,
            error_data
        ))

        # Call registered callbacks for this category
        for callback in self._error_callbacks.get(category, []):
            try:
                callback(error_data)
            except Exception as e:
                self.logger.error(f"Error in error callback: {e}", exc_info=True)

    def register_callback(self, category: str, callback: Callable) -> None:
        """Register a callback for a specific error category."""
        if category not in self._error_callbacks:
            self._error_callbacks[category] = []
        self._error_callbacks[category].append(callback)

    def unregister_callback(self, category: str, callback: Callable) -> None:
        """Unregister a callback for a specific error category."""
        if category in self._error_callbacks:
            try:
                self._error_callbacks[category].remove(callback)
            except ValueError:
                pass  # Callback wasn't registered

    @staticmethod
    def format_user_message(error: Exception) -> str:
        """Format an error message suitable for displaying to users."""
        if isinstance(error, NetworkError):
            return "Unable to connect to the messaging service. Please check your internet connection."
        elif isinstance(error, ThreadError):
            return "There was a problem with the message thread. Please try again."
        elif isinstance(error, MessageError):
            return "Failed to send or receive messages. Please try again."
        else:
            return "An unexpected error occurred. Please try again later."