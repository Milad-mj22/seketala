from django.utils import timezone

from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from users.models import raw_material, FoodRawMaterial
from .models import FoodIngredient, RawMaterialPrice
from .forms import FoodIngredientForm, FoodForm   # تو باید این دو فرم را بسازی


# -------------------------------
# 1) Show all foods
# -------------------------------
def foods_list(request):
    foods = FoodRawMaterial.objects.all()

    for food in foods :
        ingredients = FoodIngredient.objects.filter(food=food)
        total_cost = sum([i.total_cost() for i in ingredients])
        food.total_cost = total_cost
    return render(request, "foods_list.html", {"foods": foods})


# -------------------------------
# 2) Create a new food
# -------------------------------

# -------------------------------
# 3) Show ingredients of a food
# -------------------------------
def food_ingredients(request, food_id):
    food = get_object_or_404(FoodRawMaterial, pk=food_id)
    ingredients = FoodIngredient.objects.filter(food=food)

    # Add new ingredient
    if request.method == "POST":
        form = FoodIngredientForm(request.POST)
        if form.is_valid():
            ing = form.save(commit=False)
            ing.food = food
            ing.save()
            messages.success(request, "ماده اولیه با موفقیت اضافه شد.")
            return redirect("food_ingredients", food_id=food.id)

    else:
        form = FoodIngredientForm()

    total_quantity = sum([i.quantity for i in ingredients])
    total_wastage = sum([i.wastage_percent for i in ingredients])
    total_cost = sum([i.total_cost() for i in ingredients])

    context = {
        'food': food,
        'ingredients': ingredients,
        'total_quantity': total_quantity,
        'total_wastage': total_wastage,
        'total_cost': total_cost
    }
    return render(request, 'food_ingredients.html', context)
# -------------------------------
# 4) Delete ingredient
# -------------------------------
def delete_food_ingredient(request, ingredient_id):
    ing = get_object_or_404(FoodIngredient, pk=ingredient_id)
    food_id = ing.food.id
    ing.delete()
    messages.success(request, "ماده اولیه حذف شد.")
    return redirect("food_ingredients", food_id=food_id)



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from .models import FoodIngredient, RawMaterialPrice

def update_ingredient(request, ingredient_id):
    ingredient = get_object_or_404(FoodIngredient, id=ingredient_id)
    raw_material_obj = ingredient.raw_material_price.raw_material

    # گرفتن آخرین قیمت موجود برای پیش‌فرض
    last_price_obj = raw_material_obj.prices.first()
    last_price = last_price_obj.price if last_price_obj else 0

    if request.method == 'POST':
        quantity = request.POST.get('quantity')
        wastage_percent = request.POST.get('wastage_percent', 0)
        price_input = request.POST.get('price', None)

        if quantity:
            ingredient.quantity = float(quantity)
        if wastage_percent:
            ingredient.wastage_percent = float(wastage_percent)

        # اگر قیمت وارد شده بود، یک رکورد جدید RawMaterialPrice ایجاد شود
        if price_input:
            new_price = RawMaterialPrice.objects.create(
                raw_material=raw_material_obj,
                price=float(price_input),
                newest_price = float(price_input),
                date=timezone.now()
            )
            ingredient.raw_material_price = new_price

        ingredient.save()
        messages.success(request, f'ماده {raw_material_obj.name} بروزرسانی شد.')
        return redirect('food_ingredients', food_id=ingredient.food.id)

    context = {
        'ingredient': ingredient,
        'last_price': last_price,
        'raw_material': raw_material_obj
    }
    return render(request, 'update_ingredient.html', context)



def add_ingredient(request, food_id):
    food = get_object_or_404(FoodRawMaterial, id=food_id)

    if request.method == 'POST':
        raw_material_id = request.POST.get('raw_material')
        material_obj = get_object_or_404(raw_material, id=raw_material_id)

        quantity = float(request.POST.get('quantity'))
        wastage_percent = float(request.POST.get('wastage_percent', 0))
        price_input = request.POST.get("price", 0)
        if price_input =='':
            price_input =0
        try:
            price_input = float(price_input)
        except:
            price_input = 0


        # create new price
        new_price = RawMaterialPrice.objects.create(
            raw_material=material_obj,
            price=price_input,
            newest_price=price_input,
            date=timezone.now()
        )

        # create ingredient
        FoodIngredient.objects.create(
            food=food,
            raw_material_price=new_price,
            quantity=quantity,
            wastage_percent=wastage_percent
        )

        messages.success(request, 'ماده اولیه جدید اضافه شد.')
        return redirect('food_ingredients', food_id=food.id)

    # ----------------------------------------------------
    # 🔥 GET ALL RAW MATERIALS + LAST PRICE FOR FRONT
    # ----------------------------------------------------
    raw_materials = raw_material.objects.all()

    materials_with_price = []
    for m in raw_materials:
        last_price = m.prices.first()  # because model Meta ordering = ['-date']
        materials_with_price.append({
            'id': m.id,
            'name': m.name,
            'unit': getattr(m, "unit", ""),  # if you have unit
            'last_price': last_price.price if last_price else None
        })

    context = {
        'food': food,
        'materials': materials_with_price,
    }

    return render(request, 'add_ingredient.html', context)



def delete_food(request, food_id):
    food = get_object_or_404(FoodRawMaterial, id=food_id)

    if request.method == "POST":
        food.delete()
        messages.success(request, "غذا با موفقیت حذف شد.")
        return redirect("foods_list")  # صفحه‌ای که لیست غذاها را نشان می‌دهد

    return redirect("foods_list")


from django.shortcuts import render, redirect
from django.contrib import messages
from .models import FoodRawMaterial
from .forms import FoodForm

def add_food(request):
    if request.method == "POST":
        form = FoodForm(request.POST, request.FILES)

        if form.is_valid():
            food = form.save()
            messages.success(request, f"غذای «{food.name}» با موفقیت ثبت شد.")
            return redirect("foods_list")  # صفحه لیست غذاها

    else:
        form = FoodForm()

    return render(request, "add_food.html", {"form": form})


def update_food(request, pk):
    food = get_object_or_404(FoodRawMaterial, pk=pk)

    if request.method == "POST":
        form = FoodForm(request.POST, request.FILES, instance=food)
        if form.is_valid():
            form.save()
            messages.success(request, "غذا با موفقیت ویرایش شد.")
            return redirect("foods_list")
    else:
        form = FoodForm(instance=food)

    return render(request, "update_food.html", {"form": form, "food": food})



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import FoodRawMaterial, FoodIngredient

# حذف ماده اولیه
def delete_ingredient(request, ingredient_id):
    ingredient = get_object_or_404(FoodIngredient, id=ingredient_id)
    food_id = ingredient.food.id
    ingredient.delete()
    messages.success(request, f'ماده اولیه {ingredient.raw_material_price.raw_material.name} حذف شد.')
    return redirect('food_ingredients', food_id=food_id)
