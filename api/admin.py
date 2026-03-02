from django.contrib import admin

from api.models import SMS, BankAccount

# Register your models here.


admin.site.register(SMS)


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'account_number', 'bank_name', 'created_at')
    search_fields = ('name', 'account_number', 'bank_name')