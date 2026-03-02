from django.db import models
from django.contrib.auth.models import User
from .utils import encrypt_text, decrypt_text


class PasswordEntry(models.Model):
    CATEGORY_CHOICES = (
        ('network', 'شبکه'),
        ('server', 'سرور'),
        ('app', 'نرم‌افزار'),
        ('other', 'سایر'),
    )

    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='network')
    system_address = models.CharField(max_length=200, blank=True, null=True)
    username = models.CharField(max_length=200, blank=True, null=True)

    # encrypted password stored in DB
    encrypted_password = models.TextField(blank=True, null=True)

    description = models.TextField(blank=True, null=True)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def set_password(self, plain_password: str):
        self.encrypted_password = encrypt_text(plain_password)

    def get_password(self) -> str:
        return decrypt_text(self.encrypted_password or "")

    def __str__(self):
        return self.title


class PasswordAttachment(models.Model):
    entry = models.ForeignKey(
        PasswordEntry,
        on_delete=models.CASCADE,
        related_name="attachments"
    )
    file = models.FileField(upload_to="vault_files/")
    description = models.CharField(max_length=200, blank=True, null=True)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.entry.title} - {self.file.name}"
