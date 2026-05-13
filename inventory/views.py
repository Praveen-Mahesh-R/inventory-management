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
from django.http import JsonResponse, HttpResponse
import pandas as pd
import openpyxl
import csv
import codecs
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import Image, Paragraph, Table
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from django.db.models import F, Func, Value, CharField

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
    
    products = StockItems.objects.filter(stock = 0).values_list('name', flat=True).distinct()
    product_list = ""
    # for p in products:
    product_list = ", ".join(products)
    if product_list == "":
        product_list = "None"

    context = {
        'revenue': revenue,
        'spent': spent,
        'products':product_list
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
        stock_table = StockTable(StockItems.objects.filter(item_type__code__contains = type, is_deleted = bool(bool_int)).order_by('-initial_date'),exclude=excluded_columns)
        if query:
            stock_table = StockTable(StockItems.objects.filter(
                Q(name__icontains = query)|Q(supplier__name__icontains = query)
            ).filter(item_type__code__contains = type, is_deleted = bool(bool_int)).order_by('-initial_date'),exclude=excluded_columns)
    
    else:
        stock_table = StockTable(StockItems.objects.filter(is_deleted = bool(bool_int)).order_by('-initial_date'),exclude=excluded_columns)
        if query:
            stock_table = StockTable(StockItems.objects.filter(
                Q(name__icontains = query)|Q(supplier__name__icontains = query)
            ).filter(is_deleted = bool(bool_int)).order_by('-initial_date'),exclude=excluded_columns)
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
    # Customer.objects.filter(profile_img="media/images/default.jpg").update(profile_img='images/default.jpg')
    query = request.GET.get("q", None)
    if query:
        customer_table = CustomerTable(Customer.objects.filter(
            Q(name__icontains = query)|Q(phone_no__icontains = query)
        ))
    RequestConfig(request).configure(customer_table)
    customer_table.paginate(page=request.GET.get("page", 1), per_page=5)
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
        form = CustomerForm(request.POST, request.FILES)
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
        form = CustomerForm(request.POST, request.FILES, instance=item)
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
    total_cost = SupplierCart.objects.filter(supplier = supplier).aggregate(Sum('total_price'))
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

@login_required
def add_new_product(request):
    return render(request, "inventory/add_new_product.html",{})

@login_required
def import_data_to_db(request):
    
    
    if request.method == 'POST':
        form = FileForm(request.POST,request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            file = data['files']
            # obj = File.objects.create(
            #     file=file
            # )
            # wb = openpyxl.load_workbook(file)
            # df = pd.read_excel(file)
            # sheet = wb.active
            reader = csv.reader(codecs.iterdecode(file,'utf-8'))
            next(reader)
            supplier = data['supplier']
            # print("------------------HELLO-------------------------------")
            for row in reader: 
                # if len(row[1])!=2:
                #     continue
                print(row[0])
                typeid = ItemType.objects.get(code = row[1]).pk
                _, created = StockItems.objects.get_or_create(
                    name=row[0],
                    item_type_id=typeid,
                    supplier=supplier,
                    stock=0,
                    quantity=row[2],
                    cost_price=row[3],
                    mrp=row[4]
                )
            return redirect('stock_list',)
        # data_to_display = df.to_html()
    else:
        form = FileForm()
    return render(request, "inventory/upload.html",{ 'form':form})




# def product_excel_export(request):
#     objs = StockItems.objects.all()
#     data = []
#     for obj in objs:
#         data.append({
#             "name": obj.name,
#             "item_type": obj.item_type,
#             "supplier": obj.supplier.name,
#             "stock": obj.stock,
#             "quantity":obj.quantity,
#         })
#     pd.DataFrame(data).to_excel('output.xlsx')
#     return JsonResponse({
#         'status': 200
#     })

@login_required
def product_csv_export(request):
    response = HttpResponse(content_type = 'text/csv')
    response['Content-Disposition'] = 'attachment; filename="products.csv"'
    writer = csv.writer(response)
    writer.writerow(['name','item_type','supplier','stock','quantity','cost_price','mrp','initial_date'])
    products = StockItems.objects.all().annotate(
                formatted_date=Func(
                    F('initial_date'),
                    Value('DD-MM-YYYY'),
                    function='to_char',
                    output_field=CharField()
                )).values_list('name','item_type__code','supplier__name','stock','quantity','cost_price','mrp','initial_date')
    for product in products:
        writer.writerow(product)
    
    return response

@login_required
def customer_csv_export(request):
    customers = Customer.objects.all().values_list('name','phone_no')
    response = HttpResponse(content_type = 'text/csv')
    response['Content-Disposition'] = 'attachment; filename="customer.csv"'
    writer = csv.writer(response)
    writer.writerow(['name','phone_no'])
    for c in customers:
        writer.writerow(c)
    return response

@login_required
def supplier_csv_export(request):
    customers = Supplier.objects.all().values_list('name','phone_no','state__name','city__name')
    response = HttpResponse(content_type = 'text/csv')
    response['Content-Disposition'] = 'attachment; filename="supplier.csv"'
    writer = csv.writer(response)
    writer.writerow(['name','phone_no','state','city'])
    for c in customers:
        writer.writerow(c)
    return response

@login_required
def customer_purchase_csv_export(request, pk):
    details = Customer.objects.get(pk=pk)
    product_data = PurchaseHistory.objects.filter(customer_no = details.phone_no)
    response = HttpResponse(content_type = 'text/csv')
    name = details.name + ".csv"
    response['Content-Disposition'] = 'attachment; filename="' + name + '"'
    writer = csv.writer(response)
    writer.writerow(['product_name','product_unit','product_price','purchase_datetime'])
    for product in product_data:
        json_data = zip(product.product_list['product_name'],product.product_list['product_unit'],product.product_list['product_price'])
        date_time = product.purchase_datetime.strftime('%Y-%m-%d %H:%M')
        for name, unit, price in json_data:
            writer.writerow([name,unit,price,date_time])

    return response

@login_required
def manage_customer(request,pk):
    return render(request, "inventory/manage_customer.html",{'pk': pk})

@login_required
def customer_pdf_report(request, pk):

    customer = Customer.objects.get(pk=pk)
    product = PurchaseHistory.objects.filter(customer_no = customer.phone_no)
    total_spent = product.aggregate(Sum('total_cost'))['total_cost__sum']
    
    #stores data on item/s a customer bought the most number of times
    most_got_product = []
    most_got_units = []
    most_got_money = []

    #stores data on item/s a customer spent the most money on during their entire purchase history
    most_spent_product = []
    most_spent_units = []
    most_spent_money = []
    name_list = []
    unit_list = []
    price_list = []

    #get all cart data in singular lists and adds units and price values if already exists in list
    for cart in product:
        json_data = zip(cart.product_list['product_name'],cart.product_list['product_unit'],cart.product_list['product_price'])
        for name, unit, price in json_data:
            if name in name_list:
                idx = name_list.index(name)
                unit_list[idx] = unit_list[idx] + unit
                price_list[idx] = price_list[idx] + unit*price
            else:
                name_list.append(name)
                unit_list.append(unit)
                price_list.append(price*unit)
    #get max value
    highest_unit = max(unit_list)
    highest_price = max(price_list)
    #get indices of max value/s
    unit_indices = [i for i, x in enumerate(unit_list) if x == highest_unit]
    price_indices = [i for i, x in enumerate(price_list) if x == highest_price]

    #store data of max value/s
    for i in unit_indices:
        most_got_product.append(name_list[i])
        most_got_units.append(unit_list[i])
        most_got_money.append(price_list[i])
    for i in price_indices:
        most_spent_product.append(name_list[i])
        most_spent_units.append(unit_list[i])
        most_spent_money.append(price_list[i])

    top_data = []
    top_data.append(('Name','Units','Total Revenue'))
    for x in reversed(sorted(range(len(price_list)), key=lambda i: price_list[i])[-5:]):
        top_data.append((name_list[x], unit_list[x], price_list[x]))
    
    table = Table(top_data, colWidths=170, rowHeights=25)
    # table.setStyle([("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    #             ("ALIGN", (0,0), (-1,-1), "CENTER"),
    #             ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black)])
    table.setStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 16),
        ('LEADING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])
    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    # p.setFillColorRGB(0.1,0.7,0.6)
    # p.rect(0,0, letter[0],letter[1], fill=True,stroke=False)
    # p.setFillColorRGB(1, 1, 1)
    p.setFont("Courier", 28)
    p.setFillColorRGB(0.153, 0.431, 0.153)
    p.drawString(50,770,"SuperMart")

    p.setFont("Helvetica", 20)
    p.setFillColorRGB(0, 0, 0)
    p.line(50, 765, 550, 765)
    width = stringWidth("Customer Report", "Helvetica", 20)
    p.drawString(50,735, "Customer Report")
    p.line(50, 730, 50+width, 730)
    p.setFont("Helvetica", 16)
    p.drawString(50,700, "Customer Name: "+customer.name)
    p.drawString(50,675, "Customer Phone No: "+str(customer.phone_no))
    p.drawString(50,650, "Total Expenditure: Rs."+str(total_spent))
    p.drawString(50,625, "Total No of Visits: "+str(product.count()))
    p.line(50, 615, 550, 615)
    p.drawString(50,585, "The product customer bought the most no of times:")
    p.drawString(50,560, "Product: "+", ".join(most_got_product))
    p.drawString(50,535, "Total units gotten: "+", ".join(map(str,most_got_units)))
    p.drawString(50,510, "Total spent: Rs."+", Rs.".join(map(str,most_got_money)))
    p.line(50, 500, 550, 500)
    p.drawString(50,470, "The product customer spent the most money on:")
    p.drawString(50,445, "Product: "+", ".join(most_spent_product))
    p.drawString(50,420, "Total units gotten: "+", ".join(map(str,most_spent_units)))
    p.drawString(50,395, "Total spent: Rs."+", Rs.".join(map(str,most_spent_money)))
    p.line(50, 385, 550, 385)
    p.drawString(50,365, "Top five Products bought:")
    table.wrapOn(p, 500, 125)
    table.drawOn(p, 50, 200)
    p.showPage()
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=customer.name+"-report.pdf")

@login_required
def sales_pdf_report(request):

    customer_count = Customer.objects.all().count()
    product = PurchaseHistory.objects.all()
    total_spent = product.aggregate(Sum('total_cost'))['total_cost__sum']

    top_customer_name = []
    customer_name=[]
    customer_money=[]
    
    #stores data on item/s all customers bought the most number of times
    most_got_product = []
    most_got_units = []
    most_got_money = []

    #stores data on item/s all customers spent the most money on during their entire purchase history
    most_spent_product = []
    most_spent_units = []
    most_spent_money = []
    name_list = []
    unit_list = []
    price_list = []

    #get all cart data in singular lists and adds values if already exists in list
    for cart in product:
        name = Customer.objects.get(phone_no=cart.customer_no).name
        if name in customer_name:
                idx = customer_name.index(name)
                customer_money[idx] = customer_money[idx] + cart.total_cost
        else:
            customer_name.append(name)
            customer_money.append(cart.total_cost)
        json_data = zip(cart.product_list['product_name'],cart.product_list['product_unit'],cart.product_list['product_price'])
        for name, unit, price in json_data:
            if name in name_list:
                idx = name_list.index(name)
                unit_list[idx] = unit_list[idx] + unit
                price_list[idx] = price_list[idx] + unit*price
            else:
                name_list.append(name)
                unit_list.append(unit)
                price_list.append(price*unit)
    #get max value
    highest_unit = max(unit_list)
    highest_price = max(price_list)
    print(price_list)
    #get indices of max value/s
    unit_indices = [i for i, x in enumerate(unit_list) if x == highest_unit]
    price_indices = [i for i, x in enumerate(price_list) if x == highest_price]

    #store data of max value/s
    for i in unit_indices:
        most_got_product.append(name_list[i])
        most_got_units.append(unit_list[i])
        most_got_money.append(price_list[i])
    for i in price_indices:
        most_spent_product.append(name_list[i])
        most_spent_units.append(unit_list[i])
        most_spent_money.append(price_list[i])

    highest_revenue = max(customer_money)
    revenue_indices = [i for i, x in enumerate(customer_money) if x == highest_revenue]

    print(highest_revenue)
    for i in revenue_indices:
        top_customer_name.append(customer_name[i])
    

    top_data = []
    top_data.append(('Name','Units','Total Revenue'))
    for x in reversed(sorted(range(len(price_list)), key=lambda i: price_list[i])[-5:]):
        top_data.append((name_list[x], unit_list[x], price_list[x]))
    
    table = Table(top_data, colWidths=[250,110,150], rowHeights=25)
    # table.setStyle([("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    #             ("ALIGN", (0,0), (-1,-1), "CENTER"),
    #             ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black)])
    table.setStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 16),
        ('LEADING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])
    
    

    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)

    
    # p.setFillColorRGB(0.1,0.7,0.6)
    # p.rect(0,0, letter[0],letter[1], fill=True,stroke=False)
    # p.setFillColorRGB(1, 1, 1)
    p.setFont("Courier", 28)
    p.setFillColorRGB(0.153, 0.431, 0.153)
    p.drawString(50,770,"SuperMart")

    p.setFont("Helvetica", 20)
    p.setFillColorRGB(0, 0, 0)
    p.line(50, 765, 550, 765)
    width = stringWidth("Sales Report", "Helvetica", 20)
    p.drawString(50,735, "Sales Report")
    p.line(50, 730, 50+width, 730)
    p.setFont("Helvetica", 16)
    p.drawString(50,700, "Total Revenue: Rs."+str(total_spent))
    p.drawString(50,675, "Total no of checkouts: "+str(product.count()))
    p.drawString(50,650, "Total no of Customers: "+str(customer_count))
    p.line(50, 640, 550, 640)
    p.drawString(50,620, "Top Customer/s: "+", ".join(top_customer_name))
    p.drawString(50,595, "Highest Revenue from Top Customer/s: "+str(highest_revenue))
    p.line(50, 585, 550, 585)
    p.drawString(50,565, "The product customers bought the most no of times:")
    p.drawString(50,540, "Product: "+", ".join(most_got_product))
    p.drawString(50,515, "Total units gotten: "+", ".join(map(str,most_got_units)))
    p.drawString(50,490, "Total spent: Rs."+", Rs.".join(map(str,most_got_money)))
    p.line(50, 480, 550, 480)
    p.drawString(50,460, "The product customers spent the most money on:")
    p.drawString(50,435, "Product: "+", ".join(most_spent_product))
    p.drawString(50,410, "Total units gotten: "+", ".join(map(str,most_spent_units)))
    p.drawString(50,385, "Total spent: Rs."+", Rs.".join(map(str,most_spent_money)))
    p.line(50, 375, 550, 375)
    p.drawString(50,355, "Top five Products Sold:")
    table.wrapOn(p, 500, 125)
    table.drawOn(p, 50, 190)


    p.showPage()
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="Sales-report.pdf")
# obj = get_object_or_404(PurchaseHistory,pk=pk)
# product = zip(obj.product_list['product_name'],obj.product_list['product_unit'],obj.product_list['product_price'])
# context = {
#     'product':product,
#     'total':obj.total_cost
# }

