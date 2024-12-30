"""
Messaging App
A Windows thin client for iMessage
"""

from .domain import *
from .services import *
from .controllers import *
from .config import *
from .ui import *
from .bubbles import *

__version__ = '0.1.0'

from .app import MessagingApp
from .app_lifecycle import MessageAppLifecycle
from .event_handling import MessageAppEventHandler
from .ui import MessageAppUI

__all__ = [
    'MessagingApp',
    'MessageAppLifecycle',
    'MessageAppEventHandler',
    'MessageAppUI'
]