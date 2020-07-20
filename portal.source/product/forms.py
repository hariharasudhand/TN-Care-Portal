from django import forms
from django.conf import settings

from .models import Product, Batch, Item


class ProductForm(forms.ModelForm):
    pro_name = forms.CharField(label="Product Name")
    pro_price = forms.IntegerField(label="Product Price")
    exp_duration = forms.IntegerField(label="Expiry Duration")

    class Meta:
        model = Product
        fields = ['pro_name', 'pro_price', 'exp_duration', 'status', 'org']
        # widgets = {'org_id': forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)


class BatchForm(forms.ModelForm):
    release_date = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS,
                                    widget=forms.TextInput(attrs={'type': 'date'}
                                    ))
    no_of_products = forms.IntegerField(label="Number of Items")

    class Meta:
        model = Batch
        fields = ['batch_name', 'prod_id', 'no_of_products', 'status', 'org', 'release_date']

    def __init__(self, *args, **kwargs):
        super(BatchForm, self).__init__(*args, **kwargs)
