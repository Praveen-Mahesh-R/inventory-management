from django.db import models
from django.db.models import Model

# Create your models here.

class Supplier(Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)

    def __str__(self):
        return super().__str__()

class AbstractItems(Model):
    name = models.CharField(max_length=100)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, blank=True, null=True)
    stock = models.IntegerField(null=True)
    quantity = models.CharField(max_length=20)

    class Meta:
        abstract = True
    
    def __str__(self):
        return self.name
    


class Fresh_Produce(AbstractItems):
    PRODUCE_CHOICES = (
        ('F','Fruits'),
        ('V','Vegetable'),
        ('G','Leafy Greens'),
    )
    type = models.CharField(
        max_length=1,
        choices=PRODUCE_CHOICES,
            default='F')
    def __str__(self):
        return self.name
    
class Grains(AbstractItems):
    pass

class Readymade_Food(AbstractItems):
    pass

class Dairy(AbstractItems):
    pass

class Snacks(AbstractItems):
    pass

class Beverages(AbstractItems):
    pass

class Personal_Care(AbstractItems):
    pass

class Household_Supplies(AbstractItems):
    pass

class Stationery(AbstractItems):
    pass

class Condiments(AbstractItems):
    pass



    

