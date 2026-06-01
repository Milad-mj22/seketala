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
        max_digits=18,
        decimal_places=0,
        label="کارتخوان بانک مهر",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مقدار را وارد کنید'})
    )
    bank_parsian = CommaDecimalField(
        max_digits=18,
        decimal_places=0,
        label="کارتخوان بانک پارسیان پایین",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مقدار را وارد کنید'})
    )


    kiosk1 = CommaDecimalField(
        max_digits=18,
        decimal_places=0,
        label="کارتخوان بانک پارسیان کیوسک۱",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مقدار را وارد کنید'})
    )

    kiosk2 = CommaDecimalField(
        max_digits=18,
        decimal_places=0,
        label="کارتخوان بانک پارسیان کیوسک۲",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مقدار را وارد کنید'})
    )

    kiosk3 = CommaDecimalField(
        max_digits=18,
        decimal_places=0,
        label="کارتخوان بانک پارسیان کیوسک۳",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مقدار را وارد کنید'})
    )

    bank_melli = CommaDecimalField(
        max_digits=18,
        decimal_places=0,
        label="کارتخوان بانک ملی",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مقدار را وارد کنید'})
    )
    bank_maral = CommaDecimalField(
        max_digits=18,
        decimal_places=0,
        label="واریزی های بانک مارال",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مقدار را وارد کنید'})
    )
    bank_marina = CommaDecimalField(
        max_digits=18,
        decimal_places=0,
        label="واریزی های بانک مارینا",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مقدار را وارد کنید'})
    )
    cash = CommaDecimalField(
        max_digits=18,
        decimal_places=0,
        label="وجه نقد صندوق",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مقدار را وارد کنید'})
    )
    employee_salary = CommaDecimalField(
        max_digits=18,
        decimal_places=0,
        label="نسیه پرسنل",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مقدار را وارد کنید'})
    )
    snapp_food = CommaDecimalField(
        max_digits=18,
        decimal_places=0,
        label="اسنپ فود",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مقدار را وارد کنید'})
    )
    snapp_delivery = CommaDecimalField(
        max_digits=18,
        decimal_places=0,
        label="پیک اسنپ فود",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مقدار را وارد کنید'})
    )
    discounts = CommaDecimalField(
        max_digits=18,
        decimal_places=0,
        label="تخفیفات",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مقدار را وارد کنید'})
    )
    net_total = CommaDecimalField(
        max_digits=18,
        decimal_places=0,
        label="جمع خالص",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مقدار را وارد کنید'})
    )
    gross_sales = CommaDecimalField(
        max_digits=18,
        decimal_places=0,
        label="فروش ناخالص",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مقدار را وارد کنید'})
    )
    delivery_commission = CommaDecimalField(
        max_digits=18,
        decimal_places=0,
        label="کمیسیون پیک ها",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مقدار را وارد کنید'})
    )
    payment_to_shams = CommaDecimalField(
        max_digits=18,
        decimal_places=0,
        label="پرداختی به آقای شمس",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مقدار را وارد کنید'})
    )
    refund_to_customer = CommaDecimalField(
        max_digits=18,
        decimal_places=0,
        label="استرداد به مشتری",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مقدار را وارد کنید'})
    )
    gross_total = CommaDecimalField(
        max_digits=18,
        decimal_places=0,
        label="جمع ناخالص",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مقدار را وارد کنید'})
    )
    cashbox_adjustment = CommaDecimalField(
        max_digits=18,
        decimal_places=0,
        label="کسر/اضافه صندوق",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مقدار را وارد کنید'})
    )
    other_expenses = CommaDecimalField(
        max_digits=18,
        decimal_places=0,
        label="سایر هزینه ها",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مقدار را وارد کنید'})
    )


    peyk_pos_1 = CommaDecimalField(
        max_digits=18,
        decimal_places=0,
        label="پیک ۱ پارسیان (99387213)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مقدار را وارد کنید'})
    )

    peyk_pos_2 = CommaDecimalField(
        max_digits=18,
        decimal_places=0,
        label="پیک ۲ پارسیان (99387216)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مقدار را وارد کنید'})
    )
    peyk_pos_3 = CommaDecimalField(
        max_digits=18,
        decimal_places=0,
        label="پیک ۳ پارسیان (99387215)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مقدار را وارد کنید'})
    )
    peyk_pos_4 = CommaDecimalField(
        max_digits=18,
        decimal_places=0,
        label="پیک ۴ پارسیان (99387217)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مقدار را وارد کنید'})
    )
    peyk_pos_5 = CommaDecimalField(
        max_digits=18,
        decimal_places=0,
        label="پیک ۵ پارسیان (99387214)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مقدار را وارد کنید'})
    )
    peyk_pos_6 = CommaDecimalField(
        max_digits=18,
        decimal_places=0,
        label="پیک 6 مهر (6546423)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مقدار را وارد کنید'})
    )
    
    notes = forms.CharField(
        required=False,
        label="توضیحات",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'توضیحات را وارد کنید'})
    )

    def __init__(self, *args, pardakht_data=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # تعریف نگاشت فیلدها به کلیدهای داده
        field_mapping = {
            'bank_mehr': 'مهر',
            'bank_parsian': 'parsian_pain',
            'kiosk1': 'کیوسک۱',
            'kiosk2': 'کیوسک۲',
            'kiosk3': 'کیوسک۳',
            'bank_melli': 'ملی',
            'snapp_food': 'اسنپ',
            'snapp_delivery': 'اسنپ پیک',
            'employee_salary': 'نسیه پرسنل',
            'discounts': 'تخفیفات',
            'bank_maral': 'واریز1',
            'bank_marina': 'واریز',
            'cash': 'نقدی',
            'net_total': 'جمع خالص',
            'delivery_commission': 'کمیسیون پیک',
        }

        # لیست تمام فیلدهایی که باید مقداردهی اولیه شوند
        all_fields = [
            'bank_mehr', 'bank_parsian', 'kiosk1', 'kiosk2', 'kiosk3', 
            'bank_melli', 'bank_maral', 'bank_marina', 'cash', 
            'employee_salary', 'snapp_food', 'snapp_delivery', 'discounts', 
            'net_total', 'gross_sales', 'delivery_commission', 'payment_to_shams', 
            'refund_to_customer', 'gross_total', 'cashbox_adjustment', 
            'other_expenses', 'peyk_pos_1', 'peyk_pos_2', 'peyk_pos_3', 
            'peyk_pos_4', 'peyk_pos_5', 'peyk_pos_6'
        ]

        # ایجاد دیکشنری مقادیر اولیه
        initial_values = {}

        # 1. مقداردهی بر اساس pardakht_data (اگر وجود داشت)
        if pardakht_data:
            for field_name, pardakht_key in field_mapping.items():
                val = pardakht_data.get(pardakht_key)
                if val is not None:
                    # حذف صفر انتهایی اگر عدد اعشاری باشد
                    if isinstance(val, float) and val.is_integer():
                        val = int(val)
                    # یا اگر به صورت string است:
                    elif isinstance(val, str) and val.endswith('.0'):
                        val = val.rstrip('.0')
                    
                    initial_values[field_name] = val
                    # تنظیم همان help_text که قبلاً داشتید
                    if field_name in self.fields:
                        self.fields[field_name].help_text = f"💰 مبلغ ثبت شده: {val:,} ریال"

        # 2. پر کردن بقیه فیلدها با صفر (اگر در initial_values نبودند)
        for field in all_fields:
            if field not in initial_values:
                initial_values[field] = 0
        
        # مقداردهی نهایی برای فیلدهای متنی
        initial_values['notes'] = ''

        # اعمال تمام مقادیر به فیلدها
        self.initial.update(initial_values)



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
        'notes': 'توضیحات',
        'kiosk1': 'کیوسک۱',
        'kiosk2': 'کیوسک۲',
        'kiosk3': 'کیوسک۳',
        'peyk_pos_1': 'پیک ۱ پارسیان',
        'peyk_pos_2': 'پیک ۲ پارسیان',
        'peyk_pos_3': 'پیک ۳ پارسیان',
        'peyk_pos_4': 'پیک ۴ پارسیان',
        'peyk_pos_5': 'پیک ۵ پارسیان',
        'peyk_pos_6': 'پیک ۶ پارسیان',
        
    }
    
    # Create new dictionary with Persian keys
    persian_data = {}
    for field_name, value in form_data.items():
        persian_key = persian_mapping.get(field_name)
        if persian_key:
            persian_data[persian_key] = value
        else:
            persian_data[field_name] = value
    
    return persian_data