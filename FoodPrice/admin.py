from django.contrib import admin

from FoodPrice.models import FoodIngredient, RawMaterialPrice

# Register your models here.


@admin.register(FoodIngredient)
class FoodIngredientAdmin(admin.ModelAdmin):
    list_display = ('food', 'quantity', 'wastage_percent')

@admin.register(RawMaterialPrice)
class RawMaterialPriceAdmin(admin.ModelAdmin):
    list_display = ( 'price', 'date')
