from django.shortcuts import render

# Create your views here.

def contact_us(request):

    return render(request,'contactus/first.html')



from django.http import JsonResponse
from .models import BankCard, Feedback

def submit_feedback(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            rating = request.POST.get('rating')
            message = request.POST.get('message')

            # Simple validation
            if not all([name, rating, message]):
                return JsonResponse({'status': 'error', 'message': 'لطفاً تمام فیلدها را پر کنید.'}, status=400)

            # Save to database
            Feedback.objects.create(
                name=name,
                rating=rating,
                message=message
            )

            return JsonResponse({'status': 'success', 'message': 'ممنون از ثبت نظر شما'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'خطایی رخ داد.'}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

    



def bank_card_list(request):
    cards = BankCard.objects.select_related('bank').all().order_by('-is_active', 'bank__name')
    active_card = BankCard.objects.filter(is_active=True).select_related('bank').first()

    return render(request, 'bank_cards/card_list.html', {
        'cards': cards,
        'active_card': active_card,
    })
