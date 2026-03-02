from django import forms
from .models import CustomForm
from django.contrib.auth.models import User

class DynamicFormCreateForm(forms.ModelForm):
    allowed_submit_users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=False,
        label='کاربران مجاز برای ارسال فرم'
    )

    class Meta:
        model = CustomForm
        fields = ['name', 'allowed_submit_users']