from django.shortcuts import get_object_or_404, render

# Create your views here.
# views.py
import os
import sqlite3
from django.shortcuts import render, redirect
from django.conf import settings
import jdatetime

from .folder_utils.sepidar_date import format_jalali_datetime
from .forms import DBUploadForm
from .models import InvoiceItem, Sale
from persiantools.jdatetime import JalaliDate


def upload_db(request):
    if request.method == "POST":
        form = DBUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.cleaned_data["file"]
            temp_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)
            with open(temp_path, "wb+") as dest:
                for chunk in uploaded_file.chunks():
                    dest.write(chunk)

            # Connect to uploaded DB
            conn = sqlite3.connect(temp_path)
            cursor = conn.cursor()

            try:
                cursor.execute("SELECT factnum, dat, total, kname, tel, adress FROM facts")  # adjust table name
                rows = cursor.fetchall()

                # Import data
                for row in rows:


                    jalali_str = row[1]  # example: "03/10/27"

                    # Clean and parse Jalali date (assuming format: YY/MM/DD or YYYY/MM/DD)
                    try:
                        parts = jalali_str.replace("“", "").replace("”", "").split("/")
                        if len(parts[0]) == 2:
                            # If year is short like 03 → convert to 1403
                            year = int(parts[0]) + 1400
                        else:
                            year = int(parts[0])
                        month = int(parts[1])
                        day = int(parts[2])

                        gregorian_date = JalaliDate(year, month, day).to_gregorian()
                    except Exception as e:
                        #print(f"⚠️ Error converting date {jalali_str}: {e}")
                        continue  # skip bad records








                    Sale.objects.get_or_create(
                        factnum=row[0],
                        defaults={
                            'dat': gregorian_date,
                            'total': row[2],
                            'kname': row[3],
                            'tel': row[4],
                            'address': row[5],
                       
                        }
                    )
                conn.close()
                os.remove(temp_path)
                return render(request, "UploadDB/upload_success.html", {"count": len(rows)})

            except Exception as e:
                conn.close()
                return render(request, "UploadDB/upload_error.html", {"error": str(e)})

    else:
        form = DBUploadForm()

    return render(request, "UploadDB/upload_db.html", {"form": form})


from django.shortcuts import render
from django.db.models import Sum
from django.db.models.functions import TruncDate

from django.shortcuts import render
from django.db.models import Sum
from django.db.models.functions import TruncDate

from .models import Invoice, InvoiceItem


from django.db.models import Sum
from django.db.models import Sum, F, ExpressionWrapper, DurationField, DateField
from django.db.models.functions import TruncDate
from django.db import models
from datetime import timedelta, time
from django.db.models import Sum, F, DateTimeField, ExpressionWrapper


def dashboard(request):
    top_customers = list(
        Invoice.objects.values('phone')
        .annotate(total_spent=Sum('total_price'))
        .order_by('-total_spent')[:10]
    )

    daily_sales = list(
        Invoice.objects
        .annotate(
            shifted_time=ExpressionWrapper(
                F('created_at') - timedelta(hours=3),
                output_field=DateTimeField()
            )
        )
        .annotate(day=TruncDate('shifted_time'))
        .values('day')
        .annotate(total_day=Sum('total_price'))
        .order_by('day')
    )

    summary = Invoice.objects.aggregate(total_revenue=Sum('total_price'))

    daily_item_volume = list(
        InvoiceItem.objects
        .annotate(
            shifted_time=ExpressionWrapper(
                F('invoice__created_at') - timedelta(hours=3),
                output_field=DateTimeField()
            )
        )
        .annotate(day=TruncDate('shifted_time'))
        .values('day')
        .annotate(total_qty=Sum('quantity'))
        .order_by('day')
    )

    customers_count = Invoice.objects.values('phone').distinct().count()

    context = {
        'top_customers': top_customers,
        'daily_sales': daily_sales,
        'total_revenue': summary['total_revenue'] or 0,
        'days_count': len(daily_sales),
        'customers_count': customers_count,
        'daily_item_volume': daily_item_volume,
    }
    return render(request, 'factors_data_dashboard.html', context)







from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Invoice
from .utils import extract_payment_methods, jalali_date_time_to_gregorian




