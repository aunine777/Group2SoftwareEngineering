

from django.core.management.base import BaseCommand
from django.db.models import Count
from django.db import transaction
from store.models import OrderItem

class Command(BaseCommand):
    help = 'Resolve duplicate OrderItems'

    def handle(self, *args, **kwargs):
        with transaction.atomic():
            duplicates = OrderItem.objects.values(
                'order', 'product'
            ).annotate(
                count=Count('id')
            ).filter(count__gt=1)

            for duplicate in duplicates:
                items = OrderItem.objects.filter(
                    order=duplicate['order'],
                    product=duplicate['product']
                )
                total_quantity = sum(item.quantity for item in items)
                first_item = items.first()
                first_item.quantity = total_quantity
                first_item.save()
                items.exclude(pk=first_item.pk).delete()  # Delete other items except the first

                self.stdout.write(self.style.SUCCESS(
                    f'Resolved {len(items)-1} duplicates for order {duplicate["order"]} and product {duplicate["product"]}'
                ))
