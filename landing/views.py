from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

def landing(request):
    return render(request, 'landing/landing.html')



import os
import json
import base64
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import openai
from pathlib import Path

# تنظیم OpenAI
openai.api_key = settings.OPENAI_API_KEY

@csrf_exempt  # فقط برای تست، در production از @csrf_protect استفاده کن
def voice_assistant(request):
    """
    دریافت متن از کاربر، ارسال به OpenAI، دریافت جواب،
    تبدیل به صدا با TTS و برگردوندن audio_url
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'فقط متد POST پشتیبانی میشه'}, status=405)

    try:
        data = json.loads(request.body)
        user_text = data.get('text', '').strip()

        if not user_text:
            return JsonResponse({'error': 'متن وارد نشده'}, status=400)

        # ===== 1. ارسال به OpenAI =====
        # شما می‌تونید از سیستم‌پرامپت مناسب برای رستوران استفاده کنید
        system_prompt = """
        شما یک دستیار هوشمند برای رستوران فست‌فود «سکه طلا» هستید.
        وظیفه شما کمک به مشتریان برای ثبت سفارش، پاسخ به سوالات درباره منو،
        قیمت‌ها و زمان تحویل است.
        منوی رستوران شامل:
        - برگر طلایی: ۲۵۰,۰۰۰ تومان
        - پیتزا مخصوص: ۳۸۰,۰۰۰ تومان
        - ساندویچ مرغ: ۱۹۰,۰۰۰ تومان
        - سیب‌زمینی ویژه: ۱۲۰,۰۰۰ تومان
        - نوشابه: ۳۰,۰۰۰ تومان
        
        زمان تحویل: زیر ۲۰ دقیقه
        آدرس: تهران، خیابان ولیعصر، پلاک ۴۵
        تلفن: ۰۲۱-۱۲۳۴۵۶۷۸
        
        لطفاً به فارسی و با لحن دوستانه پاسخ بده.
        اگر کاربر سفارش داد، لیست سفارش‌ها رو جمع‌بندی کن و قیمت کل رو محاسبه کن.
        """

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # یا "gpt-4"
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text}
            ],
            temperature=0.7,
            max_tokens=500
        )

        reply_text = response.choices[0].message.content

        # ===== 2. تبدیل متن به صدا با OpenAI TTS =====
        try:
            # OpenAI TTS (نسخه جدید)
            from openai import OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            
            speech_response = client.audio.speech.create(
                model="tts-1",
                voice="nova",  # گزینه‌های: alloy, echo, fable, onyx, nova, shimmer
                input=reply_text,
                speed=1.0
            )

            # ذخیره فایل صوتی
            audio_filename = f"voice_response_{hash(reply_text)}.mp3"
            audio_path = Path('media') / 'audio' / audio_filename
            audio_path.parent.mkdir(parents=True, exist_ok=True)
            
            # ذخیره فایل
            with open(audio_path, 'wb') as f:
                f.write(speech_response.content)
            
            audio_url = f"/media/audio/{audio_filename}"

        except Exception as tts_error:
            print(f"TTS Error: {tts_error}")
            audio_url = None

        # ===== 3. برگردوندن جواب =====
        return JsonResponse({
            'reply': reply_text,
            'audio_url': audio_url,
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON نامعتبر'}, status=400)
    except Exception as e:
        print(f"Error: {e}")
        return JsonResponse({'error': str(e)}, status=500)