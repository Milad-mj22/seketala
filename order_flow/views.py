from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from users.models import Inventory, RestaurantBranch, Warehouse,create_order,NightOrderRemainder,mother_food,Profile,raw_material
# Create your views here.
from .models import OrderStep,MaterialUsage
import ast
from decimal import Decimal
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Prefetch, F, DecimalField, Q  # Import DecimalField

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from decimal import Decimal


CENTER_KITCHEN = 'مرکزی'
CENTER_KITCHEN_OBJ = Warehouse.objects.filter(name=CENTER_KITCHEN).first()

TEMP_FOOD_KITCHEN = 'خاقانی'
TEMP_FOOD_KITCHEN_OBJ = Warehouse.objects.filter(name=TEMP_FOOD_KITCHEN).first()






def get_total_quantity(material,warehouse=None):
    if warehouse is None:
        total = Inventory.objects.filter(inventory_raw_material=material).aggregate(Sum('quantity'))['quantity__sum']
        return total or 0  # اگر مقدار None بود، 0 برگردانید
    else:

        total = Inventory.objects.filter(inventory_raw_material=material,warehouse=warehouse).aggregate(Sum('quantity'))['quantity__sum']
        return total or 0  # اگر مقدار None بود، 0 برگردانید



@login_required
def show_flow(request,order_id):
    if request.method == 'GET':

        context = {
            'order_id': order_id,
        }

        return render(request, 'show_flow.html',context)



def convert_raw_material2object(materials):
    result = {}
    materials_dict = ast.literal_eval(materials)
    materials_dict.pop('additional_details',None)

    # Reverse keys and values
    reversed_dmaterials_dictict = {v: k for k, v in materials_dict.items()}
    for material in list(materials_dict.keys()):
        

        obj = raw_material.objects.filter(name=material).first()

        


        if material in result.keys():
            try:
                v = float(result[material].quantity_used)
            except:
                v = 0

            obj.quantity_used = v + float(materials_dict[material])
        else:
            try:
                v = float(materials_dict[material])
            except:
               
                v = 0
            obj.quantity_used = v

        obj.quantity_used = round(obj.quantity_used,4)

        if obj.quantity_used >0.0 :
            result[material] = obj
    
    return result



def check_order_confirmed(order , stepNumber:int):

    ret_confirmed =  OrderStep.objects.filter(order = order , step_number=stepNumber).first()
    if ret_confirmed is not None:
        return ret_confirmed
    return False



def get_allowed_confirm_users(stepNumber:int):

    if stepNumber==1:
        allowed_roles = ['manager', 'fishzan','Kitchen Officer','Programmer','CEO']  # Adjust based on your logic
        return allowed_roles

    if stepNumber==2:

        allowed_roles = ['manager', 'fishzan','prepration officer','Programmer','CEO']  # Adjust based on your logic
        return allowed_roles

    if stepNumber==3:
        allowed_roles = ['manager', 'fishzan','Kitchen Officer','Programmer','CEO']  # Adjust based on your logic
        return allowed_roles
  
    if stepNumber==4:
        allowed_roles = ['manager', 'fishzan','Kitchen Officer','Programmer','CEO']  # Adjust based on your logic

        allowed_roles = ['manager', 'fishzan','prepration officer','Programmer','CEO']   # Adjust based on your logic
        return allowed_roles

    if stepNumber==3:
        allowed_roles = ['manager', 'fishzan','Kitchen Officer','Programmer','CEO']   # Adjust based on your logic
        return allowed_roles
  
    if stepNumber==4:
        allowed_roles = ['manager', 'fishzan','Kitchen Officer','Programmer','CEO']   # Adjust based on your logic

        return allowed_roles  
    
