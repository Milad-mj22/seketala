from django import forms

from cameras.models import AIFeatureName, Camera



class CameraForm(forms.ModelForm):


    ai_features = forms.ModelMultipleChoiceField(
        queryset=AIFeatureName.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="قابلیت‌های هوش مصنوعی"
    )


    class Meta:
        model = Camera
        fields = ['name', 'ip_address', 'port', 'username', 'password', 'location', 'description','ai_features']
        widgets = {
            'password': forms.PasswordInput(),
        }


        labels = {
            'name': 'نام دوربین',
            'ip_address': 'آی پی آدرس',
            'port': 'شماره پورت',
            'username': 'نام کاربری',
            'password': 'رمز عبور',
            'location': 'محل قرارگیری',
            'description': 'سایر توضیحات',
        }