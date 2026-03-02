from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import time
import os
import cv2
from selenium.webdriver.common.by import By
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException
import time
from django.db import connection
from SocialApps.models import WhatsAppMessage



LEFT_TOLBAR_XPATH = '/html/body/div[1]/div/div/div[3]/div/header/div/div[1]'
LEFT_CHATS = "/html/body/div[1]/div/div/div[3]/div/div[3]/div/div[3]/div[1]/div/div/div[{}]/div/div"
MESSAGE = '/html/body/div[1]/div/div/div[3]/div/div[4]/div/div[3]/div/div[2]/div[3]/div[{}]/div/div'
MESSAGE_SPARE = '/html/body/div[1]/div/div/div[3]/div/div[4]/div/div[2]/div/div[2]/div[3]/div[{}]/div/div'
CHAT_SCROLL_BAR = '/html/body/div[1]/div/div/div[3]/div/div[4]/div/div[3]/div/div[2]'
NAMES_SCROLL_BAR = '/html/body/div[1]/div/div/div[3]/div/div[3]/div/div[3]'

def get_session_dir(user_id:int):
    return f"sessions/user_{user_id}"


class WebDriver():
    def __init__(self,session_dir):
        chrome_options = Options()
        chrome_options.add_argument(f"--user-data-dir={os.path.abspath(session_dir)}")
        # chrome_options.add_argument("--window-size=1920x1080")
        chrome_options.add_argument("--start-maximized")

        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        # chrome_options.add_argument("--headless=new")
        

        self.driver = webdriver.Chrome(options=chrome_options)
    
    def get_driver(self):
        return self.driver


def is_user_logged_in(driver):
    try:
        # آیکن منوی اصلی که فقط پس از ورود نمایش داده می‌شود
        driver.find_element(by=By.XPATH,value=LEFT_TOLBAR_XPATH)
        return True
    except:
        return False
    

def capture_qr(driver, qr_path_cropped):
    try:
        qr_element = driver.find_element("css selector", "canvas")
        location = qr_element.location
        size = qr_element.size

        full_path = qr_path_cropped.replace("Crop_qrcodes", "qrcodes")
        driver.save_screenshot(full_path)
        image = cv2.imread(full_path)

        left = int(location['x'])
        top = int(location['y'])
        right = left + int(size['width'])
        bottom = top + int(size['height'])

        qr_image = image[top:bottom, left:right]
        cv2.imwrite(qr_path_cropped, qr_image)
        



        os.remove(full_path)

        #print("✅ QR ذخیره شد:", qr_path_cropped)
        return qr_path_cropped
    except Exception as e:
        #print("⚠️ خطا در ذخیره QR:", e)
        return False

def start_whatsapp_session(user_id):
    session_dir = get_session_dir(user_id=user_id)
    qr_path_cropped = f"media/Crop_qrcodes/user_{user_id}.png"

    os.makedirs('media/Crop_qrcodes', exist_ok=True)
    os.makedirs("media/qrcodes", exist_ok=True)
    os.makedirs(session_dir, exist_ok=True)

    web_driver = WebDriver(session_dir)
    driver = web_driver.get_driver() 

    driver.get("https://web.whatsapp.com/")
    time.sleep(10)

    start_time = time.time()
    while time.time() - start_time < 60:  # تا ۶۰ ثانیه
        if is_user_logged_in(driver):
            #print("🎉 کاربر لاگین شد.")
            driver.quit()
            return True,''

        ret = capture_qr(driver, qr_path_cropped)
        if ret is not None:
            return False,ret
        driver.quit()
        time.sleep(15)

    #print("⌛ زمان تمام شد، کاربر لاگین نشد.")
    
    
    driver.quit()
    return "NOT_LOGGED_IN"




from selenium.common.exceptions import NoSuchElementException

def close_popups(driver):
    popup_selectors = [
        'div[role="button"][title="Use here"]',
        'div[role="button"][aria-label="Dismiss"]',
        'div[role="button"][aria-label="Close"]',
    ]
    
    for selector in popup_selectors:
        try:
            button = driver.find_element("css selector", selector)
            button.click()
            time.sleep(1)
        except NoSuchElementException:
            continue


