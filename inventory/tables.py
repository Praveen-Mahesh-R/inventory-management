import django_tables2 as tables
from django_tables2.utils import A
from django_tables2.columns import JSONColumn
from .models import *
from django.utils.safestring import mark_safe
from django.shortcuts import get_object_or_404

class SupplierTable(tables.Table):
    class Meta:
        model = Supplier
        template_name = "django_tables2/bootstrap4.html"
    edit = tables.TemplateColumn(verbose_name="Edit",template_code='{% load static %}<a href="{% url "edit_supplier" record.id %}"> <img src="{% static \'icons/pencil-square.svg\' %}" </a>', orderable=False)

class StockTable(tables.Table):
    class Meta:
        model = StockItems
        exclude = ('id','is_deleted',)
        template_name = "django_tables2/bootstrap4.html"
    manage = tables.TemplateColumn(verbose_name="Manage",template_code='{% load static %}<a href="{% url "manage_item" record.id %}"> <img src="{% static \'icons/gear-fill.svg\' %}" </a>', orderable=False)
    restore = tables.TemplateColumn(verbose_name="Restore",template_code='{% load static %}<a href="{% url "restore_check" record.id %}"> <img src="{% static \'icons/restore-svgrepo-com.svg\' %}" width="30" height="30"> </a>', orderable=False)

class CustomerTable(tables.Table):
    class Meta:
        model = Customer
        template_name = "django_tables2/bootstrap4.html"
    edit = tables.TemplateColumn(verbose_name="Edit",template_code='{% load static %}<a href="{% url "edit_customer" record.id %}"> <img src="{% static \'icons/pencil-square.svg\' %}" </a>', orderable=False)
    

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

# class ProductListTable(tables.Table):
#     product_name = tables.Column()
#     product_unit = tables.Column()
#     product_price = tables.Column()


class HistoryTable(tables.Table):
    customer_name = tables.Column(empty_values=())
    product_list = tables.TemplateColumn(template_code='<a href="{% url "cart_list" record.id %}" style="text-decoration: underline;">Check Cart </a>')
    class Meta:
        model = PurchaseHistory
        template_name = "django_tables2/bootstrap4.html"
        exclude = ("id",)
        order_by = ("-purchase_datetime",)
        sequence = ('customer_no','customer_name','...')
    
    def render_customer_name(self,record):
        customer = get_object_or_404(Customer, phone_no = record.customer_no)
        return customer.name
    
    

