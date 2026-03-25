from django.shortcuts import render,redirect, get_object_or_404
# from .forms import PostForm
from .models import *
from .tables import *
from .forms import *
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.db import IntegrityError
from datetime import date
from json2html import *


#login view
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

#logout page view
def logout_check(request):
    return render(request, 'registration/logout.html', {})


#default home page view
def home(request):
    return render(request, "inventory/home.html",{})


#Views of all the table pages in website

#Table of supplier
@login_required
def supplier_list(request):
    supplier_table = SupplierTable(Supplier.objects.all())
    return render(request, "inventory/supplier_list.html",{"supplier_table":supplier_table,})

#Table of items (including deleted items)
@login_required
def stock_list(request,type, bool_int = 0):
    excluded_columns = ()
    if bool_int:
        excluded_columns = ('manage',)
    else:
        excluded_columns = ('restore',)
    stock_table = StockTable(StockItems.objects.filter(item_type__code__contains = type, is_deleted = bool(bool_int)),exclude=excluded_columns)
    
        
    return render(request, "inventory/stock_list.html",{"stock_table":stock_table, "type":type})

#Table of past purchase history
@login_required
def history_list(request):
    history_table = HistoryTable(PurchaseHistory.objects.all())
    
    return render(request, "inventory/history_list.html",{"history_table":history_table,})

#Table of past purchase history items (accessed through the above table)
@login_required
def cart_list(request,pk):
    obj = get_object_or_404(PurchaseHistory,pk=pk)
    product = zip(obj.product_list['product_name'],obj.product_list['product_unit'],obj.product_list['product_price'])
    print(obj.product_list['product_name'])
    context = {
        'product':product,
        'total':obj.total_cost
    }
    return render(request, "inventory/product_list.html", context)

#Table of customer
@login_required
def customer_list(request):
    customer_table = CustomerTable(Customer.objects.all())
    return render(request, "inventory/customer_list.html",{"customer_table":customer_table,})


#Views to add new or edit content in database

#Adding new item to inventory catalogue
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
            return redirect('stock_list', type = item.item_type.code)
        print(form.is_valid())
    else:
        form = ItemForm()
    return render(request, "inventory/new_item_add.html",{'form': form})

#Page to view and select various functions regarding inventory item
@login_required
def manage_item(request,pk):
    return render(request, "inventory/manage_item.html",{'pk':pk})

#Editng details of existing item in catalogue
@login_required
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
            return redirect('stock_list', type = item.item_type.code)
        print(request.POST)
    else:
        form = ItemForm(instance=item)
    return render(request, "inventory/item_edit.html",{'form': form})

#Replenishing stock of an item in inventory
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
            return redirect('stock_list', type = obj.item_type.code)
    else:
        form = StockForm()
    return render(request, "inventory/add_stock.html",{'form': form})

#Adding new supplier to database
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

#Editing existing supplier details
@login_required
def edit_supplier(request,pk):
    item = get_object_or_404(Supplier, pk=pk)
    if request.method == "POST":
        form = SupplierForm(request.POST, instance=item)
        if form.is_valid():
            item = form.save(commit=False)
            item.save()
            return redirect('supplier_list')
    else:
        form = SupplierForm(instance=item)
    return render(request, "inventory/supplier_add.html",{'form': form})

