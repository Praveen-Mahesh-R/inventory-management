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
        exclude = ('id','is_deleted',)
        template_name = "django_tables2/bootstrap4.html"
    manage = tables.TemplateColumn(verbose_name="Manage",template_code='{% load static %}<a href="{% url "manage_item" record.id %}"> <img src="{% static \'icons/gear-fill.svg\' %}" </a>', orderable=False)
    restore = tables.TemplateColumn(verbose_name="Restore",template_code='{% load static %}<a href="{% url "restore_check" record.id %}"> <img src="{% static \'icons/restore-svgrepo-com.svg\' %}" width="30" height="30"> </a>', orderable=False)

    

class cartTable(tables.Table):
    class Meta:
        model = Cart
        exclude = ('id','supplier')
        template_name = "django_tables2/bootstrap.html"
    plus = tables.TemplateColumn(verbose_name="", template_code='{% load static %}<a href="{% url "plus_units" record.id %}"> <img src="{% static \'icons/plus-square.svg\' %}" </a>')
    minus = tables.TemplateColumn(verbose_name="", template_code='{% load static %}<a href="{% url "minus_units" record.id %}"> <img src="{% static \'icons/dash-square.svg\' %}" </a>')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.columns['plus'].column.attrs = {"td":{"style" : "width:1%;" }}
        self.columns['minus'].column.attrs = {"td":{"style" : "width:1%;" }}

