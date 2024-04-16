from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_consumer = models.BooleanField(default=True)
    is_seller = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s profile"

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, blank=True, null=True)
    email = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name or self.user.username

class Product(models.Model):
    name = models.CharField(max_length=200, blank=False)
    author = models.CharField(max_length=255, default='Unknown')
    num_pages = models.IntegerField(null=True, blank=True)  # Allow null values
    description = models.TextField(default='No description available')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    digital = models.BooleanField(default=False)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    seller = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    average_rating = models.FloatField(default=0.0, blank=True)
    ratings_count = models.IntegerField(default=0, blank=True)
    reenlisted = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @property
    def imageURL(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return '/static/images/default-product.jpg' 
    
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=200, null=True, blank=True)
    delivered = models.BooleanField(default=False)

    def __str__(self):
        return f"Order {self.id}"

    @property
    def shipping(self):
        return any(not item.product.digital for item in self.order_items.all())

    @property
    def get_cart_total(self):
        return sum(item.get_total for item in self.order_items.all())

    @property
    def get_cart_items(self):
        return sum(item.quantity for item in self.order_items.all())
    


class OrderItem(models.Model):
    product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True, related_name='order_items')
    order = models.ForeignKey('Order', on_delete=models.SET_NULL, null=True, related_name='order_items')
    quantity = models.IntegerField(default=0)
    status = models.CharField(max_length=100, default='pending', choices=[
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('returned', 'Returned')
    ])
    returned = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('product', 'order', 'status')

    def __str__(self):
        return f"{self.quantity} of {self.product.name if self.product else 'Unknown Product'}"

    @property
    def get_total(self):
        return self.product.price * self.quantity if self.product else 0

    @property
    def is_active(self):
        """Determines if the order item is considered active, i.e., not returned."""
        return self.status in ['pending', 'shipped', 'delivered'] and not self.returned

    def mark_as_returned(self):
        """Marks the order item as returned and updates inventory if necessary."""
        if not self.returned:
            self.returned = True
            self.status = 'returned'
            self.save()
            self.product.increment_inventory(self.quantity)  # Assuming a method on Product model that increments inventory.

    def save(self, *args, **kwargs):
        """Custom save method to handle business logic before saving."""
        if self.returned and self.status != 'returned':
            self.status = 'returned'
        super().save(*args, **kwargs)


class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    address = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True)
    zipcode = models.CharField(max_length=200, null=True)
    default = models.BooleanField(default=False) 
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.address}, {self.city}, {self.state} {self.zipcode}"


class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    read = models.BooleanField(default=False)
    type = models.CharField(max_length=50, default='info')  # Type of notification
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        read_status = "Read" if self.read else "Unread"
        return f"{self.recipient.username} - {self.message} ({read_status})"

    def mark_as_read(self):
        """Mark the notification as read."""
        self.read = True
        self.save()

    class Meta:
        ordering = ['-created_at']  # Newest notifications first


class Rating(models.Model):
    SCORE_CHOICES = (
        (1, 'Poor'),
        (2, 'Fair'),
        (3, 'Good'),
        (4, 'Very Good'),
        (5, 'Excellent'),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ratings',
        db_index=True
    )
    book = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='ratings',
        db_index=True
    )
    score = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        choices=SCORE_CHOICES
    )
    comment = models.TextField(blank=True, null=True)  # Allows for optional comments

    class Meta:
        unique_together = ('user', 'book')

    def __str__(self):
        return f"{self.user.username} rated {self.book.title} as {self.score}"


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
