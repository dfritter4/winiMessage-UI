class ImageCache {
  constructor() {
    this.cache = new Map();
    this.downloading = new Map(); // Track ongoing downloads
    this.maxCacheSize = 100; // Maximum number of cached images
    this.maxAge = 7 * 24 * 60 * 60 * 1000; // 7 days in milliseconds
    this.dbName = 'WiniMessageImageCache';
    this.dbVersion = 1;
    this.storeName = 'images';
    this.db = null;
    
    // Initialize IndexedDB and load existing cache
    this.initDB();
  }

  // Initialize IndexedDB
  async initDB() {
    try {
      this.db = await new Promise((resolve, reject) => {
        const request = indexedDB.open(this.dbName, this.dbVersion);
        
        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);
        
        request.onupgradeneeded = (event) => {
          const db = event.target.result;
          if (!db.objectStoreNames.contains(this.storeName)) {
            const store = db.createObjectStore(this.storeName, { keyPath: 'url' });
            store.createIndex('timestamp', 'timestamp', { unique: false });
          }
        };
      });
      
      // Load existing cache into memory
      await this.loadExistingCache();
      console.log('Image cache initialized with IndexedDB');
      
    } catch (error) {
      console.error('Failed to initialize IndexedDB for image cache:', error);
      // Fallback to memory-only cache
    }
  }

  // Load existing cache from IndexedDB
  async loadExistingCache() {
    if (!this.db) return;
    
    try {
      const transaction = this.db.transaction([this.storeName], 'readonly');
      const store = transaction.objectStore(this.storeName);
      const request = store.getAll();
      
      const results = await new Promise((resolve, reject) => {
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
      });
      
      const now = Date.now();
      let loadedCount = 0;
      let expiredCount = 0;
      
      for (const item of results) {
        // Check if expired
        if (now - item.timestamp > this.maxAge) {
          expiredCount++;
          await this.removeFromDB(item.url);
          continue;
        }
        
        // Create blob URL from stored blob
        const blobUrl = URL.createObjectURL(item.blob);
        
        this.cache.set(item.url, {
          blobUrl: blobUrl,
          originalUrl: item.url,
          timestamp: item.timestamp,
          size: item.blob.size
        });
        
        loadedCount++;
      }
      
      console.log(`Loaded ${loadedCount} cached images, removed ${expiredCount} expired images`);
      
    } catch (error) {
      console.error('Failed to load existing cache:', error);
    }
  }

  // Generate cache key from URL
  getCacheKey(url) {
    return url;
  }

  // Check if image is in cache and not expired
  isInCache(url) {
    const key = this.getCacheKey(url);
    const cached = this.cache.get(key);
    
    if (!cached) return false;
    
    // Check if expired
    if (Date.now() - cached.timestamp > this.maxAge) {
      this.cache.delete(key);
      URL.revokeObjectURL(cached.blobUrl); // Clean up blob URL
      return false;
    }
    
    return true;
  }

  // Get cached image URL
  getCachedUrl(url) {
    const key = this.getCacheKey(url);
    const cached = this.cache.get(key);
    return cached ? cached.blobUrl : null;
  }

  // Download and cache image
  async cacheImage(url) {
    const key = this.getCacheKey(url);
    
    // If already in cache, return cached URL
    if (this.isInCache(url)) {
      return this.getCachedUrl(url);
    }
    
    // If already downloading, wait for existing download
    if (this.downloading.has(key)) {
      return await this.downloading.get(key);
    }

    // Start download
    const downloadPromise = this._downloadImage(url);
    this.downloading.set(key, downloadPromise);
    
    try {
      const blobUrl = await downloadPromise;
      this.downloading.delete(key);
      return blobUrl;
    } catch (error) {
      this.downloading.delete(key);
      throw error;
    }
  }

  // Save to IndexedDB
  async saveToDB(url, blob, timestamp) {
    if (!this.db) return;
    
    try {
      const transaction = this.db.transaction([this.storeName], 'readwrite');
      const store = transaction.objectStore(this.storeName);
      
      await new Promise((resolve, reject) => {
        const request = store.put({
          url: url,
          blob: blob,
          timestamp: timestamp,
          size: blob.size
        });
        
        request.onsuccess = () => resolve();
        request.onerror = () => reject(request.error);
      });
      
    } catch (error) {
      console.error('Failed to save to IndexedDB:', error);
    }
  }

  // Remove from IndexedDB
  async removeFromDB(url) {
    if (!this.db) return;
    
    try {
      const transaction = this.db.transaction([this.storeName], 'readwrite');
      const store = transaction.objectStore(this.storeName);
      
      await new Promise((resolve, reject) => {
        const request = store.delete(url);
        request.onsuccess = () => resolve();
        request.onerror = () => reject(request.error);
      });
      
    } catch (error) {
      console.error('Failed to remove from IndexedDB:', error);
    }
  }

  // Internal method to download image
  async _downloadImage(url) {
    try {
      console.log('Downloading image for cache:', url);
      
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const blob = await response.blob();
      const blobUrl = URL.createObjectURL(blob);
      const timestamp = Date.now();
      
      // Store in memory cache
      const key = this.getCacheKey(url);
      this.cache.set(key, {
        blobUrl: blobUrl,
        originalUrl: url,
        timestamp: timestamp,
        size: blob.size
      });
      
      // Store in IndexedDB for persistence
      await this.saveToDB(url, blob, timestamp);
      
      // Clean up old entries if cache is too large
      this._cleanupCache();
      
      console.log('Image cached successfully:', url);
      return blobUrl;
      
    } catch (error) {
      console.error('Failed to cache image:', url, error);
      throw error;
    }
  }

  // Clean up old cache entries
  async _cleanupCache() {
    if (this.cache.size <= this.maxCacheSize) return;
    
    // Convert to array and sort by timestamp (oldest first)
    const entries = Array.from(this.cache.entries())
      .sort((a, b) => a[1].timestamp - b[1].timestamp);
    
    // Remove oldest entries
    const toRemove = entries.slice(0, this.cache.size - this.maxCacheSize);
    
    for (const [key, cached] of toRemove) {
      URL.revokeObjectURL(cached.blobUrl);
      this.cache.delete(key);
      await this.removeFromDB(key);
    }
    
    console.log(`Cleaned up ${toRemove.length} old cached images`);
  }

  // Clear all cache
  async clearCache() {
    this.cache.forEach(cached => {
      URL.revokeObjectURL(cached.blobUrl);
    });
    this.cache.clear();
    this.downloading.clear();
    
    // Clear IndexedDB
    if (this.db) {
      try {
        const transaction = this.db.transaction([this.storeName], 'readwrite');
        const store = transaction.objectStore(this.storeName);
        await new Promise((resolve, reject) => {
          const request = store.clear();
          request.onsuccess = () => resolve();
          request.onerror = () => reject(request.error);
        });
      } catch (error) {
        console.error('Failed to clear IndexedDB cache:', error);
      }
    }
    
    console.log('Image cache cleared');
  }

  // Get cache stats
  getCacheStats() {
    const totalSize = Array.from(this.cache.values())
      .reduce((sum, cached) => sum + (cached.size || 0), 0);
    
    return {
      count: this.cache.size,
      totalSize: totalSize,
      maxSize: this.maxCacheSize
    };
  }
}

// Create global instance
const imageCache = new ImageCache();

export default imageCache;