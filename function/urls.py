from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  
    path('author/', views.author, name = 'author'),
    path('theme/', views.theme, name = 'theme'),
    path('catalog/', views.product_list, name = 'catalog'),
    path('catalog/<int:pk>/', views.product_detail, name = 'detail'),
    path('cart/add/<int:item_id>/',views.add_to_cart,name = 'add_to_cart'),
    path('cart/update/<int:item_id>/', views.cart_update, name='cart_update'),
    path('cart/remove/<int:item_id>/', views.cart_remove, name='cart_remove'),
    path('cart/', views.cart_view, name='cart_view'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('checkout/', views.checkout, name='checkout'),
    path('register/',views.register,name='register'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('api/products/', views.api_products, name='api_products'),

    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile_view, name='profile'),

    path('api/me/', views.api_me_get, name='api_me'),
    path('api/me/update/', views.api_me_patch, name='api_me_patch'),
    path('api/products/', views.api_products_list, name='api_products'),
    path('api/products/create/', views.api_product_create, name='api_product_create'),
    path('api/products/<int:product_id>/', views.api_product_update, name='api_product_update'),
    path('api/products/<int:product_id>/delete/', views.api_product_delete, name='api_product_delete'),
    path('api/orders/', views.api_orders_list, name='api_orders'),
    path('api/orders/<int:order_id>/', views.api_order_detail, name='api_order_detail'),
    path('api/cart/count/', views.api_cart_count, name='api_cart_count'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)