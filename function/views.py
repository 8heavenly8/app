from django.shortcuts import render
from .models import Product

def home(request):
    return render(request, 'sheets/home.html')

def author(request):
    return render(request, 'sheets/author.html')

def theme(request):
    return render(request, 'sheets/theme.html')

def product_list(request):
    items = Product.objects.all() 
    return render(request, 'sheets/product_list.html', {'products': items})
    
def product_detail(request):
    return render(request, 'sheets/theme.html')
    
def update_cart(request):
    return render(request, 'sheets/theme.html')
    
def remove_from_cart(request):
    return render(request, 'sheets/theme.html')
    
def cart_view(request):
    return render(request, 'sheets/theme.html')
    
def add_to_cart(request):
    return render(request, 'sheets/theme.html')