from django import forms
from users.models import FoodRawMaterial, raw_material
from .models import FoodIngredient


class FoodForm(forms.ModelForm):
    class Meta:
        model = FoodRawMaterial
        fields = ["name", "details"]


class FoodIngredientForm(forms.ModelForm):
    class Meta:
        model = FoodIngredient
        fields = ["raw_material_price", "quantity", "wastage_percent"]


from django import forms
from .models import FoodRawMaterial

class FoodForm(forms.ModelForm):
    class Meta:
        model = FoodRawMaterial


        
        fields = ['mother', 'name', 'price', 'discount', 'priority', 'details', 'image']

        labels = {
            'mother': 'دسته بندی غذا ',
            'name': 'نام غذا',
            'price': 'قیمت پایه (تومان)',
            'discount': 'درصد تخفیف (%)',
            'priority': 'اولویت نمایش',
            'details': 'توضیحات',
            'image': 'تصویر غذا',
        }

        widgets = {
            'mother': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'priority': forms.NumberInput(attrs={'class': 'form-control'}),
            'details': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
