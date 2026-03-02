from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User


class Mine(models.Model):
    MINE_TYPE_CHOICES = [
        ('surface', 'معدن زمینی'),
        ('store', 'انبار کوپ'),
    ]

    name = models.CharField(max_length=200, verbose_name='نام معدن')
    city = models.CharField(max_length=100, verbose_name='شهر')
    location = models.CharField(max_length=300, verbose_name='موقعیت جغرافیایی')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    mine_type = models.CharField(
        max_length=20,
        choices=MINE_TYPE_CHOICES,
        verbose_name='نوع معدن',
        default='surface'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='ایجادکننده')

    def __str__(self):
        return self.name