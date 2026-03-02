from django import forms
from .models import SoldOutStatus

class SoldOutForm(forms.ModelForm):
    class Meta:
        model = SoldOutStatus
        fields = ['branch', 'product', 'is_sold_out']