from itertools import product
from django.db.models import Count, Sum
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
import datetime
from .models import *
from .utils import cookieCart, cartData, guestOrder
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
import sqlite3
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.views import LogoutView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import Profile
# from .forms import BookForm
from .forms import AddBookForm
from .forms import NewUserForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F
from django.views.decorators.http import require_POST
import json
from django.contrib import messages
from django.db.models import DecimalField
from .forms import CheckoutForm



# Create your views here.
def store(request):
     if request.user.is_authenticated:
        # Ensure the user has a profile
        profile, created = Profile.objects.get_or_create(user=request.user)
        print("Is Seller:", profile.is_seller)
     data = cartData(request)
     cartItems = data['cartItems']

     products = Product.objects.all()
     context = {'products': products, 'cartItems': cartItems}
     return render(request, 'store/store.html', context)

def cart(request):
    # Retrieve cart data using the cartData helper function
    data = cartData(request)
    print("Cart Data:", data)

    # Extract individual data items from the returned dictionary
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    # Prepare the context for rendering the cart template
    context = {
        'items': items,
        'order': order,
        'cartItems': cartItems
    }

    # Render and return the cart template with the context data
    return render(request, 'store/cart.html', context)



from django.contrib.auth.decorators import login_required
from django.db import transaction

@login_required
def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    if request.user.is_authenticated:
        customer = Customer.objects.get(user=request.user)
        address = ShippingAddress.objects.filter(customer=customer, default=True).first()
    else:
        customer, address = None, None

    if request.method == 'POST':
        address_data = request.POST
        if 'address' in address_data and 'city' in address_data and 'state' in address_data and 'zipcode' in address_data:
            ShippingAddress.objects.update_or_create(
                customer=customer,
                defaults={
                    'address': address_data['address'],
                    'city': address_data['city'],
                    'state': address_data['state'],
                    'zipcode': address_data['zipcode'],
                    'default': address_data.get('set_default') == 'on'
                },
            )
            order.complete = True
            order.save()
            request.session['last_order_id'] = order.id 
            messages.success(request, "Your order has been completed successfully.")
            return HttpResponseRedirect(reverse('order_success'))
        else:
            messages.error(request, "Please fill in all required fields.")

    context = {
        'items': items,
        'order': order,
        'cartItems': cartItems,
        'address': address  
    }
    return render(request, 'store/checkout.html', context)


@require_POST
@csrf_exempt
def updateItem(request):
    try:
        data = json.loads(request.body)
        productId = data.get('productId')
        action = data.get('action')
        logger.debug(f"Action: {action}, Product ID: {productId}")

        if productId is None or action not in ['add', 'remove']:
            logger.error("Missing product ID or invalid action")
            return JsonResponse({'error': 'Missing product ID or invalid action'}, status=400)

        product = get_object_or_404(Product, id=productId)

        customer, _ = Customer.objects.get_or_create(user=request.user)
        order, _ = Order.objects.get_or_create(customer=customer, complete=False)

        orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

        with transaction.atomic():
            if action == 'add':
                orderItem.quantity += 1
                logger.debug(f"Added: Current quantity of {product.name} is {orderItem.quantity}")
            elif action == 'remove':
                orderItem.quantity = max(orderItem.quantity - 1, 0)
                logger.debug(f"Removed: Current quantity of {product.name} is {orderItem.quantity}")

            orderItem.save()

            if orderItem.quantity == 0:
                orderItem.delete()
                logger.debug(f"Deleted {product.name} from cart because quantity reached 0")

        return JsonResponse({'message': 'Item was updated', 'quantity': orderItem.quantity}, safe=False)

    except Product.DoesNotExist:
        logger.error("Product not found")
        return JsonResponse({'error': 'Product not found'}, status=404)
    except Exception as e:
        logger.error(f"Error updating item: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)



class CustomLogoutView(LogoutView):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

def index(request):
    return render(request, 'store/index.html')

def register(request):
    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            Customer.objects.get_or_create(user=user)

            # Get or create the Profile instance for the user
            profile, created = Profile.objects.get_or_create(user=user)

            # Set user role based on the selected option
            role = form.cleaned_data.get('role')
            if role == 'consumer':
                profile.is_consumer = True
            elif role == 'seller':
                profile.is_seller = True
            elif role == 'admin':
                profile.is_admin = True
            profile.save()

            login(request, user)
            return redirect('login')  # Redirect to the home page or dashboard

    else:
        form = NewUserForm()
    return render(request, 'store/register.html', {'form': form})


def manage_users(request):
    if request.user.is_superuser:
        users = NewUserForm.objects.all()
        return render(request, 'store/manage_users.html', {'users': users})
    else:
        return redirect('search_books')




def search_books(request):
    query = request.GET.get('query', '').strip()
    products = Product.objects.filter(name__icontains=query) if query else Product.objects.none()
    return render(request, 'store/search_books.html', {'products': products, 'query': query})



def add_book(request):
    if request.user.is_authenticated and request.user.profile.is_seller:
        if request.method == 'POST':
            form = AddBookForm(request.POST, request.FILES)
            if form.is_valid():
                product = form.save(commit=False)
                product.seller = request.user.profile
                product.save()
                print(f"Book added with id: {product.id}")  
                return redirect('seller_dashboard')  # Redirect to the seller dashboard or inventory view
        else:
            form = AddBookForm()
        return render(request, 'store/add_book.html', {'form': form}) 
    else:
        # Redirect non-sellers to a different page or show an error message
        return redirect('search_books')

def view_inventory(request):
    products = Product.objects.all()  # Get all products from the database
    context = {
        'products': products
    }
    return render(request, 'store/inventory.html', context)

import logging
logger = logging.getLogger(__name__)

def add_to_cart(request, product_id):
    logger.debug("Session cart before update: %s", request.session.get('cart', {}))
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})

    product_key = str(product_id)
    if product_key in cart:
        cart[product_key] += 1
    else:
        cart[product_key] = 1

    request.session['cart'] = cart
    request.session.modified = True  # Ensure the session is saved after modification
    logger.debug("Session cart after update: %s", request.session.get('cart', {}))

    referer_url = request.META.get('HTTP_REFERER')
    if referer_url:
        return HttpResponseRedirect(referer_url)
    else:
        return HttpResponseRedirect(reverse('search_books'))


