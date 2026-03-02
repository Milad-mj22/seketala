from django.db import models

# Create your models here.

from users.models import RestaurantBranch,FoodRawMaterial


class SoldOutStatus(models.Model):
    branch = models.ForeignKey(RestaurantBranch, on_delete=models.CASCADE, related_name="sold_out_status")
    product = models.ForeignKey(FoodRawMaterial, on_delete=models.CASCADE, related_name="sold_out_product")
    is_sold_out = models.BooleanField(default=False)  # مشخص می‌کند که محصول در این شعبه تمام شده است یا نه
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.branch.name} - {self.product.name} - {'Sold Out' if self.is_sold_out else 'Available'}"



