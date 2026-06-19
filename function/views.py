
from .models import Product, Category, Manufacturer, Cart, Cart_item,Order,OrderItem
from io import BytesIO
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib import messages
from .forms import CustomUserCreationForm
from openpyxl import Workbook
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import CustomUserCreationForm
import json
from datetime import datetime

def api_products(request):
    """API для получения списка товаров"""
    products = Product.objects.all()
    

    category = request.GET.get('category')
    if category:
        products = products.filter(category_id=category)
    
    search = request.GET.get('search')
    if search:
        products = products.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )
    
    data = []
    for p in products:
        data.append({
            'id': p.id,
            'title': p.title,
            'price': str(p.price),
            'amount_in_stock': p.amount_in_stock,
            'product_photo': p.product_photo.url if p.product_photo else None,
            'category': p.category.title,
            'manufacturer': p.manufacturer.title,
        })
    
    return JsonResponse(data, safe=False)

def home(request):
    """Главная страница"""
    categories = Category.objects.all()
    popular_products = Product.objects.filter(amount_in_stock__gt=0).order_by('-id')[:6]
    
    context = {
        'categories': categories,
        'popular_products': popular_products,
    }
    return render(request, 'sheets/home.html', context)

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

@login_required
@login_required
def add_to_cart(request, item_id):
    """Добавление товара в корзину через сессию"""
    # Проверяем, существует ли товар
    try:
        product = Product.objects.get(id=item_id)
    except Product.DoesNotExist:
        messages.error(request, 'Товар не найден!')
        return redirect('catalog')
    
    # Добавляем в сессию
    cart = request.session.get('cart', {})
    cart[str(item_id)] = cart.get(str(item_id), 0) + 1
    request.session['cart'] = cart
    
    messages.success(request, f'{product.title} добавлен в корзину!')
    return redirect('cart_view')

def cart_remove(request, item_id):
    """Удаление товара из корзины"""
    cart = request.session.get('cart', {})
    if str(item_id) in cart:
        del cart[str(item_id)]
        request.session['cart'] = cart
        messages.success(request, 'Товар удален из корзины')
    return redirect('cart_view')

def cart_update(request, item_id):
    if request.method == 'POST':
        try:
            amount = int(request.POST.get('amount', 1))
            cart = request.session.get('cart', {})
            
            if str(item_id) in cart:
                if amount <= 0:
                    del cart[str(item_id)]
                else:
                    cart[str(item_id)] = amount
                request.session['cart'] = cart
                messages.success(request, 'Корзина обновлена')
            else:
                messages.warning(request, 'Товар не найден в корзине')
        except ValueError:
            messages.error(request, 'Некорректное количество')
    
    return redirect('cart_view')

@login_required
def cart_remove(request, item_id):
    cart = request.session.get('cart', {})
    if str(item_id) in cart:
        del cart[str(item_id)]
        request.session['cart'] = cart
        messages.success(request, 'Товар удален из корзины')
    else:
        messages.warning(request, 'Товар не найден в корзине')
    
    return redirect('cart_view')


@login_required
def cart_view(request):
    """Корзина на сессиях - показывает товары"""
    cart = request.session.get('cart', {})
    
    # Получаем товары из базы по ID из сессии
    cart_items = []
    total_price = 0
    
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=int(product_id))
            item = {
                'product': product,
                'amount': quantity,
                'total': product.price * quantity
            }
            cart_items.append(item)
            total_price += item['total']
        except Product.DoesNotExist:
            # Если товара нет - удаляем из сессии
            del cart[product_id]
            request.session['cart'] = cart
    
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'cart_count': sum(cart.values())
    }
    return render(request, 'sheets/cart.html', context)
    


