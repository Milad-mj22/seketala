import base64
from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
# Create your views here.
# myapp/views.py
from django.http import HttpResponse
from users.models import User
from .WhatsApp import collect_messages_from_all_chats, start_whatsapp_session
from multiprocessing import Process
from .task import collect_user_messages

def home(request):
    return HttpResponse("Hello from my app!")
def connect_whatsapp(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    # Do something with the user (e.g., create session, show QR, etc.)

    user_id = request.user.id
    is_logged_in, qr_image_path  = start_whatsapp_session(user_id)

    qr_image_path = image_to_base64(image_path=qr_image_path)

    return render(request, 'connectWA.html', {
        'is_logged_in': is_logged_in,
        'qr_image_base64': qr_image_path
    })


def image_to_base64(image_path):
    try:
        with open(image_path, "rb") as img_file:
            encoded_string = base64.b64encode(img_file.read()).decode('utf-8')
            return f"data:image/png;base64,{encoded_string}"
    except:
        return False
    



def WA_get_messages(request,user_id):
    user_id = request.user.id
    # messages = collect_messages_from_all_chats(user_id)


    # p = Process(target=collect_messages_from_all_chats, args=(user_id,))
    # p.start()

    collect_user_messages.delay(user_id)
    return HttpResponse("Stated read my app!")



    return HttpResponse("Hello from my app!")
    

