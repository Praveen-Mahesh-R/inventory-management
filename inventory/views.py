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
from datetime import date, datetime, timedelta
from json2html import *
from django_tables2 import RequestConfig
from django.db.models import Q

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
    startdate = datetime.today()
    startdate -= timedelta(days=startdate.weekday())
    enddate = startdate + timedelta(days=6)
    sold = PurchaseHistory.objects.filter(purchase_datetime__range=[startdate,enddate])
    bought = SupplierHistory.objects.filter(purchase_datetime__range=[startdate,enddate])
    revenue = 0
    for cart in sold:
        revenue = revenue + cart.total_cost
    spent = 0
    for cart in bought:
        spent = spent + cart.total_cost
    context = {
        'revenue': revenue,
        'spent': spent
    }
    return render(request, "inventory/home.html",context)


#Views of all the table pages in website

#Table of supplier
@login_required
def supplier_list(request):
    supplier_table = SupplierTable(Supplier.objects.all())
    query = request.GET.get("q", None)
    if query:
        supplier_table = SupplierTable(Supplier.objects.filter(
            Q(name__icontains = query)|Q(city__name__icontains = query)|Q(state__name__icontains = query)|Q(phone_no__icontains = query)
        ))
    RequestConfig(request).configure(supplier_table)
    supplier_table.paginate(page=request.GET.get("page", 1), per_page=10)
    return render(request, "inventory/supplier_list.html",{"supplier_table":supplier_table,})

#Table of items (including deleted items)
@login_required
def stock_list(request,type = "all", bool_int = 0):
    excluded_columns = ()
    if bool_int:
        excluded_columns = ('manage',)
    else:
        excluded_columns = ('restore',)
    query = request.GET.get("q", None)
    if type != "all":
        stock_table = StockTable(StockItems.objects.filter(item_type__code__contains = type, is_deleted = bool(bool_int)),exclude=excluded_columns)
        if query:
            stock_table = StockTable(StockItems.objects.filter(
                Q(name__icontains = query)|Q(supplier__name__icontains = query)
            ).filter(item_type__code__contains = type, is_deleted = bool(bool_int)),exclude=excluded_columns)
    
    else:
        stock_table = StockTable(StockItems.objects.filter(is_deleted = bool(bool_int)),exclude=excluded_columns)
        if query:
            stock_table = StockTable(StockItems.objects.filter(
                Q(name__icontains = query)|Q(supplier__name__icontains = query)
            ).filter(is_deleted = bool(bool_int)),exclude=excluded_columns)
    RequestConfig(request).configure(stock_table)
    stock_table.paginate(page=request.GET.get("page", 1), per_page=10)
    typelist = ItemType.objects.filter(is_disabled=False).order_by('category')  
    category = ItemTypeCategory.objects.all().order_by('pk') 
    return render(request, "inventory/stock_list.html",{"stock_table":stock_table, "typelist":typelist, "type":type, "categories":category})

#Table of past purchase history
@login_required
def history_list(request):
    history_table = HistoryTable(PurchaseHistory.objects.all())
    history_table.paginate(page=request.GET.get("page", 1), per_page=5)
    customer_history = True
    return render(request, "inventory/history_list.html",{"history_table":history_table, 'customer_history':customer_history})

#Table of past purchase history items (accessed through the above table)
@login_required
def cart_list(request,pk):
    obj = get_object_or_404(PurchaseHistory,pk=pk)
    product = zip(obj.product_list['product_name'],obj.product_list['product_unit'],obj.product_list['product_price'])
    context = {
        'product':product,
        'total':obj.total_cost
    }
    return render(request, "inventory/product_list.html", context)

@login_required
def supply_history(request):
    history_table = SupplyHistoryTable(SupplierHistory.objects.all())
    history_table.paginate(page=request.GET.get("page", 1), per_page=5)
    return render(request, "inventory/history_list.html",{"history_table":history_table,})

#Table of past purchase history items (accessed through the above table)
@login_required
def supply_cart_list(request,pk):
    obj = get_object_or_404(SupplierHistory,pk=pk)
    product = zip(obj.product_list['product_name'],obj.product_list['product_unit'],obj.product_list['product_price'])
    supplier_cart = True
    context = {
        'product':product,
        'total':obj.total_cost,
        'supplier_cart':supplier_cart
    }
    return render(request, "inventory/product_list.html", context)
#Table of customer
@login_required
def customer_list(request):
    customer_table = CustomerTable(Customer.objects.all())
    query = request.GET.get("q", None)
    if query:
        customer_table = CustomerTable(Customer.objects.filter(
            Q(name__icontains = query)|Q(phone_no__icontains = query)
        ))
    RequestConfig(request).configure(customer_table)
    customer_table.paginate(page=request.GET.get("page", 1), per_page=8)
    return render(request, "inventory/customer_list.html",{"customer_table":customer_table,})


#Views to add new or edit content in database

