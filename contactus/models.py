from django.db import models

# Create your models here.

from django.db import models

class Feedback(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام")
    rating = models.IntegerField(verbose_name="امتیاز")
    message = models.TextField(verbose_name="پیام")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")

    def __str__(self):
        return f"{self.name} - امتیاز: {self.rating}"




# models.py
from django.db import models

class Bank(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="نام بانک")
    color = models.CharField(max_length=7, verbose_name="کد رنگ بانک (مثال: #FFFFFF)")
    logo = models.ImageField(upload_to='bank_logos/', blank=True, null=True, verbose_name="لوگوی بانک")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "بانک"
        verbose_name_plural = "بانک‌ها"

class BankCard(models.Model):
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, related_name='cards', verbose_name="بانک")
    card_number = models.CharField(max_length=16, verbose_name="شماره کارت")
    account_holder_name = models.CharField(max_length=100, verbose_name="نام صاحب حساب")
    is_active = models.BooleanField(default=False)  # فقط یکی باید True باشد
    # اطلاعاتی مثل رنگ و لوگو حالا در مدل Bank نگهداری می شوند

    def __str__(self):
        return f"{self.account_holder_name} - {self.bank.name} ({self.card_number[:4]}****)"

    class Meta:
        verbose_name = "کارت بانکی"
        verbose_name_plural = "کارت‌های بانکی"
        # می توانیم شرطی برای منحصر به فرد بودن شماره کارت در یک بانک بگذاریم، اما فعلا ساده نگه میداریم
        # unique_together = ('bank', 'card_number')
