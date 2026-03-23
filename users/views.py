from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView
from django.contrib.auth import logout

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.views import View
from django.contrib.auth.decorators import login_required
from khayyam import JalaliDatetime

from StoneFlow.models import PreInvoice, PreInvoiceItem
from order_flow.models import MaterialUsage, OrderStep
from otp_manager.utils import send_night_order_sms
from users.EntryModule.EntryUtils import get_latest_exit, is_user_in , UserWorkTimeManager
from .decorators import job_required
from users.utils.CalulatedDistance import calculate_distance

from .forms import BuyerActivityForm, BuyerAttributeForm, BuyerCategoryForm, CategoryForm, JobForm, MotherMaterialForm, RawMaterialCategoryForm, RawMaterialForm, RegisterForm, LoginForm, UpdateUserForm, UpdateProfileForm
from django.views import generic
from .models import AllowedLocation, BuyerActivity, BuyerAttribute, BuyerAttributeValue, BuyerCategory, CapturedImage, Inventory, InventoryLog, MaterialCategory, MaterialComposition, MenuItem, Post, RemainingMaterialsUsage,Tools,full_post,Profile
from django.shortcuts import get_object_or_404
import numpy as np
from django.http import HttpResponse
from .forms import PostForm_add_material,PostFormAddMotherMaterial,PostFormAddRestaurant,EntryExitForm
from .models import User,jobs , Projects , raw_material,SnappFoodList
from .models import Profile as model_profile
from .models import create_order as ModelCreateOrder
from .models import mother_material as MotherMaterial
from .models import raw_material as RawMaterial
from .models import FoodRawMaterial 
from .models import Warehouse
from .models import mother_food as MotherFood
from .models import EntryExitLog
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect
import os
from datetime import datetime, timezone , timedelta

import jdatetime
from snapp_discount.getPrice import get_price
from .constants import translate
from Constatns import Constants
import json
from decimal import Decimal
from users import models
from django.http import JsonResponse
from django.conf import settings
from django.db.models import Sum, Prefetch, F, DecimalField, Q  # Import DecimalField
from django.db.models.functions import Coalesce
import time
from persiantools.jdatetime import JalaliDate
from urllib.parse import urlparse
from pywebpush import webpush, WebPushException
import base64
from django.core.files.base import ContentFile

from .models import RestaurantBranch,NightOrderRemainder

from django.shortcuts import render, redirect
from .models import Buyer, InventoryLog
from .forms import BuyerLoginForm
from .forms import UserForm, ProfileForm

from django.core.exceptions import ObjectDoesNotExist


from .models import DailyReports , ReportTitles
from .forms import DailyReportForm
from datetime import date

from django.utils.timezone import now
from django.db.models import Max






CACHE_CITIES = 'snapp_discount/cache/cities'

# backend_endpoint

BACKEND_ENDPOINT = 'http://127.0.0.1:8000' 

from django.contrib.auth.views import LogoutView

def clean_buyer_names(buyers):
    try:
        for buyer in buyers:

            buyer.first_name = buyer.first_name.replace('�','')
            buyer.last_name = buyer.last_name.replace('�','')
            full_name = f"{buyer.first_name} {buyer.last_name or ''}"
            buyer.short_name = full_name[:40] + ('…' if len(full_name) > 50 else '')
    except:    
        return buyers

    return buyers




class CustomLogoutView(LogoutView):
    def get(self, request, *args, **kwargs):
        messages.success(request, "You have been logged out successfully.")
        logout(request)

        return redirect(to='login')
        return redirect('users-register')
        return self.post(request, *args, **kwargs)

def logout_view(request):
    logout(request)
    return render(request, 'users/logout.html')


def home(request):
    if not request.user.is_authenticated:
        return redirect('login')   # اسم urlname صفحه لاگینت رو بزن (مثلاً 'login')

    return render(request, 'users/home.html', {
        'company_name': Constants.NAME,
        'vapid_public_key': settings.VAPID_PUBLIC_KEY
    })

class RegisterView(View):

    form_class = RegisterForm
    initial = {'key': 'value'}
    template_name = 'users/register.html'

    def dispatch(self, request, *args, **kwargs):
        # will redirect to the home page if a user tries to access the register page while logged in
        if request.user.is_authenticated:
            return redirect(to='/')

        # else process dispatch as it otherwise normally would
        return super(RegisterView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            # form.save()


            obj =form.save()
            
            form.save()

            b =model_profile.objects.all().last()
            b.job_position_id =int(request.POST['job_position'])
            b.save()
            username = form.cleaned_data.get('username')

            messages.success(request, f'Account created for {username}')

            return redirect(to='login')

        return render(request, self.template_name, {'form': form})


@csrf_exempt
def save_subscription(request):
    if request.method == "POST":
        data = json.loads(request.body)
        # user_id = data.get("user_id")
        user_id =request.user.id

        try:
            user = User.objects.get(id=user_id)
            profile = Profile.objects.get(user=user)
            profile.push_endpoint = data["endpoint"]
            profile.push_p256dh = data["keys"]["p256dh"]
            profile.push_auth = data["keys"]["auth"]
            profile.save()

            return JsonResponse({"message": "Subscription saved successfully!"})
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)
        
        



class CustomLoginView(LoginView):
    form_class = LoginForm

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')

        username = form.cleaned_data.get('username')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(self.request, 'کاربری با این نام وجود ندارد.')
            return self.form_invalid(form)

        # Now check if Profile exists for that user
        try:
            profile = user.profile
        except ObjectDoesNotExist:
            messages.error(self.request, 'پروفایل کاربر یافت نشد.')
            return self.form_invalid(form)



        if not remember_me:
            self.request.session.set_expiry(0)
            self.request.session.modified = True



        # انجام ورود
        response = super().form_valid(form)
        # بررسی اینکه آیا پروفایل وجود دارد یا نه
        try:
            self.request.user.profile
        except ObjectDoesNotExist:
            messages.error(self.request, 'پروفایل شما وجود ندارد. لطفاً با مدیر سیستم تماس بگیرید.')
            
            return redirect(reverse_lazy('login'))



        return response



@login_required
def post_login_redirect(request):

    job_name = request.user.profile.job_position.name
    if hasattr(request.user, 'profile') and (job_name == 'CEO' or job_name == 'Technical Manager' or job_name == 'Programmer'):
        return redirect('mian_dashboard')  # نام view یا نام urlpattern

    return redirect('users-home')  # نام view یا نام urlpattern



class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('users-home')


class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'users/change_password.html'
    success_message = "Successfully Changed Your Password"
    success_url = reverse_lazy('users-home')


@login_required
def profile(request):
        if request.method == 'POST':
            user_form = UpdateUserForm(request.POST, instance=request.user)
            profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)

            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, 'Your profile is updated successfully')
                return redirect(to='users-profile')
        else:
            user_form = UpdateUserForm(instance=request.user)
            # if request.user
            try:

                user = Profile.objects.get(id = request.user.id)


            except Exception as e:
                #print('Error profile_form :' , e)
                return render(request, 'users/profile.html', {'user_form': user_form})


        return render(request, 'users/profile.html', {'user_form': user_form, 'user': user})


# @login_required
@job_required(['Manager', 'Admin','Programmer','CEO'])
def tools(request):
    queryset = Tools.objects.all().order_by('-title').reverse()

    return render(request, 'users/tools_new.html',{'tools':queryset})


@login_required
def create_order(request):

    if request.method == 'POST':
        
        data = dict(request.POST.dict())
        data.pop('csrfmiddlewaretoken','Not found')


        for field,value in data.items():
            if value.isnumeric():
                data[field]=float(value)



        ModelCreateOrder.objects.create(author = request.user , content = data)


        # if form.is_valid():
            # obj =form.save(commit=False)
            # obj.author = User.objects.get(pk=request.user.id)
            # form.save()
        messages.success(request,'New Forum Successfully Added')
        return redirect('/profile/my_orders')

    
        # else:
        #     messages.error(request, 'Please correct the following errors:')
        #     materials = raw_material.objects.all()
        #     return render(request, 'users/post_list_quil.html', {'materials': materials})



    else:

        # materials = raw_material.objects.all().order_by('-mother_id')
        # return render(request, 'users/create_order.html', {'materials': materials})





        # mother_materials = MotherMaterial.objects.prefetch_related('mother_material').order_by('describe').all()
 
        # return render(request, 'users/create_order.html', {'mother_materials': mother_materials})
    


        user = request.user
        # Get all categories the user can see
        # user_categories = user.profile.categories.all() 
        user_categories = user.material_categories.all()
         # assumes Profile model with ManyToMany to MaterialCategory

        # Get all mother materials
        mother_materials = MotherMaterial.objects.prefetch_related('mother_material').order_by('describe').all()

        # Prepare a list of mother_materials with filtered raw materials
        filtered_mother_materials = []
        for mother in mother_materials:
            # Filter raw materials by user's categories
            allowed_materials = mother.mother_material.filter(category__in=user_categories)
            if allowed_materials.exists():
                # Attach filtered queryset to a temporary attribute
                mother.allowed_materials = allowed_materials
                filtered_mother_materials.append(mother)

        return render(request, 'users/create_order.html', {
            'mother_materials': filtered_mother_materials,
        })













