from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_consumer = models.BooleanField(default=True)
    is_seller = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.name
    
class Product(models.Model):
    name = models.CharField(max_length=200, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    digital = models.BooleanField(default=False)  # Removed null=True
    image = models.ImageField(null=True, blank=False)
    seller = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, related_name='products')

    def __str__(self):
        return self.name
    
    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url

    

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=200, null=True)

    def __str__(self):
        return str(self.id)
    
    @property
    def shipping(self):
        return self.orderitem_set.filter(product__digital=False).exists()
    
    @property
    def get_cart_total(self):
        return sum(item.get_total for item in self.orderitem_set.all())
    
    @property
    def get_cart_items(self):
        return sum(item.quantity for item in self.orderitem_set.all())    

class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total

    class Meta:
        unique_together = ('product', 'order')

class ShippingAddress(models.Model):
        customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
        order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
        address = models.CharField(max_length=200, null=True)
        city = models.CharField(max_length=200, null=True)
        state = models.CharField(max_length=200, null=True)
        zipcode = models.CharField(max_length=200, null=True)
        date_added = models.DateTimeField(auto_now_add=True)
        credit_card_number = models.CharField(max_length=12, null=True)
        credit_card_expiration_date = models.CharField(max_length=5, null=True)
        CVV_number= models.CharField(max_length=3, null=True)

        def __str__(self):
            return self.address
        


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


    

