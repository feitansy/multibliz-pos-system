"""
Custom storage configuration for local and cloud storage support.
Uses local filesystem in development, Google Cloud Storage in production.
"""
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage

# Check if we're in production and have GCS credentials
USE_GCS = os.getenv('USE_GCS', 'False').lower() == 'true' or (
    not settings.DEBUG and os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
)

if USE_GCS:
    try:
        from storages.backends.gcloud import GoogleCloudStorage
        
        class ProductImageStorage(GoogleCloudStorage):
            """Custom GCS storage for product images"""
            bucket_name = os.getenv('GCS_BUCKET_NAME', 'multibliz-pos-media')
            location = 'products'
            default_acl = 'public-read'
            
            @property
            def file_overwrite(self):
                return True
    
    except ImportError:
        # Fallback to local storage if django-storages not installed
        class ProductImageStorage(FileSystemStorage):
            """Fallback to local filesystem"""
            location = os.path.join(settings.MEDIA_ROOT, 'products')
            base_url = os.path.join(settings.MEDIA_URL, 'products/')
else:
    # Use local filesystem storage for development
    class ProductImageStorage(FileSystemStorage):
        """Local filesystem storage for development"""
        location = os.path.join(settings.MEDIA_ROOT, 'products')
        base_url = os.path.join(settings.MEDIA_URL, 'products/')
