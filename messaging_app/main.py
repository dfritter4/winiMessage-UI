#!/usr/bin/env python3
import logging
import tkinter as tk
from messaging_app.utils import AsyncApp
from messaging_app import MessagingApp

def main():
    """Application entry point"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    try:
        # Create root window
        root = tk.Tk()
        
        # Create async wrapper
        app_wrapper = AsyncApp(root)
        
        # Create and initialize application
        app = MessagingApp(root, app_wrapper)
        
        # Start the application
        app_wrapper.start()
    except Exception as e:
        logger.error(f"Error starting application: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()