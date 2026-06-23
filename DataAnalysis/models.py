from django.db import models

# Create your models here.


class Sale(models.Model):
    factnum = models.CharField(max_length=1000, unique=True)
    dat = models.DateField()  # the date of sale
    total = models.DecimalField(max_digits=22, decimal_places=2)
    kname = models.CharField(max_length=1000)  # customer name
    tel = models.CharField(max_length=30)
    address = models.TextField()

    def __str__(self):
        return f"{self.kname} - {self.factnum}"



class Invoice(models.Model):
    unique_invoice_number =  models.IntegerField(default=-1)
    invoice_number = models.IntegerField()
    name = models.CharField(max_length=200,default='')
    nahveh = models.CharField(max_length=300,default='')
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField()
    
    
    discount = models.IntegerField(default=0)
    total_price = models.BigIntegerField()

    peyk = models.PositiveIntegerField(default=0)
    anaam = models.PositiveIntegerField(default=0)

    moshtarak = models.CharField(max_length=20,null=True,blank=True)
    serv = models.CharField(max_length=20,null=True,blank=True)
    pnum =models.CharField(max_length=20,null=True,blank=True)
    shomare_pos =models.CharField(max_length=20,null=True,blank=True)
    mablagh_pos = models.CharField(max_length=20,null=True,blank=True)
    hazine_peyk = models.CharField(max_length=20,null=True,blank=True)
    naghdi = models.CharField(max_length=20,null=True,blank=True)
    nonaghdi = models.CharField(max_length=20,null=True,blank=True)
    mandeh = models.CharField(max_length=20,null=True,blank=True)




class InvoiceItem(models.Model):
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="items"
    )

    food_name = models.CharField(max_length=100)
    price = models.BigIntegerField()
    quantity = models.IntegerField()
    total = models.BigIntegerField()


class Payment(models.Model):

    class PaymentMethod(models.TextChoices):
        CASH = "cash", "Cash"
        CARD = "card", "Card"
        POS = "pos", 'Pos'
        ONLINE = "online", "Online"
        PEYK = "nesiye", "Nesiye"
        ANAAM = "anaam", 'Anaam'

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="payments"
    )

    method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices
    )

    amount = models.BigIntegerField()
    created_at = models.DateTimeField()
    
    
    
class SMSLog(models.Model):
    invoice_number = models.CharField(max_length=50, unique=True, verbose_name="شماره فاکتور")
    is_sent = models.BooleanField(default=False, verbose_name="آیا ارسال شده؟")
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ارسال")

    def __str__(self):
        return f"{self.invoice_number} - {'ارسال شده' if self.is_sent else 'ارسال نشده'}"


