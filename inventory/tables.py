import django_tables2 as tables
from django_tables2.utils import A
from .models import *

class SupplierTable(tables.Table):
    class Meta:
        model = Supplier
        template_name = "django_tables2/bootstrap4.html"

class StockTable(tables.Table):
    class Meta:
        model = StockItems
        template_name = "django_tables2/bootstrap.html"
    add = tables.TemplateColumn(verbose_name="Add stock",template_code='<a href="{% url "add_stock" record.id %}" class="btn btn-success">Add</a>', orderable=False)

class cartTable(tables.Table):
    class Meta:
        model = Cart
        exclude = ('id',)
        template_name = "django_tables2/bootstrap.html"


