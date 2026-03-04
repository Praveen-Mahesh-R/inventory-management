import django_tables2 as tables
from .models import *

class SupplierTable(tables.Table):
    class Meta:
        model = Supplier
        template_name = "django_tables2/bootstrap4.html"

class StockTable(tables.Table):
    class Meta:
        model = StockItems
        template_name = "django_tables2/bootstrap.html"

