# message_service.py

import requests
from typing import Dict, List, Optional
from dataclasses import dataclass
import time

@dataclass
class Message:
    text: str
    sender_name: str
    timestamp: float
    thread_name: Optional[str] = None
    cache_key: Optional[str] = None
    direction: Optional[str] = None
    attachment_path: Optional[str] = None
    attachment_url: Optional[str] = None


@dataclass
class Thread:
    guid: str
    name: str
    messages: List[Message]
    phone_number: Optional[str] = None

class MessageService:
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.message_cache: Dict[str, List[Message]] = {}
        self.thread_names: Dict[str, str] = {}

    def initialize_threads(self) -> Dict[str, Thread]:
        try:
            response = requests.get(f"{self.server_url}/messages", timeout=5)
            response.raise_for_status()
            threads_data = response.json().get("threads", {})
            result = {}
            self.message_cache.clear()
            self.thread_names.clear()

            for thread_guid, messages in threads_data.items():
                if not messages:
                    continue

                thread_name = messages[0].get("thread_name", "Unknown")
                self.thread_names[thread_guid] = thread_name
                self.message_cache[thread_guid] = []

                thread_messages = []
                for msg in messages:
                    message = Message(
                        text=str(msg.get("text", "")),
                        sender_name=str(msg.get("sender_name", "Unknown")),
                        timestamp=msg.get("timestamp", time.time()),
                        thread_name=msg.get("thread_name"),
                        direction=msg.get("direction", "incoming"),
                        attachment_path=msg.get("attachment_path"),
                        attachment_url=msg.get("attachment_url")
                    )
                    thread_messages.append(message)
                    #print(f"Message attachment URL: {msg.get('attachment_url')}")

                result[thread_guid] = Thread(
                    guid=thread_guid,
                    name=thread_name,
                    messages=thread_messages
                )

            return result
        except Exception as e:
            raise ConnectionError(f"Error initializing threads: {str(e)}")

    def poll_messages(self) -> Dict[str, List[Message]]:
        try:
            response = requests.get(f"{self.server_url}/messages", timeout=5)
            response.raise_for_status()
            threads_data = response.json().get("threads", {})
            updates: Dict[str, List[Message]] = {}

            for thread_guid, messages in threads_data.items():
                if thread_guid not in self.message_cache:
                    self.message_cache[thread_guid] = []

                thread_updates = []
                existing_keys = {f"{m.sender_name}:{m.text}:{m.timestamp}" for m in self.message_cache[thread_guid]}

                for msg in messages:
                    cache_key = f"{msg.get('sender_name', 'Unknown')}:{msg.get('text', '')}:{msg.get('timestamp', time.time())}"

                    if cache_key not in existing_keys:
                        message = Message(
                            text=str(msg.get("text", "")),
                            sender_name=str(msg.get("sender_name", "Unknown")),
                            timestamp=msg.get("timestamp", time.time()),
                            thread_name=msg.get("thread_name"),
                            direction=msg.get("direction", "incoming"),
                            attachment_path=msg.get("attachment_path"),
                            attachment_url=msg.get("attachment_url"),
                        )
                        thread_updates.append(message)
                        self.message_cache[thread_guid].append(message)

                if thread_updates:
                    updates[thread_guid] = thread_updates


            return updates
        except Exception as e:
            raise ConnectionError(f"Error polling messages: {str(e)}")

    def get_thread_by_guid(self, guid: str) -> Optional[Thread]:
        if guid in self.message_cache:
            return Thread(
                guid=guid,
                name=self.thread_names.get(guid, "Unknown"),
                messages=self.message_cache[guid]
            )
        return None

    def send_message(self, thread_guid: str, message: str, recipient: Optional[str] = None) -> bool:
        try:
            recipient = recipient or self.get_thread_recipient(thread_guid)
            if not recipient:
                raise ValueError("Could not determine recipient")

            payload = {
                "recipient": recipient,
                "message": message
            }

            response = requests.post(
                f"{self.server_url}/send",
                json=payload,
                timeout=5
            )
            response.raise_for_status()
            return True

        except Exception as e:
            raise ConnectionError(f"Error sending message: {str(e)}")

    def get_thread_recipient(self, thread_guid: str) -> Optional[str]:
        # Simplified logic: return thread_guid assuming it's a phone number or identifier
        return thread_guid
