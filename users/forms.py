from typing import Any, Mapping
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms.renderers import BaseRenderer
from django.forms.utils import ErrorList
from .models import BuyerActivity, BuyerAttribute, BuyerCategory, Location, Profile,Post_quill,jobs,SnappFoodList,cities,EntryExitLog
from django import forms
from .models import QuillPost , full_post , raw_material , mother_material
from django import forms
from django_quill.forms import QuillFormField
from django import forms
# forms.py
from django import forms
from .models import MaterialComposition

class RegisterForm(UserCreationForm):
    # fields we want to include and customize in our form
    first_name = forms.CharField(max_length=100,
                                 required=True,
                                 widget=forms.TextInput(attrs={'placeholder': 'First Name',
                                                               'class': 'form-control',
                                                               }))
    last_name = forms.CharField(max_length=100,
                                required=True,
                                widget=forms.TextInput(attrs={'placeholder': 'Last Name',
                                                              'class': 'form-control',
                                                              }))
    username = forms.CharField(max_length=100,
                               required=True,
                               widget=forms.TextInput(attrs={'placeholder': 'Username',
                                                             'class': 'form-control',
                                                             }))
    email = forms.EmailField(required=True,
                             widget=forms.TextInput(attrs={'placeholder': 'Email',
                                                           'class': 'form-control',
                                                           }))
    CHOICES = (('Option 1', 'Option 1'),('Option 2', 'Option 2'),)
    jobs_list = jobs.objects.values_list('id','name')
    # #print(a)
    job_position = forms.ChoiceField(choices=jobs_list,required=True,
                                     widget=forms.Select(attrs={'class':'form-control'}))


    password1 = forms.CharField(max_length=50,
                                required=True,
                                widget=forms.PasswordInput(attrs={'placeholder': 'Password',
                                                                  'class': 'form-control',
                                                                  'data-toggle': 'password',
                                                                  'id': 'password',
                                                                  }))
    password2 = forms.CharField(max_length=50,
                                required=True,
                                widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password',
                                                                  'class': 'form-control',
                                                                  'data-toggle': 'password',
                                                                  'id': 'password',
                                                                  }))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2','job_position']






class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=100,
                               required=True,
                               widget=forms.TextInput(attrs={'placeholder': 'نام کاربری',
                                                             'class': 'form-control',
                                                             }))
    password = forms.CharField(max_length=50,
                               required=True,
                               widget=forms.PasswordInput(attrs={'placeholder': 'رمز عبور',
                                                                 'class': 'form-control',
                                                                 'data-toggle': 'password',
                                                                 'id': 'password',
                                                                 'name': 'password',
                                                                 }))
    remember_me = forms.BooleanField(required=False)

    class Meta:
        model = User
        fields = ['username', 'password', 'remember_me']


class UpdateUserForm(forms.ModelForm):
    username = forms.CharField(max_length=100,
                               required=True,
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True,
                             widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email']


class UpdateProfileForm(forms.ModelForm):
    avatar = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control-file'}))
    bio = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}))
    job_position = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 6}))
    class Meta:
        model = Profile
        fields = ['avatar', 'bio','job_position']




class QuillFieldForm(forms.Form):
    content = QuillFormField()



class QuillPostForm(forms.ModelForm):
    class Meta:
        model = QuillPost
        fields = (
            'content',
        )




class PostForm(forms.ModelForm):
   class Meta:
      model = Post_quill
      fields = ['slug','title', 'body','author']




class full_PostForm(forms.ModelForm):
   class Meta:
      model = Post_quill
      fields = ['slug','title', 'body','author']


from django import forms
# from django.contrib.flatpages.models import FlatPage
# from tinymce.widgets import TinyMCE

from django.forms import ModelForm, TextInput, EmailInput , CharField ,SlugField

class PostForm_tinymce(forms.ModelForm):
    class Meta:
        model = full_post
        fields = ['slug','title', 'content']

        widgets = {
            'title': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'title'
                }),
            'slug': TextInput(attrs={
                'class': "form-control", 
                'style': 'max-width: 300px;',
                'placeholder': 'Url'
                }),
            # 'author':forms.HiddenInput(),
        }


