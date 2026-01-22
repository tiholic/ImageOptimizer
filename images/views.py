from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import transaction
import logging
from .models import Image
from .serializers import ImageSerializer, ImageUploadSerializer
from storage.models import StorageProvider
from storage.backends import get_storage_backend
from .utils import optimize_image, get_image_info, generate_storage_path

logger = logging.getLogger(__name__)


class ImageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing images
    
    list: Get all images for the authenticated user
    create: Upload a new image
    retrieve: Get details of a specific image
    update: Update image metadata (tags, etc.)
    partial_update: Partially update image metadata
    destroy: Delete an image
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        return Image.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ImageUploadSerializer
        return ImageSerializer
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Upload and process an image"""
        serializer = ImageUploadSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        image_file = serializer.validated_data['image']
        optimize = serializer.validated_data.get('optimize', True)
        tags = serializer.validated_data.get('tags', [])
        
        # Get storage provider
        storage_provider = serializer.validated_data.get('storage_provider')
        if not storage_provider:
            # Use default storage provider
            storage_provider = StorageProvider.objects.filter(
                user=request.user,
                is_default=True,
                is_active=True
            ).first()
            
            if not storage_provider:
                return Response({
                    'error': 'No storage provider configured. Please configure a storage provider first.'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get image info
        image_info = get_image_info(image_file)
        
        # Get original file size
        image_file.seek(0, 2)  # Seek to end
        original_size = image_file.tell()
        image_file.seek(0)  # Reset
        
        # Optimize image if requested
        optimized_size = None
        optimization_percentage = None
        metadata = {}
        
        if optimize:
            optimized_file, opt_metadata = optimize_image(
                image_file,
                quality=85,
                max_width=2048,
                max_height=2048
            )
            metadata = opt_metadata
            
            # Get optimized size
            optimized_file.seek(0, 2)
            optimized_size = optimized_file.tell()
            optimized_file.seek(0)
            
            # Calculate optimization percentage
            optimization_percentage = ((original_size - optimized_size) / original_size) * 100
            
            # Use optimized file for upload
            upload_file = optimized_file
            is_optimized = True
        else:
            upload_file = image_file
            is_optimized = False
        
        # Generate storage path
        storage_path = generate_storage_path(request.user.id, image_file.name)
        
        # Upload to storage
        try:
            backend = get_storage_backend(storage_provider)
            backend.upload(upload_file, storage_path)
        except Exception as e:
            return Response({
                'error': f'Failed to upload to storage: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Create Image record
        image = Image.objects.create(
            user=request.user,
            storage_provider=storage_provider,
            original_filename=image_file.name,
            file_size=original_size,
            content_type=image_file.content_type,
            storage_path=storage_path,
            width=image_info['width'],
            height=image_info['height'],
            is_optimized=is_optimized,
            optimized_size=optimized_size if is_optimized else None,
            optimization_percentage=optimization_percentage if is_optimized else None,
            tags=tags,
            metadata=metadata
        )
        
        # Return serialized image
        image_serializer = ImageSerializer(image)
        return Response(image_serializer.data, status=status.HTTP_201_CREATED)
    
    def destroy(self, request, *args, **kwargs):
        """Delete an image and remove from storage"""
        image = self.get_object()
        
        # Try to delete from storage
        try:
            backend = get_storage_backend(image.storage_provider)
            backend.delete(image.storage_path)
        except Exception as e:
            # Log error but continue with database deletion
            logger.error(f"Error deleting image from storage: {e}")
        
        # Delete from database
        image.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get statistics about user's images"""
        images = self.get_queryset()
        
        total_images = images.count()
        total_size = sum(img.file_size for img in images)
        optimized_images = images.filter(is_optimized=True).count()
        total_saved = sum(
            (img.file_size - img.optimized_size) 
            for img in images.filter(is_optimized=True) 
            if img.optimized_size
        )
        
        return Response({
            'total_images': total_images,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'optimized_images': optimized_images,
            'total_saved_bytes': total_saved,
            'total_saved_mb': round(total_saved / (1024 * 1024), 2),
        })
