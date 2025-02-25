from flask import Flask, request, jsonify
import asyncio
import aiohttp
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import logging

app = Flask(__name__)

logging.basicConfig(filename='requests.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])  
    except ValueError:
        return False

def get_site_name(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc  

async def send_request(session, url):
    site_name = get_site_name(url)  
    try:
        async with session.get(url, timeout=5) as response:
            page_title = "ERROR"  
            if response.status == 200:
                soup = BeautifulSoup(await response.text(), "html.parser")
                page_title = soup.title.string.strip() if soup.title else "UNKNOWN"
                return {"site": site_name, "title": page_title, "status": 200}
            else:
                return {"site": site_name, "title": page_title, "status": response.status}
    except Exception as e:
        logging.error(f"خطأ أثناء الاتصال بـ {url}: {e}")
        return {"site": site_name, "error": str(e), "status": "FAILED"}

async def manage_requests(url, concurrency):
    if not is_valid_url(url):
        return {"error": "الرابط غير صالح!"}

    connector = aiohttp.TCPConnector(limit=concurrency)  
    timeout = aiohttp.ClientTimeout(total=10)  
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        tasks = [send_request(session, url) for _ in range(concurrency)]
        results = await asyncio.gather(*tasks)

    success_count = sum(1 for res in results if res["status"] == 200)
    fail_count = len(results) - success_count

    return {"success": success_count, "fail": fail_count, "results": results}

@app.route('/send_requests', methods=['POST'])
def send_requests():
    data = request.json
    url = data.get("url")
    concurrency = int(data.get("concurrency", 100))  

    if not url or not is_valid_url(url):
        return jsonify({"error": "يرجى إدخال رابط صحيح!"}), 400

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    response = loop.run_until_complete(manage_requests(url, concurrency))

    return jsonify(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
