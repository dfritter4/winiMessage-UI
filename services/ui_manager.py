import tkinter as tk
import logging
from typing import Optional, Dict
from ..domain import IMessageDisplay, Message, IEventBus, Event, EventType
from ..config import AppConfig
from ..bubbles import TextBubble, ImageBubble, EnhancedTextBubble
from ..modern_ui import ModernScrolledText

class MessageDisplayManager(IMessageDisplay):
    def __init__(
        self,
        container: ModernScrolledText,
        config: AppConfig,
        event_bus: IEventBus
    ):
        self.container = container
        self.config = config
        self.event_bus = event_bus
        self.logger = logging.getLogger(__name__)
        self._current_thread_guid: Optional[str] = None
        self._message_widgets: Dict[str, tk.Widget] = {}

    def display_message(self, message: Message) -> None:
        """Display a single message in the UI."""
        try:
            # Create container frame for the message
            container = tk.Frame(
                self.container.scrollable_frame,
                bg=self.config.colors.background
            )
            container.pack(
                fill="x",
                padx=15,
                pady=5
            )

            # Determine if this is an image message
            is_image = (
                message.attachment_url is not None and
                any(message.attachment_url.lower().endswith(ext)
                    for ext in ['.jpg', '.jpeg', '.png', '.gif', '.heic', '.heif'])
            )

            # Create appropriate bubble type
            if is_image:
                bubble = ImageBubble(
                    container,
                    message.text,
                    message.attachment_url,
                    is_outgoing=message.direction == "outgoing",
                    timestamp=message.timestamp,
                    sender_name=message.sender_name
                )
            else:
                bubble = EnhancedTextBubble(
                    container,
                    message.text,
                    is_outgoing=message.direction == "outgoing",
                    timestamp=message.timestamp,
                    sender_name=message.sender_name
                )

            bubble.pack(
                side="right" if message.direction == "outgoing" else "left",
                fill="none",
                expand=False
            )

            # Store widget reference
            message_id = f"{message.sender_name}:{message.timestamp}"
            self._message_widgets[message_id] = container

            # Update container
            self.container.scrollable_frame.update_idletasks()
            self.container._on_frame_configure()

            # Publish message displayed event
            self.event_bus.publish(Event(
                EventType.MESSAGE_DISPLAYED,
                {"message_id": message_id}
            ))

        except Exception as e:
            self.logger.error(f"Error displaying message: {e}", exc_info=True)
            self.event_bus.publish(Event(
                EventType.ERROR_OCCURRED,
                {"error": str(e), "context": "message_display"}
            ))

    def clear_display(self) -> None:
        """Clear all messages from the display."""
        try:
            # Remove all widgets
            for widget in self._message_widgets.values():
                widget.destroy()
            self._message_widgets.clear()

            # Reset scroll region
            self.container._on_frame_configure()

        except Exception as e:
            self.logger.error(f"Error clearing display: {e}", exc_info=True)
            self.event_bus.publish(Event(
                EventType.ERROR_OCCURRED,
                {"error": str(e), "context": "clear_display"}
            ))

    def scroll_to_bottom(self) -> None:
        """Scroll the display to the bottom."""
        try:
            self.container.scroll_to_bottom()
        except Exception as e:
            self.logger.error(f"Error scrolling to bottom: {e}", exc_info=True)
            self.event_bus.publish(Event(
                EventType.ERROR_OCCURRED,
                {"error": str(e), "context": "scroll_to_bottom"}
            ))

    def set_current_thread(self, thread_guid: str) -> None:
        """Set the current thread being displayed."""
        self._current_thread_guid = thread_guid

    def remove_message(self, message_id: str) -> None:
        """Remove a specific message from the display."""
        try:
            if message_id in self._message_widgets:
                self._message_widgets[message_id].destroy()
                del self._message_widgets[message_id]
                self.container._on_frame_configure()
        except Exception as e:
            self.logger.error(f"Error removing message: {e}", exc_info=True)
            self.event_bus.publish(Event(
                EventType.ERROR_OCCURRED,
                {"error": str(e), "context": "remove_message"}
            ))

    def update_message_status(self, message_id: str, status: str) -> None:
        """Update the status of a message (e.g., sent, delivered, read)."""
        # This will be implemented when we add message status features
        pass