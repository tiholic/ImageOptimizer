"""
Storage backend abstraction layer for different cloud storage providers
"""
import os
from io import BytesIO
from abc import ABC, abstractmethod


class StorageBackend(ABC):
    """Abstract base class for storage backends"""
    
    @abstractmethod
    def upload(self, file_obj, path):
        """Upload file to storage"""
        pass
    
    @abstractmethod
    def download(self, path):
        """Download file from storage"""
        pass
    
    @abstractmethod
    def delete(self, path):
        """Delete file from storage"""
        pass
    
    @abstractmethod
    def exists(self, path):
        """Check if file exists"""
        pass
    
    @abstractmethod
    def get_url(self, path):
        """Get public URL for file"""
        pass


class S3Backend(StorageBackend):
    """AWS S3 storage backend"""
    
    def __init__(self, credentials, config):
        import boto3
        
        self.bucket = config['bucket']
        self.region = config.get('region', 'us-east-1')
        
        self.client = boto3.client(
            's3',
            aws_access_key_id=credentials['access_key_id'],
            aws_secret_access_key=credentials['secret_access_key'],
            region_name=self.region
        )
    
    def upload(self, file_obj, path):
        """Upload file to S3"""
        self.client.upload_fileobj(file_obj, self.bucket, path)
        return path
    
    def download(self, path):
        """Download file from S3"""
        file_obj = BytesIO()
        self.client.download_fileobj(self.bucket, path, file_obj)
        file_obj.seek(0)
        return file_obj
    
    def delete(self, path):
        """Delete file from S3"""
        self.client.delete_object(Bucket=self.bucket, Key=path)
    
    def exists(self, path):
        """Check if file exists in S3"""
        try:
            self.client.head_object(Bucket=self.bucket, Key=path)
            return True
        except:
            return False
    
    def get_url(self, path):
        """Get public URL for S3 object"""
        return f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{path}"


class AzureBlobBackend(StorageBackend):
    """Azure Blob Storage backend"""
    
    def __init__(self, credentials, config):
        from azure.storage.blob import BlobServiceClient
        
        self.container = config['container']
        
        account_url = f"https://{credentials['account_name']}.blob.core.windows.net"
        self.blob_service_client = BlobServiceClient(
            account_url=account_url,
            credential=credentials['account_key']
        )
        self.container_client = self.blob_service_client.get_container_client(self.container)
    
    def upload(self, file_obj, path):
        """Upload file to Azure Blob"""
        blob_client = self.container_client.get_blob_client(path)
        blob_client.upload_blob(file_obj, overwrite=True)
        return path
    
    def download(self, path):
        """Download file from Azure Blob"""
        blob_client = self.container_client.get_blob_client(path)
        file_obj = BytesIO()
        blob_client.download_blob().readinto(file_obj)
        file_obj.seek(0)
        return file_obj
    
    def delete(self, path):
        """Delete file from Azure Blob"""
        blob_client = self.container_client.get_blob_client(path)
        blob_client.delete_blob()
    
    def exists(self, path):
        """Check if blob exists"""
        blob_client = self.container_client.get_blob_client(path)
        return blob_client.exists()
    
    def get_url(self, path):
        """Get public URL for blob"""
        blob_client = self.container_client.get_blob_client(path)
        return blob_client.url


class GCSBackend(StorageBackend):
    """Google Cloud Storage backend"""
    
    def __init__(self, credentials, config):
        from google.cloud import storage as gcs_storage
        from google.oauth2 import service_account
        import json
        
        self.bucket_name = config['bucket']
        
        # Parse credentials JSON and create credentials object
        credentials_dict = json.loads(credentials['credentials_json'])
        creds = service_account.Credentials.from_service_account_info(credentials_dict)
        
        self.client = gcs_storage.Client(credentials=creds, project=credentials_dict.get('project_id'))
        self.bucket = self.client.bucket(self.bucket_name)
    
    def upload(self, file_obj, path):
        """Upload file to GCS"""
        blob = self.bucket.blob(path)
        blob.upload_from_file(file_obj)
        return path
    
    def download(self, path):
        """Download file from GCS"""
        blob = self.bucket.blob(path)
        file_obj = BytesIO()
        blob.download_to_file(file_obj)
        file_obj.seek(0)
        return file_obj
    
    def delete(self, path):
        """Delete file from GCS"""
        blob = self.bucket.blob(path)
        blob.delete()
    
    def exists(self, path):
        """Check if blob exists"""
        blob = self.bucket.blob(path)
        return blob.exists()
    
    def get_url(self, path):
        """Get public URL for blob"""
        return f"https://storage.googleapis.com/{self.bucket_name}/{path}"


