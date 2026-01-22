from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from storage.models import StorageProvider
from cryptography.fernet import Fernet


class StorageProviderTestCase(TestCase):
    """Test cases for StorageProvider model and API"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Generate a test encryption key
        from django.conf import settings
        settings.STORAGE_ENCRYPTION_KEY = Fernet.generate_key().decode()
    
    def test_create_storage_provider(self):
        """Test creating a storage provider"""
        data = {
            'name': 'Test S3 Provider',
            'provider_type': 's3',
            'is_default': True,
            'config': {
                'bucket': 'test-bucket',
                'region': 'us-east-1'
            },
            'credentials': {
                'access_key_id': 'test_key',
                'secret_access_key': 'test_secret'
            }
        }
        
        response = self.client.post('/api/storage/providers/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Test S3 Provider')
        self.assertEqual(response.data['provider_type'], 's3')
        
        # Verify credentials were encrypted
        provider = StorageProvider.objects.get(id=response.data['id'])
        self.assertIsNotNone(provider.encrypted_credentials)
        
        # Verify credentials can be decrypted
        decrypted = provider.get_credentials()
        self.assertEqual(decrypted['access_key_id'], 'test_key')
    
    def test_list_storage_providers(self):
        """Test listing storage providers"""
        # Create a provider
        provider = StorageProvider.objects.create(
            user=self.user,
            name='Test Provider',
            provider_type='s3',
            config={'bucket': 'test'}
        )
        provider.set_credentials({'key': 'value'})
        provider.save()
        
        response = self.client.get('/api/storage/providers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
    
    def test_only_one_default_provider(self):
        """Test that only one provider can be default"""
        from django.conf import settings
        settings.STORAGE_ENCRYPTION_KEY = Fernet.generate_key().decode()
        
        # Create first provider as default
        provider1 = StorageProvider.objects.create(
            user=self.user,
            name='Provider 1',
            provider_type='s3',
            is_default=True,
            config={'bucket': 'test1'}
        )
        provider1.set_credentials({'key': 'value1'})
        provider1.save()
        
        # Create second provider as default
        provider2 = StorageProvider.objects.create(
            user=self.user,
            name='Provider 2',
            provider_type='azure',
            is_default=True,
            config={'container': 'test2'}
        )
        provider2.set_credentials({'key': 'value2'})
        provider2.save()
        
        # Refresh first provider from DB
        provider1.refresh_from_db()
        
        # First provider should no longer be default
        self.assertFalse(provider1.is_default)
        self.assertTrue(provider2.is_default)
    
    def test_storage_provider_requires_auth(self):
        """Test that storage provider endpoints require authentication"""
        client = APIClient()
        response = client.get('/api/storage/providers/')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
