#!/usr/bin/env python3
"""
Example script demonstrating how to use the ImageOptimizer API
"""
import requests
import json
from pathlib import Path

# API Configuration
BASE_URL = "http://localhost:8000/api"
USERNAME = "user@example.com"  # Replace with your email
PASSWORD = "password"  # Replace with your password

class ImageOptimizerClient:
    def __init__(self, base_url, username=None, password=None, token=None):
        self.base_url = base_url
        self.token = token
        
        if not token and username and password:
            self.token = self.get_token(username, password)
    
    def get_token(self, username, password):
        """Get authentication token"""
        response = requests.post(
            f"{self.base_url}/auth/token/",
            json={"username": username, "password": password}
        )
        response.raise_for_status()
        return response.json()["token"]
    
    def _headers(self):
        """Get headers with authentication"""
        return {"Authorization": f"Token {self.token}"}
    
    def create_storage_provider(self, name, provider_type, config, credentials, is_default=True):
        """Create a new storage provider"""
        data = {
            "name": name,
            "provider_type": provider_type,
            "is_default": is_default,
            "is_active": True,
            "config": config,
            "credentials": credentials
        }
        
        response = requests.post(
            f"{self.base_url}/storage/providers/",
            headers=self._headers(),
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def list_storage_providers(self):
        """List all storage providers"""
        response = requests.get(
            f"{self.base_url}/storage/providers/",
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()
    
    def test_storage_connection(self, provider_id):
        """Test connection to a storage provider"""
        response = requests.post(
            f"{self.base_url}/storage/providers/{provider_id}/test_connection/",
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()
    
    def upload_image(self, image_path, tags=None, optimize=True, storage_provider_id=None):
        """Upload an image"""
        files = {"image": open(image_path, "rb")}
        data = {"optimize": optimize}
        
        if tags:
            data["tags"] = tags
        
        if storage_provider_id:
            data["storage_provider"] = storage_provider_id
        
        response = requests.post(
            f"{self.base_url}/images/",
            headers=self._headers(),
            files=files,
            data=data
        )
        response.raise_for_status()
        return response.json()
    
    def list_images(self, page=1):
        """List all images"""
        response = requests.get(
            f"{self.base_url}/images/",
            headers=self._headers(),
            params={"page": page}
        )
        response.raise_for_status()
        return response.json()
    
    def get_image(self, image_id):
        """Get image details"""
        response = requests.get(
            f"{self.base_url}/images/{image_id}/",
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()
    
    def update_image(self, image_id, tags):
        """Update image metadata"""
        response = requests.patch(
            f"{self.base_url}/images/{image_id}/",
            headers=self._headers(),
            json={"tags": tags}
        )
        response.raise_for_status()
        return response.json()
    
    def delete_image(self, image_id):
        """Delete an image"""
        response = requests.delete(
            f"{self.base_url}/images/{image_id}/",
            headers=self._headers()
        )
        response.raise_for_status()
    
    def get_stats(self):
        """Get image statistics"""
        response = requests.get(
            f"{self.base_url}/images/stats/",
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()


def main():
    """Example usage"""
    print("ImageOptimizer API Example\n" + "="*50)
    
    # Initialize client (you need to have a user account first)
    # For this example, you'll need to create a user via Google OAuth first
    # and then use the token directly
    
    # Option 1: Use token directly
    # client = ImageOptimizerClient(BASE_URL, token="your-token-here")
    
    # Option 2: Get token with username/password (if you set up a regular user)
    # client = ImageOptimizerClient(BASE_URL, username=USERNAME, password=PASSWORD)
    
    print("\n1. Example: Create AWS S3 Storage Provider")
    print("-" * 50)
    example_s3_provider = {
        "name": "My S3 Bucket",
        "provider_type": "s3",
        "config": {
            "bucket": "my-images-bucket",
            "region": "us-east-1"
        },
        "credentials": {
            "access_key_id": "AKIAIOSFODNN7EXAMPLE",
            "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        }
    }
    print(json.dumps(example_s3_provider, indent=2))
    
    print("\n2. Example: Upload Image")
    print("-" * 50)
    print("client.upload_image('vacation.jpg', tags=['vacation', 'beach'], optimize=True)")
    
    print("\n3. Example: Get Image Statistics")
    print("-" * 50)
    example_stats = {
        "total_images": 42,
        "total_size_bytes": 220200960,
        "total_size_mb": 210.0,
        "optimized_images": 35,
        "total_saved_bytes": 104857600,
        "total_saved_mb": 100.0
    }
    print(json.dumps(example_stats, indent=2))
    
    print("\n" + "="*50)
    print("\nTo use this script:")
    print("1. First, login via Google OAuth at http://localhost:8000/accounts/google/login/")
    print("2. Get your API token from the admin interface or create one")
    print("3. Uncomment and update the client initialization code above")
    print("4. Run the script to interact with the API")


if __name__ == "__main__":
    main()
