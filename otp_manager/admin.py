from django.contrib import admin

from otp_manager.models import SMS_Persons, SMS_Recievers, SMS_Service, SMS_Template

# Register your models here.


admin.site.register(SMS_Service)
admin.site.register(SMS_Template)
admin.site.register(SMS_Persons)
admin.site.register(SMS_Recievers)