@login_required
def my_orders(request):
    from django.utils.timezone import now  # better than datetime.now() in Django

    orders = ModelCreateOrder.objects.order_by('updated_at')
    # orders = orders.order_by('-updated_at').reverse()
    orders = orders.reverse()
    orders = orders[:15]
    editable = []

    
    materials_quantity = get_material_quantity(show_all=True)


    for order in orders:
        order.content = eval(order.content)
        try:
            if order.night_order is not None:
                order.night_order = eval(order.night_order)

        except:
            print('Error : my_orders night order ERORrrrrrrrrrrr')

        # --- EDITABLE LOGIC ---
        created_date = order.created_at
        tomorrow = (created_date + timedelta(days=1)).replace(
            hour=4, minute=0, second=0, microsecond=0
        )

        if now() < tomorrow:
            order.created_at = True   # editable
        else:
            order.created_at = False  # not editable


        date = order.updated_at
        # convert_to_jalali(date_str=date)
        jalali_datetime = jdatetime.date.fromgregorian(date=date)
        # Format the Jalali date and time
        formatted_jalali_date = jalali_datetime.strftime('%Y-%m-%d')  # Format the Jalali date
        formatted_jalali_time = date.strftime('%H:%M')  # Format the time (remains the same)

        # Combine date and time
        formatted_jalali_datetime = f"{formatted_jalali_date} {formatted_jalali_time}"
        order.updated_at = formatted_jalali_datetime








            # material = materials_quantity.get(name = rw)

      
            # quantity =float(Decimal(material.total_quantity))

            # if quantity<value:

            #     if rw in list(required_items.keys()): 

            #         required_items[rw] =round(value - quantity + required_items[rw],3)
            #     else:
            #         required_items[rw] =round(value - quantity,3)






        values = order.content

        data = {}



        for field in values.keys():
            if field!='additional_details'  :
                try:
                    if float(values[field])>0:
                        try:
                            # #print(field)
                            value = float(values[field])

                            data = {}

                            obj = raw_material.objects.filter(name = field).first()
                            if obj.unit != 'number':
                                values[field] = '{} {}'.format(round(value,3),translate(obj.unit))
                            else:
                                values[field] = '{} {}'.format(int(value),translate(obj.unit))


                     

                            material = materials_quantity.get(name = field)
                            quantity =float(Decimal(material.total_quantity))
                            
                            exist=True
                            if quantity<round(float(value),3):
                                exist = False


                            values[field] += '| موجود {}'.format(quantity)

                            if quantity!=0:
                                values[field] +=' {}'.format( translate(obj.unit))


                        
                            data = {
                                'amount':values[field],
                                'exist' : exist
                            }

                            values[field] = data
                        
                        
                        except:
                            print('eror')
                except:
                    pass
                    # print('Error in my_order : ')


    return render(request, 'users/my_orders.html', {'orders': orders,'editable':editable})




def convert_to_jalali(date_str):
    # Parse the date string to a datetime object
    date_obj = datetime.strptime(date_str, '%b. %d, %Y, %I:%M %p')
    
    # Convert to Jalali
    jalali_date = jdatetime.date.fromgregorian(date=date_obj)

    # Format the Jalali date
    return jalali_date.strftime('%Y-%m-%d')


@login_required
def add_raw_material(request):
    if request.method == 'POST':
        form = PostForm_add_material(request.POST, request.FILES)  # ✅ اضافه کردن request.FILES
        if form.is_valid():
            obj = form.save(commit=False)
            obj.author = request.user  # اگر فیلد author در مدل هست
            mother_id = form.cleaned_data['mother_material']
            obj.mother = get_object_or_404(MotherMaterial, id=mother_id)

            obj.save()  # ✅ ذخیره obj با تصویر
            messages.success(request, 'ماده اولیه با موفقیت افزوده شد.')
            return redirect('/profile/my_orders')
        else:
            messages.error(request, 'لطفاً خطاهای فرم را اصلاح کنید.')
            return render(request, 'users/create_material.html', {'form': form})
    else:
        form = PostForm_add_material()
        return render(request, 'users/create_material.html', {'form': form})
    
    

@login_required
def add_mother_material(request):

    if request.method == 'POST':
        form = PostFormAddMotherMaterial(request.POST)
        if form.is_valid():
            obj =form.save(commit=False)
            obj.author = User.objects.get(pk=request.user.id)
            form.save()
            messages.success(request,'New Forum Successfully Added')
            return redirect('/profile/my_orders')

        
        else:
            messages.error(request, 'Please correct the following errors:')
            return render(request,'users/create_mother_material.html',{'form':form})
        
    else:
        form = PostFormAddMotherMaterial()
        context = {
            'form':form
        }
        return render(request, 'users/create_mother_material.html',context)








@login_required
def post_edit_quil(request,id):
    materials = get_object_or_404(ModelCreateOrder,id=id)
    materials = eval(materials.content)


    if 'additional_details' in materials.keys():
        details = materials['additional_details']
        materials.pop('additional_details')
    else:
        details=''


    if request.method == 'GET':

        # new_mat = {}
        # for field,value in materials.items():
        #     if isinstance(value,int) :
        #         new_mat[field] = value

        # context = {'form': PostForm_tinymce(instance=post), 'id': id}
        # return render(request,'users/create_post.html',context)
        # materials = raw_material.objects.all()
        return render(request, 'users/edit_order.html', {'materials': materials,'edit':True,'details':details})


   
    elif request.method == 'POST':

        data = dict(request.POST.dict())

        data.pop('csrfmiddlewaretoken','Not found')


        for field,value in data.items():
            if value.isnumeric():
                data[field]=float(value)


        ret = ModelCreateOrder.objects.filter(id=id).first()
        if ret:
            ret.content=data
            ret.save()


        # b = ModelCreateOrder.objects.update_or_create(author = request.user , content = data)


        messages.success(request, 'The post has been updated successfully.')
        return redirect('/profile/my_orders')
        # else:
        #     messages.error(request, 'Please correct the following errors:')
        #     return render(request,'posts/post_form.html',{'form':form})
        





# @login_required
def show_order(request,id):
    materials = get_object_or_404(ModelCreateOrder,id=id)
    materials = eval(materials.content)
    if request.method == 'GET':

        # context = {'form': PostForm_tinymce(instance=post), 'id': id}
        # return render(request,'users/create_post.html',context)
        # materials = raw_material.objects.all()






        return render(request, 'users/edit_order.html', {'materials': materials,'edit':False})


   
    elif request.method == 'POST':

        data = dict(request.POST.dict())
        data.pop('csrfmiddlewaretoken','Not found')


        b = ModelCreateOrder.objects.update_or_create(author = request.user , content = data)


        messages.success(request, 'The post has been updated successfully.')
        return redirect('/profile/my_orders')
        # else:
        #     messages.error(request, 'Please correct the following errors:')
        #     return render(request,'posts/post_form.html',{'form':form})
        



@login_required
def snapp(request):

    #print('show snapp page')

    try:
        cities = os.listdir(CACHE_CITIES)
    except:
        cities = []

    return render(request, 'users/snapp_cities.html',{'cities':cities})




def show_restaurant_list(request,city):


    #print('show snapp page')
    restaurants = SnappFoodList.objects.all().order_by('-name')

    try:
        path = os.path.join(CACHE_CITIES,city)
        restaurants_ = os.listdir( path)

        restaurants = []

        for res in restaurants_:
            restaurants.append(res[:-5])

    except:
        restaurants = []

    return render(request, 'users/snapp_restaurants.html',{'city':city,'restaurants':restaurants})







def restaurant_food_list(request,city,res_name):


    # try:

    gp = get_price(res_name=res_name,city=city)




    prices = gp.ret_price()
    prices = prices[res_name]
    #print('show restaurant_list page')


    # except:
    #     prices = []


    return render(request, 'users/show_prices.html',{'city':city,'prices':prices})


def add_restaurant(request):


    if request.method == 'POST':
        form = PostFormAddRestaurant(request.POST)
        if form.is_valid():
            obj =form.save(commit=False)
            obj.author = User.objects.get(pk=request.user.id)
            form.save()

            # get_price()

            data = request.POST.dict()

            gp = get_price(res_name=data['name'],res_link=data['link'],city= data['city'])
            gp.get_name_price()

            messages.success(request,'New Forum Successfully Added')

            # return render(request, 'users/snapp_restaurants.html',{'city':city,'restaurants':restaurants})
            return tools(request=request)
        else:
            messages.error(request, 'Please correct the following errors:')
            return render(request,'users/create_mother_material.html',{'form':form})
        
    else:
        form = PostFormAddRestaurant()
        context = {
            'form':form
        }
        return render(request, 'users/create_mother_material.html',context)






@login_required
def print_order(request,id):
    materials = get_object_or_404(ModelCreateOrder,id=id)
    
    material_dict = eval(materials.content)
    new_materials ={}

    orderStep1 = OrderStep.objects.filter(order=materials,step_number=1).first()
    orderStep2 = OrderStep.objects.filter(order=materials,step_number=2).first()
    orderStep3 = OrderStep.objects.filter(order=materials,step_number=3).first()
    orderStep4 = OrderStep.objects.filter(order=materials,step_number=4).first()



    for material,value in material_dict.items():
        try:
           if value!='':
                if float(value)>0:
                    unit =''
                    try:
                        ret = raw_material.objects.get(name=material)
                        unit = ret.unit
                        mother_id = ret.mother.describe
                        material_id = ret.describe
                        full_id = mother_id+material_id

                    except:
                        print('Cant get unit')
                        #print('Cant get unit {}'.format(material))
                    new_materials[material] = {}
                    new_materials[material]['code'] = str(full_id)
                    new_materials[material]['unit'] = translate(str(unit))
                    
                    new_materials[material]['value'] = str(value)

                    if orderStep2:
                        step2 = MaterialUsage.objects.filter(step=orderStep2,material=ret).first()
                        new_materials[material]['step2'] = str(step2.quantity)
                    if orderStep3:
                        step3 = MaterialUsage.objects.filter(step=orderStep3,material=ret).first()
                        new_materials[material]['step3'] = str(step3.quantity)
                    if orderStep4:
                        step4 = MaterialUsage.objects.filter(step=orderStep4,material=ret).first()
                        new_materials[material]['step4'] = str(step4.quantity)
        except Exception as e:
            print(e)


    headers = ['کد کالا','نام کالا','واحد','درخواستی','ارسالی','تحویلی','مانده','کد کالا','نام کالا','واحد','درخواستی','ارسالی','تحویلی','مانده']

    return render(request, 'users/print_order.html', {'materials': new_materials,'edit':False,'headers':headers})

        



@login_required
def foodRawMaterials(request):

    #print('show snapp page')
    restaurants = FoodRawMaterial.objects.all().order_by('-name')


    return render(request, 'users/food_raw_materials.html',{'foods':restaurants})






def addfoodrawmaterial(request):

    if request.method == 'POST':
        data = dict(request.POST.dict())
        data.pop('csrfmiddlewaretoken','Not found')
        food_name = data['food_name']
        data.pop('food_name','Not found location')

        mother_food =int(data['mother_food'])
        data.pop('mother_food','mother_food')



        if  FoodRawMaterial.objects.filter(name=food_name).first()==None:


            user = User.objects.get(pk=request.user.id)
    
            values ={}

            for field,value in data.items():
                # try:
                    if float(value)>0:
                        values[field]=value
                        # item = raw_material.objects.filter(name=field).first()
                        # item_id = item.id
                        # item = raw_material.objects.get(id=item_id)
                        # b=AddtoStore.objects.create(item=item,location=location,count =value, author = user)
                        # update_store(item=item,location=location,value=value)
                        # #print(b)
                # except:
                # #print('error in add to store')

            obj_mother_food = MotherFood.objects.filter(id=mother_food).first()
            if obj_mother_food:
                food_name = obj_mother_food.name+' '+food_name

            b = FoodRawMaterial.objects.update_or_create(name= food_name, data = values, mother =obj_mother_food )
            messages.success(request,'New Item Successfully Added')

            return redirect('/tools/foodrawmaterials')
        
        else:
            #print('mojooooooodddddd')
            return redirect('/tools/foodrawmaterials')



    else:
        mother_materials = MotherMaterial.objects.prefetch_related('mother_material').all()
        mother_foods = MotherFood.objects.all()

        foods = FoodRawMaterial.objects.all()
        food_list =[]
        for food in foods:
            food_list.append(food.name)
        return render(request, 'users/create_food_raw_material.html', {'mother_materials': mother_materials,'food_names':food_list,'mother_foods':mother_foods})
    



