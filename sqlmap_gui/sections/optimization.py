from sqlmap_gui.sections.widgets import OptionTab


class OptimizationTab(OptionTab):
    def __init__(self):
        super().__init__()
        self._build()

    def _build(self):
        speed = self.add_group("Speed & efficiency", columns=3)
        self.flag(speed, "Turn on all optimization switches (-o)", "-o")
        self.flag(speed, "Disable keep-alive connections (--no-keep-alive)",
                  "--no-keep-alive",
                  tooltip="Persistent HTTP(s) connections are on by default; "
                          "use this to opt out")
        self.flag(speed, "Null connection (--null-connection)",
                  "--null-connection",
                  tooltip="Response-size probing; incompatible with --text-only")

        self.number(speed, "Concurrent threads (--threads)", "--threads",
                    low=1, high=10, start=None,
                    tooltip="sqlmap maximum is 10; 1 disables threading")

        finger = self.add_group("DBMS fingerprint", columns=2)
        self.flag(finger, "Check DBMS version (-f / --fingerprint)", "--fingerprint")
        self.value(finger, "Expect this DBMS (--dbms)", "--dbms",
                   "e.g. MySQL, MSSQL, PostgreSQL, Oracle, SQLite")

    def extraInputs(self):
        return []
