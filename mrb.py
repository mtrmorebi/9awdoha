from flask import Flask
import requests
import threading
from bs4 import BeautifulSoup

app = Flask(__name__)

def chek(url):
    while True:
        try:
            response = requests.get(url)
            status_code = response.status_code
            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.title.string if soup.title else "No Title"
            print(f"[{status_code}] {title} - {url}")
        except requests.exceptions.RequestException:
            print("Request failed")

def start_threads():
    target_url = "https://iqkcnskms.whf.bz/public/login"
    for _ in range(100):
        thread = threading.Thread(target=chek, args=(target_url,))
        thread.daemon = True  # يجعل الثريدات تتوقف عند إيقاف السيرفر
        thread.start()

@app.route('/')
def home():
    return "Server is running with background threads!"

if __name__ == '__main__':
    threading.Thread(target=start_threads, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
