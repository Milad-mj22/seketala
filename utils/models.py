from django.db import models
from users.models import raw_material
# Create your models here.


class WarehouseCode(models.TextChoices):
    CODE_0 = "0", "0"
    CODE_1 = "1", "1"
    CODE_2 = "2", "2"
    CODE_3 = "3", "3"

class RawMaterialTransfer(models.Model):
    material = models.ForeignKey(raw_material, on_delete= models.CASCADE,related_name='raw_material_transfer',blank=True,null=True)


    source = models.CharField(
        max_length=1,
        choices=WarehouseCode.choices
    )

    destination = models.CharField(
        max_length=1,
        choices=WarehouseCode.choices
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "انتقال مواد اولیه"
        verbose_name_plural = "انتقالات مواد اولیه"

    def __str__(self):
        return (
            f"{self.material} : "
            f"{self.get_source_display()} → "
            f"{self.get_destination_display()}"
        )