@login_required
def section1_view(request,order_id):

    context = {'order_id': order_id}
    step_number = 1

    if request.method == 'POST':

        material_names = request.POST.getlist("materials_names[]")
        material_units = request.POST.getlist("materials_units[]")
        material_quantities = request.POST.getlist("materials_quantities[]")


        ret = create_order.objects.filter(id=order_id).first()

        # order_step_obj = get_object_or_404(OrderStep, step_number=1 , order =ret )

        user_profile = Profile.objects.get(user=request.user)

        order_step_obj, created = OrderStep.objects.get_or_create(
            step_number=1, 
            order=ret,  # Ensure 'ret' is the correct order instance
            confirmed_by = user_profile
        )
        materials_data = []
        for i in range(len(material_names)):
            materials_data.append({
                "name": material_names[i],
                "unit": material_units[i],
                "quantity": material_quantities[i]
            })
            # #print(material_names[i])
            material = get_object_or_404(raw_material, name= material_names[i])  # Find material by name
            
            MaterialUsage.objects.create(
                step=order_step_obj,
                material=material,
                quantity=material_quantities[i]
            )



    


        return redirect("section1_url", order_id=order_id)  # هدایت به صفحه دیگر
    

    else:

        # ret = create_order.objects.filter(id=order_id).first()
        ret = create_order.objects.filter(id=order_id).first()
        # #print(ret)
        raw_materials_obj = convert_raw_material2object(ret.content)
        user_profile = Profile.objects.get(user=request.user)
        user_role = user_profile.job_position.name
        allowed_roles = get_allowed_confirm_users(stepNumber=1)
        # Check if the user has access to submit this step
        can_submit = user_role in allowed_roles
        is_confirmed = check_order_confirmed(order=ret,stepNumber=1)
        return render(request, 'section1.html', {
            'material_usages': raw_materials_obj,
            'user_role': user_role,
            'can_submit': can_submit,
            'is_confirmed': is_confirmed,
            'order_id':order_id,
            'step_number' : step_number
        })







from django.db import transaction

@login_required
def section2_view(request, order_id):
    context = {'order_id': order_id}
    step_number = 2

    if request.method == 'POST':
        material_names = request.POST.getlist("materials_names[]")
        material_sent = request.POST.getlist("materials_sent[]")

        ret = create_order.objects.filter(id=order_id).first()
        user_profile = Profile.objects.get(user=request.user)



        try:
            with transaction.atomic():  # فقط همین یک بلاک کافیست

                order_step_obj, created = OrderStep.objects.get_or_create(
                    step_number=step_number,
                    order=ret,
                    confirmed_by=user_profile
                )


                for i in range(len(material_names)):
                    material = get_object_or_404(raw_material, name=material_names[i])
                    quntity_material = get_total_quantity(material=material, warehouse=CENTER_KITCHEN_OBJ)

                    inventory, _ = Inventory.objects.get_or_create(
                        inventory_raw_material=material,
                        warehouse=CENTER_KITCHEN_OBJ
                    )

                    value = Decimal(round(float(material_sent[i]), 5))
                    if value > 0:
                        if quntity_material is None:
                            raise ValueError(f"ماده {material.name} در انبار مرکزی وجود ندارد")

                        if quntity_material < value:
                            raise ValueError(
                                f"ماده {material.name} به تعداد درخواست در انبار موجود نیست. "
                                f"(موجودی: {quntity_material})"
                            )

                        # کم کردن موجودی
                        inventory.remove_stock(amount=value, user=request.user.profile)

                    MaterialUsage.objects.get_or_create(
                        step=order_step_obj,
                        material=material,
                        quantity=value
                    )




        except ValueError as e:
            #print(e)
            # اینجا دیگه نیازی به set_rollback نیست
            return render(request, "not_confirmed.html", {
                "message": str(e),
                "order_id": order_id
            })

        messages.success(request, "ثبت خروج با موفقیت انجام شد.")
        return redirect("section2_url", order_id=order_id)

    else:
        # بخش GET تغییر نکرده
        ret = create_order.objects.filter(id=order_id).first()
        raw_materials_obj = convert_raw_material2object(ret.content)
        user_profile = Profile.objects.get(user=request.user)
        user_role = user_profile.job_position.name
        allowed_roles = get_allowed_confirm_users(stepNumber=step_number)
        can_submit = user_role in allowed_roles
        is_confirmed = check_order_confirmed(order=ret, stepNumber=step_number)

        if is_confirmed:
            order_step_obj = OrderStep.objects.filter(order=ret, step_number=step_number).first()
            for material in raw_materials_obj.values():
                obj = MaterialUsage.objects.filter(step=order_step_obj, material=material).first()
                if obj is not None:
                    material.step2_quantity = obj.quantity

        return render(request, 'section2.html', {
            'material_usages': raw_materials_obj,
            'user_role': user_role,
            'can_submit': can_submit,
            'is_confirmed': is_confirmed,
            'order_id': order_id,
            'step_number': step_number
        })


