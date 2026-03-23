


from otp_manager.models import OTPVar_Enum, SMS_Recievers, SMS_Template, SMSServiceTemplate_Enum
from otp_manager.service import send_sms


def send_night_order_sms(request,status,number_type):
    translate = {}
    for item in number_type.keys():
        if 'دو نفره' in item:
            translate.update({'DOUBLE':number_type[item]})
        elif 'تک نفره' in item:
            translate.update({'SINGLE':number_type[item]})
        elif 'همبرگر' in item:
            translate.update({'HAMBER':number_type[item]})
        else:
            print('Not Found Item')

    sms_template = SMS_Template.objects.filter(name =SMSServiceTemplate_Enum.NIGHTORDER )
    if sms_template.exists():
        sms_template = sms_template.first()
        sms_recievers = SMS_Recievers.objects.filter(template = sms_template)
        for sms_rec in sms_recievers:
            phone = sms_rec.persons.phone
            f_name = sms_rec.persons.f_name
            name = 'نامشخص'
            try:
                name = request.user.profile.first_name
            except:
                pass
            ret = send_sms(sms_template,phone_number=phone\
                           ,vars={OTPVar_Enum.NAME:f_name,OTPVar_Enum.CLOSE:name\
                                  ,OTPVar_Enum.DOUBLE:translate.get('DOUBLE','نامشخص'),\
                                  OTPVar_Enum.USER:name,\
                                  OTPVar_Enum.SINGLE:translate.get('SINGLE','نامشخص'),\
                                  OTPVar_Enum.HAMBER:translate.get('HAMBER','نامشخص'),\
                                  OTPVar_Enum.ORDERID:status.id,\
                                  })








