import os
from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.urls import reverse
from django.utils import timezone
from django.db import models
from django_quill.fields import QuillField

from tinymce.models import HTMLField
from users.fields import JalaliDateField  # Adjust the import path as needed
from phonenumber_field.modelfields import PhoneNumberField
from khayyam import JalaliDatetime
try:
    RESAMPLING = Image.Resampling.LANCZOS
except AttributeError:
    RESAMPLING = Image.ANTIALIAS  # برای نسخه‌های قدیمی‌تر Pillow



# آیتم قابل نمایش در منو (مثلاً کوپ‌ها، داشبورد و غیره)
class MenuItem(models.Model):
    title = models.CharField(max_length=100, verbose_name="عنوان آیتم")
    icon = models.CharField(max_length=100, blank=True, verbose_name="آیکون (کلاس FontAwesome)")
    url = models.CharField(max_length=200, verbose_name="آدرس URL")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    def __str__(self):
        return self.title


class SubMenuItem(models.Model):
    parent_menu = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='submenus', verbose_name="منوی والد")
    title = models.CharField(max_length=100, verbose_name="عنوان زیرمنو")
    icon = models.CharField(max_length=100, blank=True, verbose_name="آیکون (کلاس FontAwesome)")
    url = models.CharField(max_length=200, verbose_name="آدرس URL")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.parent_menu.title} -> {self.title}"

class jobs(models.Model):
    name = models.CharField(max_length=200)
    persian_name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=3,unique=True)
    describe = models.CharField(max_length=800,null=True,blank=True)
    level = models.IntegerField(default=100,null=True,blank=True)

    items = models.ManyToManyField(MenuItem, blank=True, related_name="roles", verbose_name="دسترسی به آیتم‌ها",null=True)  # 👈 این خط را اضافه کن


    def __str__(self):
        return str(self.name)
    
    class Meta:
        ordering = ['-short_name']



# models.py
class ReportTitles(models.Model):
    title = models.CharField(max_length=255,blank=True,default='روزانه')

    def __str__(self):
        return self.title


class DailyReports(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_reports')
    date = models.DateField(default=timezone.now)

    # title = models.CharField(max_length=255)  # <-- Keep this
    title = models.ForeignKey(ReportTitles, on_delete=models.CASCADE,related_name='daily_reports', null=True, blank=True)  # New field

    # title = models.ForeignKey(ReportTitle, on_delete=models.CASCADE,blank=True,null=True)  # now using FK
    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username} -  ({self.date})'   #{self.title}
    


class MaterialCategory(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

    # اگر بخوای هر کاربر فقط بعضی دسته‌ها رو ببینه
    users = models.ManyToManyField(User, related_name="material_categories", blank=True)

    def __str__(self):
        return self.name



# Extending User Model Using a One-To-One Link
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.TextField(max_length=100,blank=True,null=True)
    last_name = models.TextField(max_length=100,blank=True,null=True)
    phone = models.BigIntegerField(blank=True,null=True,verbose_name='شماره تماس')
    address = models.TextField(max_length=300,blank=True,null=True)

    avatar = models.ImageField(default='default.jpg', upload_to='profile_images')
    bio = models.TextField(blank=True,null=True)
    # job_position = models.CharField(max_length=400)
    job_position = models.ForeignKey(jobs, on_delete= models.CASCADE,related_name='profile_job_position',blank=True,null=True)
    # job_position = models.TextField(max_length=300,blank=True,null=True)

    # فیلدهای مربوط به پوش نوتیفیکیشن
    push_endpoint = models.TextField(blank=True, null=True)
    push_p256dh = models.TextField(blank=True, null=True)
    push_auth = models.TextField(blank=True, null=True)


    # 👇 New Field
    code_vaset = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='کد واسط'
    )


    def __str__(self):
        return self.user.username

    # resizing images
    def save(self, *args, **kwargs):
        super().save()

        img = Image.open(self.avatar.path)

        if img.height > 800 or img.width > 800:
            max_size=(800, 800)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            img.save(self.avatar.path)

    @property
    def full_name(self):
        first = (self.first_name or "").strip()
        last = (self.last_name or "").strip()

        full = f"{first} {last}".strip()
        return full if full else self.user.username

STATUS = (
    (0,"Draft"),
    (1,"Publish")
)

