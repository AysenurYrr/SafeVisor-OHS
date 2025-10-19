"""
File validation utilities for secure file uploads
"""
import os
import imghdr
from typing import Optional
from fastapi import HTTPException, UploadFile
from app.core.config import settings


def validate_image_file(file: UploadFile, max_size: Optional[int] = None) -> None:
    """
    Validate that an uploaded file is a safe image file.
    
    Args:
        file: The uploaded file to validate
        max_size: Maximum file size in bytes (defaults to settings.MAX_FILE_SIZE)
        
    Raises:
        HTTPException: If file validation fails
    """
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Check filename
    if not file.filename:
        raise HTTPException(status_code=400, detail="File has no filename")
    
    # Check file extension
    ext = os.path.splitext(file.filename)[1].lower()
    allowed_extensions = settings.ALLOWED_UPLOAD_EXTENSIONS
    
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # Check file size
    max_bytes = max_size or settings.MAX_FILE_SIZE
    
    # Read file content for validation
    file_content = file.file.read()
    file_size = len(file_content)
    
    if file_size == 0:
        raise HTTPException(status_code=400, detail="File is empty")
    
    if file_size > max_bytes:
        max_mb = max_bytes / (1024 * 1024)
        raise HTTPException(
            status_code=400, 
            detail=f"File too large. Maximum size: {max_mb:.1f}MB"
        )
    
    # Validate actual file type by content (magic bytes)
    # Reset file position after reading
    file.file.seek(0)
    
    # Use imghdr to detect image type
    image_type = imghdr.what(None, h=file_content)
    
    if not image_type:
        raise HTTPException(
            status_code=400, 
            detail="File is not a valid image"
        )
    
    # Map imghdr types to extensions
    valid_types = {
        'jpeg': ['.jpg', '.jpeg'],
        'png': ['.png'],
        'gif': ['.gif'],
        'bmp': ['.bmp'],
    }
    
    if image_type not in valid_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported image type: {image_type}"
        )
    
    if ext not in valid_types[image_type]:
        raise HTTPException(
            status_code=400, 
            detail=f"File extension {ext} does not match content type {image_type}"
        )
    
    # Reset file position for actual use
    file.file.seek(0)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to prevent path traversal attacks.
    
    Args:
        filename: The filename to sanitize
        
    Returns:
        A safe filename
    """
    # Remove any directory components
    filename = os.path.basename(filename)
    
    # Remove any potentially dangerous characters
    # Keep only alphanumeric, dots, hyphens, and underscores
    safe_chars = []
    for char in filename:
        if char.isalnum() or char in '.-_':
            safe_chars.append(char)
        else:
            safe_chars.append('_')
    
    return ''.join(safe_chars)
