import difflib
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from .utils import detect_gender, fix_persian_text

import pandas as pd
from django.shortcuts import render
from .forms import CSVUploadForm
from users.models import Buyer, Inventory, MaterialComposition, Warehouse , mother_material , raw_material , mode_raw_materials



@login_required
def import_buyers_csv(request):
    created_count = 0
    updated_count = 0
    skipped_count = 0
    updated_names = []
    created_names = []
    skipped_names = []
    male_count = 0
    female_count = 0
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['file']

            col_first = request.POST.get('col_first')
            col_last = request.POST.get('col_last')
            col_phone = request.POST.get('col_phone')



            try:
                df = pd.read_csv(csv_file)
            except Exception as e:
                return render(request, 'import_csv.html', {
                    'form': form,
                    'error': 'خطا در خواندن فایل CSV: ' + str(e),
                })

            for _, row in df.iterrows():
                national_code = str(row.get('national_code', '')).strip()
                phone_number = str(row.get(col_phone, '')).strip()
                first_name = fix_persian_text(str(row.get(col_first, '')))
                last_name = fix_persian_text(str(row.get(col_last, '')))

                if  not phone_number :
                    skipped_count += 1
                    skipped_names.append(f'{first_name} {last_name}')
                    continue
                if  phone_number  == 'nan':
                    skipped_count += 1
                    skipped_names.append(f'{first_name} {last_name}')
                    continue
                

                if first_name == 'nan':
                    first_name = ''
                if last_name =='nan':
                    last_name = ''


                if last_name =='':
                    temp = first_name.split(' ')
                    if len(temp) > 1:
                        last_name = ' '.join(temp[1:])


                buyer = Buyer.objects.filter(first_name=first_name,last_name=last_name).first()

                if buyer:

                    buyer.phone_number = phone_number
                    buyer.save()
                    updated_count += 1
                    updated_names.append(f'{first_name} {last_name} {phone_number}')
                else:

                    # try:
                    buyer_created = False
                    if first_name !='':
                        gender = detect_gender(name=first_name)
                        if gender is not None:
                            gender = gender.lower()
                            if gender in ['male', 'female']:
                                Buyer.objects.create(
                                    first_name=first_name,
                                    last_name=last_name,
                                    phone_number=phone_number,
                                    gender = gender
                                )

                                if gender =='male':
                                    male_count+=1
                                else:
                                    female_count+=1

                                buyer_created = True

                    if not buyer_created:
                        Buyer.objects.create(
                            first_name=first_name,
                            last_name=last_name,
                            phone_number=phone_number,
                        )



                    created_count += 1
                    created_names.append(f'{first_name} {last_name} {phone_number}')


            return render(request, 'import_result.html', {
                'created': created_count,
                'updated': updated_count,
                'skipped': skipped_count,
                'created_names' : created_names,
                'update_names' : updated_names,
                'skipped_names' : skipped_names,
                'male_count':male_count,
                'female_count' : female_count,
                'not_detected' : abs(female_count-male_count),
            })
    else:
        form = CSVUploadForm()

    return render(request, 'import_csv.html', {'form': form})






