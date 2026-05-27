from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Column, Field
from django.contrib.auth.forms import AuthenticationForm
from captcha.fields import CaptchaField
from django.contrib.admin.widgets import AutocompleteSelect
from django.shortcuts import get_object_or_404
from django.core.validators import FileExtensionValidator
from django.core.files.images import get_image_dimensions
from string import Template
from django.utils.safestring import mark_safe
from image_cropping import ImageCropWidget
from image_cropping import ImageCropField, ImageRatioField

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
class SearchForm(forms.Form):
    # class Meta:
    #     model = StockItems
    #     fields = ('name',)
    #     widget = {
    #         'name': forms.Select(),
    #     }

    def product_choices():
        return [('','------')]+[(item, item ) for item in StockItems.objects.filter(is_deleted = False).values_list('name', flat=True).distinct()]
    item = forms.ChoiceField(
        label="Choose Item:",
        choices= product_choices)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'item',
            Submit('submit_item','Add Item to Cart')
        )
        # self.fields['item'].queryset = StockItems.objects.values_list('name', flat=True).distinct()
        
    def clean(self):
        cleaned_data = super().clean()
        item = cleaned_data.get('item')
        if item and Cart.objects.filter(item=item).exists():
            raise forms.ValidationError("Already there")
        if self.is_empty(item):
            raise forms.ValidationError("No stock")
        return cleaned_data
    
    def is_empty(self,item):
        counter = StockItems.objects.filter(name = item).count()
        if counter == 1:
            stock = get_object_or_404(StockItems,name = item)
            if stock.stock == 0:
                return True
        else:
            c = 0
            for item in StockItems.objects.filter(name = item, is_deleted = False):
                if item.stock == 0:
                    c = c + 1
            if c == counter:
                return True
        return False
    





#Form for adding or editing a product in inventory catalogue 
class ItemForm(forms.ModelForm):
    quantity = forms.CharField(initial="")

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
            'quantity',
            'stock',
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
        self.fields['item_type'].queryset = ItemType.objects.filter(is_disabled = False)
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
        
        # if not stock:
        #     self.add_error('stock','Stock should not be empty')
        # elif stock < 0:
        #     self.add_error('stock','Stock should be a positive number')
        
        if not quantity:
            self.add_error('quantity', 'Quantity should not be empty')
        
        if not mrp:
            self.add_error('mrp','MRP should not be empty')
        elif mrp < 0:
            self.add_error('mrp','MRP should be a positive number')

        return cleaned_data
    
# class ItemForm2(forms.Form):
#     quantity = forms.CharField()
#     cost_price = forms.IntegerField()
#     restock_date = forms.DateField()
#     expiry_date = forms.DateField()

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)


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


# class PictureWidget(forms.widgets.Widget):
#     def render(self, name, value, attrs=None, **kwargs):
#         html =  Template("""<img src="$link"/>""")
#         return mark_safe(html.substitute(link=value))
    

#Form for adding or editing customer details    
class CustomerForm(forms.ModelForm):

    # profile_img = ImageCropField(blank=True, upload_to='images/')
    # # size is "width x height"
    # cropping = ImageRatioField('profile_img', '200x200')
    class Meta:
        model = Customer
        fields = '__all__'
        widgets = {
            'profile_img': ImageCropWidget,
        }
    
    
    profile_img = forms.ImageField(widget=forms.FileInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        phone_no = cleaned_data.get('phone_no')
        profile_img = cleaned_data.get('profile_img')
        width,height = get_image_dimensions(profile_img.file)

        if profile_img:
            if profile_img.size > 2*1024*1024:
                self.add_error('profile_img','Should not be more than 2mb')
            if width > 400 or height > 400:
                self.add_error('profile_img',"Improper size.")
        else:
            self.add_error('profile_img',"Couldn't read uploaded image")
        
        
class MainCategoryForm(forms.ModelForm):

    class Meta:
        model = ItemTypeCategory
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class SubCategoryForm(forms.ModelForm):

    class Meta:
        model = ItemType
        fields = ('category','code','name',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



    def clean(self):
        cleaned_data = super().clean()
        code = cleaned_data.get('code')
        name = cleaned_data.get('name')
        category = cleaned_data.get('category')
        if not code:
            self.add_error('code','Should not be empty')
        if not name:
            self.add_error('name','Should not be empty')
        if not category:
            self.add_error('category','Should not be empty')
        return cleaned_data


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
    
class FileForm(forms.Form):

    # def supplier_choices():
    #     return [('','------')]+[(item, item ) for item in Supplier.objects.all().values_list('name', flat=True)]
    
    supplier = forms.ModelChoiceField(
        queryset= Supplier.objects.all(),
        empty_label="Select Supplier"
    )
    files = forms.FileField(
        required=True,
        validators=[FileExtensionValidator(['csv'])],
        widget=forms.ClearableFileInput(attrs={'accept':'.csv'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['supplier'].widget.attrs['class'] = 'form-control'
        self.fields['files'].widget.attrs['class'] = 'form-control'

class ScanForm(forms.Form):
    barnum = forms.IntegerField(required=True,label="Barcode Number:")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ScanBillingForm(forms.Form):
    barnum = forms.IntegerField(label="Barcode Number:")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        barnum = cleaned_data.get('barnum')
        if barnum != None:
            id=int(str(barnum)[9:12])
            item = StockItems.objects.get(pk=id).name
            if item and Cart.objects.filter(item=item).exists():
                raise forms.ValidationError("Already there")
            if self.is_empty(id):
                raise forms.ValidationError("No stock")
            return cleaned_data
    
    def is_empty(self,id):
        stock = get_object_or_404(StockItems,pk = id)
        if stock.stock == 0:
            return True
        return False
    
class DateRangeForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)




    



