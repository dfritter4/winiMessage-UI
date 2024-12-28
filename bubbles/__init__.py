"""
Bubbles package for message display components.
Provides interfaces and implementations for different types of message bubbles.
"""

# Core interfaces
from .interfaces import (
    IBubbleContent,
    IBubbleDrawer,
    IBubbleStyle,
    IBubbleFactory
)

# Base implementations
from .base.style import DefaultBubbleStyle
from .base.bubble import BaseBubble
from .base.content import BaseContent
from .base.drawer import DefaultBubbleDrawer

# Text bubbles
from .text import (
    TextBubble,
    TextContent,
    TextBubbleFactory
)

# Enhanced text bubbles
from .enhanced import (
    EnhancedTextBubble,
    EnhancedTextContent,
    EnhancedTextBubbleFactory
)

# Image bubbles
from .image import (
    ImageBubble,
    ImageContent,
    ImageBubbleFactory
)

# Shared resources
from .resources import image_cache

__all__ = [
    # Interfaces
    'IBubbleContent',
    'IBubbleDrawer',
    'IBubbleStyle',
    'IBubbleFactory',
    
    # Base implementations
    'DefaultBubbleStyle',
    'BaseBubble',
    'BaseContent',
    'DefaultBubbleDrawer',
    
    # Text bubbles
    'TextBubble',
    'TextContent',
    'TextBubbleFactory',
    
    # Enhanced text bubbles
    'EnhancedTextBubble',
    'EnhancedTextContent',
    'EnhancedTextBubbleFactory',
    
    # Image bubbles
    'ImageBubble',
    'ImageContent',
    'ImageBubbleFactory',
    
    # Resources
    'image_cache'
]