#Adding new item to inventory catalogue
@login_required
def new_item_add(request):
    if request.method == "POST":
        form = ItemForm(request.POST)
        form.fields.pop('restock_date')
        if form.is_valid():
            item = form.save(commit=False)
            item.stock = 0
            # if item.initial_date is None:
            #     item.initial_date = date.today()
            # if item.restock_date is None:
            #     item.restock_date = date.today()
            item.save()
            return redirect('stock_list', type = item.item_type.code)
    else:
        form = ItemForm()
        form.fields.pop('restock_date')
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
        if form.is_valid():
            item = form.save(commit=False)
            if item.initial_date is None:
                item.initial_date = date.today()
            item.save()
            return redirect('stock_list', type = item.item_type.code)
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
            name_list = []
            unit_list = []
            price_list = []
            total = stock['amount']*obj.cost_price
            name_list.append(obj.name)
            unit_list.append(stock["amount"])
            price_list.append(obj.cost_price)
            json_data = {
                "product_name":name_list,
                "product_unit":unit_list,
                "product_price":price_list
            }
            SupplierHistory.objects.create(
                supplier_name = obj.supplier.name,
                product_list = json_data,
                total_cost = total)
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

#Billing page to add items to cart and purchasing them (for customers)
@login_required
def billing(request,):
    if request.method == "POST":
        form = SearchForm(request.POST)
        cform = PhoneForm(request.POST)
        if 'submit_item' in request.POST:  
            if form.is_valid():
                item = form.cleaned_data['item']
                counter = StockItems.objects.filter(name = item).count()
                if counter == 1:
                    stock = get_object_or_404(StockItems,name = item)
                else:
                    price = 999999999
                    for item in StockItems.objects.filter(name = item, is_deleted = False):
                        if item.stock > 0:
                            if item.mrp < price:
                                price = item.mrp
                                pk = item.pk
                    stock = get_object_or_404(StockItems,pk = pk)
                    
                
                price = stock.mrp
                Cart.objects.create(
                    item=stock.name,
                    price= stock.mrp,
                    total_price=stock.mrp,
                    supplier = stock.supplier
                )
                # try:
                #     item.save()
                # except IntegrityError:
                #     form.add_error('item','Already there')
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
                    
                    stock_list = get_object_or_404(StockItems, name = cart.item, supplier__name__contains = cart.supplier)
                    print(stock_list.pk)
                    if stock_list.stock < cart_units:
                        messages.warning(request, "Not Enough Stock")
                        return redirect('billing')
                    name_list.append(cart.item)
                    unit_list.append(cart.units)
                    price_list.append(cart.price)
                    stock_list.stock = stock_list.stock - cart_units
                    stock_list.save()
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
                
                messages.success(request,"Purchase Successfull!!")
                return redirect('cart_list', pk=PurchaseHistory.objects.last().pk)
        else:
            cform = PhoneForm()
    else:        
        form = SearchForm()
        cform = PhoneForm()
    cart_table = cartTable(Cart.objects.all())
    total_cost = Cart.objects.aggregate(Sum('total_price'))
    
    return render(request, "inventory/billing_page.html",{'form':form, 'cform':cform, 'cart_table':cart_table, 'total_cost': total_cost,})

#Deletes all items in cart table
@login_required
def clear_table(request):
    Cart.objects.all().delete()
    return redirect('billing')

#Adds one more unit of an item added into cart
@login_required
def plus_units(request, pk):
    obj = get_object_or_404(Cart,pk=pk)
    item = get_object_or_404(StockItems, name = obj.item, supplier__name__contains = obj.supplier)
    if obj.units == item.stock:
        messages.warning(request, "No More Stock")
        return redirect('billing')
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


#Page to restock from a supplier in bulk
@login_required
def supplier_restock(request, supplier):
    product_table = SupplierCatalogueTable(StockItems.objects.filter(supplier__name__contains = supplier))
    cart_table = SupplierCartTable(SupplierCart.objects.filter(supplier = supplier))
    total_cost = SupplierCart.objects.aggregate(Sum('total_price'))
    form = CountForm()
    RequestConfig(request).configure(product_table)
    product_table.paginate(page=request.GET.get("page", 1), per_page=8)
    return render(request, "inventory/supplier_restock.html",{'product_table':product_table, 'cart_table':cart_table, 'total_cost': total_cost, 'form':form, 'supplier':supplier})

#Adds an item to cart in restocking page
@login_required
def add_to_cart(request,pk):
    obj = get_object_or_404(StockItems,pk=pk)
    SupplierCart.objects.create( 
        item_id = pk,
        price = obj.cost_price,
        total_price = obj.cost_price,
        supplier = obj.supplier.name
    )
    return redirect('supplier_restock', supplier=obj.supplier.name)

#Change the units of items to buy
@login_required
def units_amount(request, pk):
    obj = get_object_or_404(SupplierCart,pk=pk)
    supplier = obj.supplier
    if request.method == "POST":
        form = CountForm(request.POST,request.FILES)
        if form.is_valid():
            item = form.cleaned_data
            obj.units = item['units']
            obj.total_price = obj.units * obj.price
            obj.save()
            return redirect('supplier_restock', supplier = supplier)
    else:
        form = CountForm()
    return redirect('supplier_restock', supplier = supplier)

