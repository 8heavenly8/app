from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('author/', views.author, name = 'author'),
    path('theme/', views.theme, name = 'theme'),
    path('catalog/', views.product_list, name = 'catalog'),
    path('catalog/<int:pk>/', views.product_detail, name = 'detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name = 'add_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name = 'update'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name = 'detail'),
    path('cart/', views.cart_view, name = 'cart'),
]