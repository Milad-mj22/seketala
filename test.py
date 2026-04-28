import time
import pyodbc
import requests
from datetime import datetime, timedelta
import jdatetime
import logging
import os
import traceback
import json

# ================== CONFIG ==================
server = r'SERVER\AMINPARDAZ'
database = 'foodsoft140501'
driver = '{ODBC Driver 17 for SQL Server}'
API_URL = 'https://seketalamanager.ir/data_analysis/api/receive-invoice/'
API_KEY = 'SECRET123'

# ستون‌های جدول fact
columns = ['factnum', 'dat', 'tim', 'total', 'kname', 'nahveh',\
            'tel', 'adress', 'takhfif', 'peyk', 'edition',"moshtarak",\
            'serv','pnum','shomareh_pos','mablagh_pos','hazineh_peyk','naghdi',\
            'nonaghdi','mandeh']

connection_string = (
    f'DRIVER={driver};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'Trusted_Connection=yes;'
)

# پیکربندی
CHECK_INTERVAL = 120  # ثانیه (2 دقیقه)

# ================== LOGGING ==================
LOG_DIR = "logs"
MISSED_DIR = "missed_factors"
TRACKING_DIR = "tracking"
EDITED_DIR = "edited_invoices"

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(MISSED_DIR, exist_ok=True)
os.makedirs(TRACKING_DIR, exist_ok=True)
os.makedirs(EDITED_DIR, exist_ok=True)

now_jalali = jdatetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
LOG_FILE = os.path.join(LOG_DIR, f"run_{now_jalali}.log")
MISSED_FILE = os.path.join(MISSED_DIR, f"missed_{now_jalali}.txt")
TRACKING_FILE = os.path.join(TRACKING_DIR, "last_processed.json")
EDITED_FILE = os.path.join(EDITED_DIR, "edited_tracking.json")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ================== TRACKING HELPERS ==================
def load_tracking():
    """بارگذاری آخرین اطلاعات ردیابی"""
    if os.path.exists(TRACKING_FILE):
        try:
            with open(TRACKING_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"📂 بارگذاری ردیابی: آخرین factnum = {data.get('last_factnum')}")
                return data
        except Exception as e:
            logger.warning(f"⚠️ خطا در بارگذاری: {e}")
    
    return {'last_factnum': 0}

def save_tracking(last_factnum):
    """ذخیره اطلاعات ردیابی"""
    data = {
        'last_factnum': last_factnum,
        'last_check_time': datetime.now().isoformat()
    }
    try:
        with open(TRACKING_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"❌ خطا در ذخیره ردیابی: {e}")

# ================== EDITED INVOICES HELPERS ==================
def load_edited_tracking():
    """بارگذاری لیست فاکتورهای ویرایش شده قبلی"""
    if os.path.exists(EDITED_FILE):
        try:
            with open(EDITED_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"⚠️ خطا در بارگذاری فایل ویرایش: {e}")
    return {}

def save_edited_tracking(edited_dict):
    """ذخیره لیست فاکتورهای ویرایش شده"""
    try:
        with open(EDITED_FILE, 'w', encoding='utf-8') as f:
            json.dump(edited_dict, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"❌ خطا در ذخیره ویرایش‌ها: {e}")

# ================== HELPERS ==================
def short_str_to_jalali_date(short_str: str) -> jdatetime.date:
    parts = short_str.replace('/', '-').split('-')
    if len(parts) != 3:
        raise ValueError("Invalid date format")
    yy, mm, dd = parts
    year = 1400 + int(yy)
    return jdatetime.date(year, int(mm), int(dd))

def denormalize_jalali_date(jalali_date: str) -> str:
    parts = jalali_date.replace('-', '/').split('/')
    jy, jm, jd = parts
    return f"{jy[-2:]}/{jm.zfill(2)}/{jd.zfill(2)}"

