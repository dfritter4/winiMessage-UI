# controllers/state_handler.py
import logging
from messaging_app.domain import AppState, ConnectionState, IStateManager
from .interfaces import IStateHandler

class StateHandler(IStateHandler):
    def __init__(self, state_manager: IStateManager):
        self.state_manager = state_manager
        self.logger = logging.getLogger(__name__)

    def update_connection_state(self, state: str) -> None:
        """Update the application connection state."""
        try:
            current_state = self.state_manager.get_state()
            new_state = AppState(
                connection_state=ConnectionState(state),
                current_thread_guid=current_state.current_thread_guid,
                is_polling=current_state.is_polling,
                threads=current_state.threads
            )
            self.state_manager.update_state(new_state)
        except Exception as e:
            self.logger.error(f"Error updating connection state: {e}", exc_info=True)

    def update_polling_state(self, is_polling: bool) -> None:
        """Update the polling state."""
        try:
            current_state = self.state_manager.get_state()
            new_state = AppState(
                connection_state=current_state.connection_state,
                current_thread_guid=current_state.current_thread_guid,
                is_polling=is_polling,
                threads=current_state.threads
            )
            self.state_manager.update_state(new_state)
        except Exception as e:
            self.logger.error(f"Error updating polling state: {e}", exc_info=True)

    def update_current_thread(self, thread_guid: str) -> None:
        """Update the current thread in application state."""
        try:
            current_state = self.state_manager.get_state()
            new_state = AppState(
                connection_state=current_state.connection_state,
                current_thread_guid=thread_guid,
                is_polling=current_state.is_polling,
                threads=current_state.threads
            )
            self.state_manager.update_state(new_state)
        except Exception as e:
            self.logger.error(f"Error updating current thread: {e}", exc_info=True)