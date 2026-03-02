from django.db import models

from users.models import create_order , Profile , raw_material

# Create your models here.

class OrderStep(models.Model):
    """مدل برای مدیریت هر مرحله و ثبت تأییدیه هر کاربر"""
    order = models.ForeignKey(create_order, on_delete=models.CASCADE)
    step_number = models.IntegerField()  # شماره مرحله (1 تا 5)
    confirmed_by = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Step {self.step_number} - Order {self.order.id}"

class MaterialUsage(models.Model):
    """مدل برای مشخص کردن مقدار مصرف مواد اولیه در هر مرحله"""
    step = models.ForeignKey(OrderStep, on_delete=models.CASCADE)
    material = models.ForeignKey(raw_material, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=20, decimal_places=4)  # مقدار مصرف شده
    
    def __str__(self):
        return f"{self.material.name} - {self.quantity} {self.material.unit} - Step {self.step.step_number}"