from sqlmap_gui.sections.widgets import OptionTab


class HelpTab(OptionTab):
    """General/misc options tab (class name kept for import compatibility)."""

    def __init__(self):
        super().__init__()
        self._build()

    def _build(self):
        behaviour = self.add_group("Run behaviour", columns=3)
        self.flag(behaviour, "Batch: never ask for input (--batch)", "--batch",
                  tooltip="Use default answers for every interactive prompt")
        self.flag(behaviour, "Check internet connectivity (--check-internet)",
                  "--check-internet")
        self.flag(behaviour, "Show progress + ETA (--eta)", "--eta")
        self.flag(behaviour, "Test HTML forms (--forms)", "--forms")
        self.number(behaviour, "Crawl website to depth (--crawl)", "--crawl",
                    low=0, high=100,
                    tooltip="Depth 1 crawls the target URL only; 0 = off")
        self.value(behaviour, "Regex excluding pages from crawl "
                              "(--crawl-exclude)", "--crawl-exclude")

        session = self.add_group("Session & logging", columns=2)
        self.path(session, "Retrieve session from file (-s)", "-s",
                  name_filter="Session files (*.sqlite);;All Files (*)")
        self.path(session, "Log all HTTP traffic to file (-t)", "-t",
                  name_filter="Traffic log (*.log *.txt);;All Files (*)")
        self.flag(session, "Flush session for target (--flush-session)",
                  "--flush-session")
        self.flag(session, "Use cached results only (--fresh-queries)",
                  "--fresh-queries")
        self.choice(session, "Verbosity (-v)", "-v",
                    [("0 - silent", "0"), ("1 - info", "1"),
                     ("2 - debug", "2"), ("3 - payloads", "3"),
                     ("4 - http", "4"), ("5 - queries", "5"),
                     ("6 - everything", "6")])

        output = self.add_group("Output & encoding", columns=2)
        self.path(output, "Custom output directory (--output-dir)",
                  "--output-dir", mode="dir")
        self.value(output, "Character set (--charset)", "--charset",
                   "e.g. GBK / utf-8")
        self.value(output, "Scope regex to filter targets (--scope)", "--scope",
                   "e.g. (www)?\\.target\\..*")
        self.flag(output, "Parse & show DBMS errors (--parse-errors)",
                  "--parse-errors")
        self.flag(output, "Hex-dump retrieved data (--hex)", "--hex")

        info = self.add_group("Info & housekeeping", columns=3)
        self.flag(info, "Print version and exit (--version)", "--version")
        self.flag(info, "Update sqlmap from git (--update)", "--update")
        self.flag(info, "Safely remove all content (--purge)", "--purge")
        self.flag(info, "Clean up DBMS artifacts (--cleanup)", "--cleanup")
        self.flag(info, "Disable console coloring (--disable-coloring)",
                  "--disable-coloring")
        self.flag(info, "Work in offline mode (--offline)", "--offline")
        self.flag(info, "List available tamper scripts (--list-tampers)",
                  "--list-tampers")
        self.flag(info, "Simple wizard interface (--wizard)", "--wizard")
        self.flag(info, "Beep when injection found (--beep)", "--beep")
        self.flag(info, "Base64-safe processing (--base64-safe)",
                  "--base64-safe")
        self.flag(info, "Check for missing dependencies (--dependencies)",
                  "--dependencies")

        misc = self.add_group("Miscellaneous", columns=2)
        self.value(misc, "Predefined answers (--answers)", "--answers",
                   'e.g. "quit=N,follow=N"')
        self.value(misc, "Base64 parameter(s) (--base64)", "--base64",
                   "comma separated parameters to base64-encode")
        self.value(misc, "Alert command on finding (--alert)", "--alert",
                   'e.g. "notify-send found"')
