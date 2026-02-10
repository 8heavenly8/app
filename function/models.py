from django.db import models
from django.core.validators import MinValueValidator

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
    amount_in_stock = models.IntegerField(validators=[MinValueValidator(0)])
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