@login_required
def section3_view(request,order_id):
    context = {'order_id': order_id}
    step_number = 3

    if request.method == 'POST':
        try:
            with transaction.atomic():  # فقط همین یک بلاک کافیست
                material_names = request.POST.getlist("materials_names[]")
                material_sent = request.POST.getlist("materials_sent[]")
                
                ret = create_order.objects.filter(id=order_id).first()

                user_profile = Profile.objects.get(user=request.user)

                order_step_obj, created = OrderStep.objects.get_or_create(
                    step_number=step_number, 
                    order=ret,  # Ensure 'ret' is the correct order instance
                    confirmed_by = user_profile
                )
                materials_data = []
                for i in range(len(material_names)):
                    material = get_object_or_404(raw_material, name= material_names[i])  # Find material by name
                    
                    value = Decimal(round(float(material_sent[i]),5))

                    if value>0:

                        food_inventory, _ = Inventory.objects.get_or_create(
                            inventory_raw_material=material,
                            warehouse=TEMP_FOOD_KITCHEN_OBJ
                        )

                        status, message = food_inventory.add_stock(
                            amount=value, user=request.user.profile, receipt_number='7000'
                        )
                        # #print('status',status,'meesage',message)
                        
                    MaterialUsage.objects.create(
                        step=order_step_obj,
                        material=material,
                        quantity=value
                    )

                messages.success(request, "ثبت خروج با موفقیت انجام شد.")  # پیام موفقیت
                return redirect("section3_url", order_id=order_id)  # هدایت به صفحه دیگر

        except ValueError as e:
            # اینجا دیگه نیازی به set_rollback نیست
            return render(request, "not_confirmed.html", {
                "message": str(e),
                "order_id": order_id
            })



    else:
        # try:
            ret = create_order.objects.filter(id=order_id).first()
            raw_materials_obj = convert_raw_material2object(ret.content)
            user_profile = Profile.objects.get(user=request.user)
            user_role = user_profile.job_position.name
            allowed_roles = get_allowed_confirm_users(stepNumber=step_number)
            # Check if the user has access to submit this step
            can_submit = user_role in allowed_roles

            is_confirmed_step2 = check_order_confirmed(order=ret,stepNumber=2)

            if not is_confirmed_step2:
                return render(request , 'not_confirmed.html' ,{
                    'message' : '        ابتدا باید ارسال از آماده سازی  تأیید شود تا بتوانید وارد این قسمت شوید!',
                'order_id':order_id

                })

            is_confirmed_step3 = check_order_confirmed(order=ret,stepNumber=step_number)
            order_step_2_obj = OrderStep.objects.filter(order = ret , step_number=2).first()
            order_step_3_obj = OrderStep.objects.filter(order = ret , step_number=step_number).first()



            for material in raw_materials_obj.values():
                obj = MaterialUsage.objects.filter(step = order_step_2_obj,material=material).first()
                if obj is not None:
                    material.step2_quantity = obj.quantity
                    if is_confirmed_step3:
                        obj = MaterialUsage.objects.filter(step = order_step_3_obj,material=material).first()
                        material.step3_quantity = obj.quantity
                else:
                    return render(request , 'not_confirmed.html' ,{
                        'message' : '        ارسال از اماده سازی به  درستی تکمیل نشده است',
                    'order_id':order_id

                    })



            return render(request, 'section3.html', {
                'material_usages': raw_materials_obj,
                'user_role': user_role,
                'can_submit': can_submit,
                'is_confirmed': is_confirmed_step3,
                'order_id':order_id,
                'step_number' : step_number

            })  

        # except:
        #     messages.error(request,'خطا در دریافت اطلاعات')
        #     return render(request, 'section3.html', {
        #         'order_id':order_id,
        #         'messages':'خطا در دریافت اطلاعات'
        #     })  

        
