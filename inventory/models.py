from django.db import models
from django.db.models import Model
from datetime import date
from django.core.validators import MaxValueValidator, MinValueValidator


# Part of supplier address
class State(Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# Part of supplier address
class City(Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# Database of all suppliers
class Supplier(Model):
    name = models.CharField(unique=True ,max_length=100, blank=True, null=True)
    phone_no = models.IntegerField(unique=True, blank=True, null=True,
        validators=[
            MinValueValidator(1000000000,
                              message="Enter correct phone number"),
            MaxValueValidator(9999999999,
                              message="Enter correct phone number")
        ])
    state = models.ForeignKey(State, on_delete=models.CASCADE, blank=True, null=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, blank=True, null=True)
    def __str__(self):
        return self.name

# Store category of each item types
class ItemTypeCategory(Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# Store Type of an item       
class ItemType(Model):
    code = models.CharField(max_length=2, unique=True, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    category = models.ForeignKey(ItemTypeCategory, on_delete=models.CASCADE, blank=True, null=True)
    is_disabled = models.BooleanField(default=False)

    def __str__(self):
        return self.name


# Database of all items in the inventory catalogue
class StockItems(Model):
    
    name = models.CharField(max_length=100, blank=True, null=True)
    item_type = models.ForeignKey(ItemType, on_delete=models.CASCADE, blank=True, null=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, blank=True, null=True)
    stock = models.IntegerField(blank=True, null=True, verbose_name="Stock Units")
    stock_list = models.JSONField(default=list)
    quantity = models.CharField(max_length=20, verbose_name="Quantity(Per Unit)", blank=True, null=True)
    quantity_list = models.JSONField(default=list)
    cost_price = models.IntegerField(blank=True, null=True, verbose_name="Cost Price")
    cost_list = models.JSONField(default=list)
    mrp = models.IntegerField(blank=True, null=True, verbose_name="MRP")
    initial_date = models.DateField(default=date.today, blank=True, null=True)
    restock_date = models.DateField( blank=True, null=True)
    restock_date_list = models.JSONField(default=list)
    expiry_date_list = models.JSONField(default=list)
    is_deleted = models.BooleanField(default=False)

    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name','supplier'],name='unique_product')
        ]
    
    # def get_initial_date(self):
    #     from datetime import datetime
    #     return self.initial_date.strftime("%d-%m-%Y")
    
    # def get_restock_date(self):
    #     from datetime import datetime
    #     return self.restock_date.strftime("%d-%m-%Y")
    
    def __str__(self):
        return self.name



# Temporary database to store items added to cart
class Cart(Model):

    
    item = models.CharField( blank=True, null=True)
    units = models.IntegerField(default=1)
    price = models.IntegerField(verbose_name="Price (per unit)")
    total_price = models.IntegerField()
    supplier = models.CharField(max_length=100)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['item','supplier'],name='unique_cart')
        ]

    
    def __str__(self):
        return str(self.item)

# Databse of customer details    
class Customer(Model):
    name = models.CharField(max_length=100)
    phone_no = models.IntegerField(unique=True,
        validators=[
            MinValueValidator(1000000000,
                              message="Enter correct phone number"),
            MaxValueValidator(9999999999,
                              message="Enter correct phone number")
        ])

    def __str__(self):
        return self.name

# Database of past customer purchases
class PurchaseHistory(Model):
    customer_no = models.IntegerField()
    product_list = models.JSONField()
    total_cost =  models.IntegerField()
    purchase_datetime = models.DateTimeField(auto_now_add= True)

    
    def __str__(self):
        return str(self.customer_no)
    
# Database of past stock purchases from suppliers
class SupplierHistory(Model):
    supplier_name = models.CharField(max_length=100,)
    product_list = models.JSONField()
    total_cost =  models.IntegerField()
    purchase_datetime = models.DateTimeField(auto_now_add= True)

    
    def __str__(self):
        return self.supplier_name
    
class SupplierCart(Model):

    
    item = models.ForeignKey(StockItems, on_delete=models.CASCADE, blank=True, null=True)
    units = models.IntegerField(default=1,blank=True, null=True)
    price = models.IntegerField(verbose_name="Price (per unit)")
    total_price = models.IntegerField()
    supplier = models.CharField(max_length=100)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['item','supplier'],name='unique_supply_cart')
        ]

    
    def __str__(self):
        return str(self.item)
    
class File(Model):
    file = models.FileField(upload_to="excel")

# class AbstractItems(Model):
#     name = models.CharField(max_length=100)
#     supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, blank=True, null=True)
#     stock = models.IntegerField(null=True)
#     quantity = models.CharField(max_length=20)
#     cost = models.IntegerField(null=True)

#     class Meta:
#         abstract = True
    
#     def __str__(self):
#         return self.name
    


# class Fresh_Produce(AbstractItems):
#     PRODUCE_CHOICES = (
#         ('F','Fruits'),
#         ('V','Vegetable'),
#         ('G','Leafy Greens'),
#     )
#     type = models.CharField(
#         max_length=1,
#         choices=PRODUCE_CHOICES,
#             default='F')
#     def __str__(self):
#         return self.name
    
# class Grains(AbstractItems):
#     pass

# class Dairy(AbstractItems):
#     pass

# class Snacks(AbstractItems):
#     pass

# class Beverages(AbstractItems):
#     pass

# class Personal_Care(AbstractItems):
#     pass

# class Household_Supplies(AbstractItems):
#     pass

# class Stationery(AbstractItems):
#     pass

# class Condiments(AbstractItems):
#     pass



    