def seller_dashboard(request):
    if not (request.user.is_authenticated and request.user.profile.is_seller):
        return redirect('login')

    if request.method == 'POST':
        add_book_form = AddBookForm(request.POST, request.FILES)
        if add_book_form.is_valid():
            new_book = add_book_form.save(commit=False)
            new_book.seller = request.user.profile
            new_book.save()
            return redirect('seller_dashboard')
    else:
        add_book_form = AddBookForm()

    seller_books = Product.objects.filter(seller=request.user.profile).prefetch_related('order_items')
    book_sales_data = seller_books.annotate(
        total_sales=Sum('order_items__quantity'),
        total_revenue=Sum(F('order_items__quantity') * F('price'), output_field=DecimalField()),
        order_count=Count('order_items')
    )

    notifications = Notification.objects.filter(recipient=request.user, read=False)
    total_listings = seller_books.count()

    context = {
        'add_book_form': add_book_form,
        'book_sales_data': book_sales_data,
        'total_listings': total_listings,
        'notifications': notifications,
    }

    return render(request, 'store/seller_dashboard.html', context)

def remove_listing(request, book_id):
    if not request.user.is_authenticated or not request.user.profile.is_seller:
        messages.error(request, "You need to be logged in as a seller to perform this action.")
        return redirect('login')
    
    book = get_object_or_404(Product, id=book_id, seller=request.user.profile)
    book.delete()
    messages.success(request, "Product removed successfully.")
    return redirect('seller_dashboard')


def mark_notification_read(request, notification_id):
    notification = Notification.objects.get(id=notification_id, recipient=request.user)
    notification.read = True
    notification.save()
    return redirect('seller_dashboard')

def clear_notification(request, notification_id):
    if request.method == 'POST':
        notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
        notification.read = True  
        notification.save()
        
        # Return a success response
        return JsonResponse({'status': 'success', 'message': 'Notification cleared.'})
    else:
        # Handle non-POST requests here, if needed
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

def order_success(request):
    order_id = request.session.get('last_order_id')
    if not order_id:
        messages.error(request, "No recent order found.")
        return redirect('store')
    
    # Use the correct related name for the reverse relation to access OrderItem instances
    order = get_object_or_404(Order, id=order_id)
    
    # Get the related items using the correct related name
    items = order.order_items.all() if order else []
    
    # Clear the session variable after retrieving the order
    if 'last_order_id' in request.session:
        del request.session['last_order_id']
    
    context = {'order': order, 'items': items}
    return render(request, 'store/order_success.html', context)

def book_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'store/book_detail.html', {'book': product})

def submit_rating(request, book_id):
    if request.method == 'POST':
        rating = int(request.POST.get('rating'))
        book = get_object_or_404(Product, id=book_id)
        total_rating = book.average_rating * book.ratings_count
        total_rating += rating
        book.ratings_count += 1
        book.average_rating = total_rating / book.ratings_count
        book.save()
        return redirect('book_detail', id=book_id)
    else:
        return redirect('error')

@csrf_exempt
def processOrder(request):
     transaction_id = datetime.datetime.now().timestamp()
     data = json.loads(request.body)

     if request.user.is_authenticated:
          customer = request.user.customer
          order, created = Order.objects.get_or_create(customer=customer, complete=False)
          total = float(data['form']['total'])
          order.transaction_id = transaction_id

          if total == order.get_cart_total:
               order.complete = True
          order.save()

     else:
          customer, order = guestOrder(request, data)
     total = float(data['form']['total'])
     order.transaction_id = transaction_id

     if total == order.get_cart_total:
          order.complete = True
          order.save()

     if order.shipping == True:
               ShippingAddress.objects.create(
                    customer=customer,
                    order=order,
                    address=data['shipping']['address'],
                    city=data['shipping']['city'],
                    state=data['shipping']['state'],
                    zipcode=data['shipping']['zipcode'],
               )
     return JsonResponse('Payment complete', safe=False)