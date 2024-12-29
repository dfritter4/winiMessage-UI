import os
import logging
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image
import pillow_heif
from urllib.parse import urlparse, unquote
import io

class ImageCache:
    """Handles local image caching operations."""
    
    _instance = None
    logger = logging.getLogger(__name__)

    def __new__(cls, cache_dir: str = "image_cache"):
        if cls._instance is None:
            cls._instance = super(ImageCache, cls).__new__(cls)
            base_dir = Path(__file__).parent.parent.parent
            cls._instance.cache_dir = base_dir / cache_dir
            cls._instance.cache_dir.mkdir(parents=True, exist_ok=True)
            # Register HEIF opener
            pillow_heif.register_heif_opener()
            cls._instance.logger.info(f"Initialized image cache at {cls._instance.cache_dir}")
        return cls._instance
    
    def _get_filename(self, url: str) -> Tuple[str, str]:
        """Extract and decode filename from URL or path, and return both original and jpg version."""
        filename = os.path.basename(urlparse(url).path or url)
        decoded_filename = unquote(filename)
        
        # For HEIC files, also return a JPG version of the filename
        name, ext = os.path.splitext(decoded_filename)
        if ext.lower() in ['.heic', '.heif']:
            jpg_filename = f"{name}.jpg"
            return decoded_filename, jpg_filename
        return decoded_filename, decoded_filename
        
    def get_cache_path(self, url: str) -> Tuple[Path, Path]:
        """Get the local cache paths for both original and jpg version."""
        orig_filename, jpg_filename = self._get_filename(url)
        orig_path = self.cache_dir / orig_filename
        jpg_path = self.cache_dir / jpg_filename
        return orig_path, jpg_path
        
    def exists(self, url: str) -> bool:
        """Check if image exists in cache."""
        orig_path, jpg_path = self.get_cache_path(url)
        exists = jpg_path.exists()  # Only check for JPG version
        self.logger.info(f"Cache check for {jpg_path.name}: {'found' if exists else 'not found'}")
        return exists
        
    def get(self, url: str) -> Optional[Image.Image]:
        """Get image from cache if it exists."""
        try:
            orig_path, jpg_path = self.get_cache_path(url)
            if jpg_path.exists():
                self.logger.info(f"Loading cached image: {jpg_path}")
                return Image.open(jpg_path)
            return None
        except Exception as e:
            self.logger.error(f"Error reading from cache: {e}")
            return None
        
    def save(self, url: str, image_data: bytes) -> None:
        """Save image data to cache, converting HEIC to JPG if needed."""
        try:
            orig_path, jpg_path = self.get_cache_path(url)
            
            # Save the original file first
            with open(orig_path, 'wb') as f:
                f.write(image_data)
            
            # If it's a HEIC/HEIF file, convert to JPG
            if orig_path.suffix.lower() in ['.heic', '.heif']:
                self.logger.info(f"Converting HEIC to JPG: {orig_path} -> {jpg_path}")
                try:
                    heif_file = pillow_heif.read_heif(orig_path)
                    image = Image.frombytes(
                        heif_file.mode,
                        heif_file.size,
                        heif_file.data,
                        "raw",
                        heif_file.mode,
                        heif_file.stride,
                    )
                    image.save(jpg_path, format='JPEG', quality=95)
                    # Remove original HEIC file since we have the JPG
                    orig_path.unlink()
                except Exception as e:
                    self.logger.error(f"Error converting HEIC to JPG: {e}")
                    # If conversion fails, remove the original to force re-download next time
                    if orig_path.exists():
                        orig_path.unlink()
            else:
                # For non-HEIC files, just ensure the jpg_path matches the orig_path
                if jpg_path != orig_path:
                    jpg_path.write_bytes(orig_path.read_bytes())
                
            self.logger.info(f"Successfully saved image to cache: {jpg_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving to cache: {e}")
            # Clean up any partially written files
            for path in [orig_path, jpg_path]:
                if path.exists():
                    path.unlink()