@login_required
def import_raw_materials_csv(request):
    created_count = 0
    updated_count = 0
    skipped_count = 0
    created_names = []
    updated_names = []
    skipped_names = []

    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['file']

            try:
                df = pd.read_csv(csv_file)
            except Exception as e:
                return render(request, 'import_csv.html', {
                    'form': form,
                    'error': 'خطا در خواندن فایل CSV: ' + str(e),
                })
            
            col_id = request.POST.get('col_id')
            col_name = request.POST.get('col_name')
            col_unit = request.POST.get('col_unit')
            col_pattern = request.POST.get('col_pattern')




            for _, row in df.iterrows():
                name = str(row.get(col_name, '')).strip()
                describe = str(row.get(col_id, '')).strip()
                unit = str(row.get(col_unit, '')).strip()
                mother_name = str(row.get(col_pattern, '')).strip()
                mode_name = str(row.get('mode', '')).strip()

                if not name or not describe:
                    skipped_count += 1
                    skipped_names.append(name or 'نام نامشخص')
                    continue



                # Get all names from the DB
                all_mother_names = mother_material.objects.values_list('name', flat=True)

                # Find the closest match using difflib
                closest_matches = difflib.get_close_matches(mother_name, all_mother_names, n=1, cutoff=0.1)

                mother = None
                if closest_matches:
                    mother = mother_material.objects.filter(name=closest_matches[0]).first()



                mode = None
                if mode_name:
                    mode = mode_raw_materials.objects.filter(name__iexact=mode_name).first()

                raw = raw_material.objects.filter(name=name).first()
                if raw:
                    # Update existing
                    raw.describe = describe
                    raw.unit = unit
                    raw.mother = mother
                    raw.mode = mode
                    raw.save()
                    updated_count += 1
                    updated_names.append(name)
                else:
                    # Create new
                    raw_material.objects.create(
                        name=name,
                        describe=describe,
                        unit=unit,
                        mother=mother,
                        mode=mode,
                    )
                    created_count += 1
                    created_names.append(name)

            return render(request, 'import_result_material.html', {
                'created': created_count,
                'updated': updated_count,
                'skipped': skipped_count,
                'created_names': created_names,
                'update_names': updated_names,
                'skipped_names': skipped_names,
            })
    else:
        form = CSVUploadForm()

    return render(request, 'import_csv_material.html', {'form': form})


def create_new_composition_materail(name , code, unit):
    mother_code = code[:4]
    mother_code  = int(float(mother_code))
    from users.models import  raw_material
    mother_obj = mother_material.objects.filter(describe=mother_code).first()

    raw_material_obj = raw_material.objects.get_or_create(name = name,describe =code ,unit = unit,mother=mother_obj)

    return raw_material_obj
    # MaterialComposition.objects.get_or_create(nam)


@login_required
def import_composition_materials_csv(request):
    created_count = 0
    updated_count = 0
    skipped_count = 0
    created_names = []
    updated_names = []
    skipped_names = []

    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['file']

            try:
                df = pd.read_csv(csv_file)
            except Exception as e:
                return render(request, 'import_csv.html', {
                    'form': form,
                    'error': 'خطا در خواندن فایل CSV: ' + str(e),
                })
            
            col_material_code = request.POST.get('col_id')
            col_sub_material_code = request.POST.get('col_id2')
            col_name = request.POST.get('col_name')
            col_ratio = request.POST.get('col_ratio')
            col_unit = request.POST.get('col_unit')




            for _, row in df.iterrows():
                material_code = str(row.get(col_material_code, '')).strip()
                sub_material_code = str(row.get(col_sub_material_code, '')).strip()
                name = str(row.get(col_name, '')).strip()
                ratio = str(row.get(col_ratio, '')).strip()
                unit = str(row.get(col_unit, '')).strip()




                if material_code[:4] == '1007' :
                    raw_material_obj = create_new_composition_materail(name = name , unit = unit , code= material_code)
                    composition_material_obj_flag = True
                    continue
                    food_material = False
                elif material_code[:4] == '1008':
                    composition_material_obj_flag = False
                    food_material = True

                if  composition_material_obj_flag:
                        
                    composition_material = raw_material_obj[0]

                    if sub_material_code !='' :
                        sub_material_obj = raw_material.objects.filter(describe=sub_material_code)  
                        if sub_material_obj.exists():
                            sub_material_obj = sub_material_obj.first()
                            # materaial_coposition_obj = MaterialComposition.objects.filter(main_material=composition_material)
                            # if materaial_coposition_obj.exists():
                            MaterialComposition.objects.get_or_create(main_material=composition_material,ingredient =sub_material_obj,ratio=ratio )
                                
                        else:
                            try:
                                #print('not exist : ',name)
                                mother_code = sub_material_code[:4]
                                mother_code  = int(float(mother_code))
                                mother_obj = mother_material.objects.filter(describe=mother_code).first()
                                sub_material_obj = raw_material.objects.create(name=name,describe=sub_material_code,unit=unit,mother=mother_obj)
                                MaterialComposition.objects.get_or_create(main_material=composition_material,ingredient =sub_material_obj,ratio=ratio )
                            except:
                                print('Errior in imnport composition')
                
                

            return render(request, 'import_result_material.html', {
                'created': created_count,
                'updated': updated_count,
                'skipped': skipped_count,
                'created_names': created_names,
                'update_names': updated_names,
                'skipped_names': skipped_names,
            })
    else:
        form = CSVUploadForm()

    return render(request, 'import_csv_material_copmosition.html', {'form': form})