def add_count_to_materials(mother_materials,data):

    # mother_materials = MotherMaterial.objects.all()

    # Create a dictionary to store submaterials for each mother material
    materials_with_submaterials = {}

    

    # Iterate through each mother material and fetch related submaterials
    for mother_material in mother_materials:
        submaterials = mother_material.mother_material.all()
        for submaterial in submaterials :
            # count = fullStore.objects.filter(item = submaterial.id).all()
            if submaterial.name in data:
                submaterial.count = data[submaterial.name]
        materials_with_submaterials[mother_material] = submaterials

    return materials_with_submaterials



def show_food_material(request,id):
        
    if request.method == 'POST':
        data = dict(request.POST.dict())
        data.pop('csrfmiddlewaretoken','Not found')
        food_name = data['food_name']

        



        data.pop('food_name','Not found location')
        user = User.objects.get(pk=request.user.id)

        values ={}

        for field,value in data.items():
            try:
                if value !='':
                    if float(value)>0:
                        values[field]=value
            except:
                print('error in add to store')

        
        food = FoodRawMaterial.objects.filter(name=food_name).first()
        food.data=values
        food.save()
        # _,ret = FoodRawMaterial.objects.update(name= food_name, data = values)
        # if ret:
        #     messages.success(request,'New Item Successfully Added')

        return redirect('/tools/foodrawmaterials')
        # else:
        #     #print('Error in update data')
        #     return redirect('/tools/foodrawmaterials')

  
    else:



        mother_materials = MotherMaterial.objects.prefetch_related(
            Prefetch(
                'mother_material',  # Replace 'raw_material' with the correct related_name of RawMaterial in MotherMaterial
                queryset=RawMaterial.objects.order_by('describe')  # Sorting by 'describe' in ascending order
            )
        ).order_by('describe')




    

        # foods = FoodRawMaterial.objects.all()
        food_name = FoodRawMaterial.objects.filter(id=id).first()
        if food_name.data is not None:
            mother_materials = add_count_to_materials(mother_materials,food_name.data)
        return render(request, 'users/show_food_raw_material.html', {'mother_materials': mother_materials,'food_name':food_name})
    




@login_required
def night_food_order(request):
    if request.method == 'POST':
        
        data = dict(request.POST.dict())
        data.pop('csrfmiddlewaretoken','Not found')
       
        if 'use_remaining' in data.keys():
            use_remaining = data['use_remaining']
            data.pop('use_remaining','Not found')
            if use_remaining:
                RemainingMaterialsUsage.objects.create(user=request.user)

        # else:
        #     return


        materials_quantity = get_material_quantity(show_all=True)

        raw_material={}
        required_items = {}
        number_type = {}

        for food_name,value in data.items():
            # if value.isnumeric():
                data[food_name]=float(value)
                
                ret = FoodRawMaterial.objects.filter(name=food_name).first()
                if ret :
                    if ret.data is not None:
                        n_value = number_type.get(ret.mother.name,0)
                        n_value+= float(value)
                        number_type.update({ret.mother.name:n_value})

                        for material in ret.data.keys():
                            
                            
                            new_value = round(float(ret.data[material])*float(value),4)


                            if material in raw_material.keys():

                                raw_material[material]+=new_value
                            
                            else:
                                raw_material[material]=new_value




        for rw , value in raw_material.items():

            material = materials_quantity.get(name = rw)

      
            quantity =float(Decimal(material.total_quantity))

            if quantity<value:

                if rw in list(required_items.keys()): 

                    required_items[rw] =round(value - quantity + required_items[rw],3)
                else:
                    required_items[rw] =round(value - quantity,3)


        status = ModelCreateOrder.objects.create(author = request.user , content = raw_material, night_order = data )

        if status:
            messages.success(request,'New Forum Successfully Added')


        send_night_order_sms(request=request,status=status,number_type=number_type)

        if required_items=={}:
            return redirect('/profile/my_orders')
        else:
            return render(request, 'users/reqiured_items.html', {'required_items': required_items})



    else:
        mother_foods = MotherFood.objects.prefetch_related('mother_food_id').all()
        try:
            producible_foods = calculateProducibleMeals()
        except:
            producible_foods = {}


        # Get the latest recorded date from RemainingMaterialsUsage
        last_usage_date = RemainingMaterialsUsage.objects.aggregate(Max('used_at'))['used_at__max']

        # Ensure we have a valid date, fallback to earliest order date if None
        if last_usage_date is None:
            last_usage_date = ModelCreateOrder.objects.earliest('created_at').created_at

        # Filter orders from last usage date to today, limiting to last 10
        last_10_orders = ModelCreateOrder.objects.filter(
            created_at__gte=last_usage_date,
            created_at__lte=now()
        ).order_by('-created_at')[:10]
        # Get all OrderStep objects related to these orders where step_number is 4
        step_4_orders = OrderStep.objects.filter(order__in=last_10_orders, step_number=4)

        # Get all MaterialUsage objects related to these steps where quantity > 0
        materials_in_step_4 = MaterialUsage.objects.filter(step__in=step_4_orders, quantity__gt=0)
        # If you want only distinct materials (without duplicate entries)
        # distinct_materials = materials_in_step_4.values_list('material', flat=True).distinct()

        # If you need full material details
        # distinct_materials_details = raw_material.objects.filter(id__in=distinct_materials)



        for mother_food in mother_foods:
            total = 0
            for food in mother_food.mother_food_id.all():
                food_name = food.name

                if food_name in list(producible_foods.keys()):
                    food.producible_quantity = producible_foods[food_name]
                    total += producible_foods[food_name]  
                else:
                    food.producible_quantity = 0


            mother_food.producible_quantity = total                 


        return render(request, 'users/night_order.html', {'mother_foods': mother_foods,'exist_materials':materials_in_step_4})
    







def show_night_order_material(request):



        data = dict(request.POST.dict())
        data.pop('csrfmiddlewaretoken','Not found')

        materials_quantity = get_material_quantity(show_all=True)

        raw_material={}
        required_items = {}
        foods = {}

        for food_name,value in data.items():
            # if value.isnumeric():
                #print(float(value))
                if float(value)>0:
                    data[food_name]=float(value)
                    
                    ret = FoodRawMaterial.objects.filter(name=food_name).first()

                    if ret :

                        foods[food_name] = {
                            'value': value,
                        }
                        for material in ret.data.keys():
                            
                            
                            new_value = round(float(ret.data[material])*float(value),4)


                            if material in raw_material.keys():

                                raw_material[material]+=new_value
                                # raw_material[material] = round(raw_material[material],4)
                            
                            else:
                                raw_material[material]=new_value
                                # raw_material[material] = round(raw_material[material],4)



        items = {}


        for rw , value in raw_material.items():

            material = materials_quantity.get(name = rw)
            if material:
        
                quantity =float(Decimal(material.total_quantity))
                quantity = round(quantity,4)
                value = round(value,4)
                items[rw] = {
                    'required': value,
                    'available': quantity,
                    'exist': quantity >= value
                }




        return render(request, 'users/show_night_order_material.html', {'items': items , 'foods':foods})











def calculateProducibleMeals():

    # mother_materials = MotherFood.objects.prefetch_related('mother_food_id').all()
    producible_foods = {}

    materials = get_material_quantity()  # Get available materials with quantities
    exist_materials = materials.values_list('name', flat=True)  # Get the names of existing materials

    foods = FoodRawMaterial.objects.all()  # Get all food recipes

    for food in foods:
        recepi = food.data  # Recipe for the food (ingredients and their required quantities)

        max_food_quantity = float('inf')  # Start with infinity, then find the limiting material

        for item, required_qty in recepi.items():  # Iterate through each material in the recipe
            if item not in exist_materials:  # If the material is not available, you can't make this food
                max_food_quantity = 0
                break

            material = materials.get(name=item)  # Get the available material from the materials list

            # Calculate how many times the available material can meet the required quantity
            available_qty = Decimal(material.total_quantity)
            possible_quantity = available_qty // Decimal(required_qty)  # Use floor division

            # The maximum food quantity is determined by the most limiting ingredient
            max_food_quantity = min(max_food_quantity, possible_quantity)

        # if max_food_quantity==0:
        #     break


        if max_food_quantity > 0 and  max_food_quantity != float('inf'):  # If at least 1 of this food can be made
            # producible_foods.append((food, max_food_quantity))  # Append the food and the quantity
            producible_foods[food.name] = int(max_food_quantity)
    # Print the producible foods and the quantity
    # for food, quantity in producible_foods:
    #     #print(f'You can make {quantity} of {food.name}')

    return producible_foods







def load_temp(request):
    return render(request,'users/temp.html')





