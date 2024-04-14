# Generated by Django 5.0.4 on 2024-04-14 08:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0015_remove_shippingaddress_order_shippingaddress_default_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='orderitem',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='status',
            field=models.CharField(default='pending', max_length=100),
        ),
        migrations.AlterUniqueTogether(
            name='orderitem',
            unique_together={('product', 'order', 'status')},
        ),
    ]