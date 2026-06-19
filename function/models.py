from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

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
# function/models.py (добавьте в модель Profile)

class Profile(models.Model):
    ROLE_CHOICES = [
        ('CUSTOMER', 'Покупатель'),
        ('MANAGER', 'Менеджер'),
        ('ADMIN', 'Администратор'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField('Полное имя', max_length=200, blank=True)
    phone = models.CharField('Телефон', max_length=20, blank=True)
    address = models.TextField('Адрес', blank=True)
    city = models.CharField('Город доставки', max_length=100, blank=True)  
    postal_code = models.CharField('Индекс', max_length=20, blank=True)    
    favorite_category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Любимая категория')  
    role = models.CharField('Роль', max_length=20, choices=ROLE_CHOICES, default='CUSTOMER')
    avatar = models.ImageField('Аватар', upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField('Дата регистрации', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    
    def __str__(self):
        return f'{self.user.username} - {self.get_role_display()}'
    
    def is_admin(self):
        return self.role == 'ADMIN' or self.user.is_superuser
    
    def is_manager(self):
        return self.role in ['MANAGER', 'ADMIN'] or self.user.is_superuser
    
    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
