# Generated by Django 5.0.4 on 2024-04-16 06:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0019_alter_notification_options_notification_type_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='reenlisted',
            field=models.BooleanField(default=False),
        ),
    ]
