from django import forms
from .models import PasswordEntry
class PasswordEntryForm(forms.ModelForm):
    password = forms.CharField(
        label="رمز عبور",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        help_text="برای عدم تغییر رمز، خالی بگذارید."
    )

    # Single file upload
    attachment = forms.FileField(
        label="فایل ضمیمه (اختیاری)",
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = PasswordEntry
        fields = [
            'title',
            'category',
            'system_address',
            'username',
            'password',
            'description',
        ]
        labels = {
            'title': 'عنوان',
            'category': 'دسته‌بندی',
            'system_address': 'آدرس / IP',
            'username': 'نام کاربری',
            'description': 'توضیحات',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'system_address': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
