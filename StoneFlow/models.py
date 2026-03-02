from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from users.models import Buyer, raw_material
# Create your models here.

STATE_CHOICES = [
        ('transport', 'حمل و نقل'),
        ('warehouse', 'انبار کوپ'),
        ('accounting', 'حسابداری'),
        ('warehouse production', 'انبار تولید'),
        ('production', 'تولید'),
        ('factory_stock', 'افزودن به انبار کارخانه'),
        ('customer_order', 'سفارش مشتری'),
        ('showroom', 'نمایشگاه'),
]







class Step(models.Model):
    order = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    url_name = models.CharField(max_length=100)
    # ...

    def __str__(self):
        return f"مرحله {self.order}: {self.title}"

    class Meta:
        ordering = ['order']

class StepAccess(models.Model):
    ACCESS_LEVEL_CHOICES = (
        ('view', 'نمایش فقط'),
        ('submit', 'نمایش و ارسال'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    step = models.ForeignKey(Step, on_delete=models.CASCADE)
    access_level = models.CharField(max_length=10, choices=ACCESS_LEVEL_CHOICES)

    class Meta:
        unique_together = ('user', 'step')

    def __str__(self):
        return f"{self.user.username} - {self.step.title} ({self.get_access_level_display()})"




class CoopStateHistory(models.Model):
    coop = models.ForeignKey('coops', on_delete=models.CASCADE, related_name='state_history')
    previous_state =  models.ForeignKey(Step, on_delete=models.CASCADE,related_name='prev_history',blank=True,null=True)
    new_state =  models.ForeignKey(Step, on_delete=models.CASCADE,related_name='new_history')
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    changed_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.coop.id} | {self.previous_state} ➝ {self.new_state} @ {self.changed_at}"
    



    # def __str__(self):
    #     return f"{self.coop.id}"
    #     # | {self.previous_state.title} ➝ {self.new_state.title} @ {self.changed_at}"







class CoopAttribute(models.Model):
    TYPE_CHOICES = (
        ('int', 'عدد صحیح'),
        ('float', 'عدد اعشاری'),
        ('str', 'متن'),
        ('select', 'منوی کشویی'),  # 👈 اضافه شد
        ('bool', 'چک‌باکس'),               # ✅ NEW
        ('image', 'تصویر'),               # ✅ NEW
        ('material', 'ماده اولیه'),       # ✅ NEW
        ('warehouse', 'انبار'),           # ✅ NEW
        ('Cutting_factory', 'کارخانه برش اره'),           # ✅ NEW
        ('CuttingSaw', 'موارد برش اره'),           # ✅ NEW
        ('CuttingAround', 'موارد دور بور شده'),           # ✅ NEW
        ('multi_select', 'چک‌باکس چندتایی'),  # ✅ new
        ('date', 'تاریخ (شمسی)'),  # ✅ اضافه شد
        ('price', 'قیمت'),  # ✅ اضافه شد
        ('show_attr', 'نمایش ویژگی دیگر'),  # ✅ جدید

    )






    name = models.CharField(max_length=100)
    label = models.CharField(max_length=200 ,  unique=True)  # Add unique=True here
    field_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    required = models.BooleanField(default=False)
    default_value = models.CharField(max_length=255, blank=True, null=True)
    step = models.ForeignKey(Step, on_delete=models.CASCADE, verbose_name="مرحله نمایش")
    # step = models.PositiveSmallIntegerField(choices=STEP_CHOICES, default=1, verbose_name="مرحله نمایش")
    select_options = models.TextField(blank=True, null=True, help_text="مقادیر منو را با کاما جدا کنید (مثلاً: کوچک,متوسط,بزرگ)")


    def __str__(self):
        return self.label
    




class coops(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='raw_material_submissions')
    material = models.ForeignKey(raw_material, on_delete=models.CASCADE, related_name='submissions')
    
    quantity = models.FloatField()
    submitted_at  = models.DateTimeField(default=timezone.now, null=True, blank=True)
    # state = models.CharField(max_length=30, choices=STATE_CHOICES, default='transport')
    state = models.ForeignKey(Step, on_delete=models.CASCADE, default=None, null=True, blank=True ,related_name='coops_step' )


    image = models.ImageField(upload_to='mining_remittance/', blank=True, null=True)  # Added field for image

    is_active = models.BooleanField(default=True)

    is_sell = models.BooleanField(default=False)


    # فقط برای نگهداری موقتی کاربر تغییر دهنده
    _changed_by = None

    def __str__(self):
        return f"{self.user.username} - {self.material.name} - {self.state.title}"

    def set_changed_by(self, user):
        self._changed_by = user
            
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        previous_state = None

        if not is_new:
            previous = coops.objects.get(pk=self.pk)
            previous_state = previous.state

        super().save(*args, **kwargs)  # اول ذخیره کن تا مطمئن باشیم pk داریم


        # فقط وقتی کوپ جدید هست یا وضعیت تغییر کرده
        if (is_new and self.state) or (not is_new and previous_state != self.state):
            CoopStateHistory.objects.create(
                coop=self,
                previous_state=previous_state,
                new_state=self.state,
                changed_by=self._changed_by
            )









class CoopDeleteRequest(models.Model):
    coop = models.ForeignKey('coops', on_delete=models.CASCADE, related_name='delete_requests')
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='delete_requests')
    requested_at = models.DateTimeField(default=timezone.now)
    approved = models.BooleanField(null=True, blank=True)  # None = pending, True = approved, False = rejected
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_delete_requests')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(blank=True)

    def __str__(self):
        return f"Delete Request for Coop #{self.coop.id} by {self.requested_by.username}"






