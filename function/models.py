from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

class Light(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    description = models.TextField(verbose_name="Описание")

def __str__(self):
    return self.title

class Category(models.Model):
    title = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(blank=True)
    def __str__(self):
        return self.title

class Product(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    product_photo = models.ImageField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    amount_in_stock = models.IntegerField(validators=[MinValueValidator(0)])#количество на складе
    category = models.ForeignKey('Category', on_delete = models.CASCADE)#связь с категорией
    manufacturer = models.ForeignKey('Manufacturer', on_delete = models.CASCADE)#связь с производителем


    def __str__(self):
        return self.title

class Manufacturer(models.Model):
    title = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"Корзина пользователя {self.user.username}"
    
    def total_price(self):
        return sum(item.item_price() for item in self.items.all())

class Cart_item(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name="Корзина")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    amount = models.PositiveIntegerField(default=1, verbose_name="Количество")

    def __str__(self):
        return f"{self.product.title} — {self.amount} шт."
    def item_price(self):
        return self.product.price * self.amount
    def clean(self):
        if self.amount > self.product.stock:
            raise ValidationError("Нету такого количества в наличии")

class Order(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,verbose_name="Пользователь")
    date_creation = models.DateTimeField(auto_now_add=True,verbose_name="Дата_создания")
    address = models.CharField(max_length=500,verbose_name="Адрес_доставки")
    phone = models.CharField(max_length=20,verbose_name="Телефон")
    comment = models.TextField(blank=True,verbose_name="Комментарий")
    total_price = models.DecimalField(max_digits=10,decimal_places=2,verbose_name="Общая стоимость")

    def __str__(self):
        return  f"Заказ №{self.id} от {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE,related_name='items',verbose_name='Заказ')
    product = models.ForeignKey(Product,on_delete=models.CASCADE,verbose_name="Товары")
    quantity = models.PositiveIntegerField(verbose_name="Количество")
    price = models.DecimalField(max_digits=10,decimal_places=2,verbose_name="Цена")
