from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Mine

@admin.register(Mine)
class MineAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'created_at', 'created_by')
    search_fields = ('name', 'location')
