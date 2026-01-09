"""
Cloud storage configuration for Django.
Uses AWS S3 for production, local filesystem for development.
AWS S3 Free Tier: 5GB storage, 20K GET + 2K PUT requests/month (free)
"""
import os
from django.conf import settings

# Check if we're using cloud storage (production on Render)
USE_S3 = os.getenv('USE_S3', 'True').lower() in ('true', '1', 'yes') and not settings.DEBUG

if USE_S3:
    try:
        from storages.backends.s3boto3 import S3Boto3Storage
        
        class ProductImageStorage(S3Boto3Storage):
            """AWS S3 storage backend for product images"""
            bucket_name = os.getenv('AWS_STORAGE_BUCKET_NAME', 'multibliz-pos-media')
            region_name = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
            custom_domain = os.getenv('AWS_S3_CUSTOM_DOMAIN', None)
            
            def __init__(self):
                super().__init__(
                    access_key=os.getenv('AWS_ACCESS_KEY_ID'),
                    secret_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                    bucket_name=self.bucket_name,
                    region_name=self.region_name,
                    default_acl='public-read',
                    file_overwrite=True,
                    signature_version='s3v4',
                )
    
    except ImportError:
        # Fallback to local storage if django-storages not installed
        from django.core.files.storage import FileSystemStorage
        
        class ProductImageStorage(FileSystemStorage):
            """Fallback to local filesystem"""
            location = os.path.join(settings.MEDIA_ROOT, 'products')
            base_url = os.path.join(settings.MEDIA_URL, 'products/')
else:
    # Use local filesystem storage for development
    from django.core.files.storage import FileSystemStorage
    
    class ProductImageStorage(FileSystemStorage):
        """Local filesystem storage for development"""
        location = os.path.join(settings.MEDIA_ROOT, 'products')
        base_url = os.path.join(settings.MEDIA_URL, 'products/')
