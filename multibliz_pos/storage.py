"""
Cloud storage configuration for Django.
Uses Google Cloud Storage for production, local filesystem for development.
"""
import os
from django.conf import settings

# Check if we're using cloud storage (production on Render)
USE_GCS = os.getenv('USE_GCS', 'True').lower() in ('true', '1', 'yes') and not settings.DEBUG

if USE_GCS:
    try:
        from storages.backends.gcloud import GoogleCloudStorage
        
        class ProductImageStorage(GoogleCloudStorage):
            """Google Cloud Storage backend for product images"""
            bucket_name = os.getenv('GCS_BUCKET_NAME', 'multibliz-pos-media')
            location = 'products'
            default_acl = 'public-read'
            
            @property
            def file_overwrite(self):
                return True
    
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
