#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multibliz_pos.settings')
django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile
from sales.forms import ProductForm
from PIL import Image
from io import BytesIO

# Create a simple test image
img = Image.new('RGB', (100, 100), color='red')
img_io = BytesIO()
img.save(img_io, 'PNG')
img_io.seek(0)

# Create form data
test_image = SimpleUploadedFile(
    "test.png",
    img_io.getvalue(),
    content_type="image/png"
)

form_data = {
    'name': 'Test Product with Image',
    'price': '10.00',
    'category': 'Test',
    'label': '',
    'description': ''
}

form = ProductForm(form_data, {'image': test_image})

if form.is_valid():
    print("✓ Form is valid!")
    product = form.save()
    print(f"✓ Product saved: {product}")
    print(f"✓ Image field: {product.image}")
    print(f"✓ Image name: {product.image.name if product.image else 'No image'}")
    print(f"✓ Image URL: {product.image.url if product.image else 'No image'}")
else:
    print("✗ Form errors:")
    for field, errors in form.errors.items():
        print(f"  {field}: {errors}")
