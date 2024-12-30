from typing import Union, Optional
from datetime import datetime

def normalize_timestamp(timestamp: Union[str, float, int, None]) -> Optional[float]:
    """
    Normalize different timestamp formats to a float timestamp.
    
    Args:
        timestamp: Timestamp in various formats (string ISO format, float/int unix timestamp)
        
    Returns:
        float: Unix timestamp in seconds
        None: If timestamp cannot be parsed
    """
    if timestamp is None:
        return None
        
    try:
        # If already a number, ensure it's a float
        if isinstance(timestamp, (int, float)):
            return float(timestamp)
            
        # Handle string timestamps
        if isinstance(timestamp, str):
            # Try parsing as ISO format
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                return dt.timestamp()
            except ValueError:
                # Try parsing as float/int string
                try:
                    return float(timestamp)
                except ValueError:
                    return None
                    
        return None
        
    except Exception:
        return None

def safe_timestamp_sort(messages: list, reverse: bool = False) -> list:
    """
    Safely sort messages by timestamp, handling mixed timestamp formats.
    
    Args:
        messages: List of message objects with timestamp attribute
        reverse: Sort in reverse order if True
        
    Returns:
        list: Sorted list of messages
    """
    def get_safe_timestamp(msg):
        ts = normalize_timestamp(msg.timestamp)
        return ts if ts is not None else float('-inf')
        
    return sorted(messages, key=get_safe_timestamp, reverse=reverse)