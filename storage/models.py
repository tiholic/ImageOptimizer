from django.db import models
from django.contrib.auth.models import User
from cryptography.fernet import Fernet
from django.conf import settings
import json


class StorageProvider(models.Model):
    """Model to store different storage provider configurations"""
    
    PROVIDER_CHOICES = [
        ('s3', 'AWS S3'),
        ('azure', 'Azure Blob Storage'),
        ('gcs', 'Google Cloud Storage'),
        ('sftp', 'SFTP'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='storage_providers')
    name = models.CharField(max_length=255, help_text="Friendly name for this storage provider")
    provider_type = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Encrypted credentials stored as JSON
    encrypted_credentials = models.TextField(blank=True, help_text="Encrypted JSON containing provider-specific credentials")
    
    # Provider-specific configuration (non-sensitive)
    config = models.JSONField(default=dict, blank=True, help_text="Provider-specific configuration like region, bucket name, etc.")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_default', '-created_at']
        unique_together = [['user', 'name']]
    
    def __str__(self):
        return f"{self.name} ({self.get_provider_type_display()})"
    
    def set_credentials(self, credentials_dict):
        """Encrypt and store credentials"""
        if not settings.STORAGE_ENCRYPTION_KEY:
            raise ValueError("STORAGE_ENCRYPTION_KEY not configured")
        
        cipher = Fernet(settings.STORAGE_ENCRYPTION_KEY.encode())
        credentials_json = json.dumps(credentials_dict)
        self.encrypted_credentials = cipher.encrypt(credentials_json.encode()).decode()
    
    def get_credentials(self):
        """Decrypt and return credentials"""
        if not settings.STORAGE_ENCRYPTION_KEY:
            raise ValueError("STORAGE_ENCRYPTION_KEY not configured")
        
        cipher = Fernet(settings.STORAGE_ENCRYPTION_KEY.encode())
        decrypted = cipher.decrypt(self.encrypted_credentials.encode())
        return json.loads(decrypted.decode())
    
    def save(self, *args, **kwargs):
        # Ensure only one default provider per user
        if self.is_default:
            StorageProvider.objects.filter(
                user=self.user,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