class Post(models.Model):
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(User, on_delete= models.CASCADE,related_name='blog_posts')
    updated_on = models.DateTimeField(auto_now= True)
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=STATUS, default=0)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        #print(reverse("blog/", kwargs={"slug": self.slug}))
        # asd
        return "blog/"+{"slug": self.slug}



class Tools(models.Model):

    ICON_CHOICES = [
        ("⚙️", "⚙️ تنظیمات"),
        ("📊", "📊 گزارش / داشبورد"),
        ("🍽️", "🍽️ غذا / منو"),
        ("📦", "📦 انبار / کالا"),
        ("💰", "💰 مالی / هزینه"),
        ("🧮", "🧮 محاسبات / ابزار"),
        ("📅", "📅 برنامه‌ریزی / زمان‌بندی"),
        ("🔧", "🔧 ابزار / تنظیمات فنی"),
        ("🧾", "🧾 فاکتور / سند"),
        ("🧠", "🧠 هوش / AI"),
    ]



    title = models.CharField(max_length=200, unique=True)
    slug = models.CharField(max_length=300, unique=True) 
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    icon = models.CharField(
        max_length=10,
        choices=ICON_CHOICES,
        default="⚙️",
        verbose_name="آیکون"
    )
    category = models.CharField(max_length=100, default="عمومی")
    status = models.CharField(
        max_length=50,
        choices=[("ready", "آماده"), ("dev", "در حال توسعه")],
        default="ready"
    )


    class Meta:
        ordering = ['-title']

    def __str__(self):
        return self.title
    


class FoodFilter(models.Model):


    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-title']

    def __str__(self):
        return self.title




class QuillPost(models.Model):
    content = QuillField()


class Post_quill(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(User, on_delete= models.CASCADE,related_name='blog_posts_quil',default=1,blank=True,null=True)
    body = QuillField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title    
    

    class Meta:
        ordering = ['-created_at']





class full_post(models.Model): 
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(User, on_delete= models.CASCADE,related_name='blog_posts_tinymce',default=1,blank=True,null=True)
    content = HTMLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.title)
    
    class Meta:
        ordering = ['-created_at']

class cities(models.Model):

    name = models.CharField(max_length=200)
    persian_name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=3,unique=True)

    def __str__(self):
        return str(self.name)
    
    class Meta:
        ordering = ['-short_name']

class Projects(models.Model):
    name = models.CharField(max_length=200)
    persian_name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=10,unique=True)
    start_date = models.DateTimeField(null=False)
    project_maanger = models.ForeignKey(User, on_delete= models.CASCADE,related_name='project_manager',default=1,blank=True,null=True)
    city = models.ForeignKey(cities, on_delete= models.CASCADE,related_name='project_city',default=1,blank=True,null=False)
    describe = models.CharField(max_length=800)

    def __str__(self):
        return str(self.name)
    
    class Meta:
        ordering = ['-short_name']



class PhoneBook(models.Model):
    
    first_name = models.CharField(max_length=200,null=False)
    last_name = models.CharField(max_length=200,null=False)
    phone = PhoneNumberField(null=False, blank=False, unique=True)
    description = models.CharField(max_length=3000,null=True,blank=True)
    project = models.ForeignKey(Projects, on_delete= models.CASCADE,related_name='project',default=1,blank=True,null=True)
    position = models.CharField(max_length=3000)

    def __str__(self):
        return str(self.first_name)
    
    class Meta:
        ordering = ['-first_name']







class mode_raw_materials(models.Model):

    name =  models.CharField(max_length=200)

    def __str__(self):
        return str(self.name)
    
    class Meta:
        ordering = ['-name']


class mother_material(models.Model):


    name = models.CharField(max_length=200)
    describe = models.CharField(max_length=800)
    image = models.ImageField(upload_to='mother_material_image/', blank=True, null=True)  # Added field for image

    mode = models.ForeignKey(mode_raw_materials,default=None, on_delete= models.CASCADE,related_name='mode_raw_materials_mother_material',blank=True,null=True)

    def __str__(self):
        return str(self.name)
    
    class Meta:
        ordering = ['describe']



    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image:
            img_path = self.image.path
            img = Image.open(img_path)

            # اگر تصویر حالت RGBA یا P دارد به RGB تبدیل کن (برای JPEG)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            # تغییر اندازه
            img.thumbnail((800, 800), RESAMPLING)

            # نام فایل فعلی را به jpg تغییر می‌دهیم
            base, ext = os.path.splitext(img_path)
            new_path = base + ".jpg"

            # ذخیره با کیفیت پایین‌تر (مثلاً 85%)
            img.save(new_path, format='JPEG', quality=85)

            # حذف فایل قدیمی (مثلاً PNG)
            if new_path != img_path and os.path.exists(img_path):
                os.remove(img_path)

            # آدرس جدید تصویر را در فیلد image ذخیره کن
            self.image.name = os.path.relpath(new_path, start='media')
            super().save(update_fields=['image'])  # فقط image را به‌روز کن




