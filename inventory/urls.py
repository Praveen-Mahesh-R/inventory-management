from django.urls import path,include
from . import views

from django.conf import settings
from django.conf.urls.static import static
# from inventory.views import Home
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('', views.home, name='home'),
    path('supermart/supplier', views.supplier_list, name="supplier_list"),
  
    path('supermart/stock/', views.stock_list, name="stock_list"),
    path('supermart/stock/<str:type>', views.stock_list, name="stock_list"),
    path('supermart/purchase_history',views.history_list, name="history_list"),
    path('supermart/supply_history',views.supply_history, name="supply_history"),
    path('supermart/customer', views.customer_list, name="customer_list"),
    path('supermart/stock/<int:bool_int>', views.stock_list, name="stock_list"),
    path('supermart/stock/<str:type>/<int:bool_int>', views.stock_list, name="stock_list"),

    path('supermart/new_item_add/<int:t>', views.new_item_add, name="new_item_add"),
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
    path('units_amount/<int:pk>', views.units_amount, name="units_amount"),
    
    path('cart_list/<int:pk>',views.cart_list, name="cart_list"),
    path('clear_table/', views.clear_table, name="clear_table"),
    path('plus_units/<int:pk>', views.plus_units, name="plus_units"),
    path('minus_units/<int:pk>', views.minus_units, name="minus_units"),

    path('supermart/<str:supplier>/restock/', views.supplier_restock, name="supplier_restock"),
    
    path('supply_cart_list/<int:pk>',views.supply_cart_list, name="supply_cart_list"),

    path('add_to_cart/<int:pk>', views.add_to_cart, name="add_to_cart"),
    path('units_amount/<int:pk><str:supplier>', views.units_amount, name="units_amount"),
    path('supermart/<str:supplier>/checkout/', views.supplier_checkout, name="supplier_checkout"),
    path('clear_supply_table/<str:supplier>', views.clear_supply_table, name="clear_supply_table"),
    path('delete_item/<int:pk>', views.delete_item, name="delete_item"),

    path('supermart/add_new_product',views.add_new_product,name="add_new_product"),

    path('import_data_to_db/', views.import_data_to_db, name="import_data_to_db"),
    path('edit_data_to_db/', views.edit_data_to_db, name="edit_data_to_db"),

    path('restock_items_bulk/', views.restock_items_bulk, name="restock_items_bulk"),
    # path('product_excel_export/', views.product_excel_export, name="product_excel_export"),
    path('product_csv_export/', views.product_csv_export, name="product_csv_export"),

    path('supermart/manage_customer/<int:pk>', views.manage_customer, name="manage_customer"),
    path('customer_purchase_csv_export/<int:pk>', views.customer_purchase_csv_export, name="customer_purchase_csv_export"),
    path('customer_csv_export/', views.customer_csv_export, name="customer_csv_export"),

    path('customer_export/', views.customer_export, name="customer_export"),

    path('customer_purchase_export/<int:pk>', views.customer_purchase_export, name="customer_purchase_export"),

    path('customer_excel_export/', views.customer_excel_export, name="customer_excel_export"),
    path('product_excel_export/', views.product_excel_export, name="product_excel_export"),
    path('customer_purchase_excel_export/<int:pk>', views.customer_purchase_excel_export, name="customer_purchase_excel_export"),
    

    path('customer_pdf_report/<int:pk>', views.customer_pdf_report, name="customer_pdf_report"),
    path('sales_pdf_report/', views.sales_pdf_report, name="sales_pdf_report"),

    path('supplier_csv_export/', views.supplier_csv_export, name="supplier_csv_export"),

    path('supply_pdf_report/', views.supply_pdf_report, name="supply_pdf_report"),

    path('supermart/item_details/<int:pk>', views.item_details, name="item_details"),
    path('supermart/barcode_scanner/', views.barcode_scanner, name="barcode_scanner"),
    path('supermart/barcode_scanner/<int:exists>', views.barcode_scanner, name="barcode_scanner"),
]

# if settings.DEBUG:
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)