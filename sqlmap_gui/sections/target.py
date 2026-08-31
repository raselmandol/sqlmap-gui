"""Target tab: how sqlmap finds and reaches the target(s)."""

from sqlmap_gui.sections.widgets import OptionTab


class TargetTab(OptionTab):
    def __init__(self):
        super().__init__()
        self._build()

    def _build(self):
        direct = self.add_group("Direct / URL", columns=2)
        self.value(direct, "Direct connection string (-d)", "-d",
                   "e.g. mysql://user:pass@host/db")
        self.value(direct, "URL (--url)", "--url",
                   "http://www.site.com/vuln.php?id=1")
        self.value(direct, "Log file to parse (-l)", "-l", "requests.log",
                   tooltip="Parse targets from a Burp/WebScarab proxy log")
        self.path(direct, "Bulkfile with URLs (-m)", "-m",
                  placeholder="targets.txt (one URL per line)")
        self.path(direct, "HTTP request file (-r)", "-r",
                  placeholder="request.txt (raw HTTP request)")

        dork = self.add_group("Search-dork targeting", columns=2)
        self.value(dork, "Google dork (-g)", "-g",
                   'e.g. inurl:"php?id="')
        self.number(dork, "Dork results page (-gpage)", "--gpage",
                    low=1, high=100,
                    tooltip="Use a specific result page of the dork results")

        payload = self.add_group("POST data & parameters", columns=2)
        self.value(payload, "Data string (--data)", "--data",
                   "e.g. username=admin&password=pass")
        self.value(payload, "Parameter delimiter (--param-del)", "--param-del",
                   "e.g. ; (splits --data/--cookie params)")

        cookie = self.add_group("Cookies", columns=2)
        self.value(cookie, "Cookie header (--cookie)", "--cookie",
                   "e.g. PHPSESSID=a8d127e..")
        self.value(cookie, "Cookie delimiter (--cookie-del)", "--cookie-del",
                   "e.g. ;")
        self.path(cookie, "Load cookies from file (--load-cookies)",
                  "--load-cookies",
                  name_filter="Netscape cookies (*.txt *.cookies);;All Files (*)",
                  tooltip="File containing cookies in Netscape/wget format")
        self.flag(cookie, "Ignore Set-Cookie headers (--drop-set-cookie)",
                  "--drop-set-cookie")

        config = self.add_group("Configuration file", columns=1)
        self.path(config, "Load options from INI file (-c)", "-c",
                  name_filter="INI config (*.ini *.conf);;All Files (*)")
        self.add_stretch()
