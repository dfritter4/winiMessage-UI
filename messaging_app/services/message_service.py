import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional
from datetime import datetime


from messaging_app.domain import (
    IMessageService,
    Message,
    Thread,
    Event,
    EventType,
    IEventBus
)
from messaging_app.config.settings import AppConfig

class MessageService(IMessageService):
    def __init__(self, config: AppConfig, event_bus: IEventBus):
        self.config = config
        self.event_bus = event_bus
        self.logger = logging.getLogger(__name__)
        self._message_cache: Dict[str, List[Message]] = {}
        self._thread_names: Dict[str, str] = {}
        
    async def initialize_threads(self) -> Dict[str, Thread]:
        """Initialize and return all message threads."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.config.network.server_url}/messages",
                    timeout=self.config.network.request_timeout
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
                    threads_data = data.get("threads", {})
                    result = {}
                    self._message_cache.clear()
                    self._thread_names.clear()

                    for thread_guid, messages in threads_data.items():
                        if not messages:
                            continue

                        thread_name = messages[0].get("thread_name", "Unknown")
                        self._thread_names[thread_guid] = thread_name
                        self._message_cache[thread_guid] = []

                        thread_messages = []
                        for msg in messages:
                            message = Message(
                                text=str(msg.get("text", "")),
                                sender_name=str(msg.get("sender_name", "Unknown")),
                                timestamp=msg.get("timestamp", datetime.now().timestamp()),
                                thread_name=msg.get("thread_name"),
                                direction=msg.get("direction", "incoming"),
                                attachment_path=msg.get("attachment_path"),
                                attachment_url=msg.get("attachment_url")
                            )
                            thread_messages.append(message)

                        result[thread_guid] = Thread(
                            guid=thread_guid,
                            name=thread_name,
                            messages=thread_messages
                        )

                    return result

        except Exception as e:
            self.logger.error(f"Error initializing threads: {str(e)}", exc_info=True)
            self.event_bus.publish(Event(
                EventType.ERROR_OCCURRED,
                {"error": str(e), "context": "initialize_threads"}
            ))
            raise

    async def poll_messages(self) -> Dict[str, List[Message]]:
        """Poll for new messages across all threads."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.config.network.server_url}/messages",
                    timeout=self.config.network.request_timeout
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
                    threads_data = data.get("threads", {})
                    updates: Dict[str, List[Message]] = {}

                    for thread_guid, messages in threads_data.items():
                        if thread_guid not in self._message_cache:
                            self._message_cache[thread_guid] = []

                        thread_updates = []
                        existing_keys = {
                            f"{m.sender_name}:{m.text}:{m.timestamp}" 
                            for m in self._message_cache[thread_guid]
                        }

                        for msg in messages:
                            cache_key = (
                                f"{msg.get('sender_name', 'Unknown')}:"
                                f"{msg.get('text', '')}:"
                                f"{msg.get('timestamp', datetime.now().timestamp())}"
                            )

                            if cache_key not in existing_keys:
                                message = Message(
                                    text=str(msg.get("text", "")),
                                    sender_name=str(msg.get("sender_name", "Unknown")),
                                    timestamp=msg.get("timestamp", datetime.now().timestamp()),
                                    thread_name=msg.get("thread_name"),
                                    direction=msg.get("direction", "incoming"),
                                    attachment_path=msg.get("attachment_path"),
                                    attachment_url=msg.get("attachment_url")
                                )
                                thread_updates.append(message)
                                self._message_cache[thread_guid].append(message)

                        if thread_updates:
                            updates[thread_guid] = thread_updates
                            # Publish event for each new message
                            for message in thread_updates:
                                self.event_bus.publish(Event(
                                    EventType.MESSAGE_RECEIVED,
                                    {"thread_guid": thread_guid, "message": message}
                                ))

                    return updates

        except Exception as e:
            self.logger.error(f"Error polling messages: {str(e)}", exc_info=True)
            self.event_bus.publish(Event(
                EventType.ERROR_OCCURRED,
                {"error": str(e), "context": "poll_messages"}
            ))
            raise

    async def send_message(self, thread_guid: str, message: str) -> bool:
        """Send a message to a specific thread."""
        try:
            recipient = self._get_thread_recipient(thread_guid)
            if not recipient:
                raise ValueError("Could not determine recipient")

            payload = {
                "recipient": recipient,
                "message": message
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.config.network.server_url}/send",
                    json=payload,
                    timeout=self.config.network.request_timeout
                ) as response:
                    response.raise_for_status()
                    
                    # Publish message sent event
                    self.event_bus.publish(Event(
                        EventType.MESSAGE_SENT,
                        {
                            "thread_guid": thread_guid,
                            "message": message,
                            "recipient": recipient
                        }
                    ))
                    
                    return True

        except Exception as e:
            self.logger.error(f"Error sending message: {str(e)}", exc_info=True)
            self.event_bus.publish(Event(
                EventType.ERROR_OCCURRED,
                {"error": str(e), "context": "send_message"}
            ))
            raise

    def _get_thread_recipient(self, thread_guid: str) -> Optional[str]:
        """Get the recipient for a thread."""
        return thread_guid  # For now, assuming thread_guid is the recipient identifier