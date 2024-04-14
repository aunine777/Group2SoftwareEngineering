from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profile, User
from .models import OrderItem, Notification
import logging


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

logger = logging.getLogger(__name__)

@receiver(post_save, sender=OrderItem)
def create_notification(sender, instance, created, **kwargs):
    if instance.product and instance.product.seller and instance.product.seller.user and instance.quantity > 0:
        if created:
            message = f"A new order has been placed for {instance.product.name} (Quantity: {instance.quantity})."
        else:
            message = f"Order for {instance.product.name} has been updated (Quantity: {instance.quantity})."
        
        # Create notification only if the seller and user are valid and quantity is greater than zero
        Notification.objects.create(
            recipient=instance.product.seller.user,
            message=message
        )
    else:
        # Log the situation for further investigation or action
        logger.error(f"Failed to create notification: Check product, seller, user, and quantity for OrderItem ID {instance.id}.")
