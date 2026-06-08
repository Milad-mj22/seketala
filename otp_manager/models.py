from django.db import models

# Create your models here.
from phonenumber_field.modelfields import PhoneNumberField


class SMSServiceTemplate_Enum(models.TextChoices):
    SIGNUP = "signup", "ثبت نام"
    AUTO_SIGNUP = "auto_signup", "ثبت نام اتوماتیک"
    LOGIN = "login", "ورود"
    CLOSESANDOGH = 'close_sandogh','بستن صندوق'
    NIGHTORDER = 'night_order','سفارش شب'
    PERSONEL_NIGHT_ORDER = 'personel_night_order','سفارش به نام پرسنل'

class SMSServiceName_Enum(models.TextChoices):
    SMS_IR = "SMS.IR", "SMS.IR"

class OTPVar_Enum(models.TextChoices):
    OTP_CODE = "CODE" , "کد یکبار مصرف"
    FIRST_NAME = "FIRST_NAME" , "نام"
    LAST_NAME = "LAST_NAME" , "نام خانوادگی"
    PHONE = "PHONE" , "شماره تماس"
    NAME = 'NAME','نام'
    VALUE = 'VALUE','مبلغ'
    CLOSE = 'CLOSE','بسته کننده'
    DOUBLE = 'DOUBLE','دوبل'
    SINGLE = 'SINGLE','دوبل'
    HAMBER = 'HAMBER','همبر'
    ORDERID = 'ORDERID','شماره سفارش'
    USER = 'USER','کاربر'
    DATE = 'DATE','تاریخ'
    AMOUNT = 'AMOUNT','مقدار'
    JOBNAME = 'JOBNAME','شغل'
    PRICE = 'PRICE','قیمت'


from django.db import models




class SMS_Service(models.Model):

    sms_panel = models.CharField(
        max_length=10,
        choices=SMSServiceName_Enum.choices
    )


    user_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="نام کاربری"
    )
    password = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="رمز عبور"
    )
    api_key = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="کلید API"
    )
    
    line_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="شماره خط ارسال"
    )

    class Meta:
        verbose_name = "سرویس پیامک"
        verbose_name_plural = "سرویس‌های پیامک"

    def __str__(self):
        return f"{self.sms_panel} - {self.user_name}"





class SMS_Template(models.Model):

    name = models.CharField(
        max_length=100,
        choices=SMSServiceTemplate_Enum.choices,
        verbose_name="نوع قالب پیامک"
    )

    service = models.ForeignKey(
        SMS_Service,
        on_delete=models.CASCADE,
        related_name="templates",
        verbose_name="سرویس پیامک"
    )

    template_id = models.CharField(
        max_length=200,
        verbose_name="شناسه قالب"
    )

    class Meta:
        verbose_name = "قالب پیامک"
        verbose_name_plural = "قالب‌های پیامک"

    def __str__(self):
        return f"{self.service} - {self.get_name_display()}"
    




class SMS_Persons(models.Model):
    f_name = models.CharField(
        max_length=200,
        verbose_name="نام"
    )
    l_name = models.CharField(
        max_length=200,
        verbose_name="نام خانوادگی"
    )

    phone = models.BigIntegerField(blank=False,null=False, unique=True,verbose_name='شماره تماس')


    def __str__(self):
        return f"{self.f_name} {self.l_name} - {self.phone}"
    

class SMS_Recievers(models.Model):


    template = models.ForeignKey(
        SMS_Template,
        on_delete=models.CASCADE,
        related_name="sms_template",
        verbose_name="قالب پیامک"
    )

    persons = models.ForeignKey(
        SMS_Persons,
        on_delete=models.CASCADE,
        related_name="sms_person",
        verbose_name="دریافت کننده"
    )