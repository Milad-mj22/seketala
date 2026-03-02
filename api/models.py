from django.db import models

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