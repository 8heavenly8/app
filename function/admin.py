from django.contrib import admin
from .models import *
from .models import Cart, Cart_item

admin.site.register(Light)
admin.site.register(Category)
admin.site.register(Manufacturer)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(Cart_item)
# Register your models here.
