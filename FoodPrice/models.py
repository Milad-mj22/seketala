from django.db import models
from users.models import raw_material , FoodRawMaterial
from django.utils import timezone





class RawMaterialPrice(models.Model):
    raw_material = models.ForeignKey(raw_material, on_delete=models.CASCADE, related_name="prices")
    price = models.DecimalField(max_digits=15, decimal_places=2)
    date = models.DateTimeField(default=timezone.now)
    newest_price = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f"{self.raw_material.name} - {self.price} ({self.date.date()})"

    class Meta:
        ordering = ['-date']

    def save(self, *args, **kwargs):
        # first save this row
        super().save(*args, **kwargs)

        # then update newest_price for ALL prices of this material
        RawMaterialPrice.objects.filter(
            raw_material=self.raw_material
        ).update(newest_price=self.price)


class FoodIngredient(models.Model):
    food = models.ForeignKey(FoodRawMaterial, on_delete=models.CASCADE, related_name="ingredients")
    raw_material_price = models.ForeignKey(
        RawMaterialPrice,
        on_delete=models.CASCADE,
        related_name="used_in_foods"
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=3)
    wastage_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.raw_material_price.raw_material.name} in {self.food.name}"

    def total_cost(self):
        """Cost = quantity × price × (1 + waste)"""
        price = self.raw_material_price.newest_price
        return self.quantity * price * (1 + (self.wastage_percent / 100))