def increment_jalali_date(jalali_date_str):
    jy, jm, jd = map(int, jalali_date_str.split('-'))
    dt = jdatetime.date(jy, jm, jd) + jdatetime.timedelta(days=1)
    return dt.strftime('%Y-%m-%d')

def get_today_yesterday_jalali():
    """دریافت تاریخ امروز و دیروز به فرمت کوتاه"""
    today = jdatetime.date.today()
    yesterday = today - jdatetime.timedelta(days=1)
    
    # تبدیل به فرمت کوتاه: 04/01/01
    today_short = f"{str(today.year)[-2:]}/{str(today.month).zfill(2)}/{str(today.day).zfill(2)}"
    yesterday_short = f"{str(yesterday.year)[-2:]}/{str(yesterday.month).zfill(2)}/{str(yesterday.day).zfill(2)}"
    
    return today_short, yesterday_short

# ================== SEND INVOICE (تابع مشترک) ==================
def send_invoice(row):
    """
    تابع مشترک برای ارسال فاکتور به API
    هم برای فاکتورهای جدید و هم ویرایش شده استفاده می‌شود
    """

    factnum, dat, tim, total, kname, nahveh,\
    tel, adress, takhfif, peyk,edition,moshtarak,\
    serv,pnum,shomareh_pos,mablagh_pos,hazineh_peyk,naghdi,\
    nonaghdi,mandeh = row
    
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    
    try:
        # دریافت آیتم‌های فاکتور
        cursor.execute("""
            SELECT kcod, tedad, takfi
            FROM factor
            WHERE factnum = ?
        """, factnum)
        
        items = []
        for kcod, tedad, takfi in cursor.fetchall():
            items.append({
                "food": kcod,
                "price": int(takfi),
                "quantity": int(tedad)
            })
            if int(tedad) == 0:
                logger.warning(f"⚠️ تعداد صفر برای فاکتور {factnum}")
        
        # ساخت payload
        payload = {
            "invoice_number": str(factnum),
            "name": kname,
            "nahveh": nahveh,
            "phone": tel,
            "date": str(short_str_to_jalali_date(dat)),
            "time": tim,
            "total_price": int(total),
            "takhfif": float(takhfif),
            "peyk": peyk,
            "items": items,
            # "is_edited": True if int(edition) > 0 else False,
            # "edit_count": int(edition)
            "moshtarak":moshtarak ,
            "serv": serv,
            "pnum": pnum,
            "shomareh_pos": shomareh_pos,
            "mablagh_pos": int(mablagh_pos),
            "hazineh_peyk": int(hazineh_peyk),
            "naghdi": int(naghdi),
            "nonaghdi": int(nonaghdi),
            "mandeh": int(mandeh),



        }
        
        headers = {"Content-Type": "application/json", "X-API-KEY": API_KEY}
        
        # تلاش برای ارسال (5 بار)
        for i in range(5):
            try:
                response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
                if response.status_code in (200, 201):
                    edit_status = "جدید" if int(edition) == 0 else f"ویرایش #{edition}"
                    logger.info(f"✅ فاکتور {factnum} ({edit_status}) ارسال شد")
                    return True, None
                else:
                    logger.error(f"❌ فاکتور {factnum} | Status={response.status_code}")
            except Exception as e:
                logger.error(f"❌ استثنا فاکتور {factnum}: {str(e)}")
                time.sleep(2)
        
        return False, str(factnum)
        
    except Exception as e:
        logger.error(f"❌ خطا در ارسال فاکتور {factnum}: {str(e)}")
        return False, str(factnum)
    finally:
        conn.close()