from decimal import Decimal, InvalidOperation
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum, F
from django.shortcuts import get_object_or_404, redirect, render


from users.models import mother_material as Mother_material  # your current import


def _to_decimal(value, default=Decimal("0")):
    if value is None:
        return default
    try:
        return Decimal(str(float(value)))
    except (ValueError, TypeError, InvalidOperation):
        return default

def manage_inventory(request):
    warehouses = Warehouse.objects.all().order_by("name")
    mother_materials = Mother_material.objects.all().order_by("name")

    # selected warehouse
    selected_warehouse_id = request.POST.get("warehouse") or request.GET.get("warehouse")
    if not selected_warehouse_id and warehouses.exists():
        selected_warehouse_id = str(warehouses.first().id)

    warehouse = None
    if selected_warehouse_id:
        warehouse = get_object_or_404(Warehouse, id=selected_warehouse_id)

    # current stock per mother material (for the selected warehouse)
    mother_stock = {}
    if warehouse:
        agg = (
            Inventory.objects.filter(warehouse=warehouse)
            .values(mother_id=F("inventory_raw_material__mother_id"))
            .annotate(total=Sum("quantity"))
        )
        mother_stock = {row["mother_id"]: row["total"] or Decimal("0") for row in agg}

    # children lists & counts (for collapse section)
    children = raw_material.objects.filter(mother__in=mother_materials).only("id", "name", "mother_id").order_by("name")
    # group children by mother id
    children_by_mother = {}
    for ch in children:
        children_by_mother.setdefault(ch.mother_id, []).append(ch)

    # counts
    child_counts = {mid: len(lst) for mid, lst in children_by_mother.items()}

    # current stock per child (to show inside collapse)
    child_stock = {}
    if warehouse:
        child_agg = (
            Inventory.objects.filter(warehouse=warehouse)
            .values(rm_id=F("inventory_raw_material_id"))
            .annotate(total=Sum("quantity"))
        )
        child_stock = {row["rm_id"]: row["total"] or Decimal("0") for row in child_agg}

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "add_items":
            if not warehouse:
                messages.error(request, "ابتدا یک انبار انتخاب کنید.")
                return redirect("manage_inventory")

            try:
                with transaction.atomic():
                    for mm in mother_materials:
                        qty_raw = request.POST.get(f"qty_{mm.id}")
                        qty_each_child = _to_decimal(qty_raw, Decimal("0"))
                        if qty_each_child > 0:
                            # add same qty to EACH child under this mother
                            for material in children_by_mother.get(mm.id, []):
                                inv, _ = Inventory.objects.get_or_create(
                                    inventory_raw_material=material,
                                    warehouse=warehouse
                                )
                                inv.add_stock(
                                    qty_each_child,
                                    request.user.profile,
                                    receipt_number=-10
                                )
                messages.success(request, "موجودی‌ها با موفقیت اضافه شدند.")
            except Exception as e:
                messages.error(request, f"خطا: {e}")

        elif action == "reset_zero":
            if not warehouse:
                messages.error(request, "ابتدا یک انبار انتخاب کنید.")
                return redirect("manage_inventory")

            try:
                with transaction.atomic():
                    inventories = Inventory.objects.select_for_update().filter(warehouse=warehouse)
                    for inv in inventories:
                        if inv.quantity and inv.quantity > 0:
                            inv.remove_stock(inv.quantity, request.user.profile)
                messages.success(request, "موجودی‌های انبار انتخاب‌شده با موفقیت صفر شد.")
            except Exception as e:
                messages.error(request, f"خطا در صفر کردن موجودی: {e}")

        return redirect(f"{request.path}?warehouse={selected_warehouse_id}")

    return render(request, "manage_inventory.html", {
        "warehouses": warehouses,
        "mother_materials": mother_materials,
        "mother_stock": mother_stock,
        "selected_warehouse_id": selected_warehouse_id,
        "children_by_mother": children_by_mother,
        "child_counts": child_counts,
        "child_stock": child_stock,
    })
