import json
from django.shortcuts import render
from django.db.models import Count
from django.contrib.auth.models import User
from django.utils.timezone import now, timedelta

from StoneFlow.models import PreInvoice
from users.models import BuyerActivity
# Create your views here.

def mian_dashboard(request):

    return render(request, 'dashboard.html')




def dashboard_employ_activity(request):
    # جمع کل فعالیت‌ها
    total_activities = BuyerActivity.objects.count()

    # تعداد هر نوع فعالیت
    activity_by_type = list(
        BuyerActivity.objects.values('activity_type').annotate(count=Count('id'))
    )
    # فعالیت بر اساس کاربر
    activity_by_user = list(BuyerActivity.objects.values('created_by__username').annotate(count=Count('id')))
    
    # کاربران فعال در هفت روز گذشته
    week_ago = now() - timedelta(days=7)
    active_users = BuyerActivity.objects.filter(timestamp__gte=week_ago).values('created_by__username').annotate(count=Count('id'))

    # کاربران بدون فعالیت (غیرفعال)
    all_users = set(User.objects.values_list('username', flat=True))
    active_usernames = set([item['created_by__username'] for item in active_users if item['created_by__username']])
    inactive_users = all_users - active_usernames


    top_activities = BuyerActivity.objects.values('title', 'activity_type').annotate(count=Count('id')).order_by('-count')[:5]


    return render(request, 'employ_partial.html', {
        'total_activities': total_activities,
        'activity_by_type': activity_by_type,
        'activity_by_user': activity_by_user,
        'active_users': active_users,
        'inactive_users': inactive_users,
        'top_activities' : top_activities
    })





from django.db.models import Sum, Count, Q, F
from django.db.models.functions import Coalesce
from django.shortcuts import render
from django.db.models import Count, Sum, F, ExpressionWrapper, DecimalField, Q
from django.contrib.auth.models import User
from django.db.models import Count, Sum, F, ExpressionWrapper, DecimalField, Q, Case, When, Value, FloatField

def preinvoice_user_report(request):
    total_price_expr = ExpressionWrapper(
        F('preinvoice__items__unit_price') - F('preinvoice__items__discount'),
        output_field=DecimalField(max_digits=12, decimal_places=0)
    )

    user_report = (
        User.objects.annotate(
            total_preinvoices=Count('preinvoice', distinct=True),
            total_price_sum=Sum(total_price_expr),
            sell_count=Count('preinvoice', filter=Q(preinvoice__is_sell=True), distinct=True),
            sell_price_sum=Sum(
                total_price_expr,
                filter=Q(preinvoice__is_sell=True)
            )
        )
        .annotate(
            sell_ratio=Case(
                When(total_preinvoices=0, then=Value(0.0)),
                default=ExpressionWrapper(
                    F('sell_count') * 1.0 / F('total_preinvoices'),
                    output_field=FloatField()
                ),
                output_field=FloatField()
            )
        )
        .order_by('-sell_ratio')
    )

    best_5 = user_report[:5]
    worst_5 = user_report.order_by('sell_ratio')[:5]

    context = {
        "user_report": user_report,
        "best_5": best_5,
        "worst_5": worst_5,
    }
    return render(request, 'preinvoice_partial.html', context)





def preinvoice_ration_sell_user_report(request):
    # کوئری قبلی که ساختی
    user_report = (
        User.objects.annotate(
            total_preinvoices=Count('preinvoice', distinct=True),
            total_price_sum=Sum(ExpressionWrapper(F('preinvoice__items__unit_price') - F('preinvoice__items__discount'), output_field=DecimalField(max_digits=12, decimal_places=0))),
            sell_count=Count('preinvoice', filter=Q(preinvoice__is_sell=True), distinct=True),
            sell_price_sum=Sum(ExpressionWrapper(F('preinvoice__items__unit_price') - F('preinvoice__items__discount'), output_field=DecimalField(max_digits=12, decimal_places=0)), filter=Q(preinvoice__is_sell=True))
        )
        .annotate(
            sell_ratio=Case(
                When(total_preinvoices=0, then=Value(0.0)),
                default=ExpressionWrapper(F('sell_count') * 1.0 / F('total_preinvoices'), output_field=FloatField()),
                output_field=FloatField()
            ),
            sell_price_ratio=Case(
                When(total_price_sum=0, then=Value(0.0)),
                default=ExpressionWrapper(F('sell_price_sum') * 1.0 / F('total_price_sum'), output_field=FloatField()),
                output_field=FloatField()
            )
        )
        .order_by('-sell_ratio')
    )

    usernames = [user.username for user in user_report]
    sell_ratios = [round((user.sell_ratio or 0) * 100, 2) for user in user_report]
    sell_price_ratios = [round((user.sell_price_ratio or 0) * 100, 2) for user in user_report]

    context = {
        'user_report':user_report,
        "usernames": json.dumps(usernames),
        "sell_ratios": json.dumps(sell_ratios),
        "sell_price_ratios": json.dumps(sell_price_ratios),
    }
    return render(request, 'preinvoice_ratio_sell.html', context)
