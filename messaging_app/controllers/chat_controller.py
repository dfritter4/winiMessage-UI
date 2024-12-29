import asyncio
import logging
from typing import Optional, Dict
from datetime import datetime

from messaging_app.domain import (
    IEventBus,
    IStateManager,
    Event,
    EventType,
    Message,
    Thread,
    ConnectionState,
    AppState
)
from messaging_app.config import AppConfig
from messaging_app.services import (
    MessageService,
    ThreadManager,
    MessageDisplayManager,
    UIManager,
    ErrorHandler
)

class ChatController:
    """
    Main controller for the chat application.
    Handles coordination between UI events, message handling, and state management.
    """
    
    def __init__(
        self,
        config: AppConfig,
        event_bus: IEventBus,
        state_manager: IStateManager,
        message_service: MessageService,
        thread_manager: ThreadManager,
        message_display: MessageDisplayManager,
        ui_manager: UIManager,
        error_handler: ErrorHandler
    ):
        self.config = config
        self.event_bus = event_bus
        self.state_manager = state_manager
        self.message_service = message_service
        self.thread_manager = thread_manager
        self.message_display = message_display
        self.ui_manager = ui_manager
        self.error_handler = error_handler
        
        self.logger = logging.getLogger(__name__)
        self._polling_active = False
        self._current_thread: Optional[Thread] = None
        
        # Set up event handlers
        self._setup_event_handlers()

    def _setup_event_handlers(self) -> None:
        """Set up handlers for various UI and system events."""
        # Message Events
        self.event_bus.subscribe(EventType.SEND_MESSAGE_REQUESTED, self._handle_send_message)
        self.event_bus.subscribe(EventType.MESSAGE_RECEIVED, self._handle_message_received)
        self.event_bus.subscribe(EventType.MESSAGE_DELETED, self._handle_message_deleted)
        self.event_bus.subscribe(EventType.MESSAGE_EDITED, self._handle_message_edited)
        self.event_bus.subscribe(EventType.MESSAGE_SEARCH_REQUESTED, self._handle_message_search)
        
        # Thread Events
        self.event_bus.subscribe(EventType.THREAD_SELECTED, self._handle_thread_selected)
        self.event_bus.subscribe(EventType.NEW_CHAT_REQUESTED, self._handle_new_chat)
        self.event_bus.subscribe(EventType.THREAD_UPDATED, self._handle_thread_updated)
        self.event_bus.subscribe(EventType.THREAD_DELETED, self._handle_thread_deleted)
        
        # System Events
        self.event_bus.subscribe(EventType.ERROR_OCCURRED, self._handle_error)
        self.event_bus.subscribe(EventType.CONNECTION_CHANGED, self._handle_connection_change)
        self.event_bus.subscribe(EventType.SHUTDOWN_REQUESTED, self._handle_shutdown)
        self.event_bus.subscribe(EventType.UI_REFRESH_REQUESTED, self._handle_ui_refresh)

    async def initialize(self) -> None:
        """Initialize the chat controller and start background tasks."""
        try:
            # Update application state
            self._update_state(ConnectionState.CONNECTING)
            
            # Initialize threads
            await self.thread_manager.initialize_threads()
            
            # Update state to connected
            self._update_state(ConnectionState.CONNECTED)
            
            # Start message polling
            self._start_polling()
            
        except Exception as e:
            self.error_handler.handle_error(e, "controller_initialization")
            self._update_state(ConnectionState.ERROR)

    def _start_polling(self) -> None:
        """Start the message polling loop."""
        if not self._polling_active:
            self._polling_active = True
            self._update_state_polling(True)
            asyncio.create_task(self._polling_loop())

    async def _polling_loop(self) -> None:
        """Background loop for polling messages."""
        while self._polling_active:
            try:
                updates = await self.message_service.poll_messages()
                if updates:
                    for thread_guid, messages in updates.items():
                        await self.thread_manager.update_thread(thread_guid, messages)
                
                await asyncio.sleep(self.config.network.poll_interval)
                
            except Exception as e:
                self.error_handler.handle_error(e, "message_polling")
                await asyncio.sleep(self.config.network.poll_interval * 2)  # Back off on error

    async def _handle_send_message(self, event: Event) -> None:
        """Handle message send requests."""
        try:
            if not self._current_thread:
                self.event_bus.publish(Event(
                    EventType.DISPLAY_ERROR,
                    {"message": "Please select a chat first."}
                ))
                return

            message_text = event.data.get("message", "").strip()
            if not message_text:
                return

            success = await self.message_service.send_message(
                self._current_thread.guid,
                message_text
            )

            if success:
                message = Message(
                    text=message_text,
                    sender_name="Me",  # Should come from user settings
                    timestamp=datetime.now().timestamp(),
                    direction="outgoing",
                    thread_name=self._current_thread.name
                )

                await self.thread_manager.update_thread(
                    self._current_thread.guid,
                    [message]
                )

                self.message_display.display_message(message)
                self.message_display.scroll_to_bottom()

        except Exception as e:
            self.error_handler.handle_error(e, "send_message")

    async def _handle_thread_selected(self, event: Event) -> None:
        """Handle thread selection events."""
        try:
            thread_name = event.data.get("thread_name")
            if not thread_name:
                self.logger.warning("No thread name provided")
                return

            # Use a timeout to prevent indefinite waiting
            thread = await asyncio.wait_for(
                self.thread_manager.get_thread_by_name(thread_name), 
                timeout=5.0
            )

            if not thread:
                self.logger.warning(f"No thread found with name: {thread_name}")
                return

            # Update current thread
            self._current_thread = thread
            
            def update_ui():
                try:
                    # Clear the current display first
                    self.message_display.clear_display()
                    
                    # Set the current thread in message display
                    self.message_display.set_current_thread(thread.guid)
                    
                    # Display thread messages in order
                    messages = sorted(thread.messages, key=lambda m: m.timestamp)
                    for message in messages:
                        self.message_display.display_message(message, thread.guid)
                    
                    self.message_display.scroll_to_bottom()
                    
                    # Update state
                    self._update_current_thread(thread.guid)
                except Exception as e:
                    self.logger.error(f"Error updating UI: {e}", exc_info=True)
            
            # Schedule UI update on main thread
            self.event_bus.publish(Event(
                EventType.UI_REFRESH_REQUESTED,
                {"action": "update_thread", "thread_name": thread_name, "update_func": update_ui}
            ))
                
        except asyncio.TimeoutError:
            self.logger.error(f"Timeout getting thread: {thread_name}")
        except Exception as e:
            self.logger.error(f"Error in thread selection: {e}", exc_info=True)
            # Publish error event
            self.event_bus.publish(Event(
                EventType.ERROR_OCCURRED,
                {"error": str(e), "context": "thread_selection"}
            ))

    async def _handle_new_chat(self, event: Event) -> None:
        """Handle new chat creation requests."""
        try:
            # Get recipient phone number
            phone_number = self.ui_manager.ask_input(
                "Enter recipient's phone number (e.g., +1234567890):",
                "New Message"
            )
            
            if not phone_number:
                return

            # Get optional display name
            display_name = self.ui_manager.ask_input(
                "Enter display name (optional):",
                "New Message"
            )

            # Create new thread
            thread = await self.thread_manager.create_thread(phone_number, display_name)
            
            # Update UI
            self._current_thread = thread
            self.message_display.clear_display()
            self.message_display.set_current_thread(thread.guid)
            
            # Update state
            self._update_current_thread(thread.guid)
            
        except Exception as e:
            self.error_handler.handle_error(e, "new_chat_creation")

    async def _handle_message_received(self, event: Event) -> None:
        """Handle received messages."""
        try:
            thread_guid = event.data.get("thread_guid")
            message = event.data.get("message")

            self.logger.info(f"Received message event:")
            self.logger.info(f"- Thread GUID: {thread_guid}")
            self.logger.info(f"- Message: {message}")
            
            if not thread_guid or not message:
                return

            # Update current display if message is for current thread
            if (self._current_thread and 
                self._current_thread.guid == thread_guid):
                self.message_display.display_message(message)
                self.message_display.scroll_to_bottom()
                
        except Exception as e:
            self.error_handler.handle_error(e, "message_received")

    def _handle_error(self, event: Event) -> None:
        """Handle error events."""
        error_data = event.data
        self.logger.error(
            f"Error in {error_data.get('context', 'unknown')}: {error_data.get('error')}"
        )
        
        # Update state if it's a connection error
        if error_data.get('context') in ['connection', 'initialization']:
            self._update_state(ConnectionState.ERROR)

    def _handle_connection_change(self, event: Event) -> None:
        """Handle connection state changes."""
        new_state = event.data.get("state")
        if new_state:
            self._update_state(new_state)

    async def _handle_message_search(self, event: Event) -> None:
        """Handle message search requests."""
        try:
            search_term = event.data.get("search_term", "").strip()
            if not search_term:
                return

            # Implement message search logic here
            # This could search through current thread or all threads
            pass
            
        except Exception as e:
            self.error_handler.handle_error(e, "message_search")

    async def _handle_message_deleted(self, event: Event) -> None:
        """Handle message deletion events."""
        try:
            message_id = event.data.get("message_id")
            thread_guid = event.data.get("thread_guid")
            
            if not message_id or not thread_guid:
                return

            # Remove from display if in current thread
            if (self._current_thread and 
                self._current_thread.guid == thread_guid):
                self.message_display.remove_message(message_id)
            
        except Exception as e:
            self.error_handler.handle_error(e, "message_deletion")

    def _update_state(self, connection_state: ConnectionState) -> None:
        """Update the application state."""
        current_state = self.state_manager.get_state()
        new_state = AppState(
            connection_state=connection_state,
            current_thread_guid=current_state.current_thread_guid,
            is_polling=current_state.is_polling,
            threads=current_state.threads
        )
        self.state_manager.update_state(new_state)

    def _update_state_polling(self, is_polling: bool) -> None:
        """Update the polling state."""
        current_state = self.state_manager.get_state()
        new_state = AppState(
            connection_state=current_state.connection_state,
            current_thread_guid=current_state.current_thread_guid,
            is_polling=is_polling,
            threads=current_state.threads
        )
        self.state_manager.update_state(new_state)

    def _update_current_thread(self, thread_guid: str) -> None:
        """Update the current thread in application state."""
        current_state = self.state_manager.get_state()
        new_state = AppState(
            connection_state=current_state.connection_state,
            current_thread_guid=thread_guid,
            is_polling=current_state.is_polling,
            threads=current_state.threads
        )
        self.state_manager.update_state(new_state)

    async def _handle_message_edited(self, event: Event) -> None:
        """Handle message edit events."""
        try:
            message_id = event.data.get("message_id")
            new_text = event.data.get("new_text")
            thread_guid = event.data.get("thread_guid")
            
            if not all([message_id, new_text, thread_guid]):
                return
                
            # Update message in thread
            await self.thread_manager.update_message(thread_guid, message_id, new_text)
            
            # Update display if in current thread
            if (self._current_thread and 
                self._current_thread.guid == thread_guid):
                self.message_display.update_message(message_id, new_text)
                
        except Exception as e:
            self.error_handler.handle_error(e, "message_edit")

    async def _handle_thread_updated(self, event: Event) -> None:
        """Handle thread update events."""
        try:
            thread_guid = event.data.get("thread_guid")
            thread_data = event.data.get("thread_data")
            
            if not thread_guid or not thread_data:
                return
                
            await self.thread_manager.update_thread_data(thread_guid, thread_data)
            
            # Refresh UI if current thread
            if (self._current_thread and 
                self._current_thread.guid == thread_guid):
                self.event_bus.publish(Event(
                    EventType.UI_REFRESH_REQUESTED,
                    {"thread_guid": thread_guid}
                ))
                
        except Exception as e:
            self.error_handler.handle_error(e, "thread_update")

    async def _handle_thread_deleted(self, event: Event) -> None:
        """Handle thread deletion events."""
        try:
            thread_guid = event.data.get("thread_guid")
            if not thread_guid:
                return
                
            await self.thread_manager.delete_thread(thread_guid)
            
            # Clear display if current thread
            if (self._current_thread and 
                self._current_thread.guid == thread_guid):
                self.message_display.clear_display()
                self._current_thread = None
                self._update_current_thread(None)
                
        except Exception as e:
            self.error_handler.handle_error(e, "thread_deletion")

    async def _handle_ui_refresh(self, event: Event) -> None:
        """Handle UI refresh requests."""
        try:
            thread_guid = event.data.get("thread_guid")
            if thread_guid and self._current_thread and self._current_thread.guid == thread_guid:
                self.message_display.clear_display()
                thread = await self.thread_manager.get_thread(thread_guid)
                if thread:
                    for message in sorted(thread.messages, key=lambda m: m.timestamp):
                        self.message_display.display_message(message)
                    self.message_display.scroll_to_bottom()
                    
        except Exception as e:
            self.error_handler.handle_error(e, "ui_refresh")

    def _handle_shutdown(self, event: Event) -> None:
        """Handle application shutdown request."""
        try:
            self.shutdown()
        except Exception as e:
            self.error_handler.handle_error(e, "shutdown")

    def shutdown(self) -> None:
        """Clean shutdown of the controller."""
        self._polling_active = False
        self._update_state_polling(False)
        self._update_state(ConnectionState.DISCONNECTED)
        
        # Publish shutdown completion event
        self.event_bus.publish(Event(
            EventType.STATE_CHANGED,
            {
                "state": ConnectionState.DISCONNECTED,
                "reason": "shutdown"
            }
        ))