@login_required
def checkout(request):
    from decimal import Decimal
    from datetime import datetime
    import json
    
    # Получаем корзину из сессии
    cart_data = request.session.get('cart', {})
    
    if not cart_data:
        messages.error(request, "Корзина пуста")
        return redirect('cart_view')
    
    # Получаем товары из корзины
    items = []
    total_price = Decimal('0')
    
    for product_id, quantity in cart_data.items():
        try:
            product = Product.objects.get(id=int(product_id))
            item_total = product.price * Decimal(str(quantity))
            item = {
                'product': product,
                'amount': quantity,
                'total': item_total
            }
            items.append(item)
            total_price += item_total
        except Product.DoesNotExist:
            del cart_data[product_id]
            request.session['cart'] = cart_data
            messages.warning(request, f'Товар с ID {product_id} больше не доступен')
            return redirect('checkout')
    
    if request.method == 'POST':
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        comment = request.POST.get('comment', '')
        
        if not address or not phone:
            messages.error(request, "Заполните все обязательные поля")
            return render(request, 'sheets/checkout.html', {
                'items': items,
                'total_price': float(total_price)  # Преобразуем в float
            })
        
        try:
            # Создаем заказ в сессии (преобразуем Decimal в строку)
            order_data = {
                'items': {str(k): v for k, v in cart_data.items()},
                'total_price': str(total_price),  # Преобразуем в строку
                'address': address,
                'phone': phone,
                'comment': comment,
                'created_at': datetime.now().isoformat()
            }
            request.session['order'] = order_data
            
            # Очищаем корзину
            request.session['cart'] = {}
            
            messages.success(request, f'Заказ успешно оформлен! Сумма: {total_price} ₽')
            return redirect('cart_view')
            
        except Exception as e:
            messages.error(request, f'Ошибка оформления заказа: {str(e)}')
            return render(request, 'sheets/checkout.html', {
                'items': items,
                'total_price': float(total_price)
            })
    
    context = {
        'items': items,
        'total_price': float(total_price)  # Преобразуем в float для шаблона
    }
    return render(request, 'sheets/checkout.html', context)

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                # Создаем пользователя
                user = form.save(commit=False)
                user.save()
                
                # Проверяем, есть ли уже профиль
                if not hasattr(user, 'profile'):
                    Profile.objects.create(user=user)
                
                login(request, user)
                messages.success(request, f'Добро пожаловать, {user.username}!')
                return redirect('catalog')
            except Exception as e:
                messages.error(request, f'Ошибка регистрации: {str(e)}')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            next_url = request.GET.get('next', 'catalog')
            return redirect(next_url)
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')
        return render(request, 'registration/login.html')

def user_logout(request):
    logout(request)
    messages.info(request, 'Вы вышли из аккаунта.')
    return redirect('home')

@login_required
def profile_view(request):
    profile = request.user.profile
    
    context = {
        'profile': profile,
    }
    return render(request, 'sheets/profile.html', context)

@login_required
def api_me_get(request):
    profile = request.user.profile
    data = {
        'id': request.user.id,
        'username': request.user.username,
        'email': request.user.email,
        'full_name': profile.full_name,
        'phone': profile.phone,
        'address': profile.address,
        'city': profile.city,
        'postal_code': profile.postal_code,
        'role': profile.role,
        'role_display': profile.get_role_display(),
        'is_admin': profile.is_admin(),
    }
    return JsonResponse(data)

@csrf_exempt
@login_required
def api_me_patch(request):
    if request.method != 'PATCH':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        data = json.loads(request.body)
        profile = request.user.profile
        fields = ['full_name', 'phone', 'address', 'city', 'postal_code']
        for field in fields:
            if field in data:
                setattr(profile, field, data[field])
        if 'email' in data:
            request.user.email = data['email']
            request.user.save()
        profile.save()
        return JsonResponse({'success': True, 'message': 'Профиль обновлен'})
    except:
        return JsonResponse({'error': 'Ошибка'}, status=400)



def api_products_list(request):
    """GET /api/products/ - список товаров (доступно всем)"""
    products = Product.objects.all()
    
    # Фильтры
    category = request.GET.get('category')
    if category:
        products = products.filter(category_id=category)
    
    search = request.GET.get('search')
    if search:
        products = products.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )
    
    data = []
    for p in products:
        data.append({
            'id': p.id,
            'title': p.title,
            'price': str(p.price),
            'amount_in_stock': p.amount_in_stock,
            'product_photo': p.product_photo.url if p.product_photo else None,
            'category': p.category.title if p.category else None,
            'manufacturer': p.manufacturer.title if p.manufacturer else None,
        })
    
    return JsonResponse(data, safe=False)

