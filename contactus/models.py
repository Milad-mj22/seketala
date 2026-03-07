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

