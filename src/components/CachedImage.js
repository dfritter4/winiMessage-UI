import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import imageCache from '../utils/imageCache';
import heic2any from 'heic2any';
import ImageModal from './ImageModal';

const ImageContainer = styled.div`
  position: relative;
  display: inline-block;
`;

const Image = styled.img`
  max-width: 300px;
  max-height: 200px;
  border-radius: 8px;
  cursor: pointer;
  display: block;
`;

const LoadingPlaceholder = styled.div`
  width: 200px;
  height: 150px;
  background-color: #f0f0f0;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  font-size: 12px;
`;

const ErrorPlaceholder = styled.div`
  width: 200px;
  height: 100px;
  background-color: #f8f8f8;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 12px;
  text-align: center;
  padding: 8px;
`;

const HeicPlaceholder = styled.div`
  width: 200px;
  height: 150px;
  background-color: #e3f2fd;
  border: 2px dashed #2196f3;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #1976d2;
  font-size: 12px;
  text-align: center;
  padding: 8px;
  cursor: pointer;
  
  &:hover {
    background-color: #bbdefb;
  }
`;

const FileIcon = styled.div`
  font-size: 24px;
  margin-bottom: 8px;
`;

function CachedImage({ src, alt, onLoad, onError, ...props }) {
  const [imageUrl, setImageUrl] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [isHeic, setIsHeic] = useState(false);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    if (!src) {
      setError(true);
      setLoading(false);
      return;
    }

    // Check if this is a HEIC file
    const isHeicFile = /\.(heic|heif)$/i.test(src);
    setIsHeic(isHeicFile);
    
    if (isHeicFile) {
      loadHeicImage(src);
    } else {
      loadImage(src);
    }
  }, [src]);

  const loadImage = async (url) => {
    try {
      setLoading(true);
      setError(false);
      
      // Check if already in cache
      if (imageCache.isInCache(url)) {
        const cachedUrl = imageCache.getCachedUrl(url);
        setImageUrl(cachedUrl);
        setLoading(false);
        if (onLoad) onLoad();
        return;
      }
      
      // Download and cache the image
      const blobUrl = await imageCache.cacheImage(url);
      setImageUrl(blobUrl);
      setLoading(false);
      if (onLoad) onLoad();
      
    } catch (err) {
      console.error('Failed to load cached image:', err);
      setError(true);
      setLoading(false);
      if (onError) onError(err);
    }
  };

  const loadHeicImage = async (url) => {
    try {
      setLoading(true);
      setError(false);
      
      // Check cache first (with .jpg suffix to distinguish from original HEIC)
      const cacheKey = url + '.converted.jpg';
      if (imageCache.isInCache(cacheKey)) {
        const cachedUrl = imageCache.getCachedUrl(cacheKey);
        setImageUrl(cachedUrl);
        setLoading(false);
        if (onLoad) onLoad();
        return;
      }
      
      console.log('Converting HEIC image:', url);
      
      // Fetch the HEIC file
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Failed to fetch HEIC: ${response.status}`);
      }
      
      const heicBlob = await response.blob();
      
      // Convert HEIC to JPEG
      const convertedBlob = await heic2any({
        blob: heicBlob,
        toType: 'image/jpeg',
        quality: 0.8
      });
      
      // Create blob URL for converted image
      const blobUrl = URL.createObjectURL(convertedBlob);
      const timestamp = Date.now();
      
      // Cache the converted image in memory
      imageCache.cache.set(cacheKey, {
        blobUrl: blobUrl,
        originalUrl: url,
        timestamp: timestamp,
        size: convertedBlob.size
      });
      
      // Save to IndexedDB for persistence
      await imageCache.saveToDB(cacheKey, convertedBlob, timestamp);
      
      setImageUrl(blobUrl);
      setLoading(false);
      if (onLoad) onLoad();
      
      console.log('HEIC conversion successful');
      
    } catch (err) {
      console.error('Failed to convert HEIC image:', err);
      setError(true);
      setLoading(false);
      if (onError) onError(err);
    }
  };

  const handleImageClick = () => {
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
  };

  const handleErrorClick = () => {
    // Try to open original URL externally as fallback
    if (window.electronAPI) {
      window.electronAPI.openExternal(src);
    } else {
      window.open(src, '_blank', 'noopener,noreferrer');
    }
  };


  if (loading) {
    return (
      <LoadingPlaceholder>
        Loading image...
      </LoadingPlaceholder>
    );
  }

  if (error || !imageUrl) {
    return (
      <ErrorPlaceholder onClick={handleErrorClick}>
        <div>Failed to load image</div>
        <div style={{ fontSize: '10px', marginTop: '4px' }}>
          Click to open externally
        </div>
      </ErrorPlaceholder>
    );
  }

  return (
    <>
      <ImageContainer>
        <Image
          src={imageUrl}
          alt={alt}
          onClick={handleImageClick}
          {...props}
        />
      </ImageContainer>
      
      {showModal && (
        <ImageModal
          imageUrl={imageUrl}
          alt={alt}
          onClose={handleCloseModal}
        />
      )}
    </>
  );
}

export default CachedImage;