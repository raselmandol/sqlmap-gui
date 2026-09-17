from sqlmap_gui.sections.widgets import OptionTab


class TechniquesTab(OptionTab):
    def __init__(self):
        super().__init__()
        self._build()

    def _build(self):
        core = self.add_group("Technique selection", columns=2)
        self.value(core, "Techniques to try (--technique)", "--technique",
                   "B=Boolean E=Error U=Union S=Stacked T=Time Q=Inline",
                   tooltip="e.g. BEUSTQ (default) or just T for time-based")
        self.number(core, "Seconds of DBMS delay (--time-sec)", "--time-sec",
                    low=1, high=3600, start=None,
                    tooltip="Default 10; raise it on slow connections")

        union = self.add_group("UNION attack tuning", columns=2)
        self.value(union, "Column range (--union-cols)", "--union-cols",
                   "e.g. 1-10 or 12-16")
        self.value(union, "Character to brute-force columns (--union-char)",
                   "--union-char", "e.g. A")
        self.value(union, "FROM table for payload (--union-from)", "--union-from",
                   "e.g. dual")

        advanced = self.add_group("Advanced / second-order", columns=2)
        self.value(advanced, "DNS exfiltration domain (--dns-domain)",
                   "--dns-domain")
        self.value(advanced, "Second-order result URL (--second-url)",
                   "--second-url")
        self.path(advanced, "Second-order request file (--second-req)",
                  "--second-req")

        misc = self.add_group("Payload post-processing", columns=2)
        self.flag(misc, "Disable payload casting (--no-cast)", "--no-cast")
        self.flag(misc, "Disable string escaping (--no-escape)", "--no-escape")
        self.flag(misc, "Retrieve data as hex (--hex)", "--hex")
