from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Column, Field
from django.contrib.auth.forms import AuthenticationForm
from captcha.fields import CaptchaField
from django.contrib.admin.widgets import AdminDateWidget




from .models import *


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
class SupplierForm(forms.ModelForm):

    class Meta:
        model = Supplier
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['city'].queryset = City.objects.none()

        if 'state' in self.data:
            print("hello")
            try:
                state_id = int(self.data.get('state'))
                self.fields['city'].queryset = City.objects.filter(state_id=state_id).order_by('name')
            except (ValueError, TypeError):
                pass  
        elif self.instance.pk:
            print("hello")
            self.fields['city'].queryset = self.instance.state.city_set.order_by('name')
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            Row(
                Column('state', css_class='form-group col-md-6 mb-0'),
                Column('city', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit','Submit'))
        
        
class StockForm(forms.Form):
    amount = forms.IntegerField(
            label = "How much are you adding?",
            required = True,
            widget=forms.TextInput(attrs={'style':'max-width: 50px;'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
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
    # def clean(self):
    #     cleaned_data = super().clean()
    #     item = cleaned_data.get('item')
    #     supplier = cleaned_data.get('supplier')
    #     if item and Cart.objects.get(item=item):
    #         if supplier and Cart.objects.get(supplier=supplier):
    #             raise forms.ValidationError("Already there")
    #     return cleaned_data

class DateInput(forms.DateInput):
    input_type = 'date'

    def format_value(self, value):
        return value.isoformat() if value is not None and hasattr(value, "isoformat") else ""

class ItemForm(forms.ModelForm):

    class Meta:
        model = StockItems
        fields = '__all__'
        # widget = { 
        #     'initial_date' : forms.DateInput(attrs={'class':'form-control', 'type':'date'}),
        # }
        

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


class CustomerForm(forms.Form):

    phone_no = forms.IntegerField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        phone_no = cleaned_data.get('phone_no')

        if not phone_no:
            self.add_error('phone_no',"Should Not be Empty")
        if len(str(phone_no)) != 10:
            self.add_error('phone_no',"Enter Valid Phone no.")
        if not Customer.objects.filter(phone_no = phone_no).exists():
            self.add_error('phone_no','There is no customer with this phone number, add new')
        return cleaned_data
    

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
        
        
