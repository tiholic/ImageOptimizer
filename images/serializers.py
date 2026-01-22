from rest_framework import serializers
from .models import Image
from storage.serializers import StorageProviderListSerializer


class ImageSerializer(serializers.ModelSerializer):
    """Serializer for Image model"""
    
    storage_provider_details = StorageProviderListSerializer(source='storage_provider', read_only=True)
    size_mb = serializers.FloatField(read_only=True)
    optimized_size_mb = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Image
        fields = [
            'id', 'original_filename', 'file_size', 'size_mb',
            'content_type', 'storage_path', 'width', 'height',
            'is_optimized', 'optimized_size', 'optimized_size_mb',
            'optimization_percentage', 'tags', 'metadata',
            'storage_provider', 'storage_provider_details',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'file_size', 'content_type', 'storage_path',
            'width', 'height', 'is_optimized', 'optimized_size',
            'optimization_percentage', 'created_at', 'updated_at'
        ]


class ImageUploadSerializer(serializers.Serializer):
    """Serializer for image upload"""
    
    image = serializers.ImageField()
    storage_provider = serializers.IntegerField(required=False)
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        allow_empty=True
    )
    optimize = serializers.BooleanField(default=True)
    
    def validate_storage_provider(self, value):
        """Validate that storage provider exists and belongs to user"""
        from storage.models import StorageProvider
        
        user = self.context['request'].user
        try:
            provider = StorageProvider.objects.get(id=value, user=user, is_active=True)
            return provider
        except StorageProvider.DoesNotExist:
            raise serializers.ValidationError("Invalid storage provider")
    
    def validate_image(self, value):
        """Validate image file"""
        # Check file size (max 50MB)
        max_size = 50 * 1024 * 1024  # 50MB
        if value.size > max_size:
            raise serializers.ValidationError(f"Image size exceeds maximum allowed size of 50MB")
        
        # Check content type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
        if value.content_type not in allowed_types:
            raise serializers.ValidationError(f"Invalid image type. Allowed types: {', '.join(allowed_types)}")
        
        return value
