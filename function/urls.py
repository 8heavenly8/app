from django.urls import path
from . import views

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
    path('checkout/', views.checkout, name='checkout'),
]