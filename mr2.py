from flask import Flask, request, render_template, jsonify
import threading
import urllib.request
import random
from user_agent import generate_user_agent
from urllib.request import ProxyHandler, build_opener

app = Flask(__name__)

def generate_random_proxy():
    """توليد بروكسي عشوائي"""
    ip = ".".join(str(random.randint(0, 255)) for _ in range(4))
    ports = [19, 20, 21, 22, 23, 24, 25, 80, 53, 111, 110, 443, 8080, 139, 445, 512, 513, 514, 4444, 2049, 1524, 3306, 5900]
    port = random.choice(ports)
    return f"{ip}:{port}"

def check_without_proxy(url):
    """فحص بدون بروكسي"""
    headers = {
        'User-Agent': generate_user_agent(),
        'Accept': '*/*',
        'Connection': 'keep-alive'
    }
    try:
        req = urllib.request.urlopen(urllib.request.Request(url, headers=headers))
        result = {"status": "GOOD", "url": url} if req.status == 200 else {"status": "BAD", "url": url}
    except Exception as e:
        result = {"status": "DOWN", "url": url, "error": str(e)}
    
    print(result)  # طباعة النتيجة في السيرفر
    return result

def check_with_proxy(url):
    """فحص مع بروكسي"""
    proxy = generate_random_proxy()
    headers = {
        'User-Agent': generate_user_agent(),
        'Accept': '*/*',
        'Connection': 'keep-alive'
    }
    try:
        proxy_handler = ProxyHandler({'http': f'http://{proxy}', 'https': f'https://{proxy}'})
        opener = build_opener(proxy_handler)
        req = opener.open(urllib.request.Request(url, headers=headers))
        result = {"status": "GOOD", "url": url, "proxy": proxy} if req.status == 200 else {"status": "BAD", "url": url, "proxy": proxy}
    except Exception as e:
        result = {"status": "DOWN", "url": url, "proxy": proxy, "error": str(e)}

    print(result)  # طباعة النتيجة في السيرفر
    return result

@app.route("/", methods=["GET"])
def home():
    return render_template("home.html")

@app.route("/check", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        check_type = request.form.get("check_type")  # "proxy" أو "no_proxy"
        num_threads = int(request.form.get("num_threads", 10))  # عدد الفحوصات المتزامنة
        
        if not url:
            return jsonify({"error": "يرجى إدخال الرابط!"})
        
        result = []
        threads = []
        for _ in range(num_threads):  
            if check_type == "proxy":
                thread = threading.Thread(target=lambda: result.append(check_with_proxy(url)))
            else:
                thread = threading.Thread(target=lambda: result.append(check_without_proxy(url)))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        return jsonify(result)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
