from django.urls import path,include
from . import views
# from inventory.views import Home

urlpatterns = [
    path('', views.home, name='home'),
    path('supermart/supplier', views.supplier_list, name="supplier_list"),
    path('supermart/stock/<str:type>', views.stock_list, name="stock_list"),
    path('supermart/new_item_add/', views.new_item_add, name="new_item_add"),
    path('supermart/add_stock/<int:pk>', views.add_stock, name="add_stock"),
    path('supermart/add_supplier/', views.add_supplier, name="add_supplier"),
    path('ajax/load-cities/', views.load_cities, name='ajax_load_cities'),
    path('supermart/logout/', views.logout_check, name="logout_check"),
    path('supermart/billing/', views.billing, name="billing"),
    path('checkout/', views.checkout, name="checkout"),
    path('clear_table/', views.clear_table, name="clear_table"),
    path('plus_units/<int:pk>', views.plus_units, name="plus_units"),
    path('minus_units/<int:pk>', views.minus_units, name="minus_units"),
]