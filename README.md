# ImageOptimizer

Bring your own storage, use this interface to access optimised version of large images quickly.

## Overview

ImageOptimizer is a Django + Django REST Framework based project that helps you upload, optimize, and manage images (like wedding shoot images, vacation images, or general photos) across different storage locations while maintaining accessibility and cost effectiveness.

## Features

- **Google OAuth Authentication**: Secure login using Google accounts (with support for more providers in the future)
- **Multiple Storage Providers**: Configure and use different storage backends
  - AWS S3
  - Azure Blob Storage
  - Google Cloud Storage
  - SFTP
- **Image Upload & Optimization**: Upload images with automatic optimization to reduce file sizes
- **REST API**: Full-featured API for programmatic access
- **Django Admin**: Manage users, storage providers, and images through Django admin interface

## Requirements

- Python 3.12+
- Django 6.0+
- PostgreSQL, MySQL, or SQLite (SQLite for development)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/tiholic/ImageOptimizer.git
cd ImageOptimizer
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy `.env.example` to `.env` and update the values:

```bash
cp .env.example .env
```

Edit `.env` and set:

- `SECRET_KEY`: Django secret key (generate using `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- `GOOGLE_CLIENT_ID`: Your Google OAuth client ID
- `GOOGLE_CLIENT_SECRET`: Your Google OAuth client secret
- `STORAGE_ENCRYPTION_KEY`: Encryption key for storage credentials (generate using `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`)

### 4. Run migrations

```bash
python manage.py migrate
```

### 5. Create a superuser (optional, for admin access)

```bash
python manage.py createsuperuser
```

### 6. Run the development server

```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`

## Google OAuth Setup

To enable Google OAuth authentication:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API
4. Create OAuth 2.0 credentials:
   - Application type: Web application
   - Authorized redirect URIs: `http://localhost:8000/accounts/google/login/callback/`
5. Copy the Client ID and Client Secret to your `.env` file

## API Endpoints

### Authentication

- `POST /api/auth/token/` - Get authentication token

### Storage Providers

- `GET /api/storage/providers/` - List all storage providers
- `POST /api/storage/providers/` - Create a new storage provider
- `GET /api/storage/providers/{id}/` - Get storage provider details
- `PUT /api/storage/providers/{id}/` - Update storage provider
- `DELETE /api/storage/providers/{id}/` - Delete storage provider
- `POST /api/storage/providers/{id}/set_default/` - Set as default provider
- `POST /api/storage/providers/{id}/test_connection/` - Test storage connection

### Images

- `GET /api/images/` - List all images
- `POST /api/images/` - Upload a new image
- `GET /api/images/{id}/` - Get image details
- `PUT /api/images/{id}/` - Update image metadata
- `DELETE /api/images/{id}/` - Delete an image
- `GET /api/images/stats/` - Get image statistics

## Usage Examples

### 1. Configure a Storage Provider

```bash
curl -X POST http://localhost:8000/api/storage/providers/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My S3 Bucket",
    "provider_type": "s3",
    "is_default": true,
    "config": {
      "bucket": "my-bucket-name",
      "region": "us-east-1"
    },
    "credentials": {
      "access_key_id": "YOUR_ACCESS_KEY",
      "secret_access_key": "YOUR_SECRET_KEY"
    }
  }'
```

### 2. Upload an Image

```bash
curl -X POST http://localhost:8000/api/images/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -F "image=@/path/to/image.jpg" \
  -F "optimize=true" \
  -F "tags=vacation,beach"
```

### 3. Get Image Statistics

```bash
curl http://localhost:8000/api/images/stats/ \
  -H "Authorization: Token YOUR_TOKEN"
```

## Storage Provider Configuration

### AWS S3

```json
{
  "name": "AWS S3 Storage",
  "provider_type": "s3",
  "config": {
    "bucket": "my-bucket",
    "region": "us-east-1"
  },
  "credentials": {
    "access_key_id": "AKIAIOSFODNN7EXAMPLE",
    "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
  }
}
```

### Azure Blob Storage

```json
{
  "name": "Azure Blob",
  "provider_type": "azure",
  "config": {
    "container": "my-container"
  },
  "credentials": {
    "account_name": "myaccount",
    "account_key": "YOUR_ACCOUNT_KEY"
  }
}
```

### Google Cloud Storage

```json
{
  "name": "Google Cloud Storage",
  "provider_type": "gcs",
  "config": {
    "bucket": "my-bucket"
  },
  "credentials": {
    "credentials_json": "{...JSON_KEY_FILE_CONTENTS...}"
  }
}
```

### SFTP

```json
{
  "name": "SFTP Server",
  "provider_type": "sftp",
  "config": {
    "remote_path": "/home/user/images"
  },
  "credentials": {
    "host": "sftp.example.com",
    "username": "user",
    "password": "password",
    "port": 22
  }
}
```

## Security

- Storage credentials are encrypted using Fernet symmetric encryption
- Google OAuth is required for authentication
- API endpoints require authentication via token or session
- HTTPS should be used in production

## Development

### Running Tests

```bash
python manage.py test
```

### Code Style

Follow PEP 8 guidelines for Python code.

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### PR Previews

Pull requests are automatically deployed to preview environments on Render.com. When you open a PR, a bot will comment with a preview URL where you can test your changes. See [PR_PREVIEW_SETUP.md](PR_PREVIEW_SETUP.md) for setup instructions. 
