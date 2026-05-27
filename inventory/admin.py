from django.contrib import admin
from django.apps import apps
from .models import *
from import_export import resources, fields

# Register your models here.
class ItemResource(resources.ModelResource):
    class Meta:
        model = StockItems
        fields = ('name','item_type__name','supplier__name','stock','quantity','cost_price','mrp','initial_date')

class CustomerResource(resources.ModelResource):
    class Meta:
        model = Customer
        exclude = 'profile_img'

# class HistoryResource(resources.ModelResource):
#     product_name = fields.Field(attribute="product_list__product_name", readonly=True)
#     product_unit = fields.Field(attribute="product_list__product_unit", readonly=True)
#     product_price = fields.Field(attribute="product_list__product_price", readonly=True)
#     class Meta:
#         model = PurchaseHistory
#         fields = ('product_name','product_unit','product_price','purchase_datetime')
#         export_order = ('purchase_datetime','product_name','product_unit','product_price')

    # def dehydrate_name(self.obj):
    #     return obj.



admin.site.register(City)
admin.site.register(State)
admin.site.register(Supplier)
admin.site.register(StockItems)
admin.site.register(Cart)
admin.site.register(Customer)
admin.site.register(PurchaseHistory)
admin.site.register(SupplierHistory)
admin.site.register(ItemType)
admin.site.register(ItemTypeCategory)