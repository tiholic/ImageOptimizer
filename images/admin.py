from django.contrib import admin
from .models import Image


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['original_filename', 'user', 'storage_provider', 'file_size', 'is_optimized', 'created_at']
    list_filter = ['is_optimized', 'storage_provider', 'created_at']
    search_fields = ['original_filename', 'user__email', 'user__username', 'tags']
    readonly_fields = ['created_at', 'updated_at', 'size_mb', 'optimized_size_mb']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'storage_provider', 'original_filename', 'content_type')
        }),
        ('File Details', {
            'fields': ('file_size', 'size_mb', 'width', 'height', 'storage_path')
        }),
        ('Optimization', {
            'fields': ('is_optimized', 'optimized_size', 'optimized_size_mb', 'optimization_percentage')
        }),
        ('Metadata', {
            'fields': ('tags', 'metadata'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
