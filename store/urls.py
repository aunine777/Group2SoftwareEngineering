
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import register
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
	path('', views.store, name="store"),
	path('cart/', views.cart, name="cart"),
	path('checkout/', views.checkout, name="checkout"),
	path('update_item/', views.updateItem, name="update_item"),
    path('process_order/', views.processOrder, name="process_order"),	
    path('index/', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='store/login.html'), name='login'),
    # path('book_list', views.book_list, name='book_list'),
    path('search/', views.search_books, name='search_books'),
    # path('decrease/<str:isbn>/', views.decrease_stock, name='decrease_stock'),
    path('add_book/', views.add_book, name='add_book'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('manage_users/', views.manage_users, name='manage_users'),
    # path('edit_inventory/', views.edit_inventory, name='edit_inventory'),
    # path('seller/', views.seller_page, name='seller_page'),
    path('checkout/', views.checkout, name='checkout'),
    path('inventory/', views.view_inventory, name='view_inventory'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('seller_dashboard/', views.seller_dashboard, name='seller_dashboard'),
    # path('get-content/<str:content_id>/', get_content, name='get-content'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
