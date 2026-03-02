from django import forms
from .models import Mine

class MineForm(forms.ModelForm):
    class Meta:
        model = Mine
        fields = ['name','mine_type', 'city' , 'location']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'mine_type': forms.Select(attrs={
                'class': 'form-select',
                'style': 'padding-top:10px; padding-bottom:10px; height:auto;'
            }),
            'location': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }