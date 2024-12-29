import os
import tkinter as tk
from urllib.parse import unquote
from PIL import Image, ImageTk
from typing import Optional, Dict, Any, Tuple
import io
import requests
import logging

from messaging_app.bubbles.image.cache import ImageCache
from ..interfaces import IBubbleContent
from ..resources import image_cache

class ImageContent(IBubbleContent):
    """Handles the content creation for image messages."""
    
    def __init__(self, image_url: Optional[str] = None, text: Optional[str] = None):
        self.image_url = image_url
        self.text = text
        self._photo_image: Optional[ImageTk.PhotoImage] = None
        self.logger = logging.getLogger(__name__)
        self._cache = ImageCache()
        
    def create_content(self, canvas: tk.Canvas, x: int, y: int, width: int, **kwargs) -> tuple[int, int]:
        """Create the image content and optional text caption."""
        style = kwargs.get('style')
        is_outgoing = kwargs.get('is_outgoing', False)
        total_height = 0
        content_width = 0
        
        self.logger.info(f"Creating image content with URL: {self.image_url}")
        
        # Add text caption if present
        if self.text:
            text_item = canvas.create_text(
                x, y,
                text=self.text,
                anchor="nw",
                fill=style.get_text_color(is_outgoing),
                width=width,
                font=(kwargs.get('font_family', "SF Pro"),
                      kwargs.get('font_size', 13))
            )
            bbox = canvas.bbox(text_item)
            if bbox:
                total_height = bbox[3] - bbox[1] + 10  # Add some padding
                content_width = max(content_width, bbox[2] - bbox[0])
        
        # Load and display image
        try:
            if not self.image_url:
                raise ValueError("No image URL provided")
                
            image_data = self._load_image()
            if image_data:
                # Calculate image dimensions
                max_width = 300
                max_height = 300
                image_ratio = image_data.width / image_data.height
                
                if image_ratio > 1:
                    new_width = min(max_width, image_data.width)
                    new_height = int(new_width / image_ratio)
                else:
                    new_height = min(max_height, image_data.height)
                    new_width = int(new_height * image_ratio)
                
                # Resize image
                image_data = image_data.resize((new_width, new_height), Image.Resampling.LANCZOS)
                self._photo_image = ImageTk.PhotoImage(image_data)
                
                # Create image on canvas
                img_y = y + total_height
                img_id = canvas.create_image(
                    x, img_y,
                    anchor="nw",
                    image=self._photo_image,
                    tags="image"
                )
                
                # Update dimensions
                total_height += new_height
                content_width = max(content_width, new_width)
                
                # Add click handler for image preview
                canvas.tag_bind(img_id, "<Button-1>", 
                              lambda e: self._show_image_preview(canvas))
                
                self.logger.info(f"Successfully created image with dimensions: {new_width}x{new_height}")
                
        except Exception as e:
            self.logger.error(f"Error loading image: {e}", exc_info=True)
            # Add error message if image fails to load
            error_text = canvas.create_text(
                x, y + total_height,
                text="[Image failed to load]",
                anchor="nw",
                fill="red",
                font=(kwargs.get('font_family', "SF Pro"),
                      kwargs.get('font_size', 11))
            )
            error_bbox = canvas.bbox(error_text)
            if error_bbox:
                total_height += error_bbox[3] - error_bbox[1]
                content_width = max(content_width, error_bbox[2] - error_bbox[0])
        
        return (content_width, total_height)
    
    def _load_image(self) -> Optional[Image.Image]:
        """Load image from cache or remote URL."""
        try:
            if not self.image_url:
                return None
                
            self.logger.info(f"Loading image from URL: {self.image_url}")
                
            # Check local cache first
            cached_image = self._cache.get(self.image_url)
            if cached_image:
                self.logger.info(f"Using cached image for {self.image_url}")
                return cached_image
                
            # If not in cache, fetch from URL
            if self.image_url.startswith(('http://', 'https://')):
                self.logger.info(f"Fetching image from URL: {self.image_url}")
                response = requests.get(self.image_url, timeout=5)
                response.raise_for_status()
                
                # Save to cache
                self._cache.save(self.image_url, response.content)
                
                # Return image
                return Image.open(io.BytesIO(response.content))
                
            # Handle local file paths
            if self.image_url.startswith('file://'):
                file_path = unquote(self.image_url[7:])
                if file_path.startswith('~'):
                    file_path = os.path.expanduser(file_path)
                return Image.open(file_path)
                
            if os.path.exists(self.image_url):
                return Image.open(self.image_url)
                
            self.logger.warning(f"No valid image source found for URL: {self.image_url}")
            return None
                
        except Exception as e:
            self.logger.error(f"Error loading image from {self.image_url}: {e}")
            return None

    def _show_image_preview(self, canvas: tk.Canvas) -> None:
        """Show full-size image preview."""
        try:
            # Create preview window
            preview = tk.Toplevel(canvas)
            preview.title("Image Preview")
            
            # Load original image
            image_data = self._load_image()
            if not image_data:
                return
                
            # Calculate dimensions
            screen_width = canvas.winfo_screenwidth()
            screen_height = canvas.winfo_screenheight()
            max_width = int(screen_width * 0.8)
            max_height = int(screen_height * 0.8)
            
            # Scale image
            width_ratio = max_width / image_data.width
            height_ratio = max_height / image_data.height
            scale = min(width_ratio, height_ratio)
            
            new_width = int(image_data.width * scale)
            new_height = int(image_data.height * scale)
            
            # Resize and create PhotoImage
            resized = image_data.resize((new_width, new_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(resized)
            
            # Create and pack label
            label = tk.Label(preview, image=photo, bg="black")
            label.image = photo  # Keep reference
            label.pack(expand=True, fill="both")
            
            # Center window
            preview.geometry(
                f"{new_width}x{new_height}+"
                f"{(screen_width-new_width)//2}+"
                f"{(screen_height-new_height)//2}"
            )
            
        except Exception as e:
            self.logger.error(f"Error showing preview: {e}", exc_info=True)