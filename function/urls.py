from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),  
    path('author/', views.author, name = 'author'),
    path('theme/', views.theme, name = 'theme'),
    path('catalog/', views.product_list, name = 'catalog'),
    path('catalog/<int:pk>/', views.product_detail, name = 'detail'),
    path('cart/add/<int:item_id>/',views.add_to_cart,name = 'add_to_cart'),
    path('cart/update/<int:item_id>/',views.cart_update,name = 'cart_update'),
    path('cart/remove/<int:item_id>/',views.cart_remove,name = 'cart_remove'),
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
]