import json
from django.core.exceptions import ObjectDoesNotExist
from .models import *

def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except json.JSONDecodeError:
        cart = {}
        print('Cart is empty or invalid JSON.')

    items = []
    order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
    cartItems = order['get_cart_items']

    for i in cart:
        try:
            product = Product.objects.get(id=i)
            total = (product.price * cart[i]['quantity'])

            order['get_cart_total'] += total
            order['get_cart_items'] += cart[i]['quantity']

            item = {
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'imageURL': product.imageURL,
                },
                'quantity': cart[i]['quantity'],
                'get_total': total
            }
            items.append(item)

            if not product.digital:
                order['shipping'] = True
        except ObjectDoesNotExist:
            print(f"Product with id {i} not found.")

    return {'cartItems': order['get_cart_items'], 'order': order, 'items': items}

def cartData(request):
    if request.user.is_authenticated:
        customer, created = Customer.objects.get_or_create(user=request.user)
        orders = Order.objects.filter(customer=customer, complete=False)
        if orders.exists():
            order = orders.first()
        else:
            order = Order.objects.create(customer=customer, complete=False)

        items = order.order_items.all()
        cartItems = sum(item.quantity for item in items)  # Corrected part

    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']

    return {'cartItems': cartItems, 'order': order, 'items': items}


def guestOrder(request, data):
    name = data['form']['name']
    email = data['form']['email']
    cookieData = cookieCart(request)
    items = cookieData['items']

    customer, created = Customer.objects.get_or_create(email=email)
    customer.name = name 
    customer.save()

    order = Order.objects.create(customer=customer, complete=False)
    for item in items:
        product = Product.objects.get(id=item['product']['id'])
        OrderItem.objects.create(
            product=product,
            order=order,
            quantity=item['quantity']
        )
    
    return customer, order
