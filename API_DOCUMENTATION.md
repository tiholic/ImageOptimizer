# ImageOptimizer API Documentation

## Base URL

```
http://localhost:8000/api
```

## Authentication

All API endpoints (except authentication endpoints) require authentication. There are two ways to authenticate:

### 1. Token Authentication (Recommended for API clients)

First, obtain a token:

```bash
POST /api/auth/token/
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "password"
}
```

Response:
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
}
```

Then use the token in subsequent requests:

```bash
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

### 2. Session Authentication (For web browsers)

Login via Google OAuth at `/accounts/google/login/`

## Endpoints

### Storage Providers

#### List Storage Providers

```bash
GET /api/storage/providers/
Authorization: Token YOUR_TOKEN
```

Response:
```json
[
  {
    "id": 1,
    "name": "My S3 Bucket",
    "provider_type": "s3",
    "provider_type_display": "AWS S3",
    "is_default": true,
    "is_active": true,
    "created_at": "2024-01-22T10:30:00Z"
  }
]
```

#### Create Storage Provider

```bash
POST /api/storage/providers/
Authorization: Token YOUR_TOKEN
Content-Type: application/json

{
  "name": "My S3 Bucket",
  "provider_type": "s3",
  "is_default": true,
  "is_active": true,
  "config": {
    "bucket": "my-bucket-name",
    "region": "us-east-1"
  },
  "credentials": {
    "access_key_id": "YOUR_ACCESS_KEY",
    "secret_access_key": "YOUR_SECRET_KEY"
  }
}
```

Response:
```json
{
  "id": 1,
  "name": "My S3 Bucket",
  "provider_type": "s3",
  "provider_type_display": "AWS S3",
  "is_default": true,
  "is_active": true,
  "config": {
    "bucket": "my-bucket-name",
    "region": "us-east-1"
  },
  "created_at": "2024-01-22T10:30:00Z",
  "updated_at": "2024-01-22T10:30:00Z"
}
```

**Note**: The `credentials` field is write-only and will not be returned in responses for security.

#### Get Storage Provider

```bash
GET /api/storage/providers/{id}/
Authorization: Token YOUR_TOKEN
```

#### Update Storage Provider

```bash
PUT /api/storage/providers/{id}/
Authorization: Token YOUR_TOKEN
Content-Type: application/json

{
  "name": "Updated S3 Bucket",
  "config": {
    "bucket": "new-bucket-name",
    "region": "us-west-2"
  }
}
```

#### Delete Storage Provider

```bash
DELETE /api/storage/providers/{id}/
Authorization: Token YOUR_TOKEN
```

#### Set as Default Provider

```bash
POST /api/storage/providers/{id}/set_default/
Authorization: Token YOUR_TOKEN
```

#### Test Connection

```bash
POST /api/storage/providers/{id}/test_connection/
Authorization: Token YOUR_TOKEN
```

Response (success):
```json
{
  "status": "success",
  "message": "Connection successful"
}
```

Response (error):
```json
{
  "status": "error",
  "message": "Connection failed: Invalid credentials"
}
```

### Images

#### List Images

```bash
GET /api/images/
Authorization: Token YOUR_TOKEN
```

Query parameters:
- `page`: Page number (default: 1)

Response:
```json
{
  "count": 42,
  "next": "http://localhost:8000/api/images/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "original_filename": "vacation.jpg",
      "file_size": 5242880,
      "size_mb": 5.0,
      "content_type": "image/jpeg",
      "storage_path": "user_1/2024/01/20240122_103000_abc123.jpg",
      "width": 1920,
      "height": 1080,
      "is_optimized": true,
      "optimized_size": 2621440,
      "optimized_size_mb": 2.5,
      "optimization_percentage": 50.0,
      "tags": ["vacation", "beach"],
      "metadata": {
        "format": "JPEG",
        "mode": "RGB"
      },
      "storage_provider": 1,
      "storage_provider_details": {
        "id": 1,
        "name": "My S3 Bucket",
        "provider_type": "s3",
        "provider_type_display": "AWS S3",
        "is_default": true,
        "is_active": true,
        "created_at": "2024-01-22T10:00:00Z"
      },
      "created_at": "2024-01-22T10:30:00Z",
      "updated_at": "2024-01-22T10:30:00Z"
    }
  ]
}
```

