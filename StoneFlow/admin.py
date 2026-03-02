from django.contrib import admin

# Register your models here.
# Register your models here.

from .models import CoopAttribute, CoopStateHistory, CuttingSaw, PreInvoiceItem, coops , CarModel , CoopAttributeValue,Step,StepAccess





class CoopStateHistoryInline(admin.TabularInline):
    model = CoopStateHistory
    extra = 0
    readonly_fields = ['previous_state', 'new_state', 'changed_by', 'changed_at']

class CoopAdmin(admin.ModelAdmin):
    inlines = [CoopStateHistoryInline]

admin.site.register(coops, CoopAdmin)
admin.site.register(CoopStateHistory)
admin.site.register(CarModel)
admin.site.register(Step)
admin.site.register(StepAccess)
admin.site.register(CuttingSaw)
admin.site.register(PreInvoiceItem)



@admin.register(CoopAttribute)
class CoopAttributeAdmin(admin.ModelAdmin):
    list_display = ['label', 'field_type', 'required', 'default_value', 'step']




@admin.register(CoopAttributeValue)
class CoopAttributeAdmin(admin.ModelAdmin):
    list_display = ['coop', 'attribute', 'value']