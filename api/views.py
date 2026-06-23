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





import os
import json
import wave
import tempfile
import subprocess

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from vosk import Model, KaldiRecognizer

# فقط یکبار لود شود
VOSK_MODEL_PATH = os.path.join('models', 'vosk-model-fa-0.42')
if os.path.exists(VOSK_MODEL_PATH):
    model = Model(VOSK_MODEL_PATH)

# 🎯 Keyword boosting مخصوص فست فود
# 1. تعریف کلمات کلیدی به صورت رشته JSON
FASTFOOD_KEYWORDS = json.dumps([
    "برگر",
    "پیتزا", 
    "مرغ",
    "سوخاری",
    "سیب زمینی",
    "سالاد",
    "نوشابه",
    "سفارش",
    "ثبت",
    "طلایی",
    "سکه"
])


def convert_audio_fast(input_path, output_path):
    """
    تبدیل سریع با ffmpeg (خیلی سریع‌تر از librosa)
    """
    command = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-ar", "16000",
        "-ac", "1",
        "-f", "wav",
        output_path
    ]
    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


@csrf_exempt
@require_http_methods(["POST"])
def speech_to_text(request):

    if 'audio' not in request.FILES:
        return JsonResponse({'success': False, 'message': 'فایل صوتی ارسال نشده'}, status=400)

    audio_file = request.FILES['audio']

    if audio_file.size > 20 * 1024 * 1024:
        return JsonResponse({'success': False, 'message': 'فایل خیلی بزرگ است'}, status=400)

    file_ext = os.path.splitext(audio_file.name)[1].lower()
    allowed_extensions = ['.wav', '.mp3', '.webm', '.ogg', '.m4a']

    if file_ext not in allowed_extensions:
        return JsonResponse({'success': False, 'message': 'فرمت پشتیبانی نمی‌شود'}, status=400)

    tmp_input = None
    tmp_output = None

    try:
        # ذخیره سریع فایل
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as f:
            for chunk in audio_file.chunks():
                f.write(chunk)
            tmp_input = f.name

        tmp_output = tmp_input.rsplit('.', 1)[0] + "_16k.wav"

        # تبدیل سریع
        convert_audio_fast(tmp_input, tmp_output)

        wf = wave.open(tmp_output, "rb")

        # چک فرمت
        if wf.getnchannels() != 1 or wf.getframerate() != 16000:
            return JsonResponse({'success': False, 'message': 'فرمت صوتی نامعتبر'}, status=400)

        rec = KaldiRecognizer(model, wf.getframerate())

        # 🎯 Boost keywords (خیلی مهم برای فست فود)
        rec.SetWords(True)
        rec.SetGrammar(FASTFOOD_KEYWORDS)

        result_text = []

        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break

            if rec.AcceptWaveform(data):
                res = json.loads(rec.Result())
                if res.get("text"):
                    result_text.append(res["text"])

        final = json.loads(rec.FinalResult())
        if final.get("text"):
            result_text.append(final["text"])

        text = " ".join(result_text).strip()
        text=  'asdawd'
        return JsonResponse({
            'success': True,
            'text': text,
            'message': 'تبدیل صدا با موفقیت انجام شد',
            'record_id': None
        })

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

    # finally:
    #     # پاکسازی امن
    #     for f in [tmp_input, tmp_output]:
    #         if f and os.path.exists(f):
    #             os.remove(f)






# views.py
import json
import openai
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import tempfile
import wave
import io
from pydub import AudioSegment
from datetime import datetime

# ===== Configuration =====
# Option 1: Using OpenAI API (Recommended)
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', 'your-openai-api-key-here')
openai.api_key = OPENAI_API_KEY

# Option 2: Using Google Speech Recognition (Free, offline alternative)
# No API key needed for basic speech recognition

def get_chat_response(user_message, conversation_history=None):
    """
    Get AI response for chat using OpenAI API
    """
    if not OPENAI_API_KEY or OPENAI_API_KEY == 'your-openai-api-key-here':
        # Fallback: Simple rule-based response
        return get_fallback_response(user_message)
    
    try:
        # Prepare messages for OpenAI
        messages = [
            {
                "role": "system",
                "content": """تو دستیار هوشمند سفارش‌گیری رستوران فست‌فود «سکه طلا» هستی.
                وظیفه تو:
                1. کمک به مشتری برای ثبت سفارش
                2. استخراج آیتم‌های غذایی و تعداد از مکالمه
                3. پاسخ‌های دوستانه و حرفه‌ای به فارسی
                4. وقتی سفارش کامل شد، خلاصه سفارش را نمایش بده
                
                منوی رستوران:
                - برگر طلایی: ۱۸۹,۰۰۰ تومان
                - مرغ سوخاری سکه‌ای: ۱۶۵,۰۰۰ تومان
                - پیتزا سلطنتی: ۲۴۹,۰۰۰ تومان
                - سیب‌زمینی طلایی: ۶۹,۰۰۰ تومان
                - نوشابه: ۲۵,۰۰۰ تومان
                - سالاد فصل: ۴۵,۰۰۰ تومان
                
                قوانین:
                - همیشه به فارسی پاسخ بده
                - اگر سفارش کامل شد، عبارت "ORDER_COMPLETE" را در انتهای پاسخ قرار بده
                - خلاصه سفارش را با فرمت: "خلاصه سفارش: [آیتم‌ها]" نمایش بده
                - اگر اطلاعات کامل نیست، سوال بپرس
                - مودب و خوش‌برخورد باش"""
            }
        ]
        
        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add user message
        messages.append({"role": "user", "content": user_message})
        
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=300,
            temperature=0.7
        )
        
        reply = response.choices[0].message.content.strip()
        return parse_reply(reply)
        
    except Exception as e:
        print(f"OpenAI error: {e}")
        return get_fallback_response(user_message)

