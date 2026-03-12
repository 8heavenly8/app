from django.shortcuts import render
from django.db.models import Q
from django.contrib import messages
from .models import Product, Category, Manufacturer, Cart
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

def home(request):
    return render(request, 'sheets/home.html')

def author(request):
    return render(request, 'sheets/author.html')

def theme(request):
    return render(request, 'sheets/theme.html')

def product_list(request):
    items = Product.objects.all() 
    category = Category.objects.all()
    manufacturer= Manufacturer.objects.all()
    
   
    categ = request.GET.get('category')
    if categ:
        items = items.filter(category_id=categ)
    
    manuf = request.GET.get('manufacturer')
    if manuf:
        items = items.filter(manufacturer_id=manuf)
    
    search = request.GET.get('search')
    if search:
        items = items.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )
    return render(request, 'sheets/product_list.html', {'products': items,'category': category,
        'manufacturer': manufacturer,})
    
def product_detail(request,pk):
    actual_id = pk
    product = get_object_or_404(Product, pk=actual_id)
    return render(request, 'sheets/product_detail.html', {
            'product': product,
            'item_pk': pk
    })
    
def update_cart(request,pk):
    return render(request, 'sheets/theme.html')
    
def remove_from_cart(request):
    return render(request, 'sheets/theme.html')
    
def cart_view(request):
    return render(request, 'sheets/theme.html')
    
def add_to_cart(request):
    return render(request, 'sheets/theme.html')