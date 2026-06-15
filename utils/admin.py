from django.contrib import admin
from .models import RawMaterialTransfer

@admin.register(RawMaterialTransfer)
class RawMaterialTransferAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'material',
        'source',
        'destination',
        'created_at',
    )

    list_filter = (
        'source',
        'destination',
        'created_at',
    )

    readonly_fields = ('created_at',)

    search_fields = ('material__name',)

    ordering = ('-created_at',)

    date_hierarchy = 'created_at'

    # autocomplete_fields = ('material',)  <-- remove this