from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Column, Field
from django.contrib.auth.forms import AuthenticationForm
from captcha.fields import CaptchaField
from django.contrib.admin.widgets import AdminDateWidget




from .models import *

#Form for login page
class LoginForm(AuthenticationForm):

    captcha = CaptchaField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'username',
            'password',
            'captcha',
            Submit('submit', 'Log In', css_class='btn-success') # Customize the submit button
        )

#Form for adding and editing supplier details
class SupplierForm(forms.ModelForm):

    class Meta:
        model = Supplier
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['city'].queryset = City.objects.none()

        if 'state' in self.data:
            try:
                state_id = int(self.data.get('state'))
                self.fields['city'].queryset = City.objects.filter(state_id=state_id).order_by('name')
            except (ValueError, TypeError):
                pass  
        elif self.instance.pk:
            self.fields['city'].queryset = self.instance.state.city_set.order_by('name')
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-6 mb-0'),
                Column('phone_no', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('state', css_class='form-group col-md-6 mb-0'),
                Column('city', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit','Submit'))
    
    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        state = cleaned_data.get('state')
        city = cleaned_data.get('city')

        if not name:
            self.add_error('name','Name should not be empty')
        if not state:
            self.add_error('state','State should not be empty')
        if not city:
            self.add_error('city','City should not be empty')
        return cleaned_data
        
#Form of replenishing stock of any item        
class StockForm(forms.Form):
    amount = forms.IntegerField(
            label = "How much are you adding?",
            required = True,
            widget=forms.TextInput(attrs={'style':'max-width: 70px;'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get('amount')
        if amount < 0:
            self.add_error('amount','Should be a positive number or zero')
        return cleaned_data


#Form for searching any product to add to cart in billing page   
class SearchForm(forms.ModelForm):
    class Meta:
        model = Cart
        fields = ('item',)
        widget = {
            'item': forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'item',
            Submit('submit_item','Add Item to Cart')
        )
        self.fields['item'].required = True
        
    def clean(self):
        cleaned_data = super().clean()
        item = cleaned_data.get('item')
        supplier = cleaned_data.get('supplier')
        if item and Cart.objects.filter(item=item).exists():
            if supplier and Cart.objects.filter(supplier=supplier).exists():
                raise forms.ValidationError("Already there")
        return cleaned_data
    



# class DateInput(forms.DateInput):
#     input_type = 'date'

#     def format_value(self, value):
#         return value.isoformat() if value is not None and hasattr(value, "isoformat") else ""

#Form for adding or editing a product in inventory catalogue 
class ItemForm(forms.ModelForm):

    class Meta:
        model = StockItems
        fields = '__all__'
        

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            Row(
                Column('item_type', css_class='form-group col-md-6 mb-0'),
                Column('supplier', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('stock', css_class='form-group col-md-6 mb-0'),
                Column('quantity', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('cost_price', css_class='form-group col-md-6 mb-0'),
                Column('mrp', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('initial_date', css_class='form-group col-md-6 mb-0'),
                Column('restock_date', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit','Submit')
        )
        self.fields['initial_date'].widget = forms.DateInput(
            format=('%Y-%m-%d'),
            attrs={
                'class':'form-control',
                'type':'date',
                
            })
        self.fields['restock_date'].widget = forms.DateInput(
            format=('%Y-%m-%d'),
            attrs={
                'class':'form-control',
                'type':'date',
                
            })
    
    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        type = cleaned_data.get('item_type')
        supplier = cleaned_data.get('supplier')
        stock = cleaned_data.get('stock')
        quantity = cleaned_data.get('quantity')
        mrp = cleaned_data.get('mrp')

        if not name:
            self.add_error('name','Name should not be empty')
        if not type:
            self.add_error('item_type','Type shoud not be empty')
        if not supplier:
            self.add_error('supplier','Supplier should not be empty')
        
        if not stock:
            self.add_error('stock','Stock should not be empty')
        elif stock < 0:
            self.add_error('stock','Stock should be a positive number')
        
        if not quantity:
            self.add_error('quantity', 'Quantity should not be empty')
        
        if not mrp:
            self.add_error('mrp','MRP should not be empty')
        elif mrp < 0:
            self.add_error('mrp','MRP should be a positive number')

        return cleaned_data

#Form for submitting phone number in billing page for checkout
class PhoneForm(forms.Form):

    phone_no = forms.IntegerField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        phone_no = cleaned_data.get('phone_no')
        self.helper = FormHelper()
        

        if not phone_no:
            self.add_error('phone_no',"Should Not be Empty")
        elif len(str(phone_no)) != 10:
            self.add_error('phone_no',"Enter Valid Phone no.")
            raise forms.ValidationError("Enter Valid Phone no.")
        elif not Customer.objects.filter(phone_no = phone_no).exists():
            self.add_error('phone_no','There is no customer with this phone number, add new')
        return cleaned_data

#Form for adding or editing customer details    
class CustomerForm(forms.ModelForm):

    class Meta:
        model = Customer
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
class MainCategoryForm(forms.ModelForm):

    class Meta:
        model = ItemTypeCategory
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class SubCategoryForm(forms.ModelForm):

    class Meta:
        model = ItemType
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class CountForm(forms.Form):
    units = forms.IntegerField(
            required = True,
            label="",
            validators=[MinValueValidator(1)],
            widget=forms.NumberInput(attrs={'style':'max-width: 70px;'})
    )

    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get('units')
        if not amount:
            self.add_error('units','Should be a positive number or zero')
        elif amount < 0:
            self.add_error('units','Should be a positive number or zero')
        return cleaned_data

# #Form for searching any product to add to cart in supplier billing page   
# class SearchSupplyForm(forms.ModelForm):
#     class Meta:
#         model = SupplierCart
#         fields = ('item',)
#         widget = {
#             'item': forms.Select(),
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.helper = FormHelper()
#         self.helper.layout = Layout(
#             'item',
#             Submit('submit_item','Add Item to Cart')
#         )
#         self.fields['item'].required = True
        
#     def clean(self):
#         cleaned_data = super().clean()
#         item = cleaned_data.get('item')
#         if item and SupplierCart.objects.filter(item=item).exists():
#                 raise forms.ValidationError("Already there")
#         return cleaned_data