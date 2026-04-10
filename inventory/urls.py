from django.urls import path,include
from . import views
# from inventory.views import Home

urlpatterns = [
    path('', views.home, name='home'),
    path('supermart/supplier', views.supplier_list, name="supplier_list"),
    # path('supermart/s', views.product, name="products"),
    path('supermart/stock/', views.stock_list, name="stock_list"),
    path('supermart/stock/<str:type>', views.stock_list, name="stock_list"),
    path('supermart/purchase_history',views.history_list, name="history_list"),
    path('supermart/supply_history',views.supply_history, name="supply_history"),
    path('supermart/customer', views.customer_list, name="customer_list"),
    path('supermart/stock/<int:bool_int>', views.stock_list, name="stock_list"),
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
    path('supermart/edit_supplier/<int:pk>', views.edit_supplier, name="edit_supplier"),

    path('supermart/new_customer/', views.new_customer, name="new_customer"),
    path('supermart/edit_customer/<int:pk>', views.edit_customer, name="edit_customer"),
    
    path('supermart/manage_category',views.manage_category,name="manage_category"),
    path('supermart/manage_category/<int:is_disabled>',views.manage_category,name="manage_category"),

    path('supermart/add_main_category',views.add_main_category,name="add_main_category"),
    path('supermart/edit_main_category/<int:pk>',views.edit_main_category,name="edit_main_category"),
    
    path('supermart/add_sub_category',views.add_sub_category,name="add_sub_category"),
    path('supermart/edit_sub_category/<int:pk>',views.edit_sub_category,name="edit_sub_category"),

    path('supermart/remove_check_category/<int:pk>',views.remove_check_category, name="remove_check_category"),
    path('supermart/remove_category/<int:pk>',views.remove_category, name="remove_category"),
    
    path('supermart/restore_check_category/<int:pk>',views.restore_check_category, name="restore_check_category"),
    path('supermart/restore_category/<int:pk>',views.restore_category, name="restore_category"),
    path('ajax/load-cities/', views.load_cities, name='ajax_load_cities'),
    
    path('supermart/logout/', views.logout_check, name="logout_check"),
    
    path('supermart/billing/', views.billing, name="billing"),
    
    path('cart_list/<int:pk>',views.cart_list, name="cart_list"),
    path('clear_table/', views.clear_table, name="clear_table"),
    path('plus_units/<int:pk>', views.plus_units, name="plus_units"),
    path('minus_units/<int:pk>', views.minus_units, name="minus_units"),

    path('supermart/<str:supplier>/restock/', views.supplier_restock, name="supplier_restock"),
    
    path('supply_cart_list/<int:pk>',views.supply_cart_list, name="supply_cart_list"),

    path('add_to_cart/<int:pk>', views.add_to_cart, name="add_to_cart"),
    path('units_amount/<int:pk>', views.units_amount, name="units_amount"),
    path('supermart/<str:supplier>/checkout/', views.supplier_checkout, name="supplier_checkout"),
    path('clear_supply_table/<str:supplier>', views.clear_supply_table, name="clear_supply_table"),
    path('delete_item/<int:pk>', views.delete_item, name="delete_item"),
]