@login_required
def section4_view(request , order_id):
    step_number=4
    
    if request.method == 'POST':


        try:
            with transaction.atomic():  # فقط همین یک بلاک کافیست
                material_names = request.POST.getlist("materials_names[]")
                material_sent = request.POST.getlist("materials_sent[]")
                
                ret = create_order.objects.filter(id=order_id).first()

                user_profile = Profile.objects.get(user=request.user)

                order_step_obj, created = OrderStep.objects.get_or_create(
                    step_number=step_number, 
                    order=ret,  # Ensure 'ret' is the correct order instance
                    confirmed_by = user_profile
                )

                for i in range(len(material_names)):
                    material = get_object_or_404(raw_material, name= material_names[i])  # Find material by name
                    MaterialUsage.objects.create(
                        step=order_step_obj,
                        material=material,
                        quantity=Decimal(float(material_sent[i]))
                    )

                messages.success(request, "ثبت مانده با موفقیت انجام شد.")  # پیام موفقیت
                return redirect("section4_url", order_id=order_id)  # هدایت به صفحه دیگر


        except ValueError as e:
            # اینجا دیگه نیازی به set_rollback نیست
            return render(request, "not_confirmed.html", {
                "message": str(e),
                "order_id": order_id
            })


    else:
        
        ret = create_order.objects.filter(id=order_id).first()
        raw_materials_obj = convert_raw_material2object(ret.content)
        user_profile = Profile.objects.get(user=request.user)
        user_role = user_profile.job_position.name
        allowed_roles = get_allowed_confirm_users(stepNumber=step_number)
        # Check if the user has access to submit this step
        can_submit = user_role in allowed_roles

        is_confirmed_step3 = check_order_confirmed(order=ret,stepNumber=3)

        if not is_confirmed_step3:
            return render(request , 'not_confirmed.html' ,{
                'message' : '        ابتدا باید تحویل رستوران انجام شود تا بتوانید وارد این قسمت شوید!',
            'order_id':order_id

            })

        is_confirmed_step4 = check_order_confirmed(order=ret,stepNumber=step_number)
        order_step_2_obj = OrderStep.objects.filter(order = ret , step_number=2).first()
        order_step_3_obj = OrderStep.objects.filter(order = ret , step_number=3).first()
        order_step_4_obj = OrderStep.objects.filter(order = ret , step_number=step_number).first()



        for material in raw_materials_obj.values():
            obj = MaterialUsage.objects.filter(step = order_step_2_obj,material=material).first()
            material.step2_quantity = obj.quantity

            obj = MaterialUsage.objects.filter(step = order_step_3_obj,material=material).first()
            material.step3_quantity = obj.quantity
            if is_confirmed_step4:
                obj = MaterialUsage.objects.filter(step = order_step_4_obj,material=material).first()
                material.step4_quantity = obj.quantity



        return render(request, 'section4.html', {
            'material_usages': raw_materials_obj,
            'user_role': user_role,
            'can_submit': can_submit,
            'is_confirmed': is_confirmed_step4,
            'order_id':order_id,
            'step_number' : step_number

        })