@login_required
def add_store(request):

    if request.method == 'POST':
        
        data = dict(request.POST.dict())
        data.pop('csrfmiddlewaretoken','Not found')



        if 'warehouse' in data.keys():
            ware_house = data['warehouse']
            data.pop('warehouse','Not found')

        else:
            return
        
        
        if 'receipt_number' in data.keys():
            receipt_number = data['receipt_number']
            data.pop('receipt_number','Not found')

        else:
            return
        

        image_data = request.POST.get('captured_image')
        # #print('image_data',image_data)
        if image_data:
            data.pop('captured_image','Not found')
            try:


                format, imgstr = image_data.split(';base64,') 
                ext = format.split('/')[-1]  

                # Fix padding issue
                missing_padding = len(imgstr) % 4  
                if missing_padding:  
                    imgstr += '=' * (4 - missing_padding)  # Add missing padding  


                # image = ContentFile(base64.b64decode(imgstr), name=f"receipt_image.{ext}")
                # #print('3')

                
                #print(f'Format: {format}')  # Check the extracted format
                #print(f'Ext: {format.split("/")[-1]}')  # Check extension
                #print(f'First 50 chars of imgstr: {imgstr[:50]}')  # Check base64 content

                try:
                    # image = ContentFile(base64.b64decode(imgstr), name=f"receipt_image.{ext}")
                    image = ContentFile(base64.urlsafe_b64decode(imgstr), name=f"receipt_image.{ext}")
                    #print("Image successfully created")
                except Exception as e:
                    print(f"Error: {e}")
            
                saved_image = CapturedImage.objects.create(image=image,receipt_number=receipt_number)  # Save to model
                #print('saved_image : ',saved_image)
            except:
                #print('Error in save image')
                pass
                
            
        #print('milaaaaaaaad')


        user_id =request.user.id
        user = User.objects.get(id=user_id)
        profile = Profile.objects.get(user=user)# Get the latest subscription for testing


        ware_house = Warehouse.objects.get(id = ware_house)

        values ={}

        for field,value in data.items():
            try:
                if value !='':
                    if float(value)>0:
                        values[field]=value
                        decimal_value = Decimal(value)
                        raw_material_instance = raw_material.objects.get(name=field)
                        inventory, created = Inventory.objects.get_or_create(inventory_raw_material=raw_material_instance,warehouse=ware_house)
                        inventory.add_stock(amount=decimal_value,user=profile,receipt_number=receipt_number)



            except:
                #print('error in add to store')
                messages.success(request,'بروز خطا در هنگام اضافه نمودن')
                return redirect('/')  # Redirect to your desired page

        messages.success(request,'مقادیر مورد نظر با موفقیت اضافه گردید')
        # return redirect('/profile/my_orders')
        return redirect('success_page')  # Redirect to your desired page

    else:

        mother_materials = MotherMaterial.objects.prefetch_related('mother_material').order_by('describe').all()

        ware_houses = Warehouse.objects.all()
 
        return render(request, 'users/store_add.html', {'mother_materials': mother_materials,'warehouses':ware_houses})
    



from .forms import MaterialCompositionForm

def material_composition_view_first(request):
    if request.method == 'POST':
        form = MaterialCompositionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success_url')  # Redirect to a success page
    else:
        form = MaterialCompositionForm()
    
    return render(request, 'material_composition.html', {'form': form})




def get_total_quantity(material):
    total = Inventory.objects.filter(inventory_raw_material=material).aggregate(Sum('quantity'))['quantity__sum']
    return total or 0  # اگر مقدار None بود، 0 برگردانید





from django.db import transaction
@transaction.atomic
# views.py
def material_composition_view(request):



    if request.method == 'POST':

        main_materials = MaterialComposition.objects.values_list("main_material__name", flat=True).distinct()



        data = dict(request.POST.dict())
        data.pop('csrfmiddlewaretoken','Not found')



        if 'warehouse' in data.keys():
            ware_house = data['warehouse']
            data.pop('warehouse','Not found')

        else:
            return


        profile = request.user.profile
        ware_house = Warehouse.objects.get(id = ware_house)



        flag_error = False
        
        try:
            with transaction.atomic():
                for key, value in data.items():
                    discard = False
                    if float(value) > 0:
                        decimal_value = Decimal(value)
                        try:
                            raw_material_instance = raw_material.objects.get(name=key)
                        except raw_material.DoesNotExist:
                            flag_error = True
                            error_message = f'ماده اولیه "{key}" یافت نشد.'
                            raise Exception(error_message)

                        inventory, _ = Inventory.objects.get_or_create(
                            inventory_raw_material=raw_material_instance,
                            warehouse=ware_house
                        )

                        if key not in main_materials:
                            # Remove stock
                            status, message = inventory.remove_stock(amount=decimal_value, user=profile)
                            #print('Remove:', key, 'value:', value)
                        else:
                            # Add stock
                            receipt_number = '9000'  # You can make this dynamic if needed
                            status, message = inventory.add_stock(amount=decimal_value, user=profile, receipt_number=receipt_number)
                            #print('Add:', key, 'value:', value)

                        if not status:
                            flag_error = True
                            error_message = f'{message} - {key}'
                            raise Exception(error_message)

        except Exception as e:
            return render(request, 'users/error_page.html', {'text': str(e)})

        return redirect('success_page')
    


    materials = raw_material.objects.all()
    
    # Create a list of dictionaries containing main materials and their ingredients
    materials_with_ingredients = []
    
    for material in materials:
        ingredients = material.components.all()  # Get related ingredients
        if ingredients.exists():
        


            ingredients_list=[]

            for composition in ingredients:


                dic = {"name": composition.ingredient.name,
                        "ratio": composition.ratio ,
                          "quantity":get_total_quantity(composition.ingredient),
                          "id":composition.ingredient.id,
                          "unit":composition.ingredient.unit,
                          "has_discard" : composition.has_discard,
                          } 
                
                ingredients_list.append(dic)




            
            materials_with_ingredients.append({
                "main_material": material.name,
                "ingredients": ingredients_list,
                "id":material.id,
                "unit":material.unit,
                # "has_discard" : material.
            })

    ware_houses = Warehouse.objects.all()
        
    context = {"materials_with_ingredients": materials_with_ingredients,'warehouses':ware_houses}
    return render(request, 'users/store_product.html',context)






@login_required
def take_store(request):



    if request.method == 'POST':
        
        data = dict(request.POST.dict())
        data.pop('csrfmiddlewaretoken','Not found')
        
        ware_house = None
        if 'warehouse' in data.keys():
            ware_house = data['warehouse']
            data.pop('warehouse','Not found')
        elif ware_house is None:
            return
        

        user_id =request.user.id
        user = User.objects.get(id=user_id)
        profile = Profile.objects.get(user=user)# Get the latest subscription for testing


        selected_warehouse = Warehouse.objects.get(name = ware_house)

        values ={}






        raw_materials_with_quantity = get_material_quantity(show_all=False,selected_warehouses=selected_warehouse)

        mother_materials = get_mother_material_quantity(show_all=False,selected_warehouses=selected_warehouse,raw_materials_with_quantity=raw_materials_with_quantity)
        if raw_materials_with_quantity is None or mother_materials is None:
            #print('error in get_mother_material_quantity')
            return False
        # Serialize your mother_materials data
        materials_data = [
            {
                'id': mother_material.id,
                'name': mother_material.name,
                'describe': mother_material.describe,
                'total_quantity':  round(mother_material.total_quantity,2),
                'submaterials': [
                    {
                        'id' :  submaterial.id,
                        'name': submaterial.name,
                        'describe': submaterial.describe,
                        'total_quantity': round(submaterial.total_quantity,2),
                        'unit': submaterial.unit,
                    }
                    for submaterial in mother_material.mother_material.all()
                ],
            }
            for mother_material in mother_materials
        ]

        # #print(time.time()-t)

        return JsonResponse({'mother_materials': materials_data,'backend_endpoint':BACKEND_ENDPOINT})











        messages.success(request,'مقادیر مورد نظر با موفقیت اضافه گردید')
        # return redirect('/profile/my_orders')
        return redirect('success_page')  # Redirect to your desired page

    else:


            ware_houses = Warehouse.objects.all()

            buyers = Buyer.objects.all()


            # raw_materials_with_quantity = get_material_quantity(show_all=True)
            # mother_materials = get_mother_material_quantity(material_name='all',show_all=True, raw_materials_with_quantity =  raw_materials_with_quantity)

            return render(request, 'users/store_take.html', {'warehouses':ware_houses,'backend_endpoint':BACKEND_ENDPOINT,'buyers':buyers})
        






@login_required
def confrim_take_store(request):

    if request.method == 'POST':
        try:
            data = dict(request.POST.dict())
            data.pop('csrfmiddlewaretoken','Not found')
            #print(data)


            if 'warehouse' in data.keys():
                ware_house = data['warehouse']
                data.pop('warehouse','Not found')
                
            else:
                return
            

            if 'buyer' in data.keys():

                buyer = data['buyer']
                data.pop('buyer','Not found')
                buyer = Buyer.objects.filter(id=buyer).first()
            else:
                return
            
            user_id =request.user.id
            user = User.objects.get(id=user_id)
            profile = Profile.objects.get(user=user)# Get the latest subscription for testing



            ware_house = Warehouse.objects.get(id = ware_house)


            items = json.loads(data['items'])  # Now items is {'119': 2, '124': 12, '133': 2}

            # Iterate through the items and pop them from the model
            
            for item_id in items.keys():
                # try:
                    # Assuming 'id' is the primary key of the Material model
                id  = item_id.split('-')[1]
                raw_material_instance = raw_material.objects.get(id=int(id))
                #print(raw_material_instance)

                decimal_value = Decimal(items[item_id])

                inventory, created = Inventory.objects.get_or_create(inventory_raw_material=raw_material_instance,warehouse=ware_house)
                status,message = inventory.remove_stock(amount=decimal_value,user=profile,buyer=buyer)
                #print('status : ',status)
                # if status:
                messages.success(request,message)
                # return redirect('/profile/my_orders')
                return JsonResponse({'status': status, 'message': message})
                # else:
                #     message = status
                #     messages.success(request,message)
                #     # return redirect('/profile/my_orders')
                #     return JsonResponse({'status': 'success', 'message': message})
        except Exception as e:
            # Add error message
            messages.error(request, str(e))
            return JsonResponse({'status': 'error', 'message': str(e)})














@login_required
def show_store(request):

        if request.method == "POST":
             
            t = time.time()
            data = dict(request.POST.dict())
            selected_warehouses = request.POST.getlist('warehouses')
            show_all = request.POST.get('show_all') == 'true'
            show_available = request.POST.get('show_available') == 'true'

            first_key, selected_warehouses = list(data.items())[0]

            if selected_warehouses !='all' or selected_warehouses !='true':
                    if str(selected_warehouses).isdigit():
                        selected_warehouses = int(selected_warehouses)
                    else:
                        if str(selected_warehouses) !='all':
                            messages.error(request, "باید یک انبار انتخاب کنید")
                            return redirect(request.path)   # stop and go back
                    

            raw_materials_with_quantity = get_material_quantity(show_all=show_all,selected_warehouses=selected_warehouses)

            mother_materials = get_mother_material_quantity(show_all=show_all,selected_warehouses=selected_warehouses,raw_materials_with_quantity=raw_materials_with_quantity)
            if raw_materials_with_quantity is None or mother_materials is None:
                #print('error in get_mother_material_quantity')
                return False
            # Serialize your mother_materials data
            materials_data = [
                {
                    'id': mother_material.id,
                    'name': mother_material.name,
                    'describe': mother_material.describe,
                    'total_quantity': round(mother_material.total_quantity,2),
                    'submaterials': [
                        {
                            'id' :  submaterial.id,
                            'name': submaterial.name,
                            'describe': submaterial.describe,
                            'total_quantity': round(submaterial.total_quantity,2),
                            'unit': submaterial.unit,
                        }
                        for submaterial in mother_material.mother_material.all()
                    ],
                }
                for mother_material in mother_materials
            ]

            #print(time.time()-t)

            return JsonResponse({'mother_materials': materials_data,'backend_endpoint':BACKEND_ENDPOINT})

        else:

            t = time.time()

            ware_houses = Warehouse.objects.all()

            raw_materials_with_quantity = get_material_quantity(show_all=True)

            mother_materials = get_mother_material_quantity(material_name='all',show_all=True, raw_materials_with_quantity =  raw_materials_with_quantity)

            #print(time.time()-t)
    
            return render(request, 'users/store.html', {'mother_materials': mother_materials,'warehouses':ware_houses,'backend_endpoint':BACKEND_ENDPOINT})
        

