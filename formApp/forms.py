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
        fields = [ 'allowed_submit_users']

    

from django import forms
from django.core.validators import MinValueValidator

from django import forms
from django.core.validators import MinValueValidator

class CommaDecimalField(forms.DecimalField):
    """فیلد عددی که کاما را حذف می‌کند قبل از تبدیل به Decimal"""
    def to_python(self, value):
        if value in self.empty_values:
            return None
        # حذف کاماها از ورودی
        value = value.replace(',', '')
        return super().to_python(value)

class NightlySalesForm(forms.Form):
    # فیلدهای فروش (20 مورد) با فیلد سفارشی برای پردازش کاما
    bank_mehr = CommaDecimalField(
        max_digits=10,
        decimal_places=0,
        label="کارتخوان بانک مهر",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مقدار را وارد کنید'})
    )
    bank_parsian = CommaDecimalField(
        max_digits=10,
        decimal_places=0,
        label="کارتخوان بانک پارسیان",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مقدار را وارد کنید'})
    )
    bank_melli = CommaDecimalField(
        max_digits=10,
        decimal_places=0,
        label="کارتخوان بانک ملی",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مقدار را وارد کنید'})
    )
    bank_maral = CommaDecimalField(
        max_digits=10,
        decimal_places=0,
        label="واریزی های بانک مارال",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مقدار را وارد کنید'})
    )
    bank_marina = CommaDecimalField(
        max_digits=10,
        decimal_places=0,
        label="واریزی های بانک مارینا",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مقدار را وارد کنید'})
    )
    cash = CommaDecimalField(
        max_digits=10,
        decimal_places=0,
        label="وجه نقد صندوق",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مقدار را وارد کنید'})
    )
    employee_salary = CommaDecimalField(
        max_digits=10,
        decimal_places=0,
        label="نسیه پرسنل",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مقدار را وارد کنید'})
    )
    snapp_food = CommaDecimalField(
        max_digits=10,
        decimal_places=0,
        label="اسنپ فود",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مقدار را وارد کنید'})
    )
    snapp_delivery = CommaDecimalField(
        max_digits=10,
        decimal_places=0,
        label="پیک اسنپ فود",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مقدار را وارد کنید'})
    )
    discounts = CommaDecimalField(
        max_digits=10,
        decimal_places=0,
        label="تخفیفات",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مقدار را وارد کنید'})
    )
    net_total = CommaDecimalField(
        max_digits=10,
        decimal_places=0,
        label="جمع خالص",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مقدار را وارد کنید'})
    )
    gross_sales = CommaDecimalField(
        max_digits=10,
        decimal_places=0,
        label="فروش ناخالص",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مقدار را وارد کنید'})
    )
    delivery_commission = CommaDecimalField(
        max_digits=10,
        decimal_places=0,
        label="کمیسیون پیک ها",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مقدار را وارد کنید'})
    )
    payment_to_shams = CommaDecimalField(
        max_digits=10,
        decimal_places=0,
        label="پرداختی به آقای شمس",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مقدار را وارد کنید'})
    )
    refund_to_customer = CommaDecimalField(
        max_digits=10,
        decimal_places=0,
        label="استرداد به مشتری",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مقدار را وارد کنید'})
    )
    gross_total = CommaDecimalField(
        max_digits=10,
        decimal_places=0,
        label="جمع ناخالص",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مقدار را وارد کنید'})
    )
    cashbox_adjustment = CommaDecimalField(
        max_digits=10,
        decimal_places=0,
        label="کسر/اضافه صندوق",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مقدار را وارد کنید'})
    )
    other_expenses = CommaDecimalField(
        max_digits=10,
        decimal_places=0,
        label="سایر هزینه ها",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مقدار را وارد کنید'})
    )
    
    notes = forms.CharField(
        required=False,
        label="توضیحات",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'توضیحات را وارد کنید'})
    )


        # Add default values via __init__ method
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default values for all fields
        self.initial.update({
            'bank_mehr': 0,
            'bank_parsian': 0,
            'bank_melli': 0,
            'bank_maral': 0,
            'bank_marina': 0,
            'cash': 0,
            'employee_salary': 0,
            'snapp_food': 0,
            'snapp_delivery': 0,
            'discounts': 0,
            'net_total': 0,
            'gross_sales': 0,
            'delivery_commission': 0,
            'payment_to_shams': 0,
            'refund_to_customer': 0,
            'gross_total': 0,
            'cashbox_adjustment': 0,
            'other_expenses': 0,
            'notes': '',
        })


def save_with_persian_labels(form_data):
    """
    Converts form data to use Persian labels as keys (for database/storage)
    
    Example usage:
    persian_data = save_with_persian_labels(form.cleaned_data)
    """
    persian_mapping = {
        'bank_mehr': 'کارتخوان بانک مهر',
        'bank_parsian': 'کارتخوان بانک پارسیان',
        'bank_melli': 'کارتخوان بانک ملی',
        'bank_maral': 'واریزی های بانک مارال',
        'bank_marina': 'واریزی های بانک مارینا',
        'cash': 'وجه نقد صندوق',
        'employee_salary': 'نسیه پرسنل',
        'snapp_food': 'اسنپ فود',
        'snapp_delivery': 'پیک اسنپ فود',
        'discounts': 'تخفیفات',
        'net_total': 'جمع خالص',
        'gross_sales': 'فروش ناخالص',
        'delivery_commission': 'کمیسیون پیک ها',
        'payment_to_shams': 'پرداختی به آقای شمس',
        'refund_to_customer': 'استرداد به مشتری',
        'gross_total': 'جمع ناخالص',
        'cashbox_adjustment': 'کسر/اضافه صندوق',
        'other_expenses': 'سایر هزینه ها',
        'notes': 'توضیحات'
    }
    
    # Create new dictionary with Persian keys
    persian_data = {}
    for field_name, value in form_data.items():
        persian_key = persian_mapping.get(field_name)
        if persian_key:
            persian_data[persian_key] = value
    
    return persian_data