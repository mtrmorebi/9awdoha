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

from flask import Flask, render_template_string, request
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from faker import Faker
from fake_useragent import UserAgent

app = Flask(__name__)

fake = Faker()
ua = UserAgent()

# إصلاح مشكلة event loop للأنظمة التشغيلية المختلفة
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# دالة لإرسال الطلبات المتزامنة باستخدام aiohttp
async def fetch(session, url):
    try:
        ip = fake.ipv4()
        headers = {
            "User-Agent": ua.random,
            "X-Forwarded-For": ip
        }
        async with session.get(url, headers=headers) as response:
            status_code = response.status
            text = await response.text()
            soup = BeautifulSoup(text, "html.parser")
            title = soup.title.string if soup.title else "No Title"
            print(f"[{status_code}] {title} - {url} - IP: {ip}")
            return status_code, title, url, ip
    except Exception as e:
        print(f"Request failed: {e}")
        return None, None, url, None

# دالة لبدء العديد من الطلبات
async def start_requests(target_url, num_threads):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(num_threads):
            task = asyncio.create_task(fetch(session, target_url))
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

# واجهة الصفحة الرئيسية (index.html)
@app.route('/')
def home():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Send Requests</title>
    </head>
    <body>
        <h1>Send Requests to a URL</h1>
        <form action="/send_requests" method="post">
            <label for="url">URL:</label>
            <input type="text" id="url" name="url" required><br><br>
            
            <label for="threads">Number of Threads:</label>
            <input type="number" id="threads" name="threads" min="1" value="10" required><br><br>
            
            <button type="submit">Send Requests</button>
        </form>
    </body>
    </html>
    ''')

# واجهة إرسال الطلبات
@app.route('/send_requests', methods=['POST'])
def send_requests():
    url = request.form['url']
    num_threads = int(request.form['threads'])
    
    # تشغيل الطلبات بشكل غير متزامن
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    results = loop.run_until_complete(start_requests(url, num_threads))

    # عرض النتائج
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Results</title>
    </head>
    <body>
        <h1>Results for URL: {{ url }}</h1>
        <table border="1">
            <thead>
                <tr>
                    <th>Status Code</th>
                    <th>Title</th>
                    <th>URL</th>
                    <th>IP</th>
                </tr>
            </thead>
            <tbody>
                {% for status_code, title, url, ip in results %}
                <tr>
                    <td>{{ status_code }}</td>
                    <td>{{ title }}</td>
                    <td>{{ url }}</td>
                    <td>{{ ip }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        <br>
        <a href="/">Go Back</a>
    </body>
    </html>
    ''', results=results, url=url)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)  # تم تعديل البورت هنا
