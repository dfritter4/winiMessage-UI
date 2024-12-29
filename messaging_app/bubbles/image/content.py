import os
import tkinter as tk
from urllib.parse import unquote
from PIL import Image, ImageTk
from typing import Optional, Dict, Any
import io
import requests
from ..interfaces import IBubbleContent
from ..resources import image_cache

class ImageContent(IBubbleContent):
    """Handles the content creation for image messages."""
    
    def __init__(self, image_url: Optional[str] = None, text: Optional[str] = None):
        # Prefer attachment_url if provided
        self.image_url = image_url or ""
        self.text = text
        self._photo_image: Optional[ImageTk.PhotoImage] = None
        
    def create_content(self, canvas: tk.Canvas, x: int, y: int, width: int, **kwargs) -> tuple[int, int]:
        """Create the image content and optional text caption."""
        style = kwargs.get('style')
        is_outgoing = kwargs.get('is_outgoing', False)
        total_height = 0
        content_width = 0
        
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
                total_height = bbox[3] - bbox[1]
                content_width = max(content_width, bbox[2] - bbox[0])
        
        # Load and display image
        try:
            image_data = self._load_image()
            if image_data:
                # Calculate image dimensions
                image_ratio = image_data.width / image_data.height
                if image_ratio > 1:
                    new_width = min(300, image_data.width)
                    new_height = int(new_width / image_ratio)
                else:
                    new_height = min(300, image_data.height)
                    new_width = int(new_height * image_ratio)
                
                # Resize image
                image_data = image_data.resize((new_width, new_height), Image.LANCZOS)
                self._photo_image = ImageTk.PhotoImage(image_data)
                
                # Create image on canvas
                img_y = y + total_height + (10 if self.text else 0)
                img_id = canvas.create_image(
                    x, img_y,
                    anchor="nw",
                    image=self._photo_image,
                    tags="image"
                )
                
                # Update dimensions
                total_height += new_height + (10 if self.text else 0)
                content_width = max(content_width, new_width)
                
                # Add click handler for image preview
                canvas.tag_bind(img_id, "<Button-1>", 
                              lambda e: self._show_image_preview(canvas))
                
        except Exception as e:
            print(f"Error loading image: {e}")
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
        """Load and process the image data."""
        try:
            # Prioritize attachment_url if available
            image_url = self.image_url
            
            # Use attachment URL if it's a proper HTTP/HTTPS URL
            if image_url.startswith(('http://', 'https://')):
                # Check cache first
                if image_url in image_cache:
                    return Image.open(io.BytesIO(image_cache[f"{image_url}_original"]))
                
                # Fetch from server
                response = requests.get(image_url, timeout=5)
                response.raise_for_status()
                
                # Try HEIF support with pillow-heif
                try:
                    import pillow_heif
                    pillow_heif.register_heif_opener()
                    image_data = Image.open(io.BytesIO(response.content))
                except (ImportError, ModuleNotFoundError):
                    # If pillow-heif is not installed, fall back to Pillow
                    image_data = Image.open(io.BytesIO(response.content))
                
                # Cache original image data
                image_cache[f"{image_url}_original"] = response.content
                
                return image_data
            
            # Fallback to local file handling
            if image_url.startswith('file://'):
                file_path = unquote(image_url[7:])
                if file_path.startswith('~'):
                    file_path = os.path.expanduser(file_path)
                
                # Try HEIF support for local files
                try:
                    import pillow_heif
                    pillow_heif.register_heif_opener()
                    return Image.open(file_path)
                except (ImportError, ModuleNotFoundError):
                    return Image.open(file_path)
            
            # Local path handling as a last resort
            if os.path.exists(image_url):
                try:
                    import pillow_heif
                    pillow_heif.register_heif_opener()
                    return Image.open(image_url)
                except (ImportError, ModuleNotFoundError):
                    return Image.open(image_url)
            
            # If no valid image source is found
            print(f"No valid image source found for URL: {image_url}")
            return None
                
        except Exception as e:
            print(f"Error loading image from {self.image_url}: {e}")
            return None
    
    def _show_image_preview(self, canvas: tk.Canvas) -> None:
        """Show full-size image preview."""
        try:
            # Create preview window
            preview = tk.Toplevel(canvas)
            preview.title("Image Preview")
            
            # Load original image
            if f"{self.image_url}_original" in image_cache:
                image_data = Image.open(
                    io.BytesIO(image_cache[f"{self.image_url}_original"])
                )
            else:
                response = requests.get(self.image_url, timeout=5)
                response.raise_for_status()
                image_data = Image.open(io.BytesIO(response.content))
                image_cache[f"{self.image_url}_original"] = response.content
            
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
            resized = image_data.resize((new_width, new_height), Image.LANCZOS)
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
            print(f"Error showing preview: {e}")