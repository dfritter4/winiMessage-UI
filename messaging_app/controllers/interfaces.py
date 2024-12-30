# controllers/interfaces.py
from abc import ABC, abstractmethod
from typing import Optional
from messaging_app.domain import Event

class IMessageHandler(ABC):
    @abstractmethod
    async def send_message(self, thread_guid: str, message_text: str) -> bool:
        pass
    
    @abstractmethod
    async def handle_message_received(self, event: Event) -> None:
        pass

class IThreadHandler(ABC):
    @abstractmethod
    async def select_thread(self, thread_name: str) -> None:
        pass
    
    @abstractmethod
    async def create_thread(self, phone_number: str, display_name: Optional[str]) -> None:
        pass

class IStateHandler(ABC):
    @abstractmethod
    def update_connection_state(self, state: str) -> None:
        pass
    
    @abstractmethod
    def update_polling_state(self, is_polling: bool) -> None:
        pass

class IUIEventHandler(ABC):
    @abstractmethod
    async def handle_ui_refresh(self, event: Event) -> None:
        pass
    
    @abstractmethod
    def handle_error(self, event: Event) -> None:
        pass