def get_material_quantity(material_name = 'all',show_all=False,selected_warehouses = 'all'):

    raw_materials_with_quantity = None            
    if material_name == 'all' and selected_warehouses=='all':

        raw_materials_with_quantity = raw_material.objects.annotate(
                total_quantity=Coalesce(Sum('inventory__quantity'), 0, output_field=DecimalField())
            ).order_by('describe')
        

    elif material_name == 'all' and selected_warehouses != 'all':
                        
        raw_materials_with_quantity = raw_material.objects.annotate(
            total_quantity=Coalesce(
                Sum('inventory__quantity', filter=Q(inventory__warehouse_id=selected_warehouses)),  # Filter by warehouse ID
                0,
                output_field=DecimalField()
            )
                ).order_by('describe')


    if  not(show_all) and raw_materials_with_quantity is not None:

        raw_materials_with_quantity = raw_materials_with_quantity.filter(total_quantity__gt=0)

    return raw_materials_with_quantity



def get_mother_material_quantity(material_name = 'all',show_all=False,selected_warehouses='all',raw_materials_with_quantity=None):

    mother_materials_with_quantity = None

    if material_name == 'all' and selected_warehouses=='all':
        
        if raw_material is None:
            raw_materials_with_quantity = raw_material.objects.annotate(
                total_quantity=Coalesce(Sum('inventory__quantity'), 0, output_field=DecimalField())
            ).order_by('describe')

        # Prefetch raw_materials into mother_materials with the annotated quantity
        mother_materials_with_quantity = MotherMaterial.objects.prefetch_related(
            Prefetch(
                'mother_material',  # Assuming this is the correct related_name to access raw_materials
                queryset=raw_materials_with_quantity,  # Prefetched raw materials with total quantities
            )
        ).annotate(
            total_quantity=Coalesce(Sum('mother_material__inventory__quantity'), 0, output_field=DecimalField())  # Set output_field for the total quantity
        ).order_by('describe')

    elif  material_name == 'all' and selected_warehouses != 'all':
    

        # Prefetch raw materials into mother materials with the annotated quantity for the specific warehouse
        mother_materials_with_quantity = MotherMaterial.objects.prefetch_related(
            Prefetch(
                'mother_material',  # Related name to access raw materials
                queryset=raw_materials_with_quantity,  # Prefetched raw materials with total quantities for warehouse 1
            )
        ).annotate(
            total_quantity=Coalesce(
                Sum('mother_material__inventory__quantity', filter=Q(mother_material__inventory__warehouse_id=selected_warehouses)),  # Filter by warehouse ID
                0,
                output_field=DecimalField()
            )
        ).order_by('describe')
                

    if  not(show_all) and mother_materials_with_quantity is not None:

        mother_materials_with_quantity = mother_materials_with_quantity.filter(total_quantity__gt=0)



    return mother_materials_with_quantity





from django.core.paginator import Paginator
from django.shortcuts import render
from datetime import timedelta

def log_view_store(request):
    # Base queryset (use select_related to cut template-time queries)
    logs = (
        InventoryLog.objects
        .select_related(
            'inventory',
            'inventory__warehouse',
            'inventory__inventory_raw_material',
            'user',                 # adjust to your relation (Profile / FK name)
            # 'user__user',         # uncomment if your Profile links to auth.User as "user"
        )
        .order_by('-date')
    )

    # ---- Datasets for filters
    users = User.objects.all()
    raw_materials = RawMaterial.objects.all()
    warehouses = Warehouse.objects.all()

    # ---- Filters
    # Receipt number (only if it's a clean int)
    receipt_number = (request.GET.get('receipt_number') or '').strip()
    if receipt_number:
        try:
            logs = logs.filter(receipt_Number=int(receipt_number))
        except (TypeError, ValueError):
            pass

    # User (single select with "select_all" support)
    user = request.GET.get('user')
    if user and user != 'select_all':
        try:
            user_obj = User.objects.filter(id=int(user)).first()
            if user_obj:
                # Adjust this line to your actual relation from log to user/profile
                logs = logs.filter(user=user_obj.profile)
        except (TypeError, ValueError, AttributeError):
            # Fallback: ignore if mapping differs
            pass

    # Change type
    change_type = (request.GET.get('change_type') or '').strip()
    if change_type:
        logs = logs.filter(change_type=change_type)

    # Warehouse (single select with "select_all" support)
    warehouse = request.GET.get('warehouse')
    if warehouse and warehouse != 'select_all':
        logs = logs.filter(inventory__warehouse__id=warehouse)

    # Raw materials (MULTI-select via checkboxes)
    # If you also show a "select_all" checkbox in the dropdown, we ignore it here.
    raw_material_ids = request.GET.getlist('raw_materials')
    raw_material_ids = [x for x in raw_material_ids if x and x != 'select_all']
    if raw_material_ids:
        logs = logs.filter(inventory__inventory_raw_material__id__in=raw_material_ids).distinct()

    # Dates (Jalali strings -> Gregorian datetimes)
    start_date_str = (request.GET.get('date_from') or '').strip()
    end_date_str   = (request.GET.get('date_to')   or '').strip()

    if start_date_str:
        if start_date_str !='None':

            start_dt = convert_jalali_to_gregorian(start_date_str)  # implement this util
            if start_dt:
                logs = logs.filter(date__gte=start_dt)

    if end_date_str:
        if end_date_str !='None':

            end_dt_str = convert_jalali_to_gregorian(end_date_str)  # e.g. '2025-08-15'
            try:
                end_dt = datetime.strptime(end_dt_str, '%Y-%m-%d')  # adjust format if needed
                end_dt_inclusive = end_dt + timedelta(hours=23, minutes=59, seconds=59, microseconds=999999)
                logs = logs.filter(date__lte=end_dt_inclusive)
            except ValueError:
                pass
    # ---- Pagination
    per_page_param = (request.GET.get('per_page') or '').strip()
    default_page_size = 20

    if per_page_param == 'all':
        page_size = max(1, logs.count())
        page_number = 1  # force first page
    else:
        try:
            page_size = int(per_page_param) if per_page_param else default_page_size
            if page_size <= 0: page_size = default_page_size
        except ValueError:
            page_size = default_page_size
        page_number = request.GET.get('page')

    paginator = Paginator(logs, page_size)
    logs_page = paginator.get_page(page_number)

    # ---- Defaults back to template
    default_user = request.GET.get('user', None)
    default_change_type = request.GET.get('change_type', None)
    default_date_from = request.GET.get('date_from', None)
    default_date_to = request.GET.get('date_to', None)
    default_raw_materials = request.GET.getlist('raw_materials', [])
    default_warehouse = request.GET.get('warehouse', None)

    # Parse ids if possible (for preselect)
    try:
        default_user = int(default_user)
    except (TypeError, ValueError):
        pass
    try:
        default_warehouse = int(default_warehouse)
    except (TypeError, ValueError):
        pass

    # Build "show all" querystring
    qs = request.GET.copy()
    qs.pop('page', None)          # remove pagination page
    qs['per_page'] = 'all'        # force show all
    show_all_query = qs.urlencode()




    context = {
        'logs': logs_page,
        'users': users,
        'warehouses': warehouses,
        'raw_materials': raw_materials,

        'default_user': default_user,
        'default_change_type': default_change_type,
        'default_date_from': default_date_from,
        'default_date_to': default_date_to,
        'default_raw_materials': default_raw_materials,
        'default_warehouse': default_warehouse,

        'show_all_query': show_all_query,   # ✅ here

        
    }
    return render(request, 'users/store_log.html', context)



def convert_georgian2jalali(jdate):

    # Convert the string to JalaliDate object
    # First, convert Persian numbers to English numbers
    persian_to_english = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')
    jalali_date_str_english = jdate.translate(persian_to_english)

    # Convert to JalaliDate object
# Split the date string to extract year, month, and day
    year, month, day = map(int, jalali_date_str_english.split('/'))

    # Create a JalaliDate object
    jalali_date = JalaliDate(year, month, day)

    # Convert to Gregorian date
    georgian_date = jalali_date.to_gregorian()


    return georgian_date









def register_entry(request, id):
 
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            latitude = data.get('latitude')
            longitude = data.get('longitude')

            latitude = float(latitude)
            longitude = float(longitude)

            # Here you can decide if it's an entry or exit based on your logic
            # For example, you might want to check if the user is in an allowed location
            user = User.objects.get(id=id)  # Fetch user by ID
            allowed_locations = AllowedLocation.objects.get(user=user)

            # Check if the latitude and longitude are within the allowed locations
            for location in allowed_locations.locations.all():
                distance = calculate_distance(latitude, longitude, float(Decimal(location.latitude)), float(Decimal(location.longitude)))
                if distance <= location.radius_meters:
                    # Save the location to the database as an entry


                    status = is_user_in(user)

                    if status is not None:
                        status = not status
                    
                    else:
                        status = True

                    log_entry = EntryExitLog.objects.create(
                        user=user,
                        is_entry=status,  # Set to True for entry
                        location=location
                    )

                    translate_status = 'خروج'

                    if status:
                        translate_status = 'ورود'
                    
                    return JsonResponse({'success': True, 'message': '{} شما در {} با موفقیت ثبت گردید'.format(translate_status,location.name)})
            
            return JsonResponse({'success': False, 'message': 'شما در موقعیت صحیح قرار ندارید'})
        
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'مشکل در ثبت'})
        

    else:
            
        user = get_object_or_404(User, id=request.user.id)  # Get the user by id
        latest_log = get_latest_exit(user)
        return render(request, 'users/register_entry.html',{'last_status': latest_log })




