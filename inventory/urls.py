from django.urls import path,include
from . import views
# from inventory.views import Home

urlpatterns = [
    path('', views.home, name='home'),
    path('supermart/supplier', views.supplier_list, name="supplier_list"),
    path('supermart/stock/<str:type>', views.stock_list, name="stock_list"),
    path('supermart/stock/<str:type>/<int:bool_int>', views.stock_list, name="stock_list"),
    path('supermart/new_item_add/', views.new_item_add, name="new_item_add"),
    path('supermart/manage_item/<int:pk>', views.manage_item, name="manage_item"),
    path('supermart/item_edit/<int:pk>', views.item_edit, name="item_edit"),
    path('supermart/add_stock/<int:pk>', views.add_stock, name="add_stock"),
    path('supermart/remove_check/<int:pk>',views.remove_check, name="remove_check"),
    path('supermart/remove/<int:pk>',views.remove, name="remove"),
    path('supermart/restore_check/<int:pk>',views.restore_check, name="restore_check"),
    path('supermart/restore/<int:pk>',views.restore, name="restore"),
    path('supermart/add_supplier/', views.add_supplier, name="add_supplier"),
    path('ajax/load-cities/', views.load_cities, name='ajax_load_cities'),
    path('supermart/logout/', views.logout_check, name="logout_check"),
    path('supermart/billing/', views.billing, name="billing"),
    path('checkout/', views.checkout, name="checkout"),
    path('clear_table/', views.clear_table, name="clear_table"),
    path('plus_units/<int:pk>', views.plus_units, name="plus_units"),
    path('minus_units/<int:pk>', views.minus_units, name="minus_units"),
]