@csrf_exempt
@login_required
def api_product_create(request):
    """POST /api/products/create/ - создать товар (только ADMIN)"""
    # Проверка прав
    if not request.user.profile.is_admin():
        raise PermissionDenied('Только администратор может создавать товары')
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        category = Category.objects.get(id=data.get('category_id'))
        manufacturer = Manufacturer.objects.get(id=data.get('manufacturer_id'))
        
        product = Product.objects.create(
            title=data.get('title'),
            description=data.get('description', ''),
            price=data.get('price'),
            amount_in_stock=data.get('amount_in_stock', 0),
            category=category,
            manufacturer=manufacturer,
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Товар создан',
            'product_id': product.id
        }, status=201)
        
    except Category.DoesNotExist:
        return JsonResponse({'error': 'Категория не найдена'}, status=400)
    except Manufacturer.DoesNotExist:
        return JsonResponse({'error': 'Производитель не найден'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@login_required
def api_product_update(request, product_id):
    """PUT/PATCH /api/products/<id>/ - обновить товар (только ADMIN)"""
    if not request.user.profile.is_admin():
        raise PermissionDenied('Только администратор может изменять товары')
    
    if request.method not in ['PUT', 'PATCH']:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        product = get_object_or_404(Product, id=product_id)
        data = json.loads(request.body)
        
        # Обновляем поля
        if 'title' in data:
            product.title = data['title']
        if 'description' in data:
            product.description = data['description']
        if 'price' in data:
            product.price = data['price']
        if 'amount_in_stock' in data:
            product.amount_in_stock = data['amount_in_stock']
        if 'category_id' in data:
            product.category = Category.objects.get(id=data['category_id'])
        if 'manufacturer_id' in data:
            product.manufacturer = Manufacturer.objects.get(id=data['manufacturer_id'])
        
        product.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Товар обновлен',
            'product': {
                'id': product.id,
                'title': product.title,
                'price': str(product.price),
                'amount_in_stock': product.amount_in_stock,
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@login_required
def api_product_delete(request, product_id):
    """DELETE /api/products/<id>/ - удалить товар (только ADMIN)"""
    if not request.user.profile.is_admin():
        raise PermissionDenied('Только администратор может удалять товары')
    
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        product = get_object_or_404(Product, id=product_id)
        product.delete()
        return JsonResponse({
            'success': True,
            'message': 'Товар удален'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# ============ API: Заказы ============

@login_required
def api_orders_list(request):
    """GET /api/orders/ - список заказов"""
    if request.user.profile.is_admin():
        # Админ видит все заказы
        orders = Order.objects.all().order_by('-created_at')
    else:
        # Покупатель видит только свои
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    data = []
    for order in orders:
        data.append({
            'id': order.id,
            'created_at': order.created_at.strftime('%d.%m.%Y %H:%M'),
            'total_price': str(order.total_price),
            'address': order.address,
            'phone': order.phone,
            'comment': order.comment or '',
            'items_count': order.items.count() if hasattr(order, 'items') else 0,
            'is_my_order': order.user == request.user,
        })
    
    return JsonResponse(data, safe=False)

@login_required
def api_order_detail(request, order_id):
    """GET /api/orders/<id>/ - детали заказа"""
    order = get_object_or_404(Order, id=order_id)
    
    # Проверка прав: админ или владелец
    if not request.user.profile.is_admin() and order.user != request.user:
        raise PermissionDenied('У вас нет доступа к этому заказу')
    
    items = []
    for item in order.items.all():
        items.append({
            'product_title': item.product.title,
            'quantity': item.quantity,
            'price': str(item.price),
            'total': str(item.price * item.quantity),
        })
    
    data = {
        'id': order.id,
        'created_at': order.created_at.strftime('%d.%m.%Y %H:%M'),
        'total_price': str(order.total_price),
        'address': order.address,
        'phone': order.phone,
        'comment': order.comment or '',
        'items': items,
        'is_my_order': order.user == request.user,
    }
    
    return JsonResponse(data)

def handler403(request, exception):
    return JsonResponse({
        'error': 'Доступ запрещен',
        'detail': str(exception)
    }, status=403)

def api_cart_count(request):
    cart_data = request.session.get('cart', {})
    total = sum(cart_data.values())
    return JsonResponse({'count': total})

