from sqlmap_gui.sections.widgets import OptionTab


class FileTab(OptionTab):
    def __init__(self):
        super().__init__()
        self._build()

    def _build(self):
        files = self.add_group("File system access", columns=1)
        self.path(files, "Read file from back-end (--file-read)", "--file-read",
                  name_filter="All Files (*.*)",
                  placeholder="e.g. /etc/passwd or C:\\boot.ini")
        self.path(files, "Write local file to back-end (--file-write)",
                  "--file-write", name_filter="All Files (*.*)",
                  placeholder="local file to upload")
        self.value(files, "Destination path on server (--file-dest)",
                   "--file-dest", "e.g. /var/www/html/shell.php")
        self.flag(files, "Brute-force common files (--common-files)",
                  "--common-files")

        os_takeover = self.add_group("OS takeover", columns=2)
        self.value(os_takeover, "Execute OS command (--os-cmd)", "--os-cmd",
                   'e.g. "whoami"')
        self.flag(os_takeover, "Interactive OS shell (--os-shell)", "--os-shell")
        self.flag(os_takeover, "Out-of-band stateful shell (--os-pwn)",
                  "--os-pwn", tooltip="Requires Meterpreter/payload setup")
        self.flag(os_takeover, "SMB relay attack (--os-smbrelay)", "--os-smbrelay")
        self.flag(os_takeover, "BOF exploit attempt (--os-bof)", "--os-bof")
        self.flag(os_takeover, "Escalate to DBA root privileges (--priv-esc)",
                  "--priv-esc")

        metasploit = self.add_group("Metasploit Framework bridge", columns=2)
        self.path(metasploit, "Local MSF path (--msf-path)", "--msf-path",
                  mode="dir",
                  tooltip="Folder where Metasploit Framework is installed")
        self.value(metasploit, "Temporary files path on server (--tmp-path)",
                   "--tmp-path", "e.g. /tmp")

        udf = self.add_group("UDF injection (MySQL/PostgreSQL)", columns=1)
        self.flag(udf, "Inject custom user-defined functions (--udf-inject)",
                  "--udf-inject")
        self.path(udf, "Shared library to compile/upload (--shared-lib)",
                  "--shared-lib")
