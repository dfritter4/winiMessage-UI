# messaging_app/utils/async_utils.py

import asyncio
import tkinter as tk
import logging
from typing import Coroutine, Any

class AsyncApp:
    """Wrapper to handle async operations in tkinter."""
    
    def __init__(self, root: tk.Tk, async_loop=None):
        self.root = root
        self.loop = async_loop or asyncio.new_event_loop()
        self.tasks = []
        self.logger = logging.getLogger(__name__)
        asyncio.set_event_loop(self.loop)

    def run_async(self, coro: Coroutine) -> asyncio.Task:
        """Schedule a coroutine to run on the event loop."""
        async def wrapped():
            try:
                await coro
            except Exception as e:
                self.logger.error(f"Error in async task: {e}", exc_info=True)
                
        task = self.loop.create_task(wrapped())
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

    def start(self) -> None:
        """Start processing async events."""
        self.root.after(50, self.process_events)
        self.root.mainloop()

    def stop(self) -> None:
        """Stop all async tasks and clean up."""
        for task in self.tasks:
            task.cancel()
        self.loop.stop()
        self.tasks.clear()