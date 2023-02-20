# FUUUUUUUUUUUUUUUUUUUUUCK THIS 
from django import forms
from django.forms import TextInput, EmailInput
class SearchBarForm(forms.Form):
    item_name = forms.CharField(
        widget=forms.TextInput(
            attrs={'placeholder': 'Item name..', 'style': 'width: 300px;', 'class': 'form-control'}))
