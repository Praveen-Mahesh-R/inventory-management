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
from dal import autocomplete
from django.db.models import Sum


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
def stock_list(request,type):
    stock_table = StockTable(StockItems.objects.filter(type = type))
    return render(request, "inventory/stock_list.html",{"stock_table":stock_table, "type":type})

@login_required
def new_item_add(request):
    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.save()
            return redirect('stock_list', type = item.type)
    else:
        form = ItemForm()
    return render(request, "inventory/new_item_add.html",{'form': form})

@login_required
def add_stock(request,pk):
    obj = get_object_or_404(StockItems,pk=pk)
    if request.method == "POST":
        form = StockForm(request.POST,request.FILES)
        if form.is_valid():
            stock = form.cleaned_data
            obj.stock = obj.stock + stock["amount"]
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
    print("hello")
    if request.method == "POST":
        print("bye")
        form = SearchForm(request.POST)
        if form.is_valid():
            item = form.cleaned_data
            stock = StockItems.objects.get(name=item['item'])
            price = stock.cost
            cart = Cart(item = item['item'], price = price)
            cart.save()
            return redirect('billing')
    form = SearchForm()
    cart_table = cartTable(Cart.objects.all())
    total_cost = Cart.objects.aggregate(Sum('price'))
    print("hi")
    return render(request, "inventory/billing_page.html",{'form':form, 'cart_table':cart_table, 'total_cost': total_cost})

def clear_table(request):
    Cart.objects.all().delete()
    return redirect('billing')

@login_required
def load_cities(request):
    state_id = request.GET.get('state')
    cities = City.objects.filter(state_id=state_id).all()
    return render(request, 'inventory/city_list.html', {'cities': cities})


class ItemAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        
        qs = StockItems.objects.all()

        if self.q:
            qs = qs.filter(item__istartswith=self.q)

        return qs


