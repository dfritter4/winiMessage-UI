import tkinter as tk
import logging
from typing import Optional, Dict, List, Set
from messaging_app.bubbles.base import DefaultBubbleStyle
from messaging_app.bubbles.text_handlers import EnhancedTextContent
from messaging_app.domain import IMessageDisplay, Message, IEventBus, Event, EventType
from messaging_app.config import AppConfig
from messaging_app.bubbles import TextBubble, ImageBubble, EnhancedTextBubble
from messaging_app.ui import ModernScrolledText

class MessageDisplayManager(IMessageDisplay):
    def __init__(self, container: ModernScrolledText, config: AppConfig, event_bus: IEventBus):
        self.container = container
        self.config = config
        self.event_bus = event_bus
        self.logger = logging.getLogger(__name__)
        self._current_thread_guid: Optional[str] = None
        self._displayed_guids: Set[str] = set()  # Track displayed message GUIDs
        self._message_widgets: Dict[str, Dict[str, tk.Widget]] = {}

    def display_message(self, message: Message, thread_guid: Optional[str] = None) -> None:
        """Display a message in the current thread's chat window with guid-based deduplication."""
        if thread_guid is None:
            thread_guid = self._current_thread_guid
            
        if thread_guid != self._current_thread_guid:
            self.logger.debug(f"Skipping display of message for non-active thread {thread_guid}")
            return

        if not message.guid:
            self.logger.warning("Message has no GUID, skipping display")
            return
            
        if message.guid in self._displayed_guids:
            self.logger.debug(f"Skipping duplicate message: {message.guid}")
            return

        if not message.text and not message.attachments:
            self.logger.debug(f"Skipping empty message with no text or attachments")
            return

        try:
            # Create a container for the message bubble
            container = tk.Frame(
                self.container.scrollable_frame,
                bg=self.config.colors.background
            )
            container.pack(fill="x", padx=15, pady=5)

            # Create a container for all message content
            message_content = tk.Frame(container, bg=self.config.colors.background)
            message_content.pack(
                side="right" if message.direction == "outgoing" else "left",
                fill="none",
                expand=False
            )

            style = DefaultBubbleStyle(self.config)

            # Process each attachment vertically
            for attachment in message.attachments:
                is_image = attachment.mime_type.startswith('image/')
                
                if is_image:
                    bubble = ImageBubble(
                        message_content,
                        content=message.text if len(message.attachments) == 1 else "",
                        image_url=attachment.url,
                        style=style,
                        is_outgoing=message.direction == "outgoing",
                        timestamp=message.timestamp if attachment == message.attachments[-1] else None,
                        sender_name=message.sender_name if attachment == message.attachments[0] else None,
                    )
                    bubble.pack(
                        fill="none",
                        expand=False,
                        pady=(0, 5)
                    )
                    self.logger.info(f"Created ImageBubble with URL: {attachment.url}")

            # If there's text and multiple attachments, show it in a separate bubble
            if message.text and len(message.attachments) > 1:
                bubble = EnhancedTextBubble(
                    message_content,
                    content=message.text,
                    style=style,
                    is_outgoing=message.direction == "outgoing",
                    timestamp=message.timestamp,
                    sender_name=None,
                )
                bubble.pack(
                    fill="none",
                    expand=False,
                )

            # If there's text but no attachments, create a text bubble
            if not message.attachments and message.text:
                bubble = EnhancedTextBubble(
                    message_content,
                    content=message.text,
                    style=style,
                    is_outgoing=message.direction == "outgoing",
                    timestamp=message.timestamp,
                    sender_name=message.sender_name,
                )
                bubble.pack(
                    fill="none",
                    expand=False,
                )

            # Store the widget reference
            if thread_guid not in self._message_widgets:
                self._message_widgets[thread_guid] = {}
            self._message_widgets[thread_guid][message.guid] = container
            self._displayed_guids.add(message.guid)

            # Force immediate updates
            container.update()
            message_content.update()
            self.container.scrollable_frame.update()
            self.container.update_idletasks()
            self.scroll_to_bottom()
            # Force immediate update
            container.update_idletasks()
            message_content.update_idletasks()
            self.container.scrollable_frame.update_idletasks()
            self.scroll_to_bottom()
            
        except Exception as e:
            self.logger.error(f"Error displaying message: {e}", exc_info=True)

    def clear_display(self) -> None:
        """Clear all messages from the display."""
        try:
            for widget in self.container.scrollable_frame.winfo_children():
                widget.destroy()
            
            if self._current_thread_guid in self._message_widgets:
                self._message_widgets[self._current_thread_guid].clear()
                
            self._displayed_guids.clear()
            self.container._on_frame_configure()
            self.container.update_idletasks()

        except Exception as e:
            self.logger.error(f"Error clearing display: {e}", exc_info=True)
            self.event_bus.publish(Event(
                EventType.ERROR_OCCURRED,
                {"error": str(e), "context": "clear_display"}
            ))

    def set_current_thread(self, thread_guid: str) -> None:
        """Set the current thread being displayed."""
        if thread_guid != self._current_thread_guid:
            self.logger.info(f"Switching to thread {thread_guid}")
            self.clear_display()
            self._current_thread_guid = thread_guid
            
            # Initialize message widgets dict for this thread if needed
            if thread_guid not in self._message_widgets:
                self._message_widgets[thread_guid] = {}
            
            # Ensure proper scrolling after thread switch
            self.scroll_to_bottom()

    def remove_message(self, message_id: str, thread_guid: Optional[str] = None) -> None:
        """Remove a specific message from the display."""
        if thread_guid is None:
            thread_guid = self._current_thread_guid
            
        try:
            if (thread_guid in self._message_widgets and 
                message_id in self._message_widgets[thread_guid]):
                self._message_widgets[thread_guid][message_id].destroy()
                del self._message_widgets[thread_guid][message_id]
                self.container._on_frame_configure()
                self.container.update_idletasks()
        except Exception as e:
            self.logger.error(f"Error removing message: {e}", exc_info=True)
            self.event_bus.publish(Event(
                EventType.ERROR_OCCURRED,
                {"error": str(e), "context": "remove_message"}
            ))

    def scroll_to_bottom(self) -> None:
        """Scroll the display to the bottom."""
        try:
            self.container.scroll_to_bottom()
            self.container.update_idletasks()
        except Exception as e:
            self.logger.error(f"Error scrolling to bottom: {e}", exc_info=True)