#Delete the cart for one supplier
@login_required
def clear_supply_table(request, supplier):
    SupplierCart.objects.filter(supplier=supplier).delete()
    return redirect('supplier_restock', supplier = supplier)

#Delete single item in restock cart
@login_required
def delete_item(request, pk,):
    obj = get_object_or_404(SupplierCart,pk=pk)
    supplier = obj.supplier
    SupplierCart.objects.filter(pk=pk).delete()
    return redirect('supplier_restock', supplier = supplier)

#Buying the items to restock
@login_required
def supplier_checkout(request,supplier):
    name_list = []
    unit_list = []
    price_list = []
    for cart in SupplierCart.objects.filter(supplier=supplier):
        cart_units = cart.units
        
        stock_list = get_object_or_404(StockItems, pk = cart.item.pk)
        print(stock_list.pk)
        name_list.append(cart.item.name)
        unit_list.append(cart.units)
        price_list.append(cart.price)
        stock_list.stock = stock_list.stock + cart_units
        stock_list.save()
    json_data = {
        "product_name":name_list,
        "product_unit":unit_list,
        "product_price":price_list
    }
    total_cost = SupplierCart.objects.filter(supplier=supplier).aggregate(Sum('total_price'))['total_price__sum']
    SupplierHistory.objects.create(
        supplier_name = supplier,
        product_list = json_data,
        total_cost = total_cost)
    
    messages.success(request,"Purchase Successfull!!")
    return redirect('supply_cart_list', pk=SupplierHistory.objects.last().pk)



#Check and manage all the item categories
@login_required
def manage_category(request, is_disabled = 0):
    typelist = ItemType.objects.filter(is_disabled = is_disabled).order_by('category')  
    category = ItemTypeCategory.objects.all().order_by('pk')
    return render(request, "inventory/manage_category.html",{"categories":category, "typelist":typelist})

#Adding a new main category
@login_required
def add_main_category(request):
    if request.method == "POST":
        form = MainCategoryForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.save()
            return redirect('manage_category')
    else:
        form = MainCategoryForm()
    return render(request, "inventory/category_form.html",{'form': form})

#Editing a new main category
@login_required
def edit_main_category(request,pk):
    obj = get_object_or_404(ItemTypeCategory,pk=pk)
    if request.method == "POST":
        form = MainCategoryForm(request.POST, instance = obj)
        if form.is_valid():
            item = form.save(commit=False)
            item.save()
            return redirect('manage_category')
    else:
        form = MainCategoryForm(instance = obj)
    return render(request, "inventory/category_form.html",{'form': form})


#Adding a new sub category
@login_required
def add_sub_category(request):
    if request.method == "POST":
        form = SubCategoryForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.save()
            return redirect('manage_category')
    else:
        form = SubCategoryForm()
    return render(request, "inventory/category_form.html",{'form': form})

#Editing a sub category
@login_required
def edit_sub_category(request,pk):
    obj = get_object_or_404(ItemType,pk=pk)
    if request.method == "POST":
        form = SubCategoryForm(request.POST, instance = obj)
        if form.is_valid():
            item = form.save(commit=False)
            item.save()
            return redirect('manage_category')
    else:
        form = SubCategoryForm(instance = obj)
    return render(request, "inventory/category_form.html",{'form': form})


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
    if obj.item_type.is_disabled == True:
        messages.warning(request, "The category this item belongs to is disabled! Enable it first or change category")
        return redirect('stock_list', type="all", bool_int=1)
    obj.is_deleted = False
    obj.save()
    return redirect('stock_list', type = type)
    


#Loads dropdown-list of city based on the state seleted in supplier form
@login_required
def load_cities(request):
    state_id = request.GET.get('state')
    cities = City.objects.filter(state_id=state_id).all()
    return render(request, 'inventory/city_list.html', {'cities': cities})



#Page asking confirmation on deleting an subcategory
@login_required
def remove_check_category(request,pk):
    return render(request, "inventory/remove_check_category.html",{'pk': pk})

#Page asking confirmation on restoring an subcategory
@login_required
def restore_check_category(request,pk):
    return render(request, "inventory/restore_check_category.html",{'pk': pk})

#Deletes subcategory
@login_required
def remove_category(request,pk):
    obj = get_object_or_404(ItemType,pk=pk)
    type = obj.code
    for item in StockItems.objects.filter(item_type__code__contains = type):
        item.is_deleted = True
        item.save()
    obj.is_disabled = True
    obj.save()
    return redirect('manage_category')

#Restores subcategory
@login_required
def restore_category(request,pk):
    obj = get_object_or_404(ItemType,pk=pk)

    type = obj.code
    for item in StockItems.objects.filter(item_type__code__contains = type):
        item.is_deleted = False
        item.save()
    obj.is_disabled = False
    obj.save()
    return redirect('manage_category')