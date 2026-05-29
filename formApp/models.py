from django.db import models

# Create your models here.


# models.py
from django.db import models
from django.contrib.auth.models import User

class CustomForm(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_forms')
    allowed_creators = models.ManyToManyField(User, related_name='can_create_forms', blank=True)
    allowed_submitters = models.ManyToManyField(User, related_name='can_submit_forms', blank=True)
    is_closed = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title

class FormField(models.Model):
    FIELD_TYPES = (
        ('text', 'Text'),
        ('textarea', 'Text Area'),
        ('number', 'Number'),
        ('date', 'Date'),
    )
    form = models.ForeignKey(CustomForm, on_delete=models.CASCADE, related_name='fields')
    label = models.CharField(max_length=255)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES)

    def __str__(self):
        return f"{self.label} ({self.form.title})"

class FormSubmission(models.Model):
    form = models.ForeignKey(CustomForm, on_delete=models.CASCADE)
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)

class FormSubmissionData(models.Model):
    submission = models.ForeignKey(FormSubmission, on_delete=models.CASCADE, related_name='data')
    field = models.ForeignKey(FormField, on_delete=models.CASCADE)
    value = models.TextField()






class NightlyFormModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)  # تاریخ ارسال فرم (روز)
    data = models.JSONField(default=dict)      # داده‌های فرم (انعطاف‌پذیر برای تغییر تعداد فیلدها)
    created_at = models.DateTimeField(auto_now_add=True)  # زمان ارسال اولیه
    updated_at = models.DateTimeField(auto_now=True)      # آخرین ویرایش
    voice_note = models.FileField(
        upload_to='nightly_voices/',
        blank=True,
        null=True,
        verbose_name='ویس توضیحات'
    )

class NightlyFormHistory(models.Model):
    form = models.ForeignKey(NightlyFormModel, on_delete=models.CASCADE, related_name='history')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    edited_at = models.DateTimeField(auto_now_add=True)
    old_data = models.JSONField(default=dict)  # داده‌های قبل از ویرایش
    new_data = models.JSONField(default=dict)  # داده‌های جدید (اختیاری)

    def __str__(self):
        return f"{self.user} edited on {self.edited_at}"