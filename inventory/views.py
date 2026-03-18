from django.shortcuts import render,redirect, get_object_or_404
# from .forms import PostForm
from .models import *
from .tables import *
from .forms import *
from django_tables2 import SingleTableView
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.db import IntegrityError
from django.core.exceptions import MultipleObjectsReturned
from datetime import date


# Create your views here.
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        username = request.POST['username']
        password = request.POST['password']
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home') # Replace 'home' with your success URL name
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})

def logout_check(request):
    return render(request, 'registration/logout.html', {})



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

@login_required
def supplier_list(request):
    supplier_table = SupplierTable(Supplier.objects.all())
    return render(request, "inventory/supplier_list.html",{"supplier_table":supplier_table,})

@login_required
def stock_list(request,type, bool_int = 0):
    excluded_columns = ()
    if bool_int:
        excluded_columns = ('manage',)
    else:
        excluded_columns = ('restore',)
    stock_table = StockTable(StockItems.objects.filter(type = type, is_deleted = bool(bool_int)),exclude=excluded_columns)
    
        
    return render(request, "inventory/stock_list.html",{"stock_table":stock_table, "type":type})

@login_required
def new_item_add(request):
    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            if item.initial_date is None:
                item.initial_date = date.today()
            if item.restock_date is None:
                item.restock_date = date.today()
            item.save()
            return redirect('stock_list', type = item.type)
        print(form.is_valid())
    else:
        form = ItemForm()
    return render(request, "inventory/new_item_add.html",{'form': form})

@login_required
def manage_item(request,pk):
    return render(request, "inventory/manage_item.html",{'pk':pk})

def item_edit(request, pk):
    item = get_object_or_404(StockItems, pk=pk)
    if request.method == "POST":
        form = ItemForm(request.POST, instance=item)
        print("Hi")
        if form.is_valid():
            item = form.save(commit=False)
            if item.initial_date is None:
                item.initial_date = date.today()
            item.save()
            print("Hello")
            return redirect('stock_list', type = item.type)
        print(request.POST)
    else:
        form = ItemForm(instance=item)
    return render(request, "inventory/item_edit.html",{'form': form})

@login_required
def add_stock(request,pk):
    obj = get_object_or_404(StockItems,pk=pk)
    if request.method == "POST":
        form = StockForm(request.POST,request.FILES)
        if form.is_valid():
            stock = form.cleaned_data
            obj.stock = obj.stock + stock["amount"]
            obj.restock_date = date.today()
            obj.save()
            return redirect('stock_list', type = obj.type)
    else:
        form = StockForm()
    return render(request, "inventory/add_stock.html",{'form': form})

@login_required
def add_supplier(request):
    if request.method == "POST":
        form = SupplierForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.save()
            return redirect('supplier_list')
    else:
        form = SupplierForm()
    return render(request, "inventory/supplier_add.html",{'form': form})

@login_required
def billing(request):
    items = StockItems.objects.all()
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            supplier = item.item.supplier
            stock = StockItems.objects.get(name=item.item, supplier = supplier)
            price = stock.cost
            item.price = item.total_price = price
            try:
                item.save()
            except IntegrityError as e:
                message = "Already there"
            return redirect('billing',)
    form = SearchForm()
    cart_table = cartTable(Cart.objects.all())
    total_cost = Cart.objects.aggregate(Sum('total_price'))
    print("hi")
    return render(request, "inventory/billing_page.html",{'form':form, 'cart_table':cart_table, 'total_cost': total_cost})

@login_required
def checkout(request):
    for cart in Cart.objects.all():
        cart_units = cart.units
        stock_list = get_object_or_404(StockItems, pk = cart.item.pk)
        if stock_list.stock < cart_units:
            messages.warning(request, "Not Enough Stock")
            return redirect('billing')
        stock_list.stock = stock_list.stock - cart_units
    stock_list.save()
    messages.success(request,"Purchase Successfull!!")
    # Cart.objects.all().delete()
    return redirect('home')

@login_required
def remove_check(request,pk):
    return render(request, "inventory/remove_check.html",{'pk': pk})

@login_required
def restore_check(request,pk):
    return render(request, "inventory/restore_check.html",{'pk': pk})

def remove(request,pk):
    obj = get_object_or_404(StockItems,pk=pk)
    type = obj.type
    obj.is_deleted = True
    obj.save()
    return redirect('stock_list', type = type)

def restore(request,pk):
    obj = get_object_or_404(StockItems,pk=pk)
    type = obj.type
    obj.is_deleted = False
    obj.save()
    return redirect('stock_list', type = type)
    

def clear_table(request):
    Cart.objects.all().delete()
    return redirect('billing')

def plus_units(request, pk):
    obj = get_object_or_404(Cart,pk=pk)
    obj.units = obj.units + 1
    obj.total_price =  obj.price * obj.units
    obj.save()
    return redirect('billing')

def minus_units(request, pk):
    obj = get_object_or_404(Cart,pk=pk)
    if obj.units > 1:
        obj.units = obj.units - 1
        obj.total_price =  obj.price * obj.units
        obj.save()
    else:
        Cart.objects.filter(pk=pk).delete()
    return redirect('billing')

@login_required
def load_cities(request):
    state_id = request.GET.get('state')
    cities = City.objects.filter(state_id=state_id).all()
    return render(request, 'inventory/city_list.html', {'cities': cities})





