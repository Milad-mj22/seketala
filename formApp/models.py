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
