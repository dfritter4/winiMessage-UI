# controllers/chat_controller.py
import asyncio
import logging
from messaging_app.config import AppConfig
from messaging_app.domain import (
    Event, 
    EventType, 
    ConnectionState,
    IEventBus,
    IStateManager
)
from messaging_app.services import (
    MessageService,
    ThreadManager,
    MessageDisplayManager,
    UIManager,
    ErrorHandler
)
from .message_handler import MessageHandler
from .thread_handler import ThreadHandler
from .state_handler import StateHandler
from .ui_handler import UIEventHandler

class ChatController:
    """
    Main controller that orchestrates message handling, thread management,
    and UI updates through specialized handlers.
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
        # Initialize handlers
        self.message_handler = MessageHandler(
            message_service, message_display, thread_manager, error_handler, event_bus
        )
        self.thread_handler = ThreadHandler(
            thread_manager, message_display, ui_manager, error_handler, event_bus
        )
        self.state_handler = StateHandler(state_manager)
        self.ui_handler = UIEventHandler(
            message_display, thread_manager, error_handler
        )
        
        self.config = config
        self.event_bus = event_bus
        self.error_handler = error_handler
        self.logger = logging.getLogger(__name__)
        self._polling_active = False
        
        # Set up event handlers
        self._setup_event_handlers()

    def _setup_event_handlers(self) -> None:
        """Set up handlers for various events."""
        # Message Events
        self.event_bus.subscribe(
            EventType.SEND_MESSAGE_REQUESTED,
            self._handle_send_message_event
        )
        self.event_bus.subscribe(
            EventType.MESSAGE_RECEIVED,
            self._handle_message_received_event
        )
        
        # Thread Events
        self.event_bus.subscribe(
            EventType.THREAD_SELECTED,
            self._handle_thread_selected_event
        )
        self.event_bus.subscribe(
            EventType.NEW_CHAT_REQUESTED,
            self._handle_new_chat_event
        )
        
        # UI Events
        self.event_bus.subscribe(
            EventType.UI_REFRESH_REQUESTED,
            self._handle_ui_refresh_event
        )
        self.event_bus.subscribe(
            EventType.ERROR_OCCURRED,
            self.ui_handler.handle_error
        )
        
        # State Events
        self.event_bus.subscribe(
            EventType.CONNECTION_CHANGED,
            self._handle_connection_change_event
        )
        
        # System Events
        self.event_bus.subscribe(
            EventType.SHUTDOWN_REQUESTED,
            lambda e: self.shutdown()
        )

    def _handle_send_message_event(self, event: Event) -> None:
        asyncio.get_event_loop().create_task(
            self.message_handler.send_message(
                self.thread_handler.current_thread.guid if self.thread_handler.current_thread else None,
                event.data.get("message", "").strip()
            )
        )

    def _handle_message_received_event(self, event: Event) -> None:
        asyncio.get_event_loop().create_task(
            self.message_handler.handle_message_received(event)
        )

    def _handle_thread_selected_event(self, event: Event) -> None:
        asyncio.get_event_loop().create_task(
            self.thread_handler.select_thread(event.data.get("thread_name"))
        )

    def _handle_new_chat_event(self, event: Event) -> None:
        asyncio.get_event_loop().create_task(
            self.thread_handler.create_thread(
                event.data.get("phone_number"),
                event.data.get("display_name")
            )
        )

    def _handle_ui_refresh_event(self, event: Event) -> None:
        asyncio.get_event_loop().create_task(
            self.ui_handler.handle_ui_refresh(event)
        )

    def _handle_connection_change_event(self, event: Event) -> None:
        self.state_handler.update_connection_state(event.data.get("state"))

    async def initialize(self) -> None:
        """Initialize the chat controller and start background tasks."""
        try:
            # Update application state
            self.state_handler.update_connection_state(ConnectionState.CONNECTING.value)
            
            # Initialize threads
            try:
                await self.thread_handler.thread_manager.initialize_threads()
            except Exception as e:
                self.logger.error(f"Error initializing threads: {e}", exc_info=True)
                self.error_handler.handle_error(e, "thread_initialization")
            
            # Start polling
            self._start_polling()
            
            # Update state to connected
            self.state_handler.update_connection_state(ConnectionState.CONNECTED.value)
            
        except Exception as e:
            self.logger.error(f"Error in controller initialization: {e}", exc_info=True)
            self.error_handler.handle_error(e, "controller_initialization")
            self.state_handler.update_connection_state(ConnectionState.ERROR.value)

    def _start_polling(self) -> None:
        """Start the message polling loop."""
        if not self._polling_active:
            self._polling_active = True
            self.state_handler.update_polling_state(True)
            asyncio.create_task(self._polling_loop())

    async def poll_messages(self) -> None:
        """Poll for new messages (public interface used by app_lifecycle)."""
        try:
            updates = await self.message_handler.message_service.poll_messages()
            if updates:
                for thread_guid, messages in updates.items():
                    await self.thread_handler.thread_manager.update_thread(thread_guid, messages)
        except Exception as e:
            self.error_handler.handle_error(e, "message_polling")

    async def _polling_loop(self) -> None:
        """Background loop for polling messages."""
        while self._polling_active:
            try:
                await self.poll_messages()
                await asyncio.sleep(self.config.network.poll_interval)
            except Exception as e:
                self.error_handler.handle_error(e, "message_polling")
                await asyncio.sleep(self.config.network.poll_interval * 2)  # Back off on error

    def shutdown(self) -> None:
        """Clean shutdown of the controller."""
        try:
            self._polling_active = False
            self.state_handler.update_polling_state(False)
            self.state_handler.update_connection_state(ConnectionState.DISCONNECTED.value)
            
            # Publish shutdown completion event
            self.event_bus.publish(Event(
                EventType.STATE_CHANGED,
                {
                    "state": ConnectionState.DISCONNECTED,
                    "reason": "shutdown"
                }
            ))
        except Exception as e:
            self.error_handler.handle_error(e, "shutdown")