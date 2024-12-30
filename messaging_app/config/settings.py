from dataclasses import dataclass
from typing import Dict

@dataclass
class UIConfig:
    font_family: str = "SF Pro"
    font_sizes: Dict[str, int] = None
    bubble_padding: int = 12
    max_message_width: int = 300
    min_message_width: int = 60
    
    def __post_init__(self):
        if self.font_sizes is None:
            self.font_sizes = {
                "normal": 13,
                "small": 11,
                "timestamp": 9,
                "sender": 11
            }

@dataclass
class ColorConfig:
    outgoing_bubble: str = "#007AFF"
    incoming_bubble: str = "#E9E9EB"
    timestamp: str = "#8E8E93"
    sender_name: str = "#65656A"
    outgoing_text: str = "white"
    incoming_text: str = "black"
    background: str = "white"
    sidebar: str = "#F5F5F7"

@dataclass
class NetworkConfig:
    server_url: str = "http://192.168.1.203:5001" # 0.0.0.0:5001
    poll_interval: int = 2
    request_timeout: int = 5
    max_retries: int = 3

@dataclass
class AppConfig:
    ui: UIConfig = None
    colors: ColorConfig = None
    network: NetworkConfig = None
    
    def __post_init__(self):
        if self.ui is None:
            self.ui = UIConfig()
        if self.colors is None:
            self.colors = ColorConfig()
        if self.network is None:
            self.network = NetworkConfig()

def load_config() -> AppConfig:
    """
    Load configuration from environment variables or config file.
    For now, returns default config.
    """
    return AppConfig()