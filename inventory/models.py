from django.db import models
from django.db.models import Model


# Create your models here.

class State(Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class City(Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Supplier(Model):
    name = models.CharField(unique=True ,max_length=100)
    state = models.ForeignKey(State, on_delete=models.CASCADE, blank=True, null=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, blank=True, null=True)
    def __str__(self):
        return self.name
    
class StockItems(Model):
    TYPE = (
        ('Fr','Fresh Produce'),
        ('Gr', 'Grains'),
        ('Dr', 'Dairy'),
        ('Cn', 'Condiments'),
        ('Sn', 'Snacks'),
        ('Bv', 'Beverages'),
        ('Pc', 'Personal Care'),
        ('Hs', 'Household supplies'),
        ('St', 'Stationery')
    )
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=2,
                            choices=TYPE,
                            default='Fr')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, blank=True, null=True)
    stock = models.IntegerField(null=True)
    quantity = models.CharField(max_length=20, verbose_name="Quantity(Per Unit)")
    cost = models.IntegerField(null=True, verbose_name="Cost(Per Unit)")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name','supplier'],name='unique_product')
        ]

    
    
    def __str__(self):
        return self.name

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



    

