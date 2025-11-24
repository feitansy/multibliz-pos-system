# Generated migration for adding role field to User model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.CharField(
                choices=[
                    ('admin', 'Administrator'),
                    ('manager', 'Manager'),
                    ('staff', 'Staff'),
                    ('viewer', 'Viewer'),
                ],
                default='staff',
                help_text='User role determines permission level for sensitive actions like deletion.',
                max_length=20,
            ),
        ),
    ]
