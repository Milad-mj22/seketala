

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('otp_manager', '0003_alter_sms_persons_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sms_template',
            name='name',
            field=models.CharField(choices=[('signup', 'ثبت نام'), ('login', 'ورود'), ('close_sandogh', 'بستن صندوق'), ('night_order', 'سفارش شب')], max_length=100, verbose_name='نوع قالب پیامک'),
        ),
    ]