def get_allowed_locations(request):
    user = request.user  # Get the logged-in user
    try:

        allowed_locations = AllowedLocation.objects.prefetch_related('locations').get(user=user)
        locations = allowed_locations.locations.all()

        # Create a list of locations with lat, long, and radius to send to frontend
        locations_data = [
            {
                'name': location.name,
                'latitude': float(location.latitude),
                'longitude': float(location.longitude),
                'radius': location.radius_meters
            } 
            for location in locations
        ]

        return JsonResponse({'locations': locations_data})
    except AllowedLocation.DoesNotExist:
        return JsonResponse({'locations': []})



def histoty_entry(request,id):

    if request.method == 'POST':
        return

    else:

        obj = UserWorkTimeManager()

        data , total_work = obj.user_work_time(username=request.user.id)


        # data = {
        #     user: dict(sorted(
        #         logs.items(),
        #         key=lambda item: JalaliDatetime.strptime(item[0], '%Y/%m/%d'),
        #         reverse=True  # Sort in descending order
        #     ))
        #     for user, logs in data.items()
        # }


        return render(request,'users/register_history.html',{'user_time_data':data,'total_work':total_work})


#------------------------------------------------------------------ پایان دوران سربازی در 05

########################## شروع مجدد برنامه در تاریخ 15 اذر



def update_prices(request,city,res_name):




    ret = SnappFoodList.objects.filter(
            name=res_name, city__name=city
        ).first()  # Get the first match
    

    if ret is None:
        #print('Restaurant link is not in DB')
        return

    res_link = ret.link



    gp = get_price(res_name=res_name,res_link=res_link,city= city)


    gp.get_name_price(update=True)

    #print(id)




def success_page(request):
    return render(request, 'users/success_page.html')  # Render your success page template

def error_page(request):
    return render(request, 'users/error_page.html')  # Render your success page template


def submit_data(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')

        # Here you can process the data (e.g., save to database, validate, etc.)
        #print(request.POST)

        # Send a JSON response back
        response_data = {
            'name': name,
            'email': email
        }

        return JsonResponse(response_data)

    return JsonResponse({'error': 'Invalid request method'}, status=400)


def show_test(request):

    return render(request, 'users/test.html')
        





def register_exit(request, log_id):
    log = EntryExitLog.objects.get(id=log_id)
    log.exit_time = timezone.now()
    log.save()
    return redirect('profile')  # Redirect to the profile page




def show_menu_options(request):

    menu_names = {'پیتزا ها' :'/menu/pizza' , 'سایر محصولات' : '/menu/others'}

    return render(request,'users/menu_options.html',{'menu_names':menu_names})




def no_access(request):
    return render(request, 'users/no_access.html')







from .models import Buyer
from .forms import BuyerForm
@login_required
def add_buyer(request):
    if request.method == 'POST':
        form = BuyerForm(request.POST)
        buyer_attributes = BuyerAttribute.objects.all()

        if form.is_valid():

            buyer = form.save(commit=False)
            buyer.created_by = request.user  # 👈 ست کردن کاربر لاگین شده
            buyer.save()

            for attr in buyer_attributes:
                field_name = f"attr_{attr.id}"

                if attr.field_type == 'image':
                    uploaded_image = request.FILES.get(field_name)
                    if uploaded_image:
                        BuyerAttributeValue.objects.update_or_create(
                            buyer=buyer,
                            attribute=attr,
                            defaults={'image': uploaded_image, 'value': None}
                        )
                else:
                    value = request.POST.get(field_name, '').strip()
                    BuyerAttributeValue.objects.update_or_create(
                        buyer=buyer,
                        attribute=attr,
                        defaults={'value': value, 'image': None}
                    )
            
        
            return redirect('buyer_list')  # change to your desired success URL
            
    
    
    
    
    

    
    
    
    else:
        form = BuyerForm()
        buyer_attributes = BuyerAttribute.objects.all()



    return render(request, 'Buyer/buyer_form.html', {'form': form, 'title': 'افزودن خریدار','buyer_attributes':buyer_attributes})





def edit_buyer(request, pk):
    buyer = get_object_or_404(Buyer, pk=pk)
    if request.method == 'POST':
        form = BuyerForm(request.POST, instance=buyer)
        buyer_attributes = BuyerAttribute.objects.all()

        if form.is_valid():
            buyer = form.save()
            for attr in buyer_attributes:
                field_name = f"attr_{attr.id}"

                if attr.field_type == 'image':
                    uploaded_image = request.FILES.get(field_name)
                    if uploaded_image:
                        BuyerAttributeValue.objects.update_or_create(
                            buyer=buyer,
                            attribute=attr,
                            defaults={'image': uploaded_image, 'value': None}
                        )
                else:
                    value = request.POST.get(field_name, '').strip()
                    BuyerAttributeValue.objects.update_or_create(
                        buyer=buyer,
                        attribute=attr,
                        defaults={'value': value, 'image': None}
                    )
            return redirect('buyer_list')
            
        else:
            return redirect('error_page')



    else:


        
        form = BuyerForm(instance=buyer)
        buyer_attrs = BuyerAttribute.objects.all()

        categories = BuyerCategory.objects.all()

    return render(request, 'Buyer/buyer_edit.html', {'form': form, 'title': 'ویرایش خریدار','buyer_attributes':buyer_attrs,'categories':categories})


from django.db.models import Q

def buyer_list(request):
    query = request.GET.get('q')

    if request.user.profile.job_position.name =='CEO':
        buyers = Buyer.objects.all().order_by('-id').filter(is_active=True)

    else:
        buyers = Buyer.objects.all().order_by('-id').filter(is_active=True,created_by = request.user)

    if query:
        buyers = buyers.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(phone_number__icontains=query) |
            Q(nationality__name__icontains=query)|
            Q(categories__name__icontains=query)  # این خط اضافه شد
        ).distinct()

        buyers = buyers.filter(is_active=True)


    buyers = clean_buyer_names(buyers=buyers)


    try:
        len_buyer = len(buyers)
    except:
        len_buyer = 0
    return render(request, 'Buyer/buyer_list.html', {
        'counts' : len_buyer,
        'buyers': buyers,
        'query': query,
        
    })

@login_required
def delete_buyer(request, buyer_id):
    buyer = get_object_or_404(Buyer, id=buyer_id)
    
    if request.method == 'POST':
        buyer.is_active = False
        buyer.save()
        messages.success(request, 'مشتری با موفقیت حذف شد، در انتظار تایید مدیر میباشد.')
        return redirect('buyer_list')  # replace with your actual buyer list url name

    return render(request, 'Buyer/confirm_delete.html', {'buyer': buyer})

@login_required
def review_delete_buyers_requests(request):
    requests = Buyer.objects.filter(is_active=False)
    return render(request, 'Buyer/buyer_delete_request.html', {'requests': requests})

@login_required
def confirm_delete_buyer_request(request,buyer_id):

    delete_request = get_object_or_404(Buyer, id=buyer_id, is_active=False)
    delete_request.delete()
    return redirect('review_delete_buyers_requests')

@login_required
def reject_delete_buyer_request(request,buyer_id):

    delete_request = get_object_or_404(Buyer, id=buyer_id, is_active=False)
    delete_request.is_active=True
    delete_request.save()
    return redirect('review_delete_buyers_requests')


from django.db.models import Count, Sum
from django.shortcuts import render
from .models import Buyer, InventoryLog
from django.db.models import Count, Sum
from collections import defaultdict
from StoneFlow.models import PreInvoice, PreInvoiceItem, Buyer  # Adjust import paths


def calc_buyer_dashboard():
        # Only consider sold pre-invoices
    sold_invoices = PreInvoice.objects.filter(is_sell=True)

    # مشتریان برتر (Top Buyers)
    top_buyers = sold_invoices.values('customer__id', 'customer__first_name','customer__last_name').annotate(
        total_purchases=Count('id')
    ).order_by('-total_purchases')[:10]

    # محصولات محبوب هر مشتری (Most Bought Product by Each Buyer)
    buyer_products = defaultdict(list)
    top_buyer_ids = [b['customer__id'] for b in top_buyers]
    
    # Get all items of sold invoices for top buyers
    items = PreInvoiceItem.objects.filter(pre_invoice__is_sell=True, pre_invoice__customer__id__in=top_buyer_ids)

    for item in items:
        buyer_products[item.pre_invoice.customer.id].append(item)

    top_products = []
    for buyer_id, item_list in buyer_products.items():
        product_totals = defaultdict(float)
        buyer_name = item_list[0].pre_invoice.customer.first_name if item_list else ""
        for item in item_list:
            material_name = item.coop.material.name
            product_totals[material_name] += float(item.unit_price or 0)

        if product_totals:
            top_product = max(product_totals.items(), key=lambda x: x[1])
            top_products.append({
                'buyer_id': buyer_id,
                'buyer_name': buyer_name,
                'top_product_name': top_product[0],
                'top_product_amount': top_product[1],
            })

    # مشتریان بدون خرید (Buyers Without Purchase)
    all_buyers_with_purchase = sold_invoices.values_list('customer_id', flat=True)
    inactive_buyers = Buyer.objects.exclude(id__in=all_buyers_with_purchase)
    inactive_buyers = inactive_buyers.filter(is_active=True)

    # مشتریان وفادار (Loyal Buyers - 5+ purchases)
    loyal_buyers = sold_invoices.values('customer__id', 'customer__first_name','customer__last_name').annotate(
        total_purchases=Count('id')
    ).filter(total_purchases__gte=5).order_by('-total_purchases')

    # For Chart
    chart_labels = [b['customer__first_name'] for b in top_buyers]
    chart_data = [b['total_purchases'] for b in top_buyers]

    context = {
        'top_buyers': top_buyers,
        'top_products': top_products,
        'inactive_buyers': inactive_buyers,
        'loyal_buyers': loyal_buyers,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
    }
    return context


@login_required
def buyer_dashboard(request):
    context = calc_buyer_dashboard()
    return render(request, 'Buyer/buyer_dashboard.html', context)

@login_required
def buyer_dashboard_partial(request):
    context = calc_buyer_dashboard()
    return render(request, 'Buyer/buyer_dashboard_partial.html', context)




@login_required
def buyer_user_dashboard(request):
    try:
        buyer = request.user.buyer  # Assumes OneToOne relation between User and Buyer
        logs = InventoryLog.objects.filter(buyer=buyer).order_by('-date')
    except Buyer.DoesNotExist:
        logs = []

    return render(request, 'Buyer/user_dashboard.html', {'logs': logs})





