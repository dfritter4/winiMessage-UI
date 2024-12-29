# messaging_app/utils/async_utils.py

import asyncio
import tkinter as tk
import logging
from typing import Coroutine, Any, Optional

class AsyncApp:
    """Wrapper to handle async operations in tkinter."""
    
    def __init__(self, root: tk.Tk, async_loop: Optional[asyncio.AbstractEventLoop] = None):
        self.root = root
        self.loop = async_loop or asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.tasks = []
        self.logger = logging.getLogger(__name__)

    def run_async(self, coro: Coroutine) -> asyncio.Task:
        """Schedule a coroutine to run on the event loop."""
        task = self.loop.create_task(coro)
        self.tasks.append(task)
        return task

    def process_events(self) -> None:
        """Process pending async events."""
        try:
            self.loop.stop()
            self.loop.run_forever()
        except Exception as e:
            self.logger.error(f"Error processing events: {e}", exc_info=True)
        finally:
            self.root.after(50, self.process_events)
    
    def process_async_events(self) -> None:
        """Process pending async events."""
        try:
            # Run pending tasks without blocking
            self.loop.call_soon(self.loop.stop)
            self.loop.run_forever()
        except Exception as e:
            self.logger.error(f"Error processing async events: {e}", exc_info=True)
        finally:
            # Schedule next processing
            self.root.after(50, self.process_async_events)

    def start(self) -> None:
        """Start processing async events."""
        # Initialize event processing
        self.root.after(50, self.process_async_events)
        
        # Start the Tkinter main loop
        self.root.mainloop()

    def stop(self) -> None:
        """Stop all async tasks and clean up."""
        # Cancel all pending tasks
        for task in self.tasks:
            task.cancel()
        
        # Stop the event loop
        self.loop.stop()
        
        # Clear tasks
        self.tasks.clear()