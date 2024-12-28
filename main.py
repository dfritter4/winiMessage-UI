# main.py

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, simpledialog
import threading
from dataclasses import dataclass
from typing import Dict, List, Optional
import time

from message_service import MessageService
from bubbles import TextBubble, ImageBubble, EnhancedTextBubble  # Use package-level imports

from modern_ui import (
    ModernScrolledText,
    ModernListbox,
    ModernEntry,
    ModernButton,
    ModernFrame
)

@dataclass
class Message:
    text: str
    sender_name: str
    timestamp: float
    direction: str  # 'incoming' or 'outgoing'

@dataclass
class Thread:
    guid: str
    name: str
    messages: List[Message]
    phone_number: Optional[str] = None

class MessagingApp:
    """Main application class for the Messages app."""

    def __init__(self, root):
        self.root = root
        self.root.title("Messages")
        self.root.geometry("1000x700")
        self.root.configure(bg="white")
        
        # Initialize services
        self.message_service = MessageService("http://192.168.1.203:5001")

        # Initialize UI
        self._setup_styles()
        self._create_ui()

        # Start initialization after GUI is shown
        self.root.after(100, self._async_initialize)

    def _setup_styles(self):
        """Configure ttk styles for the application."""
        style = ttk.Style()
        style.configure("Chat.TFrame", background="white")
        style.configure("Sidebar.TFrame", background="#F5F5F7")


    def _create_ui(self):
        """Create the main UI components."""
        print("Creating UI...")
        # Main container using ModernFrame
        self.main_container = ModernFrame(self.root, style="Modern.TFrame")
        self.main_container.pack(fill="both", expand=True)

        # PanedWindow to separate sidebar and chat area
        self.paned_window = tk.PanedWindow(self.main_container, orient=tk.HORIZONTAL, sashrelief="raised")
        self.paned_window.pack(fill="both", expand=True)

        self._create_sidebar()
        self._create_chat_area()
        print("UI creation complete.")  


    def _create_sidebar(self):
        """Create the sidebar with search, chat list, and new chat button."""
        print("Creating sidebar...")
        self.sidebar = ModernFrame(self.paned_window, style="Sidebar.TFrame", width=250)
        self.paned_window.add(self.sidebar, minsize=200)

        # Search Entry
        self.search_entry = ModernEntry(
            self.sidebar,
            placeholder="Search Messages",
            font=("SF Pro", 12)
        )
        self.search_entry.pack(fill="x", padx=10, pady=10)

        # Chat Listbox
        self.chat_listbox = ModernListbox(self.sidebar, height=20)
        self.chat_listbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.chat_listbox.bind("<<ListboxSelect>>", self._on_chat_selected)

        # New Chat Button
        self.new_chat_btn = ModernButton(
            self.sidebar,
            text="New Message",
            command=self._create_new_chat
        )
        self.new_chat_btn.pack(fill="x", padx=10, pady=(0, 10))
        print("Sidebar created.")

    def _create_chat_area(self):
        """Create the main chat area with message display and input."""
        print("Creating chat area...")
        self.chat_container = ModernFrame(self.paned_window, style="Chat.TFrame")
        # Removed 'weight' and added 'minsize' instead
        self.paned_window.add(self.chat_container, minsize=400)

        # Message Display using ModernScrolledText
        self.message_display = ModernScrolledText(self.chat_container)
        self.message_display.pack(fill="both", expand=True, padx=10, pady=10)

        # Message Input Area
        self.input_frame = ModernFrame(self.chat_container)
        self.input_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.message_entry = tk.Text(
            self.input_frame,
            height=3,
            font=("SF Pro", 12),
            wrap="word",
            bd=1,
            relief="solid"
        )
        self.message_entry.pack(fill="x", side="left", expand=True, padx=(0, 10))
        self.message_entry.bind("<Return>", self._on_return_key)
        self.message_entry.bind("<Shift-Return>", lambda e: 'break')

        self.send_button = ModernButton(
            self.input_frame,
            text="Send",
            command=self._send_message
        )
        self.send_button.pack(side="right")
        print("Chat area created.")

    def _async_initialize(self):
        """Initialize threads in a separate thread to prevent UI blocking."""
        print("Entered _async_initialize...")
        if not hasattr(self, "chat_listbox"):
            print("Error: chat_listbox not initialized.")
            return

        print("Preparing to start initialization thread.")
        self.chat_listbox.insert(tk.END, "Loading conversations...")
        self.chat_listbox.update_idletasks()

        def initialize_thread():
            print("Inside initialization thread.")
            try:
                threads = self.message_service.initialize_threads()
                print("Initialization in thread complete.")
                self.root.after(0, lambda: self._post_initialize(threads))
            except Exception as e:
                print(f"Initialization thread error: {e}")
                self.root.after(0, lambda e=e: self._show_error(f"Failed to load messages: {e}"))

        thread = threading.Thread(target=initialize_thread, daemon=True)
        print("Starting initialization thread...")
        thread.start()
        print("Initialization thread started.")


    def _post_initialize(self, threads: Dict[str, Thread]):
        """Post-initialization steps after threads are loaded."""
        try:
            # Clear loading message
            self.chat_listbox.delete(0, tk.END)
            # Update thread list
            self._update_thread_list(threads)
            # Start message polling
            threading.Thread(target=self._poll_messages, daemon=True).start()
        except Exception as e:
            self._show_error(f"Error completing initialization: {str(e)}")

    def _update_thread_list(self, threads: Dict[str, Thread]):
        """Populate the chat listbox with thread names."""
        try:
            for guid, thread in threads.items():
                self.chat_listbox.insert(tk.END, thread.name)
        except Exception as e:
            self._show_error(f"Error updating thread list: {str(e)}")

    def _on_chat_selected(self, event):
        """Handle chat selection from the listbox."""
        selection = self.chat_listbox.curselection()
        if not selection:
            return

        thread_name = self.chat_listbox.get(selection[0])
        thread_guid = self._get_guid_by_name(thread_name)
        if thread_guid:
            self._load_chat(thread_guid)

    def _get_guid_by_name(self, name: str) -> Optional[str]:
        """Retrieve thread GUID based on its name."""
        for guid, thread_name in self.message_service.thread_names.items():
            if thread_name == name:
                return guid
        return None

    def _load_chat(self, thread_guid: str):
        thread = self.message_service.get_thread_by_guid(thread_guid)
        if not thread:
            self._show_error("Thread not found.")
            return

        self.message_display.clear()
        
        print(f"\nLoading chat thread {thread_guid}")
        print(f"Total messages: {len(thread.messages)}")
        
        # Ensure messages are sorted and all are displayed
        sorted_messages = sorted(thread.messages, key=lambda msg: msg.timestamp)
        
        for msg in sorted_messages:
            print(f"\nProcessing message:")
            print(f"- Text: {msg.text[:30]}...")
            print(f"- Sender: {msg.sender_name}")
            print(f"- Direction: {msg.direction}")
            print(f"- Attachment: {msg.attachment_url}")
            
            self._add_message_bubble(
                msg.text,
                msg.direction == "outgoing",
                msg.sender_name,
                msg.timestamp,
                attachment_url=msg.attachment_url
            )

        self.current_thread_guid = thread_guid
        self.message_display.scroll_to_bottom()

    def _send_message(self):
        """Send a new message in the current thread."""
        if not hasattr(self, 'current_thread_guid'):
            messagebox.showerror("Error", "Please select a chat first.")
            return

        message = self.message_entry.get("1.0", "end-1c").strip()
        if not message:
            return

        try:
            success = self.message_service.send_message(
                self.current_thread_guid,
                message
            )

            if success:
                self.message_entry.delete("1.0", tk.END)
                self._add_message_bubble(message, True)
                self.message_display.scroll_to_bottom()
        except Exception as e:
            self._show_error(f"Error sending message: {str(e)}")

    def _add_message_bubble(self, message: str, is_outgoing: bool, sender_name: str = None, 
                       timestamp: float = None, attachment_url: Optional[str] = None):
        """Add a styled message bubble to the message display."""
        container = tk.Frame(self.message_display.scrollable_frame, bg="white")
        container.pack(
            fill="x",
            padx=15,
            pady=5
        )
        
        # Only treat as image if it's an actual image attachment URL
        is_image_attachment = (
            attachment_url is not None and 
            any(attachment_url.lower().endswith(ext) 
                for ext in ['.jpg', '.jpeg', '.png', '.gif', '.heic', '.heif'])
        )
        
        if is_image_attachment:
            bubble = ImageBubble(
                container,
                message,
                attachment_url,
                is_outgoing=is_outgoing,
                timestamp=timestamp,
                sender_name=sender_name
            )
        else:
            # Use EnhancedTextBubble instead of TextBubble for all text messages
            bubble = EnhancedTextBubble(
                container,
                message,
                is_outgoing=is_outgoing,
                timestamp=timestamp,
                sender_name=sender_name
            )
        
        bubble.pack(
            side="right" if is_outgoing else "left",
            fill="none",
            expand=False
        )
        
        self.message_display.scrollable_frame.update_idletasks()
        self.message_display._on_frame_configure()


    def _poll_messages(self):
        """Continuously poll for new messages without blocking the main thread."""
        while True:
            try:
                updates = self.message_service.poll_messages()
                if updates:
                    self.root.after(0, lambda: self._process_updates(updates))
            except Exception as e:
                print(f"Polling error: {e}")
            time.sleep(2)  # Poll every 2 seconds

    def _process_updates(self, updates: Dict[str, List[Message]]):
        """Process and display incoming message updates."""
        needs_scroll = False
        for thread_guid, messages in updates.items():
            thread_name = self.message_service.thread_names.get(thread_guid, "Unknown")
            if thread_name not in self.chat_listbox.get(0, tk.END):
                self.chat_listbox.insert(tk.END, thread_name)

            if hasattr(self, 'current_thread_guid') and thread_guid == self.current_thread_guid:
                for msg in messages:
                    self._add_message_bubble(
                        msg.text,
                        msg.direction == "outgoing",
                        msg.sender_name,
                        msg.timestamp,
                        attachment_url=msg.attachment_url
                    )

                needs_scroll = True

        if needs_scroll:
            self.message_display.scroll_to_bottom()

    def _on_return_key(self, event):
        """Handle the Return key to send messages."""
        if not event.state & 0x1:  # Shift key is not pressed
            self._send_message()
            return 'break'
        return None

    def _show_error(self, message):
        """Display an error message to the user."""
        messagebox.showerror("Error", message)

    def _create_new_chat(self):
        """Initiate the creation of a new chat thread."""
        phone_number = simpledialog.askstring(
            "New Message",
            "Enter recipient's phone number (e.g., +1234567890):",
            parent=self.root
        )

        if not phone_number:
            return

        # Normalize phone number format
        if not phone_number.startswith("+"):
            phone_number = "+" + phone_number
        phone_number = "+" + "".join(filter(str.isdigit, phone_number))

        try:
            display_name = simpledialog.askstring(
                "New Message",
                "Enter display name (optional):",
                parent=self.root
            )

            # Create a new thread via the message service
            new_guid = f"guid-{phone_number}"
            new_thread = Thread(
                guid=new_guid,
                name=display_name or phone_number,
                messages=[]
            )
            self.message_service.thread_names[new_guid] = new_thread.name
            self.message_service.message_cache[new_guid] = new_thread.messages

            self.chat_listbox.insert(tk.END, new_thread.name)
            last_index = self.chat_listbox.size() - 1
            self.chat_listbox.selection_clear(0, tk.END)
            self.chat_listbox.selection_set(last_index)
            self.chat_listbox.see(last_index)
            self._load_chat(new_guid)

        except Exception as e:
            self._show_error(f"Failed to create new chat: {str(e)}")

def main():
    root = tk.Tk()
    app = MessagingApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