# ================== CHECK NEW INVOICES ==================
def check_new_invoices():
    """بررسی فاکتورهای جدید"""
    tracking = load_tracking()
    last_factnum = tracking.get('last_factnum', 0)
    
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"""
            SELECT {",".join(columns)}
            FROM fact
            WHERE factnum > ?
            ORDER BY factnum ASC
        """, last_factnum)
        
        rows = cursor.fetchall()
        
        if not rows:
            logger.info("📭 فاکتور جدیدی یافت نشد")
            return last_factnum
        
        logger.info(f"📋 {len(rows)} فاکتور جدید یافت شد")
        
        error_factors = []
        max_factnum = last_factnum
        
        for row in rows:
            factnum = row[0]
            
            success, error = send_invoice(row=row)
            
            if not success:
                error_factors.append(error)
            
            max_factnum = max(max_factnum, factnum)
            time.sleep(0.3)
        
        if error_factors:
            save_errors(error_factors)
        
        return max_factnum
        
    except Exception as e:
        logger.error(f"❌ خطا در بررسی فاکتورهای جدید: {str(e)}")
        logger.error(traceback.format_exc())
        return last_factnum
    finally:
        conn.close()

# ================== CHECK EDITED INVOICES ==================
def check_edited_invoices():
    """بررسی فاکتورهای ویرایش شده در امروز و دیروز"""
    
    # دریافت تاریخ امروز و دیروز
    today_short, yesterday_short = get_today_yesterday_jalali()
    
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    
    try:
        # دریافت فاکتورهای ویرایش شده در امروز و دیروز
        cursor.execute(f"""
            SELECT {",".join(columns)}
            FROM fact
            AND dat IN (?, ?)
            ORDER BY factnum ASC
        """, today_short, yesterday_short)
        
        rows = cursor.fetchall()
        
        if not rows:
            logger.info("📭 فاکتور ویرایش شده‌ای در امروز/دیروز یافت نشد")
            return
        
        logger.info(f"✏️ {len(rows)} فاکتور ویرایش شده در امروز/دیروز یافت شد")
        
        # بارگذاری لیست قبلی
        edited_tracking = load_edited_tracking()
        
        # لیست جدید فاکتورهای ویرایش شده
        new_edited_tracking = {}
        
        # لیست فاکتورهایی که باید ارسال شوند
        to_send = []
        
        for row in rows:
            factnum = row[0]
            dat = row[1]
            tim = row[2]
            peyk = row[9]      # ستون peyk
            edit = row[10]     # ستون edition
                    
            factnum_str = str(factnum)
            current_edit = int(edit) if edit else 0
            current_peyk = int(peyk) if peyk else 0

            # ذخیره در لیست جدید
            new_edited_tracking[factnum_str] = {
                'edit_count': current_edit,
                'peyk': current_peyk,
                'date': dat,
                'time': tim
            }
            
            previous_data = edited_tracking.get(factnum_str, {})
            previous_edit = previous_data.get('edit_count')
            previous_peyk = previous_data.get('peyk')
            should_send = False

            # 1️⃣ اگر اولین بار دیده می‌شود
            if previous_edit is None:
                logger.info(f"🆕 فاکتور جدید ویرایش/پیک: {factnum}")
                should_send = True

            # 2️⃣ اگر edition تغییر کرده
            elif current_edit != previous_edit:
                logger.info(f"🔄 تغییر edition: {factnum} ({previous_edit} → {current_edit})")
                should_send = True

            # 3️⃣ اگر peyk تغییر کرده
            elif current_peyk != previous_peyk:
                logger.info(f"🚚 تغییر مبلغ پیک: {factnum} ({previous_peyk} → {current_peyk})")
                should_send = True

            if should_send:
                to_send.append(row)
            else:
                logger.info(f"⏭️ بدون تغییر مهم: {factnum}")

                    # ذخیره لیست جدید
        save_edited_tracking(new_edited_tracking)
        
        # ارسال فاکتورهای نیازمند ارسال
        if to_send:
            logger.info(f"📤 {len(to_send)} فاکتور ویرایش شده برای ارسال...")
            
            error_factors = []
            for row in to_send:
                
                success, error = send_invoice(row=row)
                
                if not success:
                    error_factors.append(error)
                
                time.sleep(0.3)
            
            if error_factors:
                save_errors(error_factors)
        else:
            logger.info("✅ هیچ فاکتور ویرایش شده جدیدی برای ارسال نیست")
            
    except Exception as e:
        logger.error(f"❌ خطا در بررسی فاکتورهای ویرایش شده: {str(e)}")
        logger.error(traceback.format_exc())
    finally:
        conn.close()

