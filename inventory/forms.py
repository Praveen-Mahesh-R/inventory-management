from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Column

from .models import *

class SupplierForm(forms.ModelForm):

    class Meta:
        model = Supplier
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
    
    

class StockForm(forms.ModelForm):

    class Meta:
        model = StockItems
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            Row(
                Column('type', css_class='form-group col-md-6 mb-0'),
                Column('supplier', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('stock', css_class='form-group col-md-6 mb-0'),
                Column('quantity', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'cost',
            Submit('submit','Add Item to Catalogue')
        )

    # def clean(self):
    #     cleaned_data = super().clean()
    #     name = cleaned_data.get('name')
    #     type = cleaned_data.get('type')
    #     supplier = cleaned_data.get('supplier')
    #     stock = cleaned_data.get('stock')
    #     quantity = cleaned_data.get('quantity')
    #     cost = cleaned_data.get('cost')

    #     if not name:
    #         self.add_error('name','Name should not be empty')
    #     if not type:
    #         self.add_error('type','Type shoud not be empty')
    #     if not supplier:
    #         self.add_error('supplier','Supplier should not be empty')
    #     if not stock:
    #         self.add_error('stock','Stock should not be empty')
    #     if not quantity:
    #         self.add_error('quantity', 'Quantity should not be empty')
    #     if not cost:
    #         self.add_error('cost','Cost should not be empty')
    #     return cleaned_data
        
        