#### Upload Image

```bash
POST /api/images/
Authorization: Token YOUR_TOKEN
Content-Type: multipart/form-data

# Form fields:
# - image: Image file (required)
# - storage_provider: Storage provider ID (optional, uses default if not specified)
# - tags: Comma-separated tags (optional)
# - optimize: Boolean, default true (optional)
```

Example using curl:
```bash
curl -X POST http://localhost:8000/api/images/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -F "image=@/path/to/image.jpg" \
  -F "optimize=true" \
  -F "tags=vacation,beach"
```

Response:
```json
{
  "id": 1,
  "original_filename": "vacation.jpg",
  "file_size": 5242880,
  "size_mb": 5.0,
  "content_type": "image/jpeg",
  "storage_path": "user_1/2024/01/20240122_103000_abc123.jpg",
  "width": 1920,
  "height": 1080,
  "is_optimized": true,
  "optimized_size": 2621440,
  "optimized_size_mb": 2.5,
  "optimization_percentage": 50.0,
  "tags": ["vacation", "beach"],
  "metadata": {},
  "storage_provider": 1,
  "storage_provider_details": { ... },
  "created_at": "2024-01-22T10:30:00Z",
  "updated_at": "2024-01-22T10:30:00Z"
}
```

#### Get Image Details

```bash
GET /api/images/{id}/
Authorization: Token YOUR_TOKEN
```

#### Update Image

```bash
PATCH /api/images/{id}/
Authorization: Token YOUR_TOKEN
Content-Type: application/json

{
  "tags": ["vacation", "beach", "sunset"]
}
```

#### Delete Image

```bash
DELETE /api/images/{id}/
Authorization: Token YOUR_TOKEN
```

This will delete both the database record and the file from storage.

#### Get Image Statistics

```bash
GET /api/images/stats/
Authorization: Token YOUR_TOKEN
```

Response:
```json
{
  "total_images": 42,
  "total_size_bytes": 220200960,
  "total_size_mb": 210.0,
  "optimized_images": 35,
  "total_saved_bytes": 104857600,
  "total_saved_mb": 100.0
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "error": "Validation error message"
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error message"
}
```

## Storage Provider Configuration Examples

### AWS S3

```json
{
  "name": "AWS S3 Storage",
  "provider_type": "s3",
  "is_default": true,
  "config": {
    "bucket": "my-images-bucket",
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
  "name": "Azure Blob Storage",
  "provider_type": "azure",
  "is_default": true,
  "config": {
    "container": "images"
  },
  "credentials": {
    "account_name": "mystorageaccount",
    "account_key": "YOUR_ACCOUNT_KEY_HERE"
  }
}
```

### Google Cloud Storage

```json
{
  "name": "Google Cloud Storage",
  "provider_type": "gcs",
  "is_default": true,
  "config": {
    "bucket": "my-images-bucket"
  },
  "credentials": {
    "credentials_json": "{\"type\":\"service_account\",\"project_id\":\"my-project\",...}"
  }
}
```

### SFTP

```json
{
  "name": "SFTP Server",
  "provider_type": "sftp",
  "is_default": true,
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

## Rate Limiting

Currently, there is no rate limiting implemented. In production, you should implement rate limiting using packages like `django-ratelimit` or similar.

## Pagination

All list endpoints support pagination with the following query parameters:

- `page`: Page number (default: 1)

The default page size is 20 items per page, configured in `settings.REST_FRAMEWORK['PAGE_SIZE']`.