def edit_request(request, order_id,step_number):
    """
    Edit an existing request for an order, updating material usage.
    """
    if request.method == "POST":
    # try:
            step_number =  request.POST.get('step_number')  # Get the step number
            if step_number is None:
                messages.error(request, "خطا در دریافت اطلاعات")
                return redirect('section1_url', order_id=order_id)
            step_number = int(step_number)
            url_name = f'section{step_number}_url'


            user_profile = Profile.objects.get(user=request.user)
            user_role = user_profile.job_position.name
            allowed_roles = get_allowed_confirm_users(stepNumber=step_number)
            if user_role not in allowed_roles:
                messages.error(request, "شما مجاز به ویرایش این درخواست نیستید.")
                return redirect(url_name, order_id=order_id)





            material_names = request.POST.getlist("materials_names[]")
            material_quantities = request.POST.getlist("materials_quantities[]")
            materials_new = request.POST.getlist("materials_sent[]")


            if len(material_names) != len(materials_new):
                messages.error(request, "خطا در دریافت اطلاعات")
                return redirect(url_name, order_id=order_id)


            new_materials_dict = {}

            for iter , item in enumerate(material_names):
                new_materials_dict[item] = materials_new[iter]



            ret = create_order.objects.filter(id=order_id).first()
            raw_materials_obj = convert_raw_material2object(ret.content)
            order_step_obj = OrderStep.objects.filter(order = ret , step_number=step_number).first()


            for material in raw_materials_obj.values():
                obj = MaterialUsage.objects.filter(step = order_step_obj,material=material).first()
                if obj is not None:
                    if material.name in list(new_materials_dict.keys()) :
                        new_value = new_materials_dict[material.name]
                        obj.quantity =Decimal(new_value)
                        obj.save()

            # # Update materials
            # for i in range(len(material_names)):
            #     material = get_object_or_404(raw_material, name=material_names[i])
            #     material_usage, _ = MaterialUsage.objects.get_or_create(
            #         step=order_step_obj, material=material
            #     )
            #     material_usage.quantity = Decimal(material_quantities[i])
            #     material_usage.save()

            messages.success(request, "ویرایش درخواست با موفقیت انجام شد.")
            return redirect(url_name, order_id=order_id)

        # except Exception as e:
        #     messages.error(request, f"خطا در ویرایش درخواست: {str(e)}")
        #     return redirect("section1_url", order_id=order_id)

    else:
    
        ret = create_order.objects.filter(id=order_id).first()
        raw_materials_obj = convert_raw_material2object(ret.content)
        user_profile = Profile.objects.get(user=request.user)
        user_role = user_profile.job_position.name
        allowed_roles = get_allowed_confirm_users(stepNumber=step_number)



        ret = create_order.objects.filter(id=order_id).first()

        raw_materials_obj = convert_raw_material2object(ret.content)
        user_profile = Profile.objects.get(user=request.user)
        user_role = user_profile.job_position.name
        allowed_roles = get_allowed_confirm_users(stepNumber=step_number)
        # Check if the user has access to submit this step
        can_submit = user_role in allowed_roles


        order_step_obj = OrderStep.objects.filter(order = ret , step_number=step_number).first()



        for material in raw_materials_obj.values():
            obj = MaterialUsage.objects.filter(step = order_step_obj,material=material).first()
            if obj is not None:
                material.step_quantity = obj.quantity
            else:
                print('Error in material edit req')
                # #print(obj)

        # is_confirmed = check_order_confirmed(order=ret,stepNumber=1)
        return render(request, 'edit.html', {
            'material_usages': raw_materials_obj,
            'user_role': user_role,
            'can_submit': can_submit,
            # 'is_confirmed': is_confirmed,
            'order_id':order_id,
            'step_number' : step_number
        })