class raw_material(models.Model):

    name = models.CharField(max_length=200)
    describe = models.CharField(max_length=800)
    unit = models.CharField(max_length=200)
    image = models.ImageField(upload_to='raw_material_image/', blank=True, null=True)  # Added field for image


    mother = models.ForeignKey(mother_material, on_delete= models.CASCADE,related_name='mother_material',blank=True,null=True)
    mode = models.ForeignKey(mode_raw_materials,default=None, on_delete= models.CASCADE,related_name='mode_raw_materials',blank=True,null=True)


    # اضافه کردن دسته‌بندی
    category = models.ForeignKey(
        MaterialCategory, on_delete=models.CASCADE,
        related_name="materials", blank=True, null=True
    )


    def __str__(self):
        return str(self.name)
    
    class Meta:
        ordering = ['describe']




    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image:
            img_path = self.image.path
            img = Image.open(img_path)

            # اگر تصویر حالت RGBA یا P دارد به RGB تبدیل کن (برای JPEG)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            # تغییر اندازه
            img.thumbnail((800, 800), RESAMPLING)

            # نام فایل فعلی را به jpg تغییر می‌دهیم
            base, ext = os.path.splitext(img_path)
            new_path = base + ".jpg"

            # ذخیره با کیفیت پایین‌تر (مثلاً 85%)
            img.save(new_path, format='JPEG', quality=85)

            # حذف فایل قدیمی (مثلاً PNG)
            if new_path != img_path and os.path.exists(img_path):
                os.remove(img_path)

            # آدرس جدید تصویر را در فیلد image ذخیره کن
            self.image.name = os.path.relpath(new_path, start='media')
            super().save(update_fields=['image'])  # فقط image را به‌روز کن



class create_order(models.Model):


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete= models.CASCADE,related_name='user_create_order',blank=True,null=True)



    content = HTMLField()

    night_order = models.CharField(max_length=20000,blank=True,null=True)

    

    def __str__(self):
        return str(self.created_at)
    
    class Meta:
        ordering = ['-created_at']
    

class SnappFoodList(models.Model):


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    city = models.ForeignKey(cities, on_delete= models.CASCADE,related_name='city_name',blank=True,null=True)
    name = models.CharField(max_length=200)
    link = models.CharField(max_length=20000)


    def __str__(self):
        return str(self.name)
    
    class Meta:
        ordering = ['-name']





class mother_food(models.Model):


    name = models.CharField(max_length=200)
    # describe = models.CharField(max_length=800)
    def __str__(self):
        return str(self.name)
    
    class Meta:
        ordering = ['-name']




class FoodRawMaterial(models.Model):
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    mother = models.ForeignKey(mother_food, on_delete= models.CASCADE,related_name='mother_food_id',blank=True,null=True)
    name = models.CharField(max_length=200)
    data = models.JSONField(blank=True,null=True)
    price = models.IntegerField(default=0,blank=True,null=True)
    image = models.ImageField(upload_to='food_images/', blank=True, null=True)  # Added field for image
    details = models.CharField(max_length=2000,default='',blank=True,null=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0, blank=True, null=True)  # Discount percentage
    priority = models.IntegerField(default=0)  # New field for priority


    def __str__(self):
        return str(self.name)

    def discounted_price(self):
        """
        Calculates the price after applying the discount.
        If discount is set to 0, returns the original price.
        """
        if self.discount > 0:
            discount_amount = (self.discount / 100) * self.price
            return self.price - discount_amount
        return self.price

    class Meta:
        ordering = ['-name']




class Warehouse(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True, null=True)
    capacity = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)  # ظرفیت انبار



    def __str__(self):
        return self.name
    
    



