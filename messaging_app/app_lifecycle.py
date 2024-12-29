# messaging_app/app_lifecycle.py
import logging
import asyncio
import tkinter as tk
from typing import Optional
from .domain import Event, EventType
from .services import EventBus, ErrorHandler
from .controllers import ChatController

class MessageAppLifecycle:
    def __init__(self, 
                 root: tk.Tk,
                 controller: ChatController,
                 event_bus: EventBus,
                 error_handler: ErrorHandler,
                 async_app):  # Add async_app parameter
        self.root = root
        self.controller = controller
        self.event_bus = event_bus
        self.error_handler = error_handler
        self.async_app = async_app  # Store reference to async_app
        self.logger = logging.getLogger(__name__)
        self._polling_task: Optional[asyncio.Task] = None
        self._is_polling = False
        
        # Set up shutdown handler
        self.root.protocol("WM_DELETE_WINDOW", self._handle_shutdown)
    
    async def initialize(self) -> None:
        """Initialize the application."""
        try:
            await self.controller.initialize()
            await self.start_polling()
        except Exception as e:
            self.logger.error(f"Initialization error: {e}", exc_info=True)
            self.error_handler.handle_error(e, "initialization")
    
    async def start_polling(self) -> None:
        """Start the message polling loop."""
        if self._is_polling:
            return

        self._is_polling = True
        self._polling_task = self.async_app.run_async(self._polling_loop())
        self.logger.info("Message polling started")

    async def stop_polling(self) -> None:
        """Stop the message polling loop."""
        self.logger.info("Stopping message polling...")
        self._is_polling = False
        if self._polling_task:
            self._polling_task.cancel()
            try:
                await asyncio.wait_for(self._polling_task, timeout=1.0)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                pass
            self._polling_task = None
        self.logger.info("Message polling stopped")

    async def _polling_loop(self) -> None:
        """Background loop for polling messages."""
        while self._is_polling:
            try:
                self.logger.info("Polling for new messages...")
                await self.controller.poll_messages()
                await asyncio.sleep(2)
            except Exception as e:
                self.logger.error(f"Error in polling loop: {e}", exc_info=True)
                self.error_handler.handle_error(e, "polling")
                await asyncio.sleep(5)

    def _handle_shutdown(self) -> None:
        """Handle application shutdown."""
        try:
            # Use the async_app to stop polling
            self.async_app.run_async(self.stop_polling())
            
            # Publish shutdown event
            self.event_bus.publish(Event(
                EventType.SHUTDOWN_REQUESTED,
                {}
            ))
            
            # Stop the async app
            self.async_app.stop()
            
            # Destroy the root window
            self.root.destroy()
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}", exc_info=True)