class SFTPBackend(StorageBackend):
    """SFTP storage backend"""
    
    def __init__(self, credentials, config):
        import paramiko
        
        self.host = credentials['host']
        self.username = credentials['username']
        self.password = credentials.get('password')
        self.key_file = credentials.get('key_file')
        self.port = credentials.get('port', 22)
        self.remote_path = config['remote_path']
        
        self.transport = None
        self.sftp = None
        self._connect()
    
    def _connect(self):
        """Establish SFTP connection"""
        import paramiko
        
        self.transport = paramiko.Transport((self.host, self.port))
        
        if self.password:
            self.transport.connect(username=self.username, password=self.password)
        elif self.key_file:
            key = paramiko.RSAKey.from_private_key_file(self.key_file)
            self.transport.connect(username=self.username, pkey=key)
        
        self.sftp = paramiko.SFTPClient.from_transport(self.transport)
    
    def _ensure_connected(self):
        """Ensure SFTP connection is active"""
        if not self.transport or not self.transport.is_active():
            self._connect()
    
    def upload(self, file_obj, path):
        """Upload file via SFTP"""
        self._ensure_connected()
        remote_path = os.path.join(self.remote_path, path)
        
        # Ensure directory exists
        remote_dir = os.path.dirname(remote_path)
        try:
            self.sftp.stat(remote_dir)
        except FileNotFoundError:
            self._mkdir_p(remote_dir)
        
        self.sftp.putfo(file_obj, remote_path)
        return path
    
    def download(self, path):
        """Download file via SFTP"""
        self._ensure_connected()
        remote_path = os.path.join(self.remote_path, path)
        file_obj = BytesIO()
        self.sftp.getfo(remote_path, file_obj)
        file_obj.seek(0)
        return file_obj
    
    def delete(self, path):
        """Delete file via SFTP"""
        self._ensure_connected()
        remote_path = os.path.join(self.remote_path, path)
        self.sftp.remove(remote_path)
    
    def exists(self, path):
        """Check if file exists via SFTP"""
        self._ensure_connected()
        remote_path = os.path.join(self.remote_path, path)
        try:
            self.sftp.stat(remote_path)
            return True
        except FileNotFoundError:
            return False
    
    def get_url(self, path):
        """Get SFTP URL (not publicly accessible)"""
        return f"sftp://{self.host}/{self.remote_path}/{path}"
    
    def _mkdir_p(self, remote_directory):
        """Create directory recursively"""
        if not remote_directory or remote_directory == '/':
            return
        
        dirs = []
        dir_path = remote_directory
        
        # Build list of directories from deepest to root
        while dir_path and dir_path != '/':
            dirs.append(dir_path)
            parent = os.path.dirname(dir_path)
            # Prevent infinite loop if dirname returns same path
            if parent == dir_path:
                break
            dir_path = parent
        
        # Create directories from root to deepest
        dirs.reverse()
        
        for dir_path in dirs:
            try:
                self.sftp.stat(dir_path)
            except (FileNotFoundError, IOError):
                try:
                    self.sftp.mkdir(dir_path)
                except (FileNotFoundError, IOError):
                    # Directory might already exist or parent doesn't exist
                    pass
    
    def __del__(self):
        """Clean up connection"""
        if self.sftp:
            self.sftp.close()
        if self.transport:
            self.transport.close()


def get_storage_backend(storage_provider):
    """Factory function to get appropriate storage backend"""
    credentials = storage_provider.get_credentials()
    config = storage_provider.config
    
    backends = {
        's3': S3Backend,
        'azure': AzureBlobBackend,
        'gcs': GCSBackend,
        'sftp': SFTPBackend,
    }
    
    backend_class = backends.get(storage_provider.provider_type)
    if not backend_class:
        raise ValueError(f"Unsupported storage provider: {storage_provider.provider_type}")
    
    return backend_class(credentials, config)
