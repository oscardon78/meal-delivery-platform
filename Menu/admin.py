from django.contrib import admin
from django.contrib.auth.models import User
from .models import *
# Register your models here.

admin.site.register(Restaurant)
admin.site.register(Food)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Category)

admin.site.register(OrderInfo)

admin.site.register(Orders)