from django.contrib import admin
from .models import Profile, Customer, Product, Order, OrderItem, ShippingAddress

class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_consumer', 'is_seller', 'is_admin']

class CustomerAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'email']

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'digital', 'seller']
    list_filter = ['digital', 'seller']
    search_fields = ['name', 'seller__user__username']

class OrderAdmin(admin.ModelAdmin):
    list_display = ['customer', 'date_ordered', 'complete']
    list_filter = ['complete', 'date_ordered']

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'order', 'quantity']
    list_filter = ['order__date_ordered']

class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ['customer', 'address', 'city', 'state', 'zipcode']
    list_filter = ['state', 'city']

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(ShippingAddress, ShippingAddressAdmin)


# @admin.register(Book)
# class BookAdmin(admin.ModelAdmin):
#     list_display = ['title', 'author', 'isbn', 'stock']
#     # Any other customization you want