def parse_reply(reply):
    """
    Parse the AI reply to extract order completion status
    """
    is_complete = False
    order_summary = None
    
    # Check if ORDER_COMPLETE is in the reply
    if "ORDER_COMPLETE" in reply:
        is_complete = True
        reply = reply.replace("ORDER_COMPLETE", "").strip()
    
    # Extract order summary if present
    if "خلاصه سفارش:" in reply:
        parts = reply.split("خلاصه سفارش:")
        if len(parts) > 1:
            order_summary = parts[1].strip()
            reply = parts[0].strip()
    
    return {
        'reply': reply,
        'order_complete': is_complete,
        'order_summary': order_summary
    }

def get_fallback_response(user_message):
    """
    Simple rule-based fallback response when OpenAI is not available
    """
    user_message = user_message.lower()
    
    # Check for common keywords
    if any(word in user_message for word in ['برگر', 'همبرگر']):
        return {
            'reply': 'برگر طلایی با پنیر چدار و سس مخصوص، ۱۸۹,۰۰۰ تومان. \nآیا می‌خواهید سفارش دهید؟',
            'order_complete': False,
            'order_summary': None
        }
    elif any(word in user_message for word in ['مرغ', 'سوخاری']):
        return {
            'reply': 'مرغ سوخاری سکه‌ای با سوخاری ترد، ۱۶۵,۰۰۰ تومان. \nآیا می‌خواهید سفارش دهید؟',
            'order_complete': False,
            'order_summary': None
        }
    elif any(word in user_message for word in ['پیتزا', 'پپرونی']):
        return {
            'reply': 'پیتزا سلطنتی با پپرونی و قارچ تازه، ۲۴۹,۰۰۰ تومان. \nآیا می‌خواهید سفارش دهید؟',
            'order_complete': False,
            'order_summary': None
        }
    elif any(word in user_message for word in ['سفارش', 'ثبت', 'بله', 'آره']):
        return {
            'reply': '✅ سفارش شما دریافت شد!\nخلاصه سفارش: برگر طلایی - ۱ عدد\n\nORDER_COMPLETE',
            'order_complete': True,
            'order_summary': 'برگر طلایی - ۱ عدد'
        }
    else:
        return {
            'reply': '👋 سلام! من دستیار سکه طلا هستم.\nچطور می‌توانم کمک کنم؟ می‌توانید از منو انتخاب کنید یا سفارش خود را بگویید.',
            'order_complete': False,
            'order_summary': None
        }

# ===== Django Views =====

@csrf_exempt
@require_http_methods(["POST"])
def chat_api(request):
    """
    Main chat API endpoint
    """
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return JsonResponse({
                'success': False,
                'message': 'پیام ارسال نشده است'
            }, status=400)
        
        # Get conversation history from session or request
        conversation_history = data.get('history', [])
        
        # Get AI response
        response = get_chat_response(user_message, conversation_history)
        
        # Prepare response
        result = {
            'success': True,
            'reply': response['reply'],
            'order_complete': response.get('order_complete', False),
            'order_summary': response.get('order_summary')
        }
        
        return JsonResponse(result)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'فرمت داده‌ها صحیح نیست'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'خطا در پردازش پیام: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def confirm_order(request):
    """
    Confirm and finalize the order
    """
    try:
        data = json.loads(request.body)
        order_summary = data.get('order', '').strip()
        
        if not order_summary:
            return JsonResponse({
                'success': False,
                'message': 'خلاصه سفارش ارسال نشده است'
            }, status=400)
        
        # Here you can save the order to database
        # Order.objects.create(
        #     user=request.user if request.user.is_authenticated else None,
        #     order_summary=order_summary,
        #     status='pending',
        #     created_at=datetime.now()
        # )
        
        return JsonResponse({
            'success': True,
            'message': 'سفارش با موفقیت ثبت شد',
            'order_id': 'ORD-' + str(int(datetime.now().timestamp()))
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'فرمت داده‌ها صحیح نیست'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'خطا در ثبت سفارش: {str(e)}'
        }, status=500)