def buyer_login_view(request):
    if request.method == 'POST':
        form = BuyerLoginForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            phone = form.cleaned_data['phone']
            try:
                buyer = Buyer.objects.filter(first_name=name, phone_number=phone).first()
                request.session['buyer_id'] = buyer.id  # Save login session
                return redirect('buyer_dashboard')
            except Buyer.DoesNotExist:
                form.add_error(None, 'اطلاعات وارد شده صحیح نیست.')
    else:
        form = BuyerLoginForm()

    return render(request, 'Buyer/buyer_login.html', {'form': form})

def buyer_dashboard_view(request):
    buyer_id = request.session.get('buyer_id')
    if not buyer_id:
        return redirect('buyer_login')

    buyer = Buyer.objects.get(id=buyer_id)
    logs = InventoryLog.objects.filter(buyer=buyer).order_by('-date')

    return render(request, 'Buyer/user_dashboard.html', {
        'buyer': buyer,
        'logs': logs
    })

def buyer_logout_view(request):
    request.session.flush()
    return redirect('buyer_login')


def confirm_purchase_view(request, log_id):
    buyer_id = request.session.get('buyer_id')
    if not buyer_id:
        return redirect('buyer_login')

    log = get_object_or_404(InventoryLog, id=log_id, buyer_id=buyer_id)

    log.confirmed_by_buyer = True
    log.save()

    messages.success(request, 'خرید با موفقیت تایید شد.')
    return redirect('buyer_dashboard')








def buyer_attr_manage(request):
    if request.method == 'POST':
        if 'attr_id' in request.POST:
            # Editing an existing attribute
            attr = get_object_or_404(BuyerAttribute, id=request.POST['attr_id'])
            form = BuyerAttributeForm(request.POST, instance=attr)
            if form.is_valid():
                form.save()
                messages.success(request, 'ویژگی با موفقیت به‌روزرسانی شد.')
                return redirect('buyer_attr_manage')
        else:
            # Adding a new attribute
            form = BuyerAttributeForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'ویژگی جدید با موفقیت اضافه شد.')
                return redirect('buyer_attr_manage')
    else:
        form = BuyerAttributeForm()

    attributes = BuyerAttribute.objects.all()
    return render(request, 'Buyer/buyer_attr_manager.html', {'form': form, 'attributes': attributes})


def delete_buyer_attribute(request, attr_id):
    attr = get_object_or_404(BuyerAttribute, id=attr_id)
    attr.delete()
    messages.success(request, 'ویژگی حذف شد.')
    return redirect('buyer_attr_manage')




def buyer_detail(request, buyer_id):
    buyer = get_object_or_404(Buyer, id=buyer_id)
    # activities = BuyerActivity.get_activity_type_labels()
    activities = BuyerActivity.get_activity_type_label_icon_list()


    buyer = clean_buyer_names(buyer )

    
    return render(request, 'Buyer/buyer_history.html', {
        'buyer': buyer,
        'activities': activities,
        
    })


def activity_presian2english(persian_activity):
    try:
        PERSIAN_TO_ENGLISH = dict((fa, en) for en, fa in BuyerActivity.ACTIVITY_TYPE_CHOICES)
        return  PERSIAN_TO_ENGLISH.get(persian_activity)
    except:
        return ''

def buyer_activity_detail(request, buyer_id, activity_type):
    activity_type_english = activity_presian2english(activity_type)
    
    activity_logs = BuyerActivity.objects.filter(buyer_id=buyer_id, activity_type=activity_type_english)
    factor_items = None
    total_price =0
    if activity_type=='فاکتور ها و خرید':
        # گرفتن فاکتورهای مربوط به مشتری خاص
        factors = PreInvoice.objects.filter(customer=buyer_id,is_sell=True)

        # گرفتن آیتم‌های مربوط به همه فاکتورها
        factor_items = PreInvoiceItem.objects.filter(pre_invoice__in=factors)
        
        for item in factor_items:
            total_price+=float(item.total_price())

        # جمع کل قیمت‌ها
        # total_price = sum(item.total_price or 0 for item in factor_items)

    return render(request, 'Buyer/partials/activity_logs.html', {
        'logs': activity_logs,
        'buyer_id': buyer_id,
        'activity_choices': BuyerActivity.get_activity_type_labels(),
        'selected_activity_type': activity_type,  # Add this line
        'factors':factor_items,
        'total_price':total_price,
    })

def add_buyer_activity(request, buyer_id):
    if request.method == 'POST':
        activity_type = request.POST.get('activity_type')
        description = request.POST.get('description')

        BuyerActivity.objects.create(
        
            buyer_id=buyer_id,
            activity_type=activity_type,
            description=description,
            created_by=request.user  # if your model supports it
        )
        return redirect('buyer_detail', buyer_id=buyer_id)



@login_required
def show_factor(request, pk):

    invoice = get_object_or_404(PreInvoice, pk=pk)
    return render(request, 'preinvoice/detail.html', {'preinvoice': invoice})


# views.py
# @login_required
# def daily_report_view(request):
#     if request.method == 'POST':
#         form = DailyReportForm(request.POST)
#         if form.is_valid():
#             report = form.save(commit=False)
#             report.user = request.user
#             report.save()
#             return redirect('daily_report')
#     else:
#         form = DailyReportForm()

#     reports = DailyReports.objects.filter(user=request.user).order_by('-date', '-created_at')
#     types = ReportTitles.objects.all()
#     return render(request, 'users/daily_report.html', {'form': form, 'reports': reports,'types':types})
import jdatetime

def convert_jalali_to_gregorian(jalali_date_str):
    # فرض: فرمت ورودی '۱۴۰۴/۰۵/۱۴' و به صورت فارسی
    jalali_date_str = jalali_date_str.translate(str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789'))
    year, month, day = map(int, jalali_date_str.split('/'))
    gregorian_date = jdatetime.date(year, month, day).togregorian()
    return gregorian_date.strftime('%Y-%m-%d')



@login_required
def daily_report_view(request):
    reports = BuyerActivity.objects.filter(created_by=request.user).order_by('-timestamp')
    last_report = reports.first()

    # داده‌هایی که می‌خواهی به قالب بفرستی
    buyers = Buyer.objects.filter(is_active=True , created_by = request.user  )
    countries = buyers.values_list('nationality__name', flat=True).distinct()

    activities = BuyerActivity.get_activity_type_label_icon_list()  # یا هر مدل مرتبط

    # Get filters
    search_query = request.GET.get('search')
    selected_country = request.GET.get('country')

    # Apply filters
    if search_query:
        buyers = buyers.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )

    if selected_country:
        if selected_country =='None':
            selected_country = None
        buyers = buyers.filter(nationality__name=selected_country)

    buyers = clean_buyer_names(buyers=buyers)



    if request.method == 'POST':
        buyer_id = request.POST.get('buyer')
        activity_type = request.POST.get('activity_type')
        title = request.POST.get('activity_title')
        description = request.POST.get('description')
        next_followup = request.POST.get('next_followup')

        if buyer_id and activity_type:
            # activity_type = get_object_or_404(ActivityType, id=activity_type_id)
            buyer = get_object_or_404(Buyer, id=buyer_id)

            if next_followup != '':

                next_followup = convert_jalali_to_gregorian(next_followup)
            
                BuyerActivity.objects.create(
                    title = title,
                    buyer=buyer,
                    activity_type=activity_type,
                    description=description,
                    created_by=request.user,  # if your model supports it
                    next_followup = next_followup
                )

            else:
                BuyerActivity.objects.create(
                    title = title,
                    buyer=buyer,
                    activity_type=activity_type,
                    description=description,
                    created_by=request.user,  # if your model supports it
                )


            return redirect('buyer_detail', buyer_id=buyer.id)

    return render(request, 'users/daily_report.html', {
        'reports': reports,
        'last_report_id': last_report.id if last_report else None,
        'buyers': buyers,
        'activities': activities,
        'countries': countries,
        'query_name': search_query,
        'query_country': selected_country,


    })


@login_required
def edit_buyer_activity(request, pk):
    activity = get_object_or_404(BuyerActivity, pk=pk, user=request.user)
    if request.method == 'POST':
        form = DailyReportForm(request.POST, instance=activity)
        if form.is_valid():
            form.save()
            return redirect('daily_report')
    else:
        form = DailyReportForm(instance=activity)

    return render(request, 'Buyer/buyer_edit_activity.html', {
        'form': form,
        'activity': activity,
    })

@login_required
def delete_buyer_activity(request, pk):
    activity = get_object_or_404(BuyerActivity, pk=pk, user=request.user)
    if request.method == 'POST':
        activity.delete()
        return redirect('daily_report')

    return render(request, 'Buyer/buyer_delete_activity.html', {
        'activity': activity,
    })



@csrf_exempt
@login_required
def subscribe(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'invalid request'}, status=400)

    data = json.loads(request.body)
    profile = request.user.profile
    keys = data.get('keys', {})

    profile.push_endpoint = data.get('endpoint')
    profile.push_p256dh = keys.get('p256dh')
    profile.push_auth = keys.get('auth')
    profile.save()

    return JsonResponse({'status': 'subscription saved'})

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from pywebpush import webpush, WebPushException
import json

@csrf_exempt
@login_required
def send_test_notification(request):
    profile = request.user.profile
    if not profile.push_endpoint:
        return JsonResponse({'error': 'No push subscription found'}, status=400)

    try:
        webpush(
            subscription_info={
                "endpoint": profile.push_endpoint,
                "keys": {
                    "p256dh": profile.push_p256dh,
                    "auth": profile.push_auth
                }
            },
            data=json.dumps({
                "title": "اعلان تستی",
                "body": "این یک اعلان تستی است 🚀"
            }),
            vapid_private_key=settings.VAPID_PRIVATE_KEY,
            vapid_claims={"sub": settings.VAPID_ADMIN_EMAIL}
        )
        return JsonResponse({'status': 'notification sent'})

    except WebPushException as ex:
        msg = str(ex)
        # ۱) اگر خود response هست و status_code داره
        if getattr(ex, "response", None) is not None:
            status = getattr(ex.response, "status_code", None)
            if status in [404, 410]:
                profile.push_endpoint = None
                profile.push_p256dh = None
                profile.push_auth = None
                profile.save()
                return JsonResponse(
                    {'error': 'Subscription removed due to invalid endpoint'},
                    status=410
                )

        # ۲) fallback: اگر داخل متن خطا 410 یا unsubscribed/expired بود
        if "410" in msg or "unsubscribed or expired" in msg:
            profile.push_endpoint = None
            profile.push_p256dh = None
            profile.push_auth = None
            profile.save()
            return JsonResponse(
                {'error': 'Subscription removed due to invalid endpoint'},
                status=410
            )

        # هر خطای دیگه → 500
        return JsonResponse({'error': msg}, status=500)