class PostForm_add_material(forms.ModelForm):
    choice = mother_material.objects.values_list('id', 'name')

    mother_material = forms.ChoiceField(
        choices=choice,
        required=True,
        label="ماده اولیه مادر",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = raw_material
        fields = ['name', 'describe', 'unit', 'mother_material', 'image']

        # ✅ Persian Labels
        labels = {
            'name': "نام ماده اولیه",
            'describe': "توضیحات",
            'unit': "واحد اندازه‌گیری",
            'mother_material': "ماده اولیه مادر",
            'image': "تصویر ماده اولیه",
        }

        # Widgets + Placeholders (Persian)
        widgets = {
            'name': forms.TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'مثال: روغن، نمک، برنج ...'
            }),
            'describe': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'توضیحات ماده اولیه'
            }),
            'unit': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'مثال: کیلوگرم، گرم، لیتر ...'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'style': 'max-width: 300px;',
            }),
        }



class PostFormAddMotherMaterial(forms.ModelForm):

    class Meta:
        model = mother_material
        fields = ['name','describe']



        widgets = {
            'name': forms.TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'Material name'
                }),
            'describe': TextInput(attrs={
                'class': "form-control", 
                'style': 'max-width: 300px;',
                'placeholder': 'describe'
                }),

        }


class PostFormAddRestaurant(forms.ModelForm):
    city = forms.ModelChoiceField(
        queryset=cities.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        to_field_name='name'
    )

    class Meta:
        model = SnappFoodList
        fields = ['name', 'link', 'city']  # Include 'name', 'link', and 'city' fields here

        widgets = {
            'name': forms.TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'نام رستوران'
            }),
            'link': forms.TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'لینک اسنپ فود'
            }),
            'city': forms.Select(attrs={
                'class': "form-control",
            }),
        }

    def save(self, commit=True):
        instance = super(PostFormAddRestaurant, self).save(commit=False)
        if commit:
            instance.save()
        return instance
    
    
    
    
    
    
    
    


class EntryExitForm(forms.ModelForm):
    class Meta:
        model = EntryExitLog
        fields = ['location']





class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['name', 'latitude', 'longitude']

    class Media:
        css = {
            'all': ('https://unpkg.com/leaflet@1.7.1/dist/leaflet.css',)
        }
        js = (
            'https://unpkg.com/leaflet@1.7.1/dist/leaflet.js',
            'js/location_map.js',  # Custom JS for map interaction
        )





from .models import EntryExitLog

class EntryExitLogForm(forms.ModelForm):
    class Meta:
        model = EntryExitLog
        fields = ['timestamp', 'is_entry', 'location']  # Add other fields as needed
        widgets = {
            'timestamp': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }










class MaterialCompositionForm(forms.ModelForm):
    class Meta:
        model = MaterialComposition
        fields = ['main_material', 'ingredient', 'ratio']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamic fields based on ingredients, for example:
        self.fields['ingredient'].queryset = raw_material.objects.all()  # Populate ingredient choices





# forms.py
from django import forms
from .models import Buyer


class BuyerForm(forms.ModelForm):
    class Meta:
        model = Buyer
        fields = ['first_name', 'last_name', 'gender', 'phone_number', 'national_code','introduction_method',
                  'province', 'city', 'address', 'details', 'nationality', 'categories']
        labels = {
            'first_name': 'نام ',
            'last_name': 'نام خانوادگی',
            'gender': 'جنسیت',
            'phone_number': 'شماره تماس',
            'national_code': 'کد ملی',
            'introduction_method': 'نحوه آشنایی',
            'province': 'استان',
            'city': 'شهر',
            'address': 'آدرس',
            'details': 'توضیحات تکمیلی',
            'nationality': 'ملیت',
            'categories': 'عضویت در دسته‌بندی‌ها',  # ← اضافه شده
        }
        widgets = {
            'gender': forms.Select(attrs={'class': 'form-control', 'size': 1}),  # 👈 ارتفاع dropdown
            'nationality': forms.Select(attrs={'class': 'form-control', 'size': 1}),
            'address': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'details': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'categories': forms.SelectMultiple(attrs={'class': 'form-control select2', 'size': 3})
        }



