import re


def get_account_no(sms_text):

    match = re.search(r'حساب(\d+)', sms_text)
    if match:
        account_number = match.group(1)  # شماره حساب
        # #print("شماره حساب:", account_number)
        return account_number
    else:
        # #print("شماره حساب یافت نشد.")
        return None