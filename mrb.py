from flask import Flask, render_template, request, jsonify
import aiohttp
import asyncio
from urllib.parse import urlparse
from bs4 import BeautifulSoup

app = Flask(__name__)

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

async def send_request(session, url, method="GET", user_agent=None, payload=None):
    headers = {}
    if user_agent:
        headers["User-Agent"] = user_agent

    try:
        if method == "POST":
            async with session.post(url, headers=headers, json=payload, timeout=5) as response:
                html = await response.text()
                return extract_response_data(response, html)
        else:
            async with session.get(url, headers=headers, timeout=5) as response:
                html = await response.text()
                return extract_response_data(response, html)
    except Exception:
        return {"status_code": "فشل الاتصال", "title": "غير متاح", "server": "غير متاح"}

def extract_response_data(response, html):
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string.strip() if soup.title else "غير متاح"
    server = response.headers.get("Server", "غير متاح")

    return {
        "status_code": response.status,
        "title": title,
        "server": server
    }

async def manage_requests(url, total_requests, concurrency, method, user_agent, payload):
    if not is_valid_url(url):
        return {"error": "الرابط غير صالح"}

    connector = aiohttp.TCPConnector(limit=concurrency)
    timeout = aiohttp.ClientTimeout(total=10)
    responses = []

    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        if method == "MRB":
            while True:
                result = await send_request(session, url, "GET", user_agent, payload)
                responses.append(result)
        else:
            tasks = [send_request(session, url, method, user_agent, payload) for _ in range(total_requests)]
            results = await asyncio.gather(*tasks)
            responses.extend(results)

    return {"results": responses, "success": sum(1 for r in responses if r["status_code"] == 200), "failed": sum(1 for r in responses if r["status_code"] != 200)}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start_test", methods=["POST"])
def start_test():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "البيانات غير صحيحة"}), 400

        url = data.get("url")
        method = data.get("method", "GET").upper()
        user_agent = data.get("user_agent", None)
        payload = data.get("payload", None)

        if method == "MRB":
            total_requests = 70000
            concurrency = 1
        else:
            total_requests = int(data.get("total_requests", 1))
            concurrency = int(data.get("concurrency", 1))

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(manage_requests(url, total_requests, concurrency, method, user_agent, payload))

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"خطأ في الخادم: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