def user_list_view(request):
    users = User.objects.all()
    return render(request, 'users/user_list.html', {'users': users})


def create_user_view(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = ProfileForm(request.POST, request.FILES)

        try:

            if user_form.is_valid() and profile_form.is_valid():
                username = request.POST['username']
                password = request.POST['password']


                # ایجاد کاربر
                user = User.objects.create_user(username=username, password=password)

                # دریافت یا ساخت پروفایل مرتبط با کاربر
                profile, created = Profile.objects.get_or_create(user=user)

                # ساخت فرم با داده‌های POST و اتصال به پروفایل موجود
                profile_form = ProfileForm(request.POST, request.FILES, instance=profile)


                # بررسی صحت فرم
                if profile_form.is_valid():
                    profile = profile_form.save(commit=False)
                    profile.user = user  # این خط اگر از get_or_create استفاده شده، لازم نیست اما برای اطمینان بد نیست
                    profile.save()

                    if created:
                        messages.success(request, "پروفایل جدید با موفقیت ایجاد شد.")
                    else:
                        messages.success(request, "پروفایل با موفقیت به‌روزرسانی شد.")

                    return redirect('user_list')
                
            else:
                messages.error(request, 'لطفا خطاهای فرم را اصلاح کنید.')
        except:
            return redirect('error_page')
            
    else:
        user_form = UserForm()
        profile_form = ProfileForm()

    return render(request, 'users/create_user.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })

def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = getattr(user, 'profile', None)

    if request.method == 'POST':
        # user_form = UserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)

        if  profile_form.is_valid():


            profile_form.save()

            messages.success(request, "ویرایش کاربر با موفقیت انجام شد.")
            return redirect('user_list')
    else:

        profile_form = ProfileForm(instance=profile)

    return render(request, 'users/user_form.html', {

        'profile_form': profile_form,
        'title': 'ویرایش کاربر',
    })



def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, "کاربر حذف شد.")
    return redirect('user_list')




@login_required
def job_list_view(request):
    jobs_qs = jobs.objects.all().order_by('level')
    return render(request, 'jobs/job_list.html', {'jobs': jobs_qs})

@login_required
def job_create_view(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'شغل با موفقیت ایجاد شد.')
            return redirect('job_list')
        
    else:
        form = JobForm()
    return render(request, 'jobs/job_form.html', {'form': form, 'title': 'ایجاد شغل جدید'})

@login_required
def job_edit_view(request, pk):
    job = get_object_or_404(jobs, pk=pk)
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'شغل با موفقیت ویرایش شد.')
            return redirect('job_list')
    else:
        form = JobForm(instance=job)
    return render(request, 'jobs/job_form.html', {'form': form, 'title': 'ویرایش شغل'})

@login_required
def job_delete_view(request, pk):
    job = get_object_or_404(jobs, pk=pk)
    if request.method == 'POST':
        job.delete()
        messages.success(request, 'شغل با موفقیت حذف شد.')
        return redirect('job_list')
    return render(request, 'jobs/job_confirm_delete.html', {'job': job})



def manage_role_access(request):
    roles = jobs.objects.all()
    menu_items = MenuItem.objects.all()

    if request.method == "POST":
        for role in roles:
            selected_items = []
            for item in menu_items:
                field_name = f"access_{role.id}_{item.id}"
                if request.POST.get(field_name):
                    selected_items.append(item)
            role.items.set(selected_items)  # 👈 ذخیره دسترسی‌های جدید

    # ساختن دیکشنری {role_id: [item_id, ...]} برای تیک زدن چک‌باکس‌ها
    role_access = {
        role.id: list(role.items.values_list('id', flat=True))
        for role in roles
    }

    return render(request, 'roles/manage_access.html', {
        'roles': roles,
        'menu_items': menu_items,
        'role_access': role_access,
    })




def category_list(request):
    categories = BuyerCategory.objects.all()
    return render(request, 'Buyer/BuyerCategories/list.html', {'categories': categories})

def category_create(request):
    form = BuyerCategoryForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('category_list')
    return render(request, 'Buyer/BuyerCategories/form.html', {'form': form, 'title': 'افزودن دسته‌بندی'})

def category_update(request, pk):
    category = get_object_or_404(BuyerCategory, pk=pk)
    form = BuyerCategoryForm(request.POST or None, instance=category)
    if form.is_valid():
        form.save()
        return redirect('category_list')
    return render(request, 'Buyer/BuyerCategories/form.html', {'form': form, 'title': 'ویرایش دسته‌بندی'})

def category_delete(request, pk):
    category = get_object_or_404(BuyerCategory, pk=pk)
    if request.method == 'POST':
        category.delete()
        return redirect('category_list')
    return render(request, 'Buyer/BuyerCategories/delete.html', {'category': category})




from django.views.generic import ListView, UpdateView, DeleteView
from django.urls import reverse_lazy

# --- MOTHER MATERIAL ---


def mother_material_list(request):
    materials = MotherMaterial.objects.all()
    return render(request, 'materials/mother_material_list.html', {'materials': materials})


def raw_material_list(request):
    materials = raw_material.objects.all()
    return render(request, 'materials/raw_material_list.html', {'materials': materials})


def mother_material_edit(request, pk):
    item = get_object_or_404(MotherMaterial, pk=pk)
    if request.method == 'POST':
        form = MotherMaterialForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect('mother_material_list')
    else:
        form = MotherMaterialForm(instance=item)
    return render(request, 'materials/mother_material_form.html', {'form': form})


def confirm_delete_view(request, pk):
    obj = get_object_or_404(MotherMaterial, pk=pk)
    if request.method == 'POST':
        obj.delete()
        return redirect('mother_material_list')
    return render(request, 'materials/mother_material_confirm_delete.html', {'materials': obj})


def mother_material_add(request):
    if request.method == "POST":
        form = MotherMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('mother_material_list')
    else:
        form = MotherMaterialForm()
    return render(request, 'materials/mother_material_form.html', {'form': form, 'title': 'افزودن ماده اولیه مادر'})





# --- Raw Material ---

def raw_material_list(request):
    materials = raw_material.objects.all()
    return render(request, 'materials/raw_material_list.html', {'materials': materials})

def raw_material_add(request):
    if request.method == 'POST':
        form = RawMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('raw_material_list')
    else:
        form = RawMaterialForm()
    return render(request, 'materials/raw_material_form.html', {'form': form, 'title': 'افزودن ماده اولیه'})

def raw_material_edit(request, pk):
    item = get_object_or_404(raw_material, pk=pk)
    if request.method == 'POST':
        form = RawMaterialForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect('raw_material_list')
    else:
        form = RawMaterialForm(instance=item)
    return render(request, 'materials/raw_material_form.html', {'form': form, 'title': 'ویرایش ماده اولیه'})

def raw_material_delete(request, pk):
    item = get_object_or_404(raw_material, pk=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('raw_material_list')
    return render(request, 'materials/mother_material_confirm_delete.html', {'object': item, 'title': 'حذف ماده اولیه'})





import random, time
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from django.contrib.auth import get_user_model, login
from django.utils import timezone

User = get_user_model()

def send_sms(phone, text):
    # TODO: integrate your SMS gateway here
    # print(f"[SMS to {phone}] {text}")
    pass

def cache_key(phone): return f"otp:{phone}"

@require_POST
def otp_send(request):
    import json
    data = json.loads(request.body or '{}')
    phone = (data.get('phone') or '').strip()
    if not phone: return JsonResponse({'detail':'شماره لازم است.'}, status=400)

    # basic throttle: 1 req per 60s
    key = cache_key(phone)
    rec = cache.get(key)
    now = time.time()
    if rec and rec.get('next_at',0) > now:
        retry_in = int(rec['next_at']-now)
        return JsonResponse({'detail':'کمی صبر کنید.', 'retry_in': retry_in}, status=429)

    code = f"{random.randint(0,999999):06d}"
    cache.set(key, {'code':code, 'exp': now+180, 'next_at': now+60}, timeout=300)

    send_sms(phone, f"کد ورود شما: {code}")
    return JsonResponse({'ok':True, 'retry_in':60})

@require_POST
def otp_verify(request):
    import json
    data = json.loads(request.body or '{}')
    phone = (data.get('phone') or '').strip()
    otp   = (data.get('otp') or '').strip()
    if not phone or not otp: return JsonResponse({'detail':'اطلاعات ناکامل است.'}, status=400)

    rec = cache.get(cache_key(phone))
    now = time.time()
    if not rec or now > rec['exp']: return JsonResponse({'detail':'کد منقضی شده است.'}, status=400)
    if otp != rec['code']: return JsonResponse({'detail':'کد نادرست است.'}, status=400)

    # get or create a customer user by phone
    user, _ = User.objects.get_or_create(username=f"cust_{phone}", defaults={'is_active':True})
    # optionally store phone in a field: user.phone = phone; user.save(update_fields=['phone'])

    login(request, user)
    cache.delete(cache_key(phone))
    return JsonResponse({'ok':True, 'next': '/customer/dashboard/'})




def categories_list(request):
    categories = MaterialCategory.objects.all()

    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("categories_list")
    else:
        form = CategoryForm()

    return render(request, "materials/categories_list.html", {
        "categories": categories,
        "form": form,
    })


def category_detail(request, category_id):
    category = get_object_or_404(MaterialCategory, id=category_id)
    materials = category.materials.all()
    return render(request, "materials/category_detail.html", {
        "category": category,
        "materials": materials
    })

def add_material_to_category(request, category_id):
    category = get_object_or_404(MaterialCategory, id=category_id)
    all_materials = raw_material.objects.all()

    if request.method == "POST":
        selected_ids = request.POST.getlist("materials")
        raw_material.objects.filter(id__in=selected_ids).update(category=category)
        return redirect("category_detail", category_id=category.id)

    return render(request, "materials/add_material.html", {
        "category": category,
        "materials": all_materials,
    })

def remove_material_from_category(request, category_id, material_id):
    category = get_object_or_404(MaterialCategory, id=category_id)
    material = get_object_or_404(raw_material, id=material_id, category=category)

    if request.method == "POST":
        material.category = None
        material.save()
        return redirect("category_detail", category_id=category.id)

    return redirect("category_detail", category_id=category.id)