class InputReceipt(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)  # تاریخ ثبت فاکتور
    updated_at = models.DateTimeField(auto_now=True)  # تاریخ آخرین ویرایش
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='input_receipts')  # انبار مربوطه
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_input_receipts', blank=True, null=True)  # کاربری که این فاکتور را ثبت کرده است
    description = models.TextField(blank=True, null=True)  # توضیحات فاکتور

    def __str__(self):
        return f"Receipt {self.id} - {self.created_at.strftime('%Y-%m-%d')}"

    class Meta:
        ordering = ['-created_at']










class Inventory(models.Model):
    inventory_raw_material = models.ForeignKey(raw_material, on_delete=models.CASCADE, related_name='inventory')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='inventories', default=1)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0)  # مقدار پیش‌فرض برای quantity
    last_updated = models.DateTimeField(default=timezone.now)
    receipt_Number = models.IntegerField( null=True,blank=True, default=0)


    def add_stock(self, amount,user,receipt_number):
        """افزودن کالا به انبار و ایجاد لاگ به‌طور خودکار"""
        try:
            self.quantity += amount
            self.last_updated = timezone.now()
            self.receipt_Number = receipt_number  # ذخیره شماره فیش
            self.save()
            InventoryLog.objects.create(inventory=self, change_type='ADD', amount=amount,user=user,receipt_Number = self.receipt_Number)
            return True , 'مقادیر مورد نظر با موفقیت اضافه گردید'
        except:
            return False, 'خطا در افزودن در دیتابیس'
    def remove_stock(self, amount,user,buyer=None):
        """برداشتن کالا از انبار و ایجاد لاگ به‌طور خودکار"""
        if self.quantity >= amount:
            self.quantity -= amount
            self.last_updated = timezone.now()
            self.receipt_Number = -123  # ذخیره شماره فیش
            self.save()
            InventoryLog.objects.create(inventory=self, change_type='REMOVE', amount=amount,user=user,receipt_Number = self.receipt_Number,buyer=buyer)
            return True , 'مقادیر مورد نظر با موفقیت حذف گردید'
        else:
            # raise ValueError("موجودی کافی نیست.")
            return False , 'موجودی کافی نیست'
    

    def coop_remove(self,coop,amount,user:Profile,buyer=None):


        object_add = InventoryLog.objects.filter(change_type='ADD', coop=coop)
        object_remove = InventoryLog.objects.filter(change_type='REMOVE', coop=coop)
        if object_add.exists() and not object_remove.exists():
            InventoryLog.objects.create(inventory=self, change_type='REMOVE',coop=coop, amount=amount,user=user,receipt_Number = '1',buyer=buyer)


            

    def __str__(self):
        return f"{self.inventory_raw_material.name} - {self.quantity} in {self.warehouse.name}"


class Nationality(models.Model):
    name = models.CharField(max_length=100, verbose_name='نام ملیت')

    def __str__(self):
        return self.name



class Nationality(models.Model):
    name = models.CharField(max_length=100, verbose_name='نام ملیت')

    def __str__(self):
        return self.name



class IntroductionMethod(models.Model):
    title = models.CharField(max_length=100, verbose_name="عنوان نحوه آشنایی")

    def __str__(self):
        return self.title


class BuyerCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name='نام دسته‌بندی')
    color = models.CharField(max_length=10, default='#cccccc')  # مثال: '#FF0000'
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')

    def __str__(self):
        return self.name

class Buyer(models.Model):

    GENDER_CHOICES = [
        ('male', 'مرد'),
        ('female', 'زن'),
        ('unknown', 'اطلاع ندارم'),
    ]

    # user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100, verbose_name='نام ')
    last_name = models.CharField(max_length=100, verbose_name='نام نام خانوادگی', null=True, blank=True)
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        default='unknown',
        verbose_name='جنسیت'
    )

    phone_number = models.CharField(max_length=20, verbose_name='شماره تماس')

    introduction_method = models.ForeignKey(
        IntroductionMethod,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="نحوه آشنایی"
    )

    nationality = models.ForeignKey(Nationality, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='ملیت')
    national_code = models.CharField(max_length=10, verbose_name='کد ملی')
    province = models.CharField(max_length=50, verbose_name='استان', blank=True, null=True)
    city = models.CharField(max_length=50, verbose_name='شهر', blank=True, null=True)
    nation = models.CharField(max_length=50, verbose_name='شهر', blank=True, null=True)
    address = models.TextField(verbose_name='آدرس', blank=True, null=True)

    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="کاربر ثبت‌کننده"
    )


    details = models.TextField(verbose_name='توضیحات تکمیلی', blank=True, null=True)

    created_date = models.DateTimeField(default=timezone.now,null=True,blank=True)

    categories = models.ManyToManyField(
        BuyerCategory,
        blank=True,
        verbose_name='دسته‌بندی‌های خریدار'
    )


    is_active = models.BooleanField(default=True)


    def __str__(self):
        return f"{self.first_name} - {self.last_name}"
    


