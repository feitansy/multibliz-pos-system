# Product Image Storage Configuration

## Local Development (Windows/Linux/Mac)

Images are stored locally in the `/media/products/` folder. This works out of the box.

```bash
# Images will be saved to:
media/products/filename.jpg
```

## Production (Render with Google Cloud Storage)

For persistent image storage on Render, follow these steps:

### Step 1: Set up Google Cloud Storage

1. Create a Google Cloud Project: https://console.cloud.google.com/
2. Enable Cloud Storage API
3. Create a GCS Bucket:
   - Name: `multibliz-pos-media` (or your preferred name)
   - Location: `us-central1`
   - Make it **Public** (for image serving)

### Step 2: Create a Service Account

1. Go to **IAM & Admin → Service Accounts**
2. Create a new service account with name: `multibliz-pos`
3. Grant role: **Storage Object Admin**
4. Create a JSON key file
5. Copy the entire JSON key content

### Step 3: Add to Render Environment Variables

In your Render dashboard for the multibliz-pos service:

1. Go to **Environment** (or **Settings**)
2. Add these variables:
   - `USE_GCS`: `true`
   - `GCS_BUCKET_NAME`: `multibliz-pos-media`
   - `GOOGLE_APPLICATION_CREDENTIALS`: (Path to credentials file on Render)

For the Google Cloud credentials, you can either:
- **Option A**: Store the JSON key directly as an environment variable (recommended for small keys)
- **Option B**: Upload credentials file to Render filesystem

### Option A: Store JSON as Environment Variable (Simpler)

1. Get your service account JSON key
2. In Render dashboard, add a new environment variable:
   - Name: `GCS_CREDENTIALS_JSON`
   - Value: (paste the entire JSON content)
3. Render will automatically use this for authentication

### Step 4: Install Dependencies

The following is already in your `requirements.txt`:
- `django-storages[google]==1.14.2` (add this if not present)
- `google-cloud-storage==3.5.0` (already installed)

### Step 5: Deploy

Push your code to GitHub:
```bash
git add -A
git commit -m "Add Google Cloud Storage support for product images"
git push
```

Render will automatically redeploy. After deployment, your product images will be stored in Google Cloud Storage and persist across container restarts.

## Testing

### Local Testing
1. Upload a product image locally
2. Check that it appears in `/media/products/`
3. Refresh the page - image should still display

### Production Testing
1. Upload a product image on Render
2. Check Google Cloud Console → Storage Bucket
3. Image should appear in the bucket
4. Refresh the page - image should still display

## Troubleshooting

### Images not saving locally?
- Check `/media/products/` folder exists
- Check folder write permissions: `chmod 755 media/products`

### Images not saving on Render?
- Verify `USE_GCS=true` in environment variables
- Check Google Cloud service account permissions
- Verify bucket name matches `GCS_BUCKET_NAME`
- Check Render logs for authentication errors

### Can't see images on Render?
- Verify bucket is set to **Public** in GCS
- Check image URL is correct: `https://storage.googleapis.com/bucket-name/products/filename.jpg`
- Verify CORS settings in GCS bucket

## Manual GCS Configuration (Advanced)

If you want to manually configure django-storages, add to settings.py:

```python
if os.getenv('USE_GCS') == 'true':
    GS_BUCKET_NAME = os.getenv('GCS_BUCKET_NAME', 'multibliz-pos-media')
    GS_PROJECT_ID = os.getenv('GCS_PROJECT_ID')
    
    # Optional: For service account JSON credentials
    GS_CREDENTIALS = service_account.Credentials.from_service_account_info(
        json.loads(os.getenv('GCS_CREDENTIALS_JSON'))
    )
```

## References

- [Django Storages Documentation](https://django-storages.readthedocs.io/en/latest/)
- [Google Cloud Storage Documentation](https://cloud.google.com/storage/docs)
- [Render Environment Variables](https://render.com/docs/environment-variables)
