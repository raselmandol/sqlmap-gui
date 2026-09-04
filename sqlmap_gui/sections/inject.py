from sqlmap_gui.sections.widgets import OptionTab


class InjectTab(OptionTab):
    def __init__(self):
        super().__init__()
        self._build()

    def _build(self):
        params = self.add_group("Testable parameters", columns=1)
        self.value(params, "Only test these parameters (-p)", "-p",
                   "e.g. id,username (comma separated)")
        self.value(params, "Skip these parameters (--skip)", "--skip",
                   "e.g. token,csrf")
        self.choice(params, "Filter by GET/POST (--param-filter)",
                    "--param-filter", ["GET", "POST"])
        self.value(params, "Exclude by regex (--param-exclude)", "--param-exclude")

        static = self.add_group("Skip boring values", columns=1)
        self.flag(static, "Skip parameters with no dynamic content "
                          "(--skip-static)", "--skip-static")
        self.flag(static, "Use big random numbers instead of 1 (--invalid-bignum)",
                  "--invalid-bignum")
        self.flag(static, "Use logical A>B instead of 1 (--invalid-logical)",
                  "--invalid-logical")
        self.flag(static, "Use random strings instead of 1 (--invalid-string)",
                  "--invalid-string")

        custom = self.add_group("Payload boundaries", columns=1)
        self.value(custom, "Payload prefix (--prefix)", "--prefix", "')AND")
        self.value(custom, "Payload suffix (--suffix)", "--suffix", "AND ('a'='a")

        tamper = self.add_group("Tamper scripts", columns=1)
        self.value(tamper, "Tamper script(s) (--tamper)", "--tamper",
                   "e.g. between,randomcase (comma separated)")
        self.value(tamper, "Character encoding (--charset)", "--charset",
                   "e.g. 0123456789abcdef")

        heur = self.add_group("Heuristics", columns=1)
        self.flag(heur, "Conduct thorough tests only on promising parameters "
                        "(--smart)", "--smart")
        self.value(heur, "Show only tests matching regex (--test-filter)",
                   "--test-filter", "e.g. row")
        self.value(heur, "Skip tests matching regex (--test-skip)",
                   "--test-skip", "e.g. BENCHMARK")
