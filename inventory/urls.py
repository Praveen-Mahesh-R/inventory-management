from django.urls import path
from . import views
# from inventory.views import Home

urlpatterns = [
    path('', views.home, name='home'),
    path('supermart/supplier', views.supplier_list, name="supplier_list"),
    path('supermart/stock/<str:type>', views.stock_list, name="stock_list"),
    path('supermart/new_item_add/', views.new_item_add, name="new_item_add")
]