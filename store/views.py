from itertools import product
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



def checkout(request):
     data = cartData(request)
     cartItems = data['cartItems']
     order = data['order']
     items = data['items']
     
     context = {'items': items, 'order': order, 'cartItems': cartItems} 
     return render(request, 'store/checkout.html', context)


@require_POST
@csrf_exempt
def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    customer, created = Customer.objects.get_or_create(user=request.user)
    orders = Order.objects.filter(customer=customer, complete=False)

    if orders.exists():
        order = orders.first()
    else:
        order = Order.objects.create(customer=customer, complete=False)

    product = Product.objects.get(id=productId)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)

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
            return redirect('search_books')  # Redirect to the home page or dashboard

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
                print(f"Book added with id: {product.id}")  # This will print to the console
                return redirect('seller_dashboard')  # Redirect to the seller dashboard or inventory view
        else:
            form = AddBookForm()
        return render(request, 'store/add_book.html', {'form': form})  # Pass the form to the context here
    else:
        # Redirect non-sellers to a different page or show an error message
        return redirect('search_books')

def view_inventory(request):
    products = Product.objects.all()  # Get all products from the database
    context = {
        'products': products
    }
    return render(request, 'store/inventory.html', context)

def add_to_cart(request, product_id):
    print("Before:", request.session.get('cart', {}))
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})

    # Convert product_id to string for consistency
    product_key = str(product_id)

    # Increment the product quantity in cart or add it if it doesn't exist
    if product_key in cart:
        cart[product_key] += 1
    else:
        cart[product_key] = 1

    # Save the cart in the session
    request.session['cart'] = cart
    print("After:", request.session.get('cart', {}))

    # Redirect back to the page where the 'Add to Cart' button was clicked
    referer_url = request.META.get('HTTP_REFERER')
    if referer_url:
        return HttpResponseRedirect(referer_url)
    else:
        # If the HTTP_REFERER is not set, redirect to a default page (e.g., 'search_books')
        return HttpResponseRedirect(reverse('search_books'))

def seller_dashboard(request):
    if request.user.is_authenticated and request.user.profile.is_seller:
        if request.method == 'POST':
            add_book_form = AddBookForm(request.POST, request.FILES)
            if add_book_form.is_valid():
                new_book = add_book_form.save(commit=False)
                new_book.seller = request.user.profile
                new_book.save()
                return redirect('seller_dashboard')  # Redirect to refresh the page and show the new book
        else:
            add_book_form = AddBookForm()

        seller_books = Product.objects.filter(seller=request.user.profile)

        # Get the number of purchases for each book
        book_purchases = {book: OrderItem.objects.filter(product=book).count() for book in seller_books}

        # Total listings by the seller
        total_listings = seller_books.count()

        context = {
            'add_book_form': add_book_form,
            'seller_books': seller_books,
            'book_purchases': book_purchases,
            'total_listings': total_listings,
        }
        return render(request, 'store/seller_dashboard.html', context)
    else:
        return redirect('login')



from django.views.decorators.csrf import csrf_exempt

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
                    credit_card_number=data['shipping']['credit_card_number'],
                    credit_card_expiration_date=data['shipping']['credit_card_expiration_date'],
                    CVV_number=data['shipping']['CVV_number'],

               )
     
     return JsonResponse('Payment complete', safe=False)

def processed_order(request):
    return render(request, 'store/processed_order.html')


