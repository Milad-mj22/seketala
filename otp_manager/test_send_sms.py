from sms_ir import SmsIr


api_key = "NFwDOyzDoUCVBxB2CSlO374WlXOAeaKGST1ubHFziSEcLbhf"
linenumber = "300790"

number = "09136563913"

message = "سلام"

template_id = "859705"
parameters = [
    {"name": "CODE", "value": "1378"},{"name": "CODE2", "value": "1379"},{"name": "awdE2", "value": "1380"},{"name": "CODE", "value": "111"}
]
sms_ir = SmsIr(api_key,linenumber,)

# ret = sms_ir.send_sms(number,message,linenumber,)
# #print(ret)

a = sms_ir.get_line_numbers()
#print(a.text)


a = sms_ir.send_verify_code(number,template_id,parameters,)

#print(a)