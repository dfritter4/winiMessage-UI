import os
import logging
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image
import pillow_heif
from urllib.parse import urlparse, unquote
import io

class ImageCache:
    """Handles local image caching operations with memory and disk caching."""
    
    _instance = None
    _image_cache = {}
    logger = logging.getLogger(__name__)

    def __new__(cls, cache_dir: str = "image_cache", max_memory_items: int = 100):
        if cls._instance is None:
            cls._instance = super(ImageCache, cls).__new__(cls)
            base_dir = Path(__file__).parent.parent.parent
            cls._instance.cache_dir = base_dir / cache_dir
            cls._instance.cache_dir.mkdir(parents=True, exist_ok=True)
            pillow_heif.register_heif_opener()
            cls._instance.logger.info(f"Initialized image cache at {cls._instance.cache_dir}")
        return cls._instance

    def _get_filename(self, url: str) -> Tuple[str, str]:
        """Extract and decode filename from URL or path, and return both original and jpg version."""
        filename = os.path.basename(urlparse(url).path or url)
        decoded_filename = unquote(filename)
        
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
        """Check if image exists in cache (memory or disk)."""
        if url in self._image_cache:
            return True
            
        orig_path, jpg_path = self.get_cache_path(url)
        exists = jpg_path.exists()
        self.logger.info(f"Cache check for {jpg_path.name}: {'found' if exists else 'not found'}")
        return exists
        
    def get(self, url: str) -> Optional[Image.Image]:
        """Get image from cache if it exists (memory first, then disk)."""
        try:
            if url in self._image_cache:
                self.logger.info(f"Memory cache hit for: {url}")
                return self._image_cache[url]

            _, jpg_path = self.get_cache_path(url)
            if jpg_path.exists():
                self.logger.info(f"Disk cache hit - loading: {jpg_path}")
                img = Image.open(jpg_path)
                self._image_cache[url] = img
                return img
            return None
        except Exception as e:
            self.logger.error(f"Error reading from cache: {e}")
            return None
        
    def save(self, url: str, image_data: bytes) -> None:
        """Save image data to both memory and disk cache, converting HEIC to JPG if needed."""
        try:
            orig_path, jpg_path = self.get_cache_path(url)
            
            with open(orig_path, 'wb') as f:
                f.write(image_data)
            
            if orig_path.suffix.lower() in ['.heic', '.heif']:
                self.logger.info(f"Converting HEIC to JPG: {orig_path} -> {jpg_path}")
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
                self._image_cache[url] = image
                orig_path.unlink()
            else:
                if jpg_path != orig_path:
                    jpg_path.write_bytes(orig_path.read_bytes())
                image = Image.open(jpg_path)
                self._image_cache[url] = image

            self.logger.info(f"Saved image to cache: {jpg_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving to cache: {e}")
            for path in [orig_path, jpg_path]:
                if path.exists():
                    path.unlink()
            if url in self._image_cache:
                del self._image_cache[url]