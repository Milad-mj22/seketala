from django.db import models
from django.contrib.auth.models import User

# Create your models here.




class SMS(models.Model):
    sender = models.CharField(max_length=50)
    message = models.TextField()
    received_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} - {self.received_at}"
    



class BankAccount(models.Model):
    name = models.CharField(max_length=255, verbose_name="نام حساب")
    account_number = models.CharField(max_length=50, unique=True, verbose_name="شماره حساب")
    bank_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="نام بانک")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")


    def __str__(self):
        return f"{self.name} - {self.account_number}"
    





class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=[('user', 'User'), ('system', 'System'), ('assistant', 'Assistant')])
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session = models.ForeignKey(ChatSession, on_delete=models.SET_NULL, null=True, blank=True)
    order_summary = models.TextField()
    status = models.CharField(max_length=20, choices=[
        ('pending', 'در انتظار'),
        ('confirmed', 'تأیید شده'),
        ('preparing', 'در حال آماده‌سازی'),
        ('ready', 'آماده'),
        ('delivered', 'تحویل داده شده'),
        ('cancelled', 'لغو شده')
    ], default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)