# ================== SEND BY DATE ==================
def send_invoices_by_date(start_jalali, end_jalali=None):
    """ارسال فاکتورهای یک بازه زمانی"""
    start_date = start_jalali.replace('/', '-')
    
    if end_jalali:
        end_date = end_jalali.replace('/', '-')
    else:
        today = jdatetime.date.today()
        yesterday = today - jdatetime.timedelta(days=1)
        end_date = yesterday.strftime('%Y-%m-%d')
    
    logger.info(f"📅 پردازش فاکتورها از {start_date} تا {end_date}")
    
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    
    current = start_date
    error_factors = []
    
    while current <= end_date:
        next_day = increment_jalali_date(current)
        
        try:
            cursor.execute(f"""
                SELECT {",".join(columns)}
                FROM fact
                WHERE dat >= ? AND dat < ?
            """, denormalize_jalali_date(current), denormalize_jalali_date(next_day))
            
            rows = cursor.fetchall()
            logger.info(f"📊 {len(rows)} فاکتور برای {current}")
            
            for row in rows:
                
                success, error = send_invoice(row=row)
                
                if not success:
                    error_factors.append(error)
                
                time.sleep(0.3)
                
        except Exception as e:
            logger.error(f"❌ خطا در پردازش تاریخ {current}: {str(e)}")
            error_factors.append(f"Date-{current}")
        
        current = next_day
    
    conn.close()
    
    if error_factors:
        save_errors(error_factors)
    
    logger.info("===== پایان ارسال فاکتورها =====")

def save_errors(error_factors):
    """ذخیره خطاها"""
    with open(MISSED_FILE, "w", encoding="utf-8") as f:
        for fact in error_factors:
            f.write(f"{fact}\n")
    logger.warning(f"⚠️ {len(error_factors)} فاکتور خطا داد")

# ================== MAIN LOOP ==================
def run_continuous_monitor():
    """حلقه اصلی - بررسی هر 2 دقیقه"""
    logger.info("🚀 شروع مانیتورینگ مداوم")
    logger.info(f"⏰ بررسی هر {CHECK_INTERVAL} ثانیه (2 دقیقه)")
    
    # اجرای اولیه - ارسال فاکتورهای دیروز
    yesterday_jalali = (
        jdatetime.date.today() - jdatetime.timedelta(days=1)
    ).strftime('%Y/%m/%d')
    
    logger.info("📤 ارسال اولیه فاکتورهای دیروز...")
    send_invoices_by_date(start_jalali=yesterday_jalali)
    
    # حلقه اصلی
    while True:
        try:
            logger.info("=" * 50)
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            logger.info(f"🔄 بررسی جدید: {current_time}")
            
            # 1. بررسی فاکتورهای جدید
            logger.info("👁️ بررسی فاکتورهای جدید...")
            last_factnum = check_new_invoices()
            
            # 2. بررسی فاکتورهای ویرایش شده (امروز و دیروز)
            logger.info("✏️ بررسی فاکتورهای ویرایش شده...")
            check_edited_invoices()

            
            
            # به‌روزرسانی ردیابی
            save_tracking(last_factnum)
            
            logger.info(f"✅ چرخه کامل شد. انتظار {CHECK_INTERVAL} ثانیه...")
            
        except Exception as e:
            logger.error(f"❌ خطای بحرانی: {str(e)}")
            logger.error(traceback.format_exc())
        
        time.sleep(CHECK_INTERVAL)

# ================== RUN ==================
if __name__ == "__main__":
    run_continuous_monitor()