class ReceiveInvoice(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        data = request.data
        if request.headers.get("X-API-KEY") != "SECRET123":
            return Response({"error": "unauthorized"}, status=403)
    
        
        
        date_time = jalali_date_time_to_gregorian(data['date'],data['time'])

        invoice, created = Invoice.objects.get_or_create(
            invoice_number=data["invoice_number"],
            defaults={
                "name": data["name"],
                "nahveh": data["nahveh"],
                "phone": data["phone"],
                "created_at": date_time,
                "total_price": data["total_price"],
                "discount" : data['takhfif'],
                "peyk" : data['peyk']
            }
        )

        if not created:
            return Response({"status": "already_exists"})

        for item in data["items"]:
            InvoiceItem.objects.create(
                invoice=invoice,
                food_name=item["food"],
                price=item["price"],
                quantity=item["quantity"],
                total=item["price"] * item["quantity"]
            )

        return Response({"status": "ok"}, status=status.HTTP_201_CREATED)
    

from django.db.models import Max
from collections import defaultdict
from datetime import datetime
import re
from django.db.models import Max
from collections import defaultdict
from datetime import datetime, timedelta, time
import re

def calc_nahve_pardakh(request):
    date_str = request.GET.get('date')

    # 🔹 اگر تاریخ نفرستاده بود → آخرین تاریخ دیتابیس
    if date_str:
        selected_date = datetime.strptime(date_str, '%Y/%m/%d').date()
    else:
        last_date = Invoice.objects.aggregate(
            max_date=Max('created_at')
        )['max_date']

        if not last_date:
            return render(request, 'utils/nahve.html', {})

        selected_date = last_date.date()

    # 🔹 بازه روز کاری: 3 صبح تا 3 صبح روز بعد
    start_datetime = datetime.combine(selected_date, time(3, 0))
    end_datetime = start_datetime + timedelta(days=1)

    invoices = Invoice.objects.filter(
        created_at__gte=start_datetime,
        created_at__lt=end_datetime
    )

    totals = defaultdict(int)

    for invoice in invoices:
        if 'اسنپ' not in invoice.name:
            methods = extract_payment_methods(invoice.nahveh)
            for method in methods:
                totals[method] += invoice.total_price - invoice.discount
        else:
            totals['اسنپ'] += invoice.total_price - invoice.discount

    context = {
        'selected_date': selected_date,
        'labels': list(totals.keys()),
        'values': list(totals.values()),
        'table_data': totals.items()
    }

    return render(request, 'utils/nahve.html', context)






from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from datetime import datetime
import pandas as pd

from .models import Invoice, InvoiceItem
from .utils import get_date_range  # or paste function directly


def invoice_report(request):
    # default = today
    date_str = request.GET.get('date')

    if date_str:
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    else:
        selected_date = timezone.now().date()

    start, end = get_date_range(selected_date)

    invoices = Invoice.objects.filter(
        created_at__range=(start, end)
    ).prefetch_related("items")

    context = {
        "invoices": invoices,
        "selected_date": selected_date
    }
    return render(request, "invoice_report.html", context)

from dateutil import parser


def download_invoice_excel(request):
    date_str = request.GET.get('date')
    if date_str:
        try:
            selected_date = parser.parse(date_str).date()
        except (ValueError, TypeError):
            selected_date = datetime.today().date()
    else:
        selected_date = datetime.today().date()


    # selected_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else timezone.localdate()

    start, end = get_date_range(selected_date)

    rows = []

    items = InvoiceItem.objects.filter(
        invoice__created_at__range=(start, end)
    ).select_related("invoice")

    for item in items:
        rows.append({
            "Invoice Number": item.invoice.invoice_number,
            "Name": item.invoice.name,
            "Phone": item.invoice.phone,
            "Food": item.food_name,
            "Price": item.price,
            "Quantity": item.quantity,
            "Total": item.total,
            "Date": item.invoice.created_at
        })

    df = pd.DataFrame(rows)

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="invoice_detail.xlsx"'

    df.to_excel(response, index=False)
    return response




def download_invoice_summary_excel(request):
    date_str = request.GET.get('date')
    selected_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else timezone.localdate()

    start, end = get_date_range(selected_date)

    items = InvoiceItem.objects.filter(
        invoice__created_at__range=(start, end)
    )

    rows = [{
        "Food": i.food_name,
        "Quantity": i.quantity,
        "Total": i.total
    } for i in items]

    df = pd.DataFrame(rows)

    summary = df.groupby("Food", as_index=False).sum()

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="invoice_summary.xlsx"'

    summary.to_excel(response, index=False)
    return response



def invoice_detail_api(request, invoice_number):
    invoice = get_object_or_404(
        Invoice.objects.prefetch_related("items"),
        invoice_number=invoice_number
    )

    data = {
        "invoice_number": invoice.invoice_number,
        "name": invoice.name,
        "phone": invoice.phone,
        "nahveh": invoice.nahveh,
        "created_at": invoice.created_at.strftime("%Y-%m-%d %H:%M"),
        "total_price": invoice.total_price,
        "discount": invoice.discount,
        "items": [
            {
                "food_name": item.food_name,
                "price": item.price,
                "quantity": item.quantity,
                "total": item.total,
            }
            for item in invoice.items.all()
        ]
    }

    return JsonResponse(data)




from io import BytesIO
from pathlib import Path
from datetime import datetime

from openpyxl import load_workbook
from openpyxl.utils import column_index_from_string
from django.http import HttpResponse
from django.utils import timezone
from .folder_utils.foodsoft_lookup import get_kname_by_kcod
from .folder_utils.sepidar_lookup import get_code_by_name


def sepidar_download_excel(request):
    date_str = request.GET.get('date')
    if date_str:
        try:
            selected_date = parser.parse(date_str).date()
        except (ValueError, TypeError):
            selected_date = datetime.today().date()
    else:
        selected_date = datetime.today().date()


    # selected_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else timezone.localdate()

    start, end = get_date_range(selected_date)

    invoices = (
        Invoice.objects
        .filter(created_at__range=(start, end))
        .prefetch_related("items")
    )

    # -----------------------------
    # 1) Build rows (one row per invoice item)
    # -----------------------------
    rows = []
    for inv in invoices:
        for it in inv.items.all():


            name = get_kname_by_kcod(it.food_name)
            code = get_code_by_name(name=name)
            if code is None:
                print(f'food soft : {it.food_name}' )

            rows.append({
                "فاكتور شماره": inv.invoice_number,
                "فاكتور نام مشتري": inv.name,
                # "phone": inv.phone,
                "قلم فاكتور كد": code,
                "قلم فاكتور في": it.price,
                "قلم فاكتور واحد اصلي": it.quantity,
                "قلم فاكتور كل": it.total,
                "فاكتور تاريخ": format_jalali_datetime(inv.created_at)
            })

    # -----------------------------
    # 2) Template + mapping
    # -----------------------------

    from user_management.utils import check_server


    # Load once at import time
    SERVER = check_server()
    if SERVER:
        template_path = r"/home/seketal1/Seketala_Kitchen_Flow/cache/sepidar_template.xlsx"  # must be .xlsx
    else:
        template_path = r'cache\sepidar_template.xlsx'
    wb = load_workbook(template_path)
    ws = wb[wb.sheetnames[0]]  # or wb["Sheet1"]

    START_ROW =2 # where the first data row begins in your template

    # Only these columns will be filled; everything else stays unchanged
    # مثال: اگر نمیخوای ستون C پر بشه، اصلا اینجا قرارش نده
    COL_MAP = {
        "فاكتور شماره": "B",
        "فاكتور تاريخ": "C",
        "قلم فاكتور كد": "F",
        "قلم فاكتور واحد اصلي": "I",
        "قلم فاكتور في": "K",
        "قلم فاكتور كل": "L",
        "فاكتور نام مشتري": "R",
        # "date": "M",   # if you don't want it, comment/remove it
    }

    # Precompute numeric column indexes (faster)
    col_idx_map = {k: column_index_from_string(v) for k, v in COL_MAP.items()}

    # -----------------------------
    # 3) Write only mapped columns
    # -----------------------------
    for i, record in enumerate(rows):
        excel_row = START_ROW + i
        for field, col_idx in col_idx_map.items():
            ws.cell(row=excel_row, column=col_idx, value=record.get(field))

    # -----------------------------
    # 4) Return as download
    # -----------------------------
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    j_date = jdatetime.date.fromgregorian(date=selected_date)

    filename = f"sepidar_{j_date.strftime('%Y-%m-%d')}.xlsx"
    resp = HttpResponse(
        output.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    resp["Content-Disposition"] = f'attachment; filename="{filename}"'
    return resp






# views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Invoice, InvoiceItem, Payment
import json


from django.contrib.auth.decorators import login_required

@login_required
def factor_list(request):
    """View to display factors for the logged-in user"""
    # Get the user's code_vaset from their profile
    pryk_id = request.user.profile.code_vaset
    
    # Filter invoices where peyk field matches user's code_vaset
    invoices = Invoice.objects.filter(peyk=pryk_id).order_by('-created_at')
    
    # Calculate payment summaries for each invoice
    for invoice in invoices:
        payments = invoice.payments.all()
        invoice.paid_amount = sum(p.amount for p in payments)
        invoice.remaining = invoice.total_price - invoice.paid_amount
        
        # Group payments by method
        payment_methods = {}
        for payment in payments:
            if payment.method not in payment_methods:
                payment_methods[payment.method] = 0
            payment_methods[payment.method] += payment.amount
        
        invoice.payment_methods = payment_methods
    
    # Add count for empty state message
    context = {
        'invoices': invoices,
        'invoices_count': invoices.count(),
        'user_code': pryk_id
    }
    
    return render(request, 'factor_list.html', context)



from django.core.exceptions import PermissionDenied

@login_required
def factor_detail(request, invoice_id):
    """View to show factor details and payment management"""
    pryk_id = request.user.profile.code_vaset
    
    # Get invoice and verify it belongs to this user
    invoice = get_object_or_404(
        Invoice.objects.prefetch_related('items', 'payments'), 
        id=invoice_id,
        peyk=pryk_id  # This ensures the invoice belongs to the logged-in user
    )
    
    # Get existing payments
    payments = invoice.payments.all()
    total_paid = sum(p.amount for p in payments)
    remaining = invoice.total_price - total_paid
    
    # Group payments by method
    payment_by_method = {}
    for payment in payments:
        if payment.method not in payment_by_method:
            payment_by_method[payment.method] = 0
        payment_by_method[payment.method] += payment.amount
    
    context = {
        'invoice': invoice,
        'items': invoice.items.all(),
        'payments': payments,
        'total_paid': total_paid,
        'remaining': remaining,
        'payment_by_method': payment_by_method,
        'payment_methods': Payment.PaymentMethod.choices,
    }
    
    return render(request, 'factor_detail.html', context)






@csrf_exempt
def update_payments(request, invoice_id):
    """API endpoint to update payments"""
    if request.method == 'POST':
        try:
            invoice = get_object_or_404(Invoice, id=invoice_id)
            data = json.loads(request.body)
            
            # Delete existing payments
            invoice.payments.all().delete()
            
            # Create new payments
            for method_data in data['payments']:
                if int(method_data['amount']) > 0:
                    Payment.objects.create(
                        invoice=invoice,
                        method=method_data['method'],
                        amount=int(method_data['amount']),
                        created_at=timezone.now()
                    )
            
            return JsonResponse({
                'success': True,
                'message': 'Payments updated successfully'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'error': 'Invalid method'}, status=405)



from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime

@login_required
def api_factors(request):
    """API endpoint for infinite scroll loading"""
    pryk_id = request.user.profile.code_vaset
    page = int(request.GET.get('page', 1))
    filter_type = request.GET.get('filter', 'today')  # 'today' or 'all'
    
    # Base queryset
    queryset = Invoice.objects.filter(peyk=pryk_id)
    
    # Apply filter
    if filter_type == 'today':
        today = timezone.now().date()
        queryset = queryset.filter(created_at__date=today)
    
    # Order by date (newest first)
    queryset = queryset.order_by('-created_at')
    
    # Paginate (20 items per page)
    paginator = Paginator(queryset, 20)
    current_page = paginator.get_page(page)
    
    # Prepare data
    invoices_data = []
    for invoice in current_page.object_list:
        payments = invoice.payments.all()
        paid_amount = sum(p.amount for p in payments)
        
        # Group payments by method
        payment_methods = {}
        for payment in payments:
            if payment.method not in payment_methods:
                payment_methods[payment.method] = 0
            payment_methods[payment.method] += payment.amount
        
        invoices_data.append({
            'id': invoice.id,
            'invoice_number': invoice.invoice_number,
            'name': invoice.name,
            'phone': invoice.phone,
            'total_price': float(invoice.total_price),
            'paid_amount': float(paid_amount),
            'remaining': float(invoice.total_price - paid_amount),
            'created_at': invoice.created_at.isoformat(),
            'payment_methods': payment_methods
        })
    
    return JsonResponse({
        'invoices': invoices_data,
        'has_more': current_page.has_next(),
        'current_page': page,
        'total_pages': paginator.num_pages
    })