from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings
from django.core.exceptions import ValidationError

class Light(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    description = models.TextField(verbose_name="Описание")

def __str__(self):
    return self.title

class Category(models.Model):
    title = models.CharField(max_length=100, verbose_name="Название")
    discription = models.TextField(blank=True)
    def __str__(self):
        return self.title

class Product(models.Model):
    title = models.CharField(max_length=200)
    discriprion = models.TextField()
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
    discription = models.TextField(blank=True)

    def __str__(self):
        return self.title

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,verbose_name="Пользователь")
    creation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Корзина пользователя {self.user}"
    
    def total_cost(self):#доделать вычисление сумму стоимости всех элементов корзины (см. модель "Элемент корзины")
        return sum(item.item_cost() for item in self.cart_item_set.all())

class Cart_item(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, verbose_name="Корзина")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    amount = models.PositiveIntegerField(default=1, verbose_name="Количество")#помогите не понимаю как сделать связь с товарами

    def __str__(self):
        return f"{self.product.title} ({self.amount} шт.)"#тут тоже не уверена что должно быть так
    
    def item_cost(self):
        return self.product.price * self.amount

    def clean(self):
        # Валидация: проверка остатка на складе (поле amount_in_stock из Product)
        if self.amount > self.product.amount_in_stock:
            raise ValidationError(f"На складе всего {self.product.amount_in_stock} шт. товара {self.product.title}")

    def save(self, *args, **kwargs):
        self.full_clean() # Чтобы валидация clean() работала при сохранении
        super().save(*args, **kwargs)