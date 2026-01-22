from django.db import models
from django.contrib.auth.models import User
from storage.models import StorageProvider


class Image(models.Model):
    """Model to track uploaded images"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='images')
    storage_provider = models.ForeignKey(StorageProvider, on_delete=models.PROTECT, related_name='images')
    
    original_filename = models.CharField(max_length=255)
    file_size = models.BigIntegerField(help_text="File size in bytes")
    content_type = models.CharField(max_length=100)
    
    # Storage path/key where the image is stored
    storage_path = models.CharField(max_length=512)
    
    # Image metadata
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    
    # Optimization metadata
    is_optimized = models.BooleanField(default=False)
    optimized_size = models.BigIntegerField(null=True, blank=True, help_text="Optimized file size in bytes")
    optimization_percentage = models.FloatField(null=True, blank=True, help_text="Percentage reduction in size")
    
    # Tags for categorization
    tags = models.JSONField(default=list, blank=True, help_text="List of tags for categorization")
    
    # Additional metadata
    metadata = models.JSONField(default=dict, blank=True, help_text="Additional image metadata (EXIF, etc.)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['storage_provider']),
        ]
    
    def __str__(self):
        return f"{self.original_filename} ({self.user.email})"
    
    @property
    def size_mb(self):
        """Return file size in MB"""
        return round(self.file_size / (1024 * 1024), 2)
    
    @property
    def optimized_size_mb(self):
        """Return optimized file size in MB"""
        if self.optimized_size:
            return round(self.optimized_size / (1024 * 1024), 2)
        return None