class BuyerActivity(models.Model):
    ACTIVITY_TYPE_CHOICES = [
        ('call', 'تماس تلفنی'),
        ('meeting', 'جلسه'),
        ('message', 'پیام'),
        ('email', 'ایمیل'),
        ('whatsapp', 'واتساپ'),
        ('note', 'یادداشت'),
        # ('update', 'به‌روزرسانی اطلاعات'),
        ('factors', 'فاکتور ها و خرید'),
    ]

    ACTIVITY_TYPE_ICONS = {
    'call': 'fa-solid fa-phone',
    'meeting': 'fa-solid fa-users',
    'message': 'fa-solid fa-comment',
    'email': 'fa-solid fa-envelope',
    'whatsapp': 'fa-brands fa-whatsapp',
    'note': 'fa-solid fa-sticky-note',
    'factors': 'fa-solid fa-file-invoice',
    }

    

    buyer = models.ForeignKey(
        Buyer,
        on_delete=models.CASCADE,
        related_name='activities',
        verbose_name="خریدار"
    )
    activity_type = models.CharField(
        max_length=20,
        choices=ACTIVITY_TYPE_CHOICES,
        verbose_name="نوع فعالیت"
    )
    title = models.CharField(max_length=255, verbose_name="عنوان فعالیت")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="کاربر ثبت‌کننده"
    )
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")
    next_followup = models.DateTimeField(null=True, blank=True, verbose_name="تاریخ پیگیری بعدی")


    logo = models.ImageField(
        upload_to='activity_logos/',
        null=True,
        blank=True,
        verbose_name='لوگو فعالیت'
    )

    

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "فعالیت خریدار"
        verbose_name_plural = "فعالیت‌های خریدار"

    def __str__(self):
        return f"{self.get_activity_type_display()} برای {self.buyer.first_name} {self.buyer.last_name} - {self.title}"

    @classmethod
    def get_activity_type_display_by_index(cls, index_key):
        """Return label for a given index_key (e.g., 'call')"""
        return dict(cls.ACTIVITY_TYPE_CHOICES).get(index_key, 'نامشخص')
    
    @classmethod
    def get_activity_type_labels(cls):
        return [label for _, label in cls.ACTIVITY_TYPE_CHOICES]
        
    @classmethod
    def get_activity_type_label_icon_list(cls):
        return [
            {
                'value': key,
                'label': label,
                'icon': cls.ACTIVITY_TYPE_ICONS.get(key, 'fa-solid fa-question')
            }
            for key, label in cls.ACTIVITY_TYPE_CHOICES
        ]
    
    def convert_persian2rnglish(cls):
        dict((fa, en) for en, fa in BuyerActivity.ACTIVITY_TYPE_CHOICES)

class BuyerAttribute(models.Model):
    FIELD_TYPES = [
        ('text', 'متن'),
        ('number', 'عدد'),
        ('date', 'تاریخ'),
        ('price', 'قیمت'),
        ('image', 'تصویر'),
    ]

    label = models.CharField(max_length=255, verbose_name='عنوان ویژگی')
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES, verbose_name='نوع فیلد')
    required = models.BooleanField(default=False, verbose_name='ضروری است')

    def __str__(self):
        return self.label
    

class BuyerAttributeValue(models.Model):
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, related_name='attributes')
    attribute = models.ForeignKey(BuyerAttribute, on_delete=models.CASCADE)
    value = models.TextField(blank=True, null=True, verbose_name='مقدار ویژگی')
    image = models.ImageField(upload_to='buyer_attrs/', blank=True, null=True, verbose_name='تصویر')

    def get_display_value(self):
        if self.attribute.field_type == 'image':
            return self.image.url if self.image else ''
        return self.value

    def __str__(self):
        return f"{self.buyer} - {self.attribute.label}"







