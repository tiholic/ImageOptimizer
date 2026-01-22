"""
Image processing utilities for optimization and metadata extraction
"""
from PIL import Image as PILImage
from io import BytesIO
import os


def optimize_image(image_file, quality=85, max_width=None, max_height=None):
    """
    Optimize an image by reducing quality and/or resizing
    
    Args:
        image_file: File-like object containing the image
        quality: JPEG quality (1-100)
        max_width: Maximum width to resize to
        max_height: Maximum height to resize to
    
    Returns:
        tuple: (optimized_file_obj, metadata_dict)
    """
    # Open image
    img = PILImage.open(image_file)
    
    # Get original dimensions
    original_width, original_height = img.size
    original_format = img.format
    
    # Convert RGBA to RGB for JPEG
    if img.mode in ('RGBA', 'LA', 'P'):
        background = PILImage.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
        img = background
    
    # Resize if needed
    if max_width or max_height:
        img.thumbnail((max_width or original_width, max_height or original_height), PILImage.Resampling.LANCZOS)
    
    # Get new dimensions
    new_width, new_height = img.size
    
    # Save to BytesIO
    output = BytesIO()
    
    # Determine format
    save_format = 'JPEG' if original_format in ['JPEG', 'JPG'] else original_format
    
    # Save with optimization
    save_kwargs = {'optimize': True}
    if save_format == 'JPEG':
        save_kwargs['quality'] = quality
    
    img.save(output, format=save_format, **save_kwargs)
    output.seek(0)
    
    # Extract metadata
    metadata = {
        'original_width': original_width,
        'original_height': original_height,
        'optimized_width': new_width,
        'optimized_height': new_height,
        'format': save_format,
        'mode': img.mode,
    }
    
    # Try to extract EXIF data
    try:
        exif = img._getexif()
        if exif:
            metadata['exif'] = {k: str(v) for k, v in exif.items() if isinstance(v, (str, int, float))}
    except:
        pass
    
    return output, metadata


def get_image_info(image_file):
    """
    Extract basic information from an image
    
    Args:
        image_file: File-like object containing the image
    
    Returns:
        dict: Image information
    """
    img = PILImage.open(image_file)
    
    info = {
        'width': img.width,
        'height': img.height,
        'format': img.format,
        'mode': img.mode,
    }
    
    # Reset file pointer
    image_file.seek(0)
    
    return info


def generate_storage_path(user_id, filename):
    """
    Generate a unique storage path for an image
    
    Args:
        user_id: User ID
        filename: Original filename
    
    Returns:
        str: Storage path
    """
    from datetime import datetime
    import uuid
    
    # Get file extension
    _, ext = os.path.splitext(filename)
    
    # Generate unique filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = uuid.uuid4().hex[:8]
    new_filename = f"{timestamp}_{unique_id}{ext}"
    
    # Create path: user_id/YYYY/MM/filename
    now = datetime.now()
    path = f"user_{user_id}/{now.year}/{now.month:02d}/{new_filename}"
    
    return path
