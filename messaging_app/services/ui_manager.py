# services/ui_manager.py

import tkinter as tk
from tkinter import messagebox, simpledialog
import logging
from typing import Optional, Any, Callable

from messaging_app.domain import IEventBus, Event, EventType

class UIManager:
    """
    Manages UI interactions and dialogs.
    Handles error displays, user inputs, and UI state.
    """
    
    def __init__(self, root: tk.Tk, event_bus: IEventBus):
        self.root = root
        self.event_bus = event_bus
        self.logger = logging.getLogger(__name__)
        self._dialog_active = False

    def show_error(self, message: str, title: str = "Error") -> None:
        """Display an error message dialog."""
        try:
            self.root.after(0, lambda: messagebox.showerror(title, message))
        except Exception as e:
            self.logger.error(f"Error showing error dialog: {e}", exc_info=True)
            # Try to publish error event as fallback
            self.event_bus.publish(Event(
                EventType.ERROR_OCCURRED,
                {
                    "error": str(e),
                    "context": "error_dialog",
                    "original_message": message
                }
            ))

    def show_info(self, message: str, title: str = "Information") -> None:
        """Display an information message dialog."""
        try:
            self.root.after(0, lambda: messagebox.showinfo(title, message))
        except Exception as e:
            self.logger.error(f"Error showing info dialog: {e}", exc_info=True)

    def ask_yes_no(self, message: str, title: str = "Question") -> bool:
        """Display a yes/no dialog and return the response."""
        try:
            self._dialog_active = True
            response = messagebox.askyesno(title, message)
            self._dialog_active = False
            return response
        except Exception as e:
            self.logger.error(f"Error showing yes/no dialog: {e}", exc_info=True)
            self._dialog_active = False
            return False

    def ask_input(self, prompt: str, title: str = "Input", 
                 initial: str = "", password: bool = False) -> Optional[str]:
        """Display an input dialog and return the user's input."""
        try:
            self._dialog_active = True
            if password:
                response = simpledialog.askstring(
                    title, prompt, 
                    show="*", 
                    parent=self.root
                )
            else:
                response = simpledialog.askstring(
                    title, prompt,
                    initialvalue=initial,
                    parent=self.root
                )
            self._dialog_active = False
            return response
        except Exception as e:
            self.logger.error(f"Error showing input dialog: {e}", exc_info=True)
            self._dialog_active = False
            return None

    def confirm_action(self, action: str, detail: str = "") -> bool:
        """Display a confirmation dialog for an action."""
        message = f"Are you sure you want to {action}?"
        if detail:
            message += f"\n\n{detail}"
        return self.ask_yes_no(message, "Confirm Action")

    def show_busy_cursor(self) -> None:
        """Show busy cursor for the entire application."""
        try:
            self.root.config(cursor="wait")
            self.root.update()
        except Exception as e:
            self.logger.error(f"Error showing busy cursor: {e}", exc_info=True)

    def restore_cursor(self) -> None:
        """Restore normal cursor."""
        try:
            self.root.config(cursor="")
            self.root.update()
        except Exception as e:
            self.logger.error(f"Error restoring cursor: {e}", exc_info=True)

    def run_with_busy_cursor(self, action: Callable[[], Any]) -> Any:
        """Run an action while showing the busy cursor."""
        self.show_busy_cursor()
        try:
            result = action()
            return result
        finally:
            self.restore_cursor()

    def is_dialog_active(self) -> bool:
        """Check if a dialog is currently active."""
        return self._dialog_active

    def schedule_notification(self, message: str, delay_ms: int = 3000) -> None:
        """Schedule a temporary notification message."""
        try:
            self.event_bus.publish(Event(
                EventType.UI_REFRESH_REQUESTED,
                {
                    "type": "notification",
                    "message": message
                }
            ))
            
            # Schedule removal
            self.root.after(delay_ms, lambda: self.event_bus.publish(Event(
                EventType.UI_REFRESH_REQUESTED,
                {
                    "type": "notification",
                    "message": None
                }
            )))
            
        except Exception as e:
            self.logger.error(f"Error scheduling notification: {e}", exc_info=True)

    def disable_ui(self) -> None:
        """Disable all UI interactions."""
        try:
            for child in self.root.winfo_children():
                self._disable_widget(child)
            self.show_busy_cursor()
        except Exception as e:
            self.logger.error(f"Error disabling UI: {e}", exc_info=True)

    def enable_ui(self) -> None:
        """Enable all UI interactions."""
        try:
            for child in self.root.winfo_children():
                self._enable_widget(child)
            self.restore_cursor()
        except Exception as e:
            self.logger.error(f"Error enabling UI: {e}", exc_info=True)

    def _disable_widget(self, widget: tk.Widget) -> None:
        """Recursively disable a widget and its children."""
        try:
            if hasattr(widget, 'state') and callable(getattr(widget, 'state')):
                widget.state(['disabled'])
            elif hasattr(widget, 'configure'):
                widget.configure(state='disabled')
                
            for child in widget.winfo_children():
                self._disable_widget(child)
        except Exception:
            pass  # Skip widgets that can't be disabled

    def _enable_widget(self, widget: tk.Widget) -> None:
        """Recursively enable a widget and its children."""
        try:
            if hasattr(widget, 'state') and callable(getattr(widget, 'state')):
                widget.state(['!disabled'])
            elif hasattr(widget, 'configure'):
                widget.configure(state='normal')
                
            for child in widget.winfo_children():
                self._enable_widget(child)
        except Exception:
            pass  # Skip widgets that can't be enabled