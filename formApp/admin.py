from django.contrib import admin

from formApp.models import CustomForm, FormField, FormSubmission, FormSubmissionData, NightlyFormModel

# Register your models here.

admin.site.register(CustomForm)
admin.site.register(FormField)
admin.site.register(FormSubmission)
admin.site.register(FormSubmissionData)
admin.site.register(NightlyFormModel)