class CoopAttributeValue(models.Model):
    coop = models.ForeignKey(coops, on_delete=models.CASCADE, related_name='attribute_values')
    attribute = models.ForeignKey(CoopAttribute, on_delete=models.CASCADE)
    value = models.CharField(max_length=5000)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='CoopAttributeValue_submissions')

    created_at = models.DateTimeField(auto_now_add=True)  # تاریخ و زمان ایجاد خودکار
    updated_at = models.DateTimeField(auto_now=True)      # تاریخ و زمان آخرین به‌روزرسانی خودکار


    def __str__(self):
        return f"{self.attribute.name}: {self.value}"


# models.py
from django.db import models
from django.contrib.auth.models import User

class CarModel(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Driver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    national_code = models.CharField(max_length=10, unique=True)
    car_model = models.ForeignKey(CarModel, on_delete=models.SET_NULL, null=True)
    license_plate = models.CharField(max_length=20)
    car_code = models.CharField(max_length=20)

    def __str__(self):
        return self.full_name






class AttributeGroup(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="نام گروه ویژگی‌ها")
    attributes = models.ManyToManyField('CoopAttribute', related_name='groups', verbose_name="ویژگی‌ها")

    def __str__(self):
        return self.name






class Cutting_factory(models.Model):

    name = models.CharField(max_length=100, unique=True, verbose_name="نام")
    city = models.CharField(max_length=100, unique=True, verbose_name="شهر")
    
    def __str__(self):
        return self.name



class CuttingSaw(models.Model):

    coop = models.ForeignKey(coops, on_delete=models.CASCADE, related_name='CuttingSaw_values')
 
    length = models.FloatField(verbose_name="طول")
    width = models.FloatField(verbose_name="عرض")
    quantity = models.PositiveIntegerField(verbose_name="تعداد")
    description = models.CharField(max_length=1000, verbose_name="توضیحات", blank=True)

    image = models.ImageField(upload_to='cuttingSaw/', blank=True, null=True)  # Added field for image
    

    is_active = models.BooleanField(default=True)
    is_sell = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.coop.material.name if self.coop.material else '---'} - {self.length} {self.width} {self.quantity} "


class CuttingAround(models.Model):

    coop = models.ForeignKey(coops, on_delete=models.CASCADE, related_name='CuttingAround_values')
    length = models.FloatField(verbose_name="طول")
    width = models.FloatField(verbose_name="عرض")
    quantity = models.PositiveIntegerField(verbose_name="تعداد")
    serial = models.PositiveIntegerField(verbose_name="شماره سریال")
    description = models.CharField(max_length=1000, verbose_name="توضیحات", blank=True)

    def __str__(self):
        return f"{self.coop.material.name if self.coop.material else '---'} - {self.lenght} {self.width} {self.quantity} "



class PriceAttribute(models.Model):
    attribute = models.OneToOneField(CoopAttribute, on_delete=models.CASCADE, related_name='price_attr')
    multiplier = models.DecimalField(max_digits=10, decimal_places=2, default=1.0, verbose_name="ضریب")

    def __str__(self):
        return f"{self.attribute.label} (ضریب: {self.multiplier})"
    




# models.py
class PreInvoice(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="ایجاد کننده")
    created_at = models.DateTimeField(auto_now_add=True)
    
    customer = models.ForeignKey(Buyer, on_delete=models.CASCADE, verbose_name="نام مشتری")

    note = models.TextField(blank=True, null=True, verbose_name="توضیحات")
    is_sell = models.BooleanField(default=False)

    def __str__(self):
        return f"پیش‌فاکتور {self.id} - {self.customer.first_name}"


class PreInvoiceItem(models.Model):
    pre_invoice = models.ForeignKey(PreInvoice, on_delete=models.CASCADE, related_name="items")
    coop = models.ForeignKey(coops, on_delete=models.CASCADE, verbose_name="کوپ انتخابی")
    unit_price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="قیمت واحد")
    discount = models.DecimalField(max_digits=10, decimal_places=0, default=0, verbose_name="تخفیف")
    is_sell = models.BooleanField(default=False)
    def total_price(self):
        return self.unit_price - self.discount

    def __str__(self):
        return f"آیتم {self.coop.material.name} برای {self.pre_invoice}"
    