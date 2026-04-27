
from .models import Product, Category, Manufacturer, Cart, Cart_item,Order,OrderItem
from django.contrib.auth import login
from io import BytesIO
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from .forms import CustomUserCreationForm
from openpyxl import Workbook
from django.core.mail import EmailMessage

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

@login_required
def add_to_cart(request, item_id):
    actual_id = item_id 
    product = get_object_or_404(Product, pk=actual_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, created = Cart_item.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'amount': 1}
    )

    if not created:
        cart_item.amount += 1
    else:
        cart_item.amount = 1

    cart_item.save()
    messages.success(request, f'{product.title} в корзине.')

    return redirect('cart_view')
@login_required
def cart_remove(request, item_id):
    actual_id = item_id
    cart = get_object_or_404(Cart,user=request.user)
    cartitem = get_object_or_404(Cart_item, cart=cart, product_id=actual_id)
    cartitem.delete()
    messages.success(request, f"{cartitem.product.title} удалён из корзины")
    return redirect('cart_view')

def cart_update(request, item_id):
    if request.method == "POST":
        amount = int(request.POST.get("amount",1))
        actual_id = item_id
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cartitem = get_object_or_404(Cart_item, cart=cart, product_id=actual_id)

        if amount > cartitem.product.amount_in_stock:
            messages.error(request, f"Максимальное количество для {cartitem.product.tiitle} — {cartitem.product.amount_in_stock}")
            amount = cartitem.product.amount_in_stock

        cartitem.amount = amount
        cartitem.save()
        messages.success(request, f"Количество {cartitem.product.title} обновлено до {cartitem.amount}")

    return redirect('cart_view')

@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = Cart_item.objects.filter(cart=cart)

    for item in items:
        item.total = item.product.price * item.amount

    total_price = sum(item.total for item in items)

    context = {
        'cart_items': items,
        'total_price': total_price
    }
    return render(request, 'sheets/cart.html', context)


@login_required
def checkout(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = Cart_item.objects.filter(cart=cart)

    if not items:
        messages.error(request, "Корзина пуста")
        return redirect('cart_view')

    # Считаем итоговую сумму с учетом количества каждого товара
    total_price = sum(item.product.price * item.amount for item in items)

    if request.method == 'POST':
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        comment = request.POST.get('comment')

        if not address or not phone:
            messages.error(request, "Заполните все обязательные поля")
            return render(request, 'sheets/checkout.html', {'items': items, 'total_price': total_price})

        # Создаем заказ
        order = Order.objects.create(
            user=request.user,
            address=address,
            phone=phone,
            comment=comment,
            total_price=total_price
        )

        # Создаем Excel-файл
        wb = Workbook()
        ws = wb.active
        ws.title = f"Заказ {order.id}"
        ws.append(["Товар", "Количество", "Цена за ед.", "Сумма"])
        
        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.amount,
                price=item.product.price
            )
            # Записываем в Excel (вызываем метод со скобками)
            ws.append([
                item.product.title,
                item.amount,
                item.product.price,
                item.item_price() 
            ])
            # Уменьшаем остаток на складе
            product = item.product
            product.amount_in_stock -= item.amount
            product.save()

        ws.append([])
        ws.append(["Итого", "", "", total_price])

        excel_file = BytesIO()
        wb.save(excel_file)
        excel_file.seek(0)

        # Подготовка письма
        subject = f"Заказ №{order.id}"
        message = f"Спасибо за заказ, {request.user.username}!\nСумма: {total_price} BYN."
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [request.user.email]

        if request.user.email:
            email = EmailMessage(subject, message, from_email, recipient_list)
            email.attach(f"check_{order.id}.xlsx", excel_file.getvalue(), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            
            # Оборачиваем отправку в try-except, чтобы сайт не падал
            try:
                email.send()
                messages.success(request, f"Заказ №{order.id} успешно оформлен! Чек отправлен.")
            except Exception as e:
                print(f"Ошибка почты: {e}")
                messages.warning(request, f"Заказ №{order.id} оформлен, но чек на почту не ушел.")
        else:
            messages.warning(request, f"Заказ №{order.id} оформлен, но у вас не указан email.")

        # ОЧИЩАЕМ КОРЗИНУ (теперь этот код сработает в любом случае)
        items.delete()
        return redirect('cart_view')

    context = {
        'items': items,
        'total_price': total_price
    }
    return render(request, 'sheets/checkout.html', context)


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            return redirect('catalog')
    else:
        form = CustomUserCreationForm()
    return render(request,'registration/register.html', {'form': form})