def supply_pdf_report(request):
    supply = SupplierHistory.objects.all()
    total_spent = supply.aggregate(Sum('total_cost'))['total_cost__sum']
    supplier_count = Supplier.objects.all().count()


    top_supplier_name = []
    supplier_name=[]
    supplier_money=[]
    
    #stores data on item/s the store bought the most number of times
    most_got_product = []
    most_got_units = []
    most_got_money = []

    #stores data on item/s the store spent the most money on during their entire purchase history
    most_spent_product = []
    most_spent_units = []
    most_spent_money = []
    name_list = []
    unit_list = []
    price_list = []

    #get all cart data in singular lists and adds values if already exists in list
    for cart in supply:
        name = cart.supplier_name
        if name in supplier_name:
                idx = supplier_name.index(name)
                supplier_name[idx] = supplier_money[idx] + cart.total_cost
        else:
            supplier_name.append(name)
            supplier_money.append(cart.total_cost)
        json_data = zip(cart.product_list['product_name'],cart.product_list['product_unit'],cart.product_list['product_price'])
        for name, unit, price in json_data:
            if name in name_list:
                idx = name_list.index(name)
                unit_list[idx] = unit_list[idx] + unit
                price_list[idx] = price_list[idx] + unit*price
            else:
                name_list.append(name)
                unit_list.append(unit)
                price_list.append(price*unit)
    #get max value
    highest_unit = max(unit_list)
    highest_price = max(price_list)
    print(price_list)
    #get indices of max value/s
    unit_indices = [i for i, x in enumerate(unit_list) if x == highest_unit]
    price_indices = [i for i, x in enumerate(price_list) if x == highest_price]

    #store data of max value/s
    for i in unit_indices:
        most_got_product.append(name_list[i])
        most_got_units.append(unit_list[i])
        most_got_money.append(price_list[i])
    for i in price_indices:
        most_spent_product.append(name_list[i])
        most_spent_units.append(unit_list[i])
        most_spent_money.append(price_list[i])

    highest_revenue = max(supplier_money)
    revenue_indices = [i for i, x in enumerate(supplier_money) if x == highest_revenue]

    for i in revenue_indices:
        top_supplier_name.append(supplier_name[i])

    
    top_data = []
    top_data.append(('Name','Units','Total Expense'))
    for x in reversed(sorted(range(len(price_list)), key=lambda i: price_list[i])[-5:]):
        top_data.append((name_list[x], unit_list[x], price_list[x]))
    
    table = Table(top_data, colWidths=[250,110,150], rowHeights=25)
    # table.setStyle([("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    #             ("ALIGN", (0,0), (-1,-1), "CENTER"),
    #             ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black)])
    table.setStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 16),
        ('LEADING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])


    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)

    
    
    p.setFont("Courier", 28)
    p.setFillColorRGB(0.153, 0.431, 0.153)
    p.drawString(50,770,"SuperMart")

    p.setFont("Helvetica", 20)
    p.setFillColorRGB(0, 0, 0)
    p.line(50, 765, 550, 765)
    width = stringWidth("Supply Report", "Helvetica", 20)
    p.drawString(50,735, "Supply Report")
    p.line(50, 730, 50+width, 730)
    p.setFont("Helvetica", 16)
    p.drawString(50,700, "Total Expenses: Rs."+str(total_spent))
    p.drawString(50,675, "Total no of expenditures: "+str(supply.count()))
    p.drawString(50,650, "Total no of Supplier: "+str(supplier_count))
    p.line(50, 640, 550, 640)
    p.drawString(50,620, "Top Supplier/s: "+", ".join(top_supplier_name))
    p.drawString(50,595, "Supplier's total expenses: "+str(highest_revenue))
    p.line(50, 585, 550, 585)
    p.drawString(50,565, "The product stocked the most no of times:")
    p.drawString(50,540, "Product: "+", ".join(most_got_product))
    p.drawString(50,515, "Total units stocked/restocked: "+", ".join(map(str,most_got_units)))
    p.drawString(50,490, "Total spent: Rs."+", Rs.".join(map(str,most_got_money)))
    p.line(50, 480, 550, 480)
    p.drawString(50,460, "The product with the most expense:")
    p.drawString(50,435, "Product: "+", ".join(most_spent_product))
    p.drawString(50,410, "Total units stocked/restocked: "+", ".join(map(str,most_spent_units)))
    p.drawString(50,385, "Total spent: Rs."+", Rs.".join(map(str,most_spent_money)))
    p.line(50, 375, 550, 375)
    p.drawString(50,355, "Top five Products (Based on Expense):")
    table.wrapOn(p, 500, 125)
    table.drawOn(p, 50, 190)

    p.showPage()
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="Supply-report.pdf")



