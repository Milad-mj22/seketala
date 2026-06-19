import requests
import logging
import json
import time

# ================== CONFIG ==================
API_URL = "http://172.20.10.2:8900/data_analysis/api/receive-invoice/"
API_KEY = "SECRET123"

TEST_MODE = True  # always test

# ================== LOGGING ==================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

# ================== FAKE TEST DATA ==================
def get_test_invoices():
    return [
        {
            "invoice_number": "25360000000000000",
            "name": "فثسسیب",
            "nahveh": "delivery",
            "phone": "09123456789",
            "date": "1404-02-10",
            "time": "12:30",
            "total_price": 250000,
            "takhfif": 10000,
            "peyk": True,
            "moshtarak": "10043",
            "serv": 2,
            "pnum": 1,
            "shomareh_pos": "POS-1",
            "mablagh_pos": 120000,
            "hazineh_peyk": 20000,
            "naghdi": 130000,
            "nonaghdi": 90000,
            "mandeh": 0,
            "items": [
                {"food": "Burger", "price": 120000, "quantity": 1},
                {"food": "Fries", "price": 60000, "quantity": 1}
            ]
        },
        {
            "invoice_number": "INV-1003",
            "name": "Pizza House",
            "nahveh": "takeaway",
            "phone": "09121234567",
            "date": "1404/02/10",
            "time": "18:45",
            "total_price": 380000,
            "takhfif": 20000,
            "peyk": False,
            "moshtarak": "VAS-8899",
            "serv": 3,
            "pnum": 2,
            "shomareh_pos": "POS-2",
            "mablagh_pos": 200000,
            "hazineh_peyk": 0,
            "naghdi": 180000,
            "nonaghdi": 180000,
            "mandeh": 20000,
            "items": [
                {"food": "Pizza", "price": 180000, "quantity": 2}
            ]
        }
    ]

# ================== SENDER ==================
def send_invoice(payload):
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": API_KEY
    }


    if TEST_MODE:
        logger.info("===== TEST MODE =====")
        logger.info(json.dumps(payload, ensure_ascii=False, indent=2))


    return requests.post(API_URL, json=payload, headers=headers, timeout=30)

# ================== MAIN ==================
def run_test():
    invoices = get_test_invoices()

    logger.info(f"Starting test with {len(invoices)} invoices")

    for inv in invoices:
        try:
            response = send_invoice(inv)

            if response.status_code in (200, 201):
                logger.info(f"SUCCESS: {inv['invoice_number']}")
            else:
                logger.error(f"FAILED: {inv['invoice_number']} | {response.text}")

        except Exception as e:
            logger.error(f"ERROR sending {inv['invoice_number']}")

        time.sleep(0.3)

    logger.info("===== TEST FINISHED =====")

# ================== RUN ==================
if __name__ == "__main__":
    run_test()