class InventoryLog(models.Model):



    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name='logs')
    change_type = models.CharField(max_length=10, choices=(('ADD', 'افزودن'), ('REMOVE', 'برداشتن')))
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(Profile, on_delete= models.CASCADE,related_name='user_inventory_log',blank=True,null=True,default=1)
    buyer = models.ForeignKey(Buyer, on_delete=models.SET_NULL, null=True, blank=True)
   
    receipt_Number = models.IntegerField( null=True,blank=True, default=0)



    
    def jalali_date(self):
        return JalaliDatetime(self.date).strftime('%Y/%m/%d %H:%M:%S')

    def __str__(self):
        return f"{self.inventory.inventory_raw_material.name} - {self.change_type} - {self.amount} in {self.inventory.warehouse.name}"






class RestaurantBranch(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True, null=True)
    capacity = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)  # ظرفیت انبار



    def __str__(self):
        return self.name







class NightOrderRemainder(models.Model):
    order = models.ForeignKey(create_order, on_delete=models.CASCADE, related_name='night_order_remainders')
    restaurant = models.ForeignKey(RestaurantBranch , on_delete=models.CASCADE, related_name='night_order_remainders')
    remainder_night_order = models.CharField(max_length=20000,blank=True,null=True)


    def __str__(self):
        return f"Order: {self.order} - Restaurant: {self.restaurant.name}"  # or self.restaurant.__str__()

    class Meta:
        ordering = ['order']






# Location model to store location details
class Location(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=14, decimal_places=9)
    longitude = models.DecimalField(max_digits=14, decimal_places=9)
    radius_meters = models.FloatField()  # Radius around these locations within which users are allowed


    def __str__(self):
        return self.name





class AllowedLocation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    locations = models.ManyToManyField(Location, related_name='allowed_locations')

    def __str__(self):
        return f"Allowed locations for {self.user.username}"


class EntryExitLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='Entry_log')
    timestamp = models.DateTimeField(default=timezone.now)  # This will store both entry and exit times
    is_entry = models.BooleanField(default=True)  # True for entry, False for exit

    location = models.ForeignKey(Location,on_delete=models.CASCADE, related_name='Entry_locations')



    def jalali_date(self):
        return JalaliDatetime(self.timestamp).strftime('%Y/%m/%d') 

    


    def __str__(self):
        event_type = 'Entry' if self.is_entry else 'Exit'
        return f"{self.user.username} - {event_type} at {self.timestamp}"








class CapturedImage(models.Model):
    image = models.ImageField(upload_to="captured_images/")
    created_at = models.DateTimeField(auto_now_add=True)
    receipt_number = models.CharField(max_length=200)

    def __str__(self):
        return f"Image {self.id} - {self.image.url}"
    




class MaterialComposition(models.Model):
    main_material = models.ForeignKey(raw_material, on_delete=models.CASCADE, related_name='components')  # ماده اصلی
    ingredient = models.ForeignKey(raw_material, on_delete=models.CASCADE, related_name='used_in')  # ماده تشکیل‌دهنده
    ratio = models.FloatField(default=1.0)  # مقدار مصرفی در هر واحد از ماده اصلی
    has_discard = models.BooleanField(default=False)  # آیا این ماده دارای ضایعات است؟

    def __str__(self):
        discard_status = " (Discarded)" if self.has_discard else ""
        return f"{self.ingredient.name} in {self.main_material.name}{discard_status}"




class ProductionLog(models.Model):
    product = models.ForeignKey(MaterialComposition, on_delete=models.CASCADE, related_name='production_logs')  # محصولی که تولید شده
    produced_quantity = models.DecimalField(max_digits=10, decimal_places=2)  # تعداد واحدهای تولید شده
    discarded_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # مقدار ضایعات
    date = models.DateTimeField(default=timezone.now)  # تاریخ تولید
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='production_logs')  # کاربری که این عملیات را ثبت کرده است

    def __str__(self):
        return f"{self.product.name} - تولید: {self.produced_quantity} - ضایعات: {self.discarded_quantity}"



class RemainingMaterialsUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    used_at = models.DateTimeField(default=timezone.now)  # تاریخ تولید

    def __str__(self):
        return f"{self.user.username} - {self.used_at}"










# اختصاص نقش به کاربر
class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="کاربر")
    role = models.ForeignKey(jobs, on_delete=models.CASCADE, verbose_name="نقش")

    def __str__(self):
        return f"{self.user.username} - {self.role.name}"
    


