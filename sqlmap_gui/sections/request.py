from PyQt5.QtWidgets import QHBoxLayout, QLineEdit, QPushButton, QVBoxLayout, QWidget

from sqlmap_gui.sections.widgets import OptionTab


class HeaderListWidget(QWidget):
    """Editable list of extra HTTP headers (one --headers entry per row)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._edits = []
        self._rows = []
        self._lay = QVBoxLayout(self)
        self._lay.setContentsMargins(0, 0, 0, 0)
        self._lay.setSpacing(4)

    def add_row(self):
        holder = QWidget()
        lay = QHBoxLayout(holder)
        lay.setContentsMargins(0, 0, 0, 0)
        edit = QLineEdit()
        edit.setPlaceholderText('Header (key:value), e.g. X-Fwd: 127.0.0.1')
        remove = QPushButton("✕")
        remove.setFixedSize(28, 24)
        remove.clicked.connect(lambda: self.remove_row(holder))
        lay.addWidget(edit, 1)
        lay.addWidget(remove)
        self._lay.addWidget(holder)
        self._edits.append(edit)
        self._rows.append(holder)

    def remove_row(self, holder):
        for index, stored in enumerate(list(self._rows)):
            if stored is holder:
                edit = self._edits.pop(index)
                self._rows.pop(index)
                self._lay.removeWidget(stored)
                stored.deleteLater()
                return

    def values(self):
        return [e.text().strip() for e in self._edits if e.text().strip()]

    def clear(self):
        while self._rows:
            self.remove_row(self._rows[0])


class RequestTab(OptionTab):
    def __init__(self):
        super().__init__()
        self.headers_list = HeaderListWidget()
        self._build()

    def _build(self):
        basic = self.add_group("Method & headers", columns=2)
        self.choice(basic, "HTTP method (--method)", "--method",
                    ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD",
                     "OPTIONS", "TRACE"])
        self.value(basic, "HTTP User-Agent (--user-agent)", "--user-agent")
        self.value(basic, "HTTP Host header (--host)", "--host")
        self.value(basic, "HTTP Referer header (--referer)", "--referer")
        self.flag(basic, "Random User-Agent (--random-agent)", "--random-agent")
        self.flag(basic, "Emulate smartphone (--mobile)", "--mobile")

        auth = self.add_group("HTTP authentication", columns=2)
        self.choice(auth, "Auth type (--auth-type)", "--auth-type",
                    ["Basic", "Digest", "NTLM", "PKI"])
        self.value(auth, "Credentials (--auth-cred)", "--auth-cred",
                   "user:password")
        self.path(auth, "Certificate/key file (--auth-file)", "--auth-file",
                  name_filter="PEM (*.pem *.crt *.key);;All Files (*)")

        conn = self.add_group("Connection & timing", columns=3)
        self.number(conn, "Delay per request seconds (--delay)", "--delay",
                    low=0, high=3600)
        self.number(conn, "Timeout seconds (--timeout)", "--timeout",
                    low=1, high=86400, start=None)
        self.number(conn, "Retries on timeout (--retries)", "--retries",
                    low=0, high=50)
        self.flag(conn, "Ignore redirects (--ignore-redirects)",
                  "--ignore-redirects")
        self.flag(conn, "Ignore timeouts (--ignore-timeouts)",
                  "--ignore-timeouts")
        self.flag(conn, "Force SSL/HTTPS (--force-ssl)", "--force-ssl")
        self.flag(conn, "HTTP parameter pollution (--hpp)", "--hpp")

        safe = self.add_group("Anti-detection (safe requests)", columns=2)
        self.value(safe, "Safe URL visited periodically (--safe-url)",
                   "--safe-url")
        self.value(safe, "Safe POST data (--safe-post)", "--safe-post")
        self.path(safe, "Safe request file (--safe-req)", "--safe-req")
        self.number(safe, "Safe requests between tests (--safe-freq)",
                    "--safe-freq", low=0, high=1000000)
        self.value(safe, "Randomize these parameters (--randomize)",
                   "--randomize", "comma-separated parameter names")

        csrf = self.add_group("Anti-CSRF handling", columns=2)
        self.value(csrf, "CSRF token parameter name (--csrf-token)",
                   "--csrf-token")
        self.value(csrf, "URL issuing CSRF token (--csrf-url)", "--csrf-url",
                   "page URL that issues the token")
        self.flag(csrf, "Skip URL encoding (--skip-urlencode)",
                  "--skip-urlencode")

        proxy = self.add_group("Proxy / Tor anonymity", columns=3)
        self.value(proxy, "Proxy URL (--proxy)", "--proxy",
                   "http://127.0.0.1:8080")
        self.value(proxy, "Proxy credentials (--proxy-cred)", "--proxy-cred",
                   "user:password")
        self.path(proxy, "Proxy list file (--proxy-file)", "--proxy-file",
                  placeholder="proxies.txt")
        self.choice(proxy, "Tor type (--tor-type)", "--tor-type",
                    ["HTTP", "SOCKS4", "SOCKS5"])
        self.value(proxy, "Tor port (--tor-port)", "--tor-port", "9050")
        self.flag(proxy, "Use Tor network (--tor)", "--tor")
        self.flag(proxy, "Verify Tor anonymity (--check-tor)", "--check-tor")
        self.flag(proxy, "Ignore system proxy (--ignore-proxy)",
                  "--ignore-proxy")

        evalg = self.add_group("Evaluate Python code per request", columns=1)
        self.value(evalg, "Python snippet (--eval)", "--eval",
                   "import hashlib; id=hashlib.md5(username.encode()).hexdigest()")

        headers = self.add_group("Extra headers (--headers, repeatable)", columns=1)
        headers.add_spanning(self.headers_list)
        add_button = QPushButton("+ Add header row")
        add_button.setFixedWidth(160)
        add_button.clicked.connect(self.headers_list.add_row)
        headers.add_spanning(add_button)

    def extraInputs(self):
        # One repeatable --headers=<value> per row keeps every entry a
        # single shell-safe argument (quoting happens centrally).
        return [f"--headers={header}" for header in self.headers_list.values()]

    def clearInputs(self):
        super().clearInputs()
        self.headers_list.clear()