#Adding new customer to database
@login_required
def new_customer(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.save()
            return redirect('customer_list')
    else:
        form = CustomerForm()
    return render(request, "inventory/customer_form.html",{'form': form})

#Editing existing customer details
@login_required
def edit_customer(request, pk):
    item = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        form = CustomerForm(request.POST, instance=item)
        if form.is_valid():
            item = form.save(commit=False)
            item.save()
            return redirect('customer_list')
    else:
        form = CustomerForm(instance=item)
    return render(request, "inventory/customer_form.html",{'form': form})


#Other views

#Billing page to add items to cart and purchasing them
@login_required
def billing(request,):
    items = StockItems.objects.all()
    if request.method == "POST":
        form = SearchForm(request.POST)
        cform = PhoneForm(request.POST)
        if 'submit_item' in request.POST:    
            if form.is_valid():
                item = form.save(commit=False)
                supplier = item.item.supplier
                stock = StockItems.objects.get(name=item.item, supplier = supplier)
                price = stock.cost
                item.price = item.total_price = price
                try:
                    item.save()
                except IntegrityError:
                    form.add_error('item','Already there')
                    print("Already there ---------------------------")
                return redirect('billing',)
        else:
            form = SearchForm()
        if 'submit_customer' in request.POST:  
            if cform.is_valid():
                cust_form = cform.cleaned_data
                name_list = []
                unit_list = []
                price_list = []
                for cart in Cart.objects.all():
                    cart_units = cart.units
                    
                    stock_list = get_object_or_404(StockItems, pk = cart.item.pk)
                    if stock_list.stock < cart_units:
                        messages.warning(request, "Not Enough Stock")
                        return redirect('billing')
                    print(cart.item)
                    name_list.append(cart.item.name)
                    unit_list.append(cart.units)
                    price_list.append(cart.price)
                    stock_list.stock = stock_list.stock - cart_units

                customer = get_object_or_404(Customer, phone_no = cust_form['phone_no'])
                json_data = {
                    "product_name":name_list,
                    "product_unit":unit_list,
                    "product_price":price_list
                }
                total_cost = Cart.objects.aggregate(Sum('total_price'))['total_price__sum']
                PurchaseHistory.objects.create(
                    customer_no = customer.phone_no,
                    product_list = json_data,
                    total_cost = total_cost
                    
                )
                stock_list.save()
                messages.success(request,"Purchase Successfull!!")
                return redirect('cart_list', pk=PurchaseHistory.objects.last().pk)
        else:
            cform = PhoneForm()
    else:        
        form = SearchForm()
        cform = PhoneForm()
    print(cform.errors)
    cart_table = cartTable(Cart.objects.all())
    total_cost = Cart.objects.aggregate(Sum('total_price'))
    
    return render(request, "inventory/billing_page.html",{'form':form, 'cform':cform, 'cart_table':cart_table, 'total_cost': total_cost,})


#Page asking confirmation on deleting an item from catalogue
@login_required
def remove_check(request,pk):
    return render(request, "inventory/remove_check.html",{'pk': pk})

#Page asking confirmation on restoring an item into catalogue
@login_required
def restore_check(request,pk):
    return render(request, "inventory/restore_check.html",{'pk': pk})

#Deletes item from inventory table
@login_required
def remove(request,pk):
    obj = get_object_or_404(StockItems,pk=pk)
    type = obj.item_type.code
    obj.is_deleted = True
    obj.save()
    return redirect('stock_list', type = type)

#Restores item back into inventory table
@login_required
def restore(request,pk):
    obj = get_object_or_404(StockItems,pk=pk)
    type = obj.item_type.code
    obj.is_deleted = False
    obj.save()
    return redirect('stock_list', type = type)
    
#Deletes all items in cart table
@login_required
def clear_table(request):
    Cart.objects.all().delete()
    return redirect('billing')

#Adds one more unit of an item added into cart
@login_required
def plus_units(request, pk):
    obj = get_object_or_404(Cart,pk=pk)
    obj.units = obj.units + 1
    obj.total_price =  obj.price * obj.units
    obj.save()
    return redirect('billing')

#Subtracts one unit from item added to cart if the unit count is more than 1, else deletes the item from cart
@login_required
def minus_units(request, pk):
    obj = get_object_or_404(Cart,pk=pk)
    if obj.units > 1:
        obj.units = obj.units - 1
        obj.total_price =  obj.price * obj.units
        obj.save()
    else:
        Cart.objects.filter(pk=pk).delete()
    return redirect('billing')

#Loads dropdown-list of city based on the state seleted in supplier form
@login_required
def load_cities(request):
    state_id = request.GET.get('state')
    cities = City.objects.filter(state_id=state_id).all()
    return render(request, 'inventory/city_list.html', {'cities': cities})




