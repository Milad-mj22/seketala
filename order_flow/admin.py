from django.contrib import admin

# Register your models here.

from .models import MaterialUsage,OrderStep


admin.site.register(MaterialUsage)
admin.site.register(OrderStep)
