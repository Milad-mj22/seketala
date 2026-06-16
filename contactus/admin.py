from django.contrib import admin

from contactus.models import Feedback,BankCard,Bank

# Register your models here.
admin.site.register(Feedback)
admin.site.register(BankCard)
admin.site.register(Bank)