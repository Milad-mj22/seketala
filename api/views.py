from django.utils import timezone
import re
from django.shortcuts import render
# Create your views here.
# api/views.py
from django.http import JsonResponse
from .signals import message_signal
from .utils import get_account_no


def home(request):
    return JsonResponse({"message": "Welcome to the API!"})




from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import SMS, BankAccount
import json

@csrf_exempt
def receive_sms(request):
    sender = request.GET.get("sender", "")
    message = request.GET.get("message", "")
    if sender=='Unknown':
        sender = request.GET.get("from", "Unknown")
    if message=='':
        message = request.GET.get("text", "")

    if message:
        SMS.objects.create(sender=sender, message=message)
        # Replace the number that comes after "مانده"
        message = clean_message(message=message)
        content = {'sender':sender,'message':message}
        message_signal.send(sender=None, values = content)

        return JsonResponse({"status": "success"}, status=201)
    return JsonResponse({"status": "error", "message": "Message is empty"}, status=400)




def sms_page(request):
    return render(request, "sms_show.html")



def clean_message(message):
    try:
        cleaned_message = re.sub(r"مانده\s*:\s*[\d,]+", "", message)
    except:
        cleaned_message = message
    return cleaned_message

def get_last_sms(request, count):
    try:
        sms_list = SMS.objects.order_by('-received_at')[:count]
        data = [
            {
                'sender': sms.sender,
                'message': clean_message(sms.message),
                'received_at': sms.received_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
            for sms in sms_list
        ]
        return JsonResponse({'messages': data})
    except Exception as e:
        print(f"Error fetching messages: {e}")
        return JsonResponse({'error': 'Error fetching messages'}, status=500)
    


def get_total_deposit(request):
    now = timezone.now()
    # 🟢 مقدار ساعت را برای دیباگ به‌صورت دستی تغییر دهید


    # Determine the start of the custom day (2:00 AM today)
    if now.hour < 2:
        start_time = (now - timezone.timedelta(days=1)).replace(hour=16, minute=0, second=0, microsecond=0)
    else:
        start_time = now.replace(hour=16, minute=0, second=0, microsecond=0)
    
    # End time is 24 hours after the start time
    end_time = start_time + timezone.timedelta(days=1)

    # Filter SMS records in the range from 2 AM today to 2 AM the next day
    today_sms = SMS.objects.filter(received_at__gte=start_time, received_at__lt=end_time)

    total_sum = 0
    for sms in today_sms:
        match = None
        if 'واریز' in sms.message :
            match = re.search(r'واریز([\d,]+)', sms.message)
        elif 'انتقال' in sms.message:
            match = re.search(r'انتقال:([\d,]+)', sms.message)

        if match is not None:
            amount = int(match.group(1).replace(',', ''))
            print(amount)
            total_sum += amount

    return JsonResponse({"success": True, "total": total_sum})



def account_list(request):
    accounts = BankAccount.objects.all()
    selected_account = None
    total_deposit = 0
    sms_count = 0
    start_date = None
    end_date = None

    if request.method == "GET" and "account" in request.GET:
        account_number = request.GET.get("account")
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")

        try:
            selected_account = BankAccount.objects.get(account_number=account_number)
            
            # فیلتر پیامک‌ها بر اساس شماره حساب و بازه زمانی
            filtered_sms = SMS.objects.filter(
                message__contains=f"حساب{selected_account.account_number}",
                received_at__date__gte=start_date,
                received_at__date__lte=end_date
            )

            # شمارش تعداد پیامک‌های واریز
            sms_count = filtered_sms.count()

            # محاسبه مجموع واریزها
            for sms in filtered_sms:
                match = re.search(r'واریز([\d,]+)', sms.message)
                if match:
                    amount = int(match.group(1).replace(',', ''))
                    total_deposit += amount

        except BankAccount.DoesNotExist:
            selected_account = None

    return render(request, "account_list.html", {
        "accounts": accounts,
        "selected_account": selected_account,
        "total_deposit": total_deposit,
        "sms_count": sms_count,
        "start_date": start_date,
        "end_date": end_date,
    })











from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import os


@csrf_exempt
@require_http_methods(["POST"])
def speech_to_text(request):
    """
    دریافت فایل صوتی از فرانت‌اند و برگرداندن متن تبدیل شده
    
    ساختار پاسخ موفق:
    {
        'success': True,
        'text': 'متن تبدیل شده',
        'record_id': 123  # اختیاری
    }
    
    ساختار پاسخ ناموفق:
    {
        'success': False,
        'message': 'پیام خطا'
    }
    """
    # try:
        # 1. بررسی وجود فایل
    if 'audio' not in request.FILES:
        return JsonResponse({
            'success': False,
            'message': 'فایل صوتی ارسال نشده است'
        }, status=400)
    
    audio_file = request.FILES['audio']
    
    # 2. بررسی حجم فایل (حداکثر 25MB)
    if audio_file.size > 25 * 1024 * 1024:
        return JsonResponse({
            'success': False,
            'message': 'حجم فایل بیشتر از 25MB است'
        }, status=400)
    
    # 3. بررسی فرمت فایل
    allowed_extensions = ['.wav', '.mp3', '.webm', '.ogg', '.flac', '.aac', '.m4a']
    file_ext = os.path.splitext(audio_file.name)[1].lower()
    if file_ext not in allowed_extensions:
        return JsonResponse({
            'success': False,
            'message': f'فرمت فایل {file_ext} پشتیبانی نمی‌شود'
        }, status=400)
    
    return JsonResponse({
        'success': True,
        'message': 'پیام موقت'
    }, status=400)