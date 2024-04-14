from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_consumer = models.BooleanField(default=True)
    is_seller = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s profile"

class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, blank=True, null=True)
    email = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.user.username if self.name is None else self.name

class Product(models.Model):
    name = models.CharField(max_length=200, blank=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    digital = models.BooleanField(default=False)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    seller = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')

    def __str__(self):
        return self.name

    @property
    def imageURL(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return '/path/to/default/image.jpg'  # Placeholder or default image

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return str(self.id)
    
    @property
    def shipping(self):
        return any(item.product.digital == False for item in self.order_items.all())

    @property
    def get_cart_total(self):
        return sum(item.get_total for item in self.order_items.all())
    
    @property
    def get_cart_items(self):
        return sum(item.quantity for item in self.order_items.all())

from django.db import models

class OrderItem(models.Model):
    product = models.ForeignKey(
        'Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_items'
    )
    order = models.ForeignKey(
        'Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_items'
    )
    quantity = models.IntegerField(default=0, null=False, blank=False)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        product_name = self.product.name if self.product else "Unknown Product"
        return f"{self.quantity} of {product_name}"

    @property
    def get_total(self):
        if self.product and self.product.price:
            return self.product.price * self.quantity
        return 0

    class Meta:
        unique_together = ('order', 'product')  # Ensuring each product is listed once per order

class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=200, null=True, blank=True)
    state = models.CharField(max_length=200, null=True, blank=True)
    zipcode = models.CharField(max_length=200, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address

class Notification(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.recipient.username}"
        


# class Book(models.Model):
#     seller = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, related_name='inventory')
#     isbn = models.CharField(max_length=13, primary_key=True)
#     title = models.CharField(max_length=255)
#     author = models.CharField(max_length=255)
#     genre = models.CharField(max_length=255)
#     pages = models.IntegerField()
#     release_date = models.DateField()
#     stock = models.IntegerField()
#     cover_image = models.ImageField(upload_to='book_covers/', default='book_covers/steve_jobs.jpeg')

#     def __str__(self):
#         return self.title

# class Cart(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart')
#     books = models.ManyToManyField(Book, through='CartEntry')

# class CartEntry(models.Model):
#     cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
#     book = models.ForeignKey(Book, on_delete=models.CASCADE)
#     quantity = models.IntegerField(default=1)

             #where do we implement the code for the user class 
