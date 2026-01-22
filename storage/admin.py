from django.contrib import admin
from .models import StorageProvider


@admin.register(StorageProvider)
class StorageProviderAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'provider_type', 'is_default', 'is_active', 'created_at']
    list_filter = ['provider_type', 'is_default', 'is_active']
    search_fields = ['name', 'user__email', 'user__username']
    readonly_fields = ['created_at', 'updated_at', 'encrypted_credentials']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'provider_type', 'is_default', 'is_active')
        }),
        ('Configuration', {
            'fields': ('config',)
        }),
        ('Credentials (Encrypted)', {
            'fields': ('encrypted_credentials',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