def get_chat_list(driver):
    # chats = driver.find_elements("css selector", "div[role='row']")
    # chats = driver.find_element(by=By.XPATH,value=LEFT_CHATS)
    chats = []
    error=0
    for person in range(1,100):
        try:
            element = LEFT_CHATS.format(person)
            chat_element = driver.find_element(by=By.XPATH,value=element)
            chats.append(chat_element)
        except Exception as e:
            error+=1
            scroll_up_chat_full_xpath(driver=driver,scrol_bar_element=NAMES_SCROLL_BAR,repeat=1)
            #print(e)
            if error>10:
                break     


    return chats


def open_chat(driver, chat_element):
    chat_element.click()
    time.sleep(3)  # wait for messages to load



def scroll_up_chat_full_xpath(driver,scrol_bar_element, repeat=5):
    chat_box = driver.find_element(by=By.XPATH,value = scrol_bar_element)

    for _ in range(repeat):
        driver.execute_script("arguments[0].scrollTop = 0", chat_box)
        time.sleep(0.6)


def get_messages(driver, limit=100,user_id=-1,contact_name=1):
    messages = []
    # scroll_up_chat_full_xpath(driver=driver,scrol_bar_element=CHAT_SCROLL_BAR,repeat=1)
    error = 0
    time.sleep(2)

    while len(messages) < limit:
        for message in range(1,20):
            try:
                try:
                    element = driver.find_element(by=By.XPATH,value= MESSAGE.format(message))
                except:
                    element = driver.find_element(by=By.XPATH,value= MESSAGE_SPARE.format(message))

                text = element.text.strip()
                if not text:
                    continue

                classes = element.get_attribute("class")
                is_from_me = "message-out" in classes

                if is_from_me:
                    sender = user_id
                    receiver = contact_name
                else:
                    sender = contact_name
                    receiver =  user_id


                message_data = {
                    "text": text,
                    "is_from_me": is_from_me,
                    "sender" : sender,
                    "receiver" : receiver,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # یا زمان دقیق‌تر با بررسی DOM
                }

                if message_data not in messages:
                    messages.append(message_data)

                error = 0
                if len(messages) >= limit:
                    break
            except:
                error+=1
                if error>17:
                    break
        
        if error >20 or len(messages)>limit :
            break

        scroll_up_chat_full_xpath(driver=driver,scrol_bar_element=CHAT_SCROLL_BAR,repeat=1)


        time.sleep(1)  # wait for new messages to load


    # messages = list(dict.fromkeys(messages))  # remove duplicates

    return messages[:limit]



def collect_messages_from_all_chats(user_id:int):
    session_dir = get_session_dir(user_id=user_id)
    web_driver = WebDriver(session_dir)
    driver = web_driver.get_driver() 
    driver.get("https://web.whatsapp.com/")
    time.sleep(10)
    close_popups(driver)
    chats = get_chat_list(driver)
    all_data = {}

    for i, chat in enumerate(chats):
        try:
            open_chat(driver, chat)
            # contact_name = driver.find_element("css selector", "header span[title]").text
            contact_name = str(chat.text).split('\n')[0]
            messages = get_messages(driver, limit=100,user_id=user_id,contact_name=contact_name)
            all_data[contact_name] = messages
            #print(contact_name," : ",len(messages))
            time.sleep(1)
        except Exception as e:
            #print(f"Failed on chat {i}: {e}")
            continue
    #print(all_data)
    
    return all_data








def worker(user_id: int):
    while True:
        try:


            # Prevent stale DB connections in multiprocessing
            connection.close()
            data = collect_messages_from_all_chats(user_id)



                # message_data = {
                #     "text": text,
                #     "is_from_me": is_from_me,
                #     "sender" : sender,
                #     "receiver" : receiver,
                #     "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # یا زمان دقیق‌تر با بررسی DOM
                # }


            # Save to DB
            for message in data:
                WhatsAppMessage.objects.create(
                    sender=message['sender'],
                    receiver=message['receiver'],
                    message_text=message['text'],
                    timestamp=message['timestamp'],
                    chat_name=message['receiver'],

                )

            #print(f"[user {user_id}] ✅ Data saved.")
        except Exception as e:
            print(f"[user  ❌ Error: {e}")
        
        time.sleep(600)  # wait 10 minutes



if __name__ == '__main__':
    # result = start_whatsapp_session(3)
    result =  collect_messages_from_all_chats(1)
    #print("نتیجه نهایی:", result)
