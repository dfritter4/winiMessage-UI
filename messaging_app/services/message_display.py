import tkinter as tk
import logging
from typing import Optional, Dict, List, Set
from messaging_app.bubbles.base import DefaultBubbleStyle
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
        self._displayed_guids: Set[str] = set()
        self._message_widgets: Dict[str, Dict[str, tk.Widget]] = {}

    def display_thread_messages(self, messages, thread_guid: str) -> None:
        """Efficiently display all thread messages at once."""
        try:
            if thread_guid != self._current_thread_guid:
                return
                
            thread_container = tk.Frame(
                self.container.scrollable_frame,
                bg=self.config.colors.background
            )
            thread_container.pack(fill="x", expand=True)
            
            for message in messages:
                if not message.guid or message.guid in self._displayed_guids:
                    continue
                    
                message_frame = self._create_message_frame(message, thread_container)
                if message_frame:
                    if thread_guid not in self._message_widgets:
                        self._message_widgets[thread_guid] = {}
                    self._message_widgets[thread_guid][message.guid] = message_frame
                    self._displayed_guids.add(message.guid)
            
            self.container.update_idletasks()
            self.container._on_frame_configure()
            self.container.scroll_to_bottom()
            
        except Exception as e:
            self.logger.error(f"Error displaying thread messages: {e}", exc_info=True)

    def _create_message_frame(self, message, parent_container):
        """Create a message frame with all its content."""
        try:
            container = tk.Frame(
                parent_container,
                bg=self.config.colors.background
            )
            container.pack(fill="x", padx=15, pady=5)

            message_content = tk.Frame(container, bg=self.config.colors.background)
            message_content.pack(
                side="right" if message.direction == "outgoing" else "left",
                fill="none",
                expand=False
            )

            style = DefaultBubbleStyle(self.config)

            if message.attachments:
                self._add_attachments(message, message_content, style)
                
            if message.text and (not message.attachments or len(message.attachments) > 1):
                self._add_text_bubble(message, message_content, style)

            return container
        except Exception as e:
            self.logger.error(f"Error creating message frame: {e}", exc_info=True)
            return None

    def _add_attachments(self, message, message_content, style):
        """Add attachment bubbles to the message content."""
        for attachment in message.attachments:
            if attachment.mime_type.startswith('image/'):
                bubble = ImageBubble(
                    message_content,
                    content=message.text if len(message.attachments) == 1 else "",
                    image_url=attachment.url,
                    style=style,
                    is_outgoing=message.direction == "outgoing",
                    timestamp=message.timestamp if attachment == message.attachments[-1] else None,
                    sender_name=message.sender_name if attachment == message.attachments[0] else None,
                )
                bubble.pack(fill="none", expand=False, pady=(0, 5))

    def _add_text_bubble(self, message, message_content, style):
        """Add a text bubble to the message content."""
        bubble = EnhancedTextBubble(
            message_content,
            content=message.text,
            style=style,
            is_outgoing=message.direction == "outgoing",
            timestamp=message.timestamp,
            sender_name=message.sender_name,
        )
        bubble.pack(fill="none", expand=False)

    def display_message(self, message: Message, thread_guid: Optional[str] = None) -> None:
        """Display a single message in the current thread."""
        if thread_guid is None:
            thread_guid = self._current_thread_guid
            
        if thread_guid != self._current_thread_guid:
            return

        if not message.guid or message.guid in self._displayed_guids or (not message.text and not message.attachments):
            return

        try:
            message_frame = self._create_message_frame(message, self.container.scrollable_frame)
            if message_frame:
                if thread_guid not in self._message_widgets:
                    self._message_widgets[thread_guid] = {}
                self._message_widgets[thread_guid][message.guid] = message_frame
                self._displayed_guids.add(message.guid)

                message_frame.update_idletasks()
                self.container._on_frame_configure()
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
        """Set the current thread and position view at bottom."""
        if thread_guid != self._current_thread_guid:
            self.clear_display()
            self._current_thread_guid = thread_guid
            self.container.canvas.yview_moveto(1.0)
            self.container.update_idletasks()
            
            if thread_guid not in self._message_widgets:
                self._message_widgets[thread_guid] = {}

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