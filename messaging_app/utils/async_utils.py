# messaging_app/utils/async_utils.py

import asyncio
import tkinter as tk
import logging
from typing import Coroutine, Any, Optional

class AsyncApp:
    """Wrapper to handle async operations in tkinter."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        # Create a new event loop for async operations
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.tasks = []
        self.logger = logging.getLogger(__name__)

    def run_async(self, coro: Coroutine) -> asyncio.Task:
        """Schedule a coroutine to run on the event loop."""
        return self.loop.create_task(coro)

    def process_asyncio(self) -> None:
        """Process any pending asyncio events."""
        try:
            # Process all pending tasks in the asyncio event loop
            self.loop.stop()
            self.loop.run_forever()
        except Exception as e:
            self.logger.error(f"Error processing asyncio events: {e}", exc_info=True)
        finally:
            # Schedule the next check
            self.root.after(100, self.process_asyncio)  # Check every 100ms

    def start(self) -> None:
        """Start the application."""
        try:
            # Start processing asyncio events
            self.process_asyncio()
            
            # Start tkinter main loop
            self.root.mainloop()
        except Exception as e:
            self.logger.error(f"Error in event loop: {e}", exc_info=True)
        finally:
            # Clean up on exit
            self.stop()

    def stop(self) -> None:
        """Stop the application and clean up."""
        # Cancel all pending tasks
        for task in self.tasks:
            task.cancel()
        
        # Run the event loop one last time to process cancellations
        pending = asyncio.all_tasks(self.loop)
        self.loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        
        # Close the event loop
        self.loop.close()