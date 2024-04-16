from django.contrib import admin
# from .models import Book

# Register your models here.

from .models import *

admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)

# @admin.register(Book)
# class BookAdmin(admin.ModelAdmin):
#     list_display = ['title', 'author', 'isbn', 'stock']
#     # Any other customization you want









