


from otp_manager.models import OTPVar_Enum, SMS_Template, SMSServiceName_Enum
from sms_ir import SmsIr #pip install smsir-python

def send_sms(template_obj:SMS_Template,phone_number,vars):

    ret = False
    
    if template_obj.service.sms_panel == SMSServiceName_Enum.SMS_IR:
        ret = sms_ir(template_obj,phone_number,vars)

    return ret



def sms_ir(template_obj:SMS_Template,phone_number,vars):

    api_key = template_obj.service.api_key
    linenumber = template_obj.service.line_number
    template_id = template_obj.template_id

    parameters = []
    for key,value in vars.items():
        parms = {"name":key,"value":value}
        parameters.append(parms)



    sms_ir = SmsIr(api_key,linenumber,)
    ret = sms_ir.send_verify_code(phone_number,template_id,parameters,)
    return ret.ok


# api_key = "API_KEY"
# linenumber = "300790"
# number = "09135689040"
# message = "سلام"
# template_id = "859705"
# parameters = [
#     {"name": "CODE", "value": "1378"}
# ]
# sms_ir = SmsIr(api_key,linenumber,)
# # ret = sms_ir.send_sms(number,message,linenumber,)
# # #print(ret)
# a = sms_ir.get_line_numbers()
# #print(a.text)
# a = sms_ir.send_verify_code(number,template_id,parameters,)
# #print(a)