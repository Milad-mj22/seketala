
from django.contrib import admin

from DataAnalysis.models import Invoice,InvoiceItem

# Register your models here.


from django.contrib import admin
from django.db.models import Sum
from .models import Invoice, InvoiceItem


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0
    fields = ('food_name', 'price', 'quantity', 'total')
    readonly_fields = ('total',)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        'invoice_number',
        'name',
        'phone',
        'nahveh',
        'created_at',
        'items_count',
        'total_price_formatted',
        'discount',
        'peyk',
        'anaam',
        'moshtarak',
        'serv',
        'pnum',
        'shomare_pos',
        'mablagh_pos',
        'hazine_peyk',
        'naghdi',
        'nonaghdi',
        'mandeh',

    )

    list_filter = ('created_at',)
    search_fields = ('invoice_number', 'name', 'phone')
    ordering = ('-created_at',)

    readonly_fields = ('total_price',)
    inlines = [InvoiceItemInline]

    fieldsets = (
        ('اطلاعات فاکتور', {
            'fields': (
                'invoice_number',
                'name',
                'phone',
                'nahveh',
                'created_at',
                'discount',
                'peyk',
                'anaam',
                        'moshtarak',
        'serv',
        'pnum',
        'shomare_pos',
        'mablagh_pos',
        'hazine_peyk',
        'naghdi',
        'nonaghdi',
        'mandeh',

            )
        }),
        ('مبالغ', {
            'fields': ('total_price',),
        }),
    )

    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = 'تعداد آیتم‌ها'

    def total_price_formatted(self, obj):
        return f"{obj.total_price:,} ریال"
    total_price_formatted.short_description = 'مبلغ کل'


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = (
        'invoice',
        'food_name',
        'price_formatted',
        'quantity',
        'total_formatted',
    )

    list_filter = ('invoice',)
    search_fields = ('food_name',)
    autocomplete_fields = ('invoice',)

    def price_formatted(self, obj):
        return f"{obj.price:,} ریال"
    price_formatted.short_description = 'قیمت واحد'

    def total_formatted(self, obj):
        return f"{obj.total:,} ریال"
    total_formatted.short_description = 'جمع کل'

