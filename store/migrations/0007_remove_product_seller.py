# Generated by Django 5.0.3 on 2024-03-26 19:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_remove_cart_books_remove_cartentry_book_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='seller',
        ),
    ]
