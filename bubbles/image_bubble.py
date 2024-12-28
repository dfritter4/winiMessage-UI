import io
import requests
from PIL import Image, ImageTk, UnidentifiedImageError
from tkinter import Toplevel, Label
from .base_bubble import BaseBubble
from .resources import image_cache

class ImageBubble(BaseBubble):
    def __init__(self, parent, message: str, attachment_url: str, **kwargs):
        super().__init__(parent, **kwargs)
        self.message = message
        self.attachment_url = attachment_url
        self._create_bubble()

    def _create_bubble(self):
        # Clear canvas
        self.delete("all")

        # Add sender name and get its height
        sender_height = self._add_sender_name()

        # Calculate text dimensions
        max_width = 300
        temp = self.create_text(
            0, 0,
            text=self.message,
            anchor="nw",
            width=max_width
        )
        bbox = self.bbox(temp)
        text_width = bbox[2] - bbox[0] if bbox else 0
        text_height = bbox[3] - bbox[1] if bbox else 0
        self.delete(temp)

        # Set initial bubble dimensions
        bubble_width = min(max(text_width + 2 * self.padding, 300), max_width)
        initial_height = text_height + 3 * self.padding + sender_height + 25

        # Configure initial canvas size
        self.configure(width=bubble_width, height=initial_height)

        # Calculate bubble position
        bubble_x = 0 if self.is_outgoing else self.padding

        # Draw initial bubble
        if self.message:
            # Add message text
            self.create_text(
                bubble_x + self.padding,
                sender_height + self.padding,
                text=self.message,
                anchor="nw",
                fill=self.text_color,
                width=max_width - 2 * self.padding
            )

        # Load image
        self._load_image(bubble_x, sender_height + text_height + 2 * self.padding)

    def _process_image_data(self, image_data: bytes) -> Image.Image:
        """Process raw image data into a PIL Image with proper error handling."""
        try:
            # For HEIC images, use pillow_heif
            if self.attachment_url.lower().endswith(('.heic', '.heif')):
                import pillow_heif
                heif_file = pillow_heif.read_heif(io.BytesIO(image_data))
                img = Image.frombytes(
                    heif_file.mode,
                    heif_file.size,
                    heif_file.data,
                    "raw",
                    heif_file.mode,
                    heif_file.stride,
                )
            else:
                # For other formats, use regular PIL
                img = Image.open(io.BytesIO(image_data))
            
            # Convert RGBA to RGB if necessary
            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[3] if len(img.split()) > 3 else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
                
            return img
        except Exception as e:
            print(f"Error processing image: {e}")
            print(f"Image URL: {self.attachment_url}")
            print(f"Data length: {len(image_data)}")
            print(f"First 32 bytes: {image_data[:32].hex()}")
            raise

    def _load_image(self, bubble_x: int, start_y: int):
        def process_image():
            try:
                if self.attachment_url in image_cache:
                    print(f"\nUsing cached image for {self.attachment_url}")
                    photo_image = image_cache[self.attachment_url]
                else:
                    print(f"\nFetching image from {self.attachment_url}")
                    response = requests.get(self.attachment_url, timeout=5)
                    response.raise_for_status()
                    
                    content_type = response.headers.get('content-type', '')
                    content_length = response.headers.get('content-length', 'unknown')
                    print(f"Response details:")
                    print(f"Content-Type: {content_type}")
                    print(f"Content-Length: {content_length}")
                    print(f"Status Code: {response.status_code}")
                    
                    # Print first few bytes of response content
                    content_preview = response.content[:32].hex()
                    print(f"Content preview (hex): {content_preview}")
                    
                    # Validate content type
                    if not content_type.startswith('image/'):
                        raise ValueError(f"Invalid content type: {content_type}")
                    
                    # Validate file signatures
                    jpeg_headers = [b'\xFF\xD8\xFF', b'\xFF\xD8\xFF\xE0', b'\xFF\xD8\xFF\xE1']
                    png_header = b'\x89PNG\r\n\x1a\n'
                    
                    is_jpeg = any(response.content.startswith(h) for h in jpeg_headers)
                    is_png = response.content.startswith(png_header)
                    
                    if not (is_jpeg or is_png):
                        print("Warning: Content doesn't match common image headers")
                    
                    # Try to process the image
                    image_data = self._process_image_data(response.content)
                    print(f"Original image size: {image_data.size}")
                    
                    # Calculate new dimensions while maintaining aspect ratio
                    image_ratio = image_data.width / image_data.height
                    if image_ratio > 1:
                        new_width = min(300, image_data.width)
                        new_height = int(new_width / image_ratio)
                    else:
                        new_height = min(300, image_data.height)
                        new_width = int(new_height * image_ratio)
                    
                    print(f"Resizing to: {new_width}x{new_height}")
                    
                    # Resize the image
                    image_data = image_data.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    # Create PhotoImage and cache it
                    photo_image = ImageTk.PhotoImage(image_data)
                    image_cache[self.attachment_url] = photo_image
                    image_cache[f"{self.attachment_url}_original"] = response.content

                # Update canvas size to accommodate image
                new_height = start_y + photo_image.height() + self.padding
                self.configure(height=new_height)

                # Draw bubble background
                self._draw_bubble_body(bubble_x, 0, self.winfo_width(), new_height)

                # Add image
                img_id = self.create_image(
                    bubble_x + self.padding,
                    start_y,
                    anchor="nw",
                    image=photo_image,
                    tags="image"
                )
                self.image = photo_image  # Prevent garbage collection

                # Add timestamp
                self._add_timestamp(bubble_x, self.winfo_width(), new_height - 15)

                # Add click handler
                self.tag_bind(img_id, "<Button-1>", lambda e: self._open_image())

            except requests.exceptions.RequestException as e:
                print(f"Network error: {e}")
                print(f"URL: {self.attachment_url}")
            except UnidentifiedImageError as e:
                print(f"Error identifying image format: {e}")
                if 'response' in locals():
                    print(f"Response headers: {dict(response.headers)}")
            except Exception as e:
                print(f"Error loading image: {e}")
                if 'response' in locals():
                    print(f"Response content length: {len(response.content)}")
                    print(f"First 32 bytes: {response.content[:32].hex()}")

        self.after(100, process_image)

    def _open_image(self):
        try:
            if f"{self.attachment_url}_original" in image_cache:
                image_data = self._process_image_data(image_cache[f"{self.attachment_url}_original"])
            else:
                response = requests.get(self.attachment_url, timeout=5)
                response.raise_for_status()
                image_data = self._process_image_data(response.content)
                image_cache[f"{self.attachment_url}_original"] = response.content

            # Create viewer window
            viewer = Toplevel(self)
            viewer.title("Image Viewer")

            # Calculate dimensions
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            max_width = int(screen_width * 0.8)
            max_height = int(screen_height * 0.8)

            # Scale image
            width_ratio = max_width / image_data.width
            height_ratio = max_height / image_data.height
            scale = min(width_ratio, height_ratio)
            
            new_width = int(image_data.width * scale)
            new_height = int(image_data.height * scale)
            
            resized = image_data.resize((new_width, new_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(resized)

            label = Label(viewer, image=photo, bg="black")
            label.image = photo
            label.pack(expand=True, fill="both")

            # Center window
            viewer.geometry(f"{new_width}x{new_height}+{(screen_width-new_width)//2}+{(screen_height-new_height)//2}")

        except Exception as e:
            print(f"Error opening image: {e}")