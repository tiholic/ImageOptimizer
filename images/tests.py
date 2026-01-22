from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from images.models import Image
from storage.models import StorageProvider
from cryptography.fernet import Fernet
from PIL import Image as PILImage
from io import BytesIO


class ImageTestCase(TestCase):
    """Test cases for Image model and API"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Generate encryption key
        from django.conf import settings
        settings.STORAGE_ENCRYPTION_KEY = Fernet.generate_key().decode()
        
        # Create a test storage provider (but we won't actually upload to it)
        self.provider = StorageProvider.objects.create(
            user=self.user,
            name='Test Provider',
            provider_type='s3',
            is_default=True,
            config={'bucket': 'test-bucket', 'region': 'us-east-1'}
        )
        self.provider.set_credentials({
            'access_key_id': 'test_key',
            'secret_access_key': 'test_secret'
        })
        self.provider.save()
    
    def create_test_image(self):
        """Create a test image file"""
        # Create a simple test image
        img = PILImage.new('RGB', (100, 100), color='red')
        img_io = BytesIO()
        img.save(img_io, format='JPEG')
        img_io.seek(0)
        
        return SimpleUploadedFile(
            "test_image.jpg",
            img_io.read(),
            content_type="image/jpeg"
        )
    
    def test_image_model_creation(self):
        """Test creating an Image model instance"""
        image = Image.objects.create(
            user=self.user,
            storage_provider=self.provider,
            original_filename='test.jpg',
            file_size=1024,
            content_type='image/jpeg',
            storage_path='test/path/test.jpg',
            width=100,
            height=100
        )
        
        self.assertEqual(image.user, self.user)
        self.assertEqual(image.original_filename, 'test.jpg')
        self.assertEqual(image.file_size, 1024)
    
    def test_image_size_mb_property(self):
        """Test size_mb property calculation"""
        image = Image.objects.create(
            user=self.user,
            storage_provider=self.provider,
            original_filename='test.jpg',
            file_size=5242880,  # 5 MB
            content_type='image/jpeg',
            storage_path='test/path/test.jpg'
        )
        
        self.assertEqual(image.size_mb, 5.0)
    
    def test_list_images_requires_auth(self):
        """Test that image endpoints require authentication"""
        client = APIClient()
        response = client.get('/api/images/')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
    
    def test_list_images(self):
        """Test listing images"""
        # Create a test image
        Image.objects.create(
            user=self.user,
            storage_provider=self.provider,
            original_filename='test.jpg',
            file_size=1024,
            content_type='image/jpeg',
            storage_path='test/path/test.jpg'
        )
        
        response = self.client.get('/api/images/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
    
    def test_get_image_stats(self):
        """Test getting image statistics"""
        # Create test images
        Image.objects.create(
            user=self.user,
            storage_provider=self.provider,
            original_filename='test1.jpg',
            file_size=5242880,  # 5 MB
            content_type='image/jpeg',
            storage_path='test/path/test1.jpg',
            is_optimized=True,
            optimized_size=2621440  # 2.5 MB
        )
        
        Image.objects.create(
            user=self.user,
            storage_provider=self.provider,
            original_filename='test2.jpg',
            file_size=10485760,  # 10 MB
            content_type='image/jpeg',
            storage_path='test/path/test2.jpg',
            is_optimized=False
        )
        
        response = self.client.get('/api/images/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data
        self.assertEqual(data['total_images'], 2)
        self.assertEqual(data['total_size_mb'], 15.0)
        self.assertEqual(data['optimized_images'], 1)
        self.assertEqual(data['total_saved_mb'], 2.5)
    
    def test_user_can_only_see_own_images(self):
        """Test that users can only see their own images"""
        # Create another user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        # Create provider for other user
        other_provider = StorageProvider.objects.create(
            user=other_user,
            name='Other Provider',
            provider_type='s3',
            is_default=True,
            config={'bucket': 'other-bucket', 'region': 'us-east-1'}
        )
        other_provider.set_credentials({
            'access_key_id': 'other_key',
            'secret_access_key': 'other_secret'
        })
        other_provider.save()
        
        # Create image for current user
        Image.objects.create(
            user=self.user,
            storage_provider=self.provider,
            original_filename='my_image.jpg',
            file_size=1024,
            content_type='image/jpeg',
            storage_path='test/path/my_image.jpg'
        )
        
        # Create image for other user
        Image.objects.create(
            user=other_user,
            storage_provider=other_provider,
            original_filename='other_image.jpg',
            file_size=1024,
            content_type='image/jpeg',
            storage_path='test/path/other_image.jpg'
        )
        
        # Current user should only see their own image
        response = self.client.get('/api/images/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['original_filename'], 'my_image.jpg')
