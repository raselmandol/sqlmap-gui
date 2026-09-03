from sqlmap_gui.sections.widgets import OptionTab


class DetectionTab(OptionTab):
    def __init__(self):
        super().__init__()
        self._build()

    def _build(self):
        intensity = self.add_group("Detection intensity", columns=2)
        self.choice(intensity, "Level of tests to perform (--level)",
                    "--level", [1, 2, 3, 4, 5])
        self.choice(intensity, "Risk of tests to perform (--risk)",
                    "--risk", [1, 2, 3])

        page = self.add_group("Page comparison", columns=2)
        self.value(page, "True-positive string (--string)", "--string",
                   "text that appears when condition is TRUE")
        self.value(page, "False-positive string (--not-string)", "--not-string",
                   "text that appears when condition is FALSE")
        self.value(page, "Regexp to match (--regexp)", "--regexp",
                   "e.g. logged.in.(true|yes)")
        self.number(page, "HTTP status code match (--code)", "--code",
                    low=100, high=599)
        self.flag(page, "Compare pages by text only (--text-only)",
                  "--text-only")
        self.flag(page, "Show HTML titles in output (--titles)", "--titles")

        waf = self.add_group("WAF / IPS awareness", columns=2)
        self.flag(waf, "Skip WAF/IPS heuristic checks (--skip-waf)",
                  "--skip-waf",
                  tooltip="WAF/IPS heuristics run by default; this opts out")