from django import forms

class BuyerLoginForm(forms.Form):
    name = forms.CharField(label="نام", max_length=100)
    phone = forms.CharField(label="شماره تلفن", max_length=20)


class BuyerAttributeForm(forms.ModelForm):
    class Meta:
        model = BuyerAttribute
        fields = ['label', 'field_type', 'required']



# forms.py
from .models import DailyReports

class DailyReportForm(forms.ModelForm):
    class Meta:
        model = DailyReports
        fields = ['title', 'content']
        widgets = {
            'title': forms.Select(attrs={'class': 'form-select'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }










from django import forms
from django.contrib.auth.models import User
from .models import Profile, jobs


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    password_confirm = forms.CharField(widget=forms.PasswordInput, required=True, label="تکرار رمز عبور")

    class Meta:
        model = User
        fields = ['username', 'email', 'password',]

        labels = {
            'username': 'نام کاربری',
            'email': 'ایمیل آدرس',
            'password': 'رمز عبور :',
            'Password': 'رمز عبور :',

        }




    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("این نام کاربری قبلا ثبت شده است. لطفا نام دیگری انتخاب کنید.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password")
        p2 = cleaned_data.get("password_confirm")
        if p1 and p2 and p1 != p2:
            self.add_error('password_confirm', "رمز عبور و تکرار آن مطابقت ندارند.")
        return cleaned_data
    


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'first_name', 'last_name', 'phone', 'address', 
            'avatar', 'bio', 'job_position'
        ]
        labels = {
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
            'phone': 'شماره تماس',
            'address': 'آدرس',
            'avatar': 'عکس پروفایل',
            'bio': 'بیوگرافی',
            'job_position': 'سمت شغلی',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control text-end'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control text-end'}),
            'phone': forms.TextInput(attrs={'class': 'form-control text-end'}),
            'address': forms.TextInput(attrs={'class': 'form-control text-end'}),
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control text-end', 'rows': 3}),
            'job_position': forms.Select(attrs={'class': 'form-control'}),
        }





from .models import jobs

class JobForm(forms.ModelForm):
    class Meta:
        model = jobs
        fields = ['name', 'persian_name', 'short_name', 'describe', 'level']
    
        labels = {
            'name': 'نام',
            'persian_name': 'نام فارسی',
            'short_name': 'نام اختصاری انگلیسی',
            'describe': 'توضیحات',
            'level': 'مرتبه شغلی',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control text-end'}),
            'persian_name': forms.TextInput(attrs={'class': 'form-control text-end'}),
            'short_name': forms.TextInput(attrs={'class': 'form-control text-end'}),
            'level': forms.NumberInput(attrs={'class': 'form-control'}),
        }

      

class BuyerCategoryForm(forms.ModelForm):
    class Meta:
        model = BuyerCategory
        fields = ['name' , 'color', 'description']
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام دسته‌بندی'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'توضیحات'}),
        }




class BuyerActivityForm(forms.ModelForm):
    class Meta:
        model = BuyerActivity
        fields = ['buyer', 'activity_type', 'title', 'description', 'next_followup']
        widgets = {
            'activity_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'next_followup': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'buyer': forms.Select(attrs={'class': 'form-select'}),
        }



class MotherMaterialForm(forms.ModelForm):
    class Meta:
        model = mother_material
        fields = '__all__'
        labels = {
            'name': 'نام',
            'describe': 'کد',
            'image': 'تصویر',
            'mode': 'حالت',
        }

class RawMaterialForm(forms.ModelForm):
    class Meta:
        model = raw_material
        fields = '__all__'
        labels = {
            'name': 'نام',
            'describe': 'کد',
            'unit': 'واحد اندازه گیری',
            'image': 'تصویر',
            'mother': 'ماده اولیه مادر',
            'mode': 'حالت',
        }





from django import forms
from .models import MaterialCategory, raw_material

class CategoryForm(forms.ModelForm):
    class Meta:
        model = MaterialCategory
        fields = ["name", "description"]


class RawMaterialCategoryForm(forms.ModelForm):
    class Meta:
        model = raw_material
        fields = ["name", "describe", "unit", "image"]
