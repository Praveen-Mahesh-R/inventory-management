from django.contrib import admin
from django.apps import apps
from .models import *


# Register your models here.


admin.site.register(City)
admin.site.register(State)
admin.site.register(Supplier)
admin.site.register(StockItems)