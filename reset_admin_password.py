#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multibliz_pos.settings')
django.setup()

from accounts.models import User

try:
    user = User.objects.get(username='admin')
    user.set_password('admin123')
    user.save()
    print('✓ Admin password successfully reset to: admin123')
except User.DoesNotExist:
    print('✗ Admin user not found')
except Exception as e:
    print(f'✗ Error: {e}')
