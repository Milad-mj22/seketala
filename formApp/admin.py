from django.contrib import admin

from formApp.models import CustomForm, FormField, FormSubmission, FormSubmissionData, NightlyFormModel

# Register your models here.

admin.site.register(CustomForm)
admin.site.register(FormField)
admin.site.register(FormSubmission)
admin.site.register(FormSubmissionData)


from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
@admin.register(NightlyFormModel)
class NightlyFormModelAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "date", "created_at", "voice_preview", "voice_download")
    list_filter = ("date", "created_at", "user")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("created_at", "updated_at", "voice_preview", "voice_download")

    # اگر data بزرگ است، این کمک می‌کند در ادیت ادمین راحت‌تر باشد
    # raw_id_fields = ("user",)

    def voice_preview(self, obj):
        """نمایش پلیر صوتی در ادمین"""
        if not obj.voice_note:
            return "—"
        return format_html(
            """
            <audio controls preload="none" style="width: 240px;">
                <source src="{}">
                مرورگر شما از پخش صدا پشتیبانی نمی‌کند.
            </audio>
            """,
            obj.voice_note.url
        )
    voice_preview.short_description = _("پخش ویس")

    def voice_download(self, obj):
        """لینک دانلود فایل صوتی"""
        if not obj.voice_note:
            return "—"
        return format_html(
            '<a href="{}" download>دانلود</a>',
            obj.voice_note.url
        )
    voice_download.short_description = _("دانلود ویس")