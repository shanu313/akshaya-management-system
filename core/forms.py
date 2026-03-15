from django import forms
from .models import Customer, Service, Bill, BillItem


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = '__all__'


class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ['customer']


class BillItemForm(forms.ModelForm):
    class Meta:
        model = BillItem
        fields = ['service', 'quantity']