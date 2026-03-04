from django.shortcuts import render,redirect
# from .forms import PostForm
from .models import *
from .tables import *
from .forms import *
from django_tables2 import SingleTableView


# Create your views here.
def home(request):
    
    # fresh_produce_table = FreshProduceTable(Fresh_Produce.objects.all())
    # grains_table = GrainsTable(Grains.objects.all())
    # dairy_table = DairyTable(Dairy.objects.all())
    # condiments_table = CondimentTable(Condiments.objects.all())
    # snacks_table = SnacksTable(Snacks.objects.all())
    # beverages_table = BeveragesTable(Beverages.objects.all())
    # personal_care_table  = PersonalCareTable(Personal_Care.objects.all())
    # household_table = HouseholdTable(Household_Supplies.objects.all())
    # stationery_table = StationeryTable(Stationery.objects.all())

    return render(request, "inventory/home.html",{})

def supplier_list(request):
    supplier_table = SupplierTable(Supplier.objects.all())
    return render(request, "inventory/supplier_list.html",{"supplier_table":supplier_table,})

def stock_list(request,type):
    stock_table = StockTable(StockItems.objects.filter(type = type))
    return render(request, "inventory/stock_list.html",{"stock_table":stock_table, "type":type})

def new_item_add(request):
    if request.method == "POST":
        form = StockForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.save()
            return redirect('stock_list', type = item.type)
    else:
        form = StockForm()
    return render(request, "inventory/new_item_add.html",{'form': form})
