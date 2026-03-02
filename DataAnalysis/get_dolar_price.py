
# web import
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
#------------------------------------------------------------------

import time
import os
import json

CACHE_PATH = 'cache/'


class web_driver():
    def __init__(self,timeout=10,socaial_webDrive=False,session_dir='') -> None:
        self.timeout = timeout
        self.socaial_webDrive = socaial_webDrive
        self.session_dir = session_dir
        self.create_driver()
        

    def create_driver(self):

     
        if self.socaial_webDrive:


            chrome_options = Options()
            chrome_options.add_argument(f"--user-data-dir={os.path.abspath(self.session_dir)}")
            chrome_options.add_argument("--window-size=1920x1080")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")

            self.driver = webdriver.Chrome(options=chrome_options)
        
        else:

            chrome_options = Options()
            chrome_options.add_argument("--start-maximized")  # باز شدن تمام صفحه
            # chrome_options.add_argument("--headless")  # اگر نمی‌خواهی مرورگر باز شود، این خط را فعال کن

            self.driver = webdriver.Chrome(options=chrome_options)


    


    def wait(self,auto=True,time=0):
        if auto:
            self.driver.implicitly_wait(self.timeout)
        else:
            self.driver.implicitly_wait(time)   

    def open_site(self,url):
        self.driver.get(url)

    def find_element(self,element,by=By.XPATH,get_text=False,click=False,manual_timeout='False',print_error = True):
        ret = {'val':False,'text':False,'click_status':False}
        if manual_timeout =='False':
            self.wait()
        else:
            self.wait(auto=False,time=int(manual_timeout))
        try:
            val = self.driver.find_element(by=by,value=element)
            ret.update({'val':val})
            if get_text:
                text = val.text
                ret.update({'text':text})
            if click:
                click_status = val.click()
                ret.update({'click_status':click_status})
        except:
            if print_error:
                print('Error in find element')
            
        return ret
    

    def sendkeys(self,element,value,by=By.XPATH):
        self.wait()
        self.driver.find_element(by=by,value=element).send_keys(value)
        

    def scrool(self,repeat=5):
        for iter in range(int(repeat)):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.2)


class get_dollar_price():
    def __init__(self) -> None:
        self.web = web_driver()
        self.json_obj = json_cache()

        self.foods={}
        self.res_names  = []
        self.city = False

        self.first_time = True
        


    def open_tgju(self,url ='https://www.tgju.org/profile/price_dollar_rl/history'):
        self.web.open_site(url)


    def set_page(self,page_index):
        
        self.web.find_element(element=f'/html/body/main/div[1]/div[2]/div[2]/div[1]/div/div[3]/div/div[2]/div/div[1]/a[2]',click=True)   # click restaurant
        time.sleep(1)
        #print('a')
        # /html/body/div[2]/div/div/form/div/button
        headers, rows = self.extract_table_from_page()
        #print(headers,rows)

        self.send_for_save(headers,rows=rows)
        # self.web.scrool()
        # self.web.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        

        time.sleep(1)


    def send_for_save(self, headers, rows):
        """
        Save or append data to JSON file.
        - Prevent duplicate dates (based on Gregorian date)
        """
        file_path = os.path.join(CACHE_PATH, "usd_price.json")

        # اگه پوشه وجود نداشت، بسازش
        if not os.path.exists(CACHE_PATH):
            os.makedirs(CACHE_PATH)

        # اگه فایل هنوز وجود نداره → یعنی بار اول اجراست
        if not os.path.exists(file_path):
            #print("🆕 Creating new JSON file...")
            json_data = {
                "headers": headers,
                "data": rows
            }
            self.json_obj.write_json(file_path, json_data)
            #print(f"✅ Created {file_path} with {len(rows)} rows.")
        else:
            # در دفعات بعدی → فقط داده‌های جدید را اضافه کن
            #print("📈 Checking for duplicate dates before append...")
            existing = self.json_obj.read_json(file_path)
            existing_data = existing.get("data", [])

            # استخراج تمام تاریخ‌های موجود (ستون اول)
            existing_dates = {row[0] for row in existing_data if len(row) > 0}

            # فیلتر کردن فقط ردیف‌های جدید
            new_rows = [r for r in rows if r[0] not in existing_dates]

            if new_rows:
                existing_data.extend(new_rows)
                existing["data"] = existing_data
                self.json_obj.write_json(file_path, existing)
                #print(f"✅ Added {len(new_rows)} new rows (total {len(existing_data)}).")
            else:
                print("⚠️ No new rows to add — all dates already exist.")




    def extract_table_from_page(self):
        """Return list of rows (as lists) and header list"""
        wait = WebDriverWait(self.web.driver, 10)
        # wait for table body rows present
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr")))
        time.sleep(0.2)  # slight wait to ensure table filled
        table = self.web.driver.find_element(By.CSS_SELECTOR, "table")
        # header
        headers_elems = table.find_elements(By.CSS_SELECTOR, "thead th")
        headers = [h.text.strip() for h in headers_elems if h.text.strip()!=""]
        # rows
        rows = []
        for tr in table.find_elements(By.CSS_SELECTOR, "tbody tr"):
            cols = [td.text.strip() for td in tr.find_elements(By.CSS_SELECTOR, "td")]
            if cols:
                rows.append(cols)
        return headers, rows





class json_cache():

    def read_json(self,file_path):
        file = open(file_path)
        data = json.load(file)
        try:
            file.close()
        except:
            #print('cant close file')
            pass
        return data



    def write_json(self, file_name, dict_obj):
        json_object = json.dumps(dict_obj, ensure_ascii=False, indent=2)
        if not file_name.endswith('.json'):
            file_name += '.json'
        with open(file_name, "w", encoding='utf-8') as outfile:
            outfile.write(json_object)


    def ret_city_cache(self,city_name):
        try:
            if os.path.exists('{}{}.json'.format(CACHE_PATH,city_name)):
                data = self.read_json(file_path=city_name)
                return data
            else:
                return []
        except:
            return []
    def write_city_restaurants(self,city_name,value):
        new_names =[]
        last_restaurants = self.ret_city_cache(city_name=city_name)
        for res_name in value:
            if res_name not in last_restaurants and res_name !=False:
                new_names.append(res_name)
        
        self.write_json(CACHE_PATH+city_name+'.json',dict=new_names)




if __name__=='__main__':

    web = get_dollar_price()
    web.open_tgju()
    for i in range(1,30):
        web.set_page(i)