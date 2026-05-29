from django.contrib import admin
from .models import SMS_Service, SMS_Template, SMS_Persons, SMS_Recievers

@admin.register(SMS_Service)
class SMS_ServiceAdmin(admin.ModelAdmin):
    list_display = ('sms_panel', 'user_name', 'line_number')
    search_fields = ('sms_panel', 'user_name', 'line_number')
    # گروه‌بندی فیلدها برای ظاهر بهتر
    fieldsets = (
        ('اطلاعات پنل', {
            'fields': ('sms_panel', 'user_name', 'line_number')
        }),
        ('اطلاعات حساس', {
            'fields': ('password', 'api_key'),
            'classes': ('collapse',) # پنهان کردن پیش‌فرض برای امنیت بیشتر
        }),
    )

@admin.register(SMS_Template)
class SMS_TemplateAdmin(admin.ModelAdmin):
    # نمایش عنوان خوانا به جای نام فنی (get_name_display)
    list_display = ('get_name_display', 'service', 'template_id')
    list_filter = ('service', 'name')
    search_fields = ('template_id', 'name')

@admin.register(SMS_Persons)
class SMS_PersonsAdmin(admin.ModelAdmin):
    list_display = ('f_name', 'l_name', 'phone')
    search_fields = ('f_name', 'l_name', 'phone')

@admin.register(SMS_Recievers)
class SMS_RecieversAdmin(admin.ModelAdmin):
    list_display = ('template', 'persons')
    list_filter = ('template',)
    # جستجو در فیلدهای مدل‌های مرتبط (با استفاده از __)
    search_fields = (
        'persons__f_name', 
        'persons__l_name', 
        'persons__phone', 
        'template__template_id'
    )
