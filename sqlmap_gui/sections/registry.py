"""Registry tab: Windows registry access through the back-end DBMS."""

from sqlmap_gui.sections.widgets import OptionTab


class RegistryTab(OptionTab):
    def __init__(self):
        super().__init__()
        self._build()

    def _build(self):
        actions = self.add_group("Registry actions", columns=3)
        self.flag(actions, "Read a registry key value (--reg-read)", "--reg-read")
        self.flag(actions, "Write a registry key value (--reg-add)", "--reg-add")
        self.flag(actions, "Delete a registry key (--reg-del)", "--reg-del")

        keys = self.add_group("Registry key details", columns=2)
        self.value(keys, "Registry key (--reg-key)", "--reg-key",
                   r"e.g. HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft")
        self.value(keys, "Value name (--reg-value)", "--reg-value",
                   "e.g. Version")
        self.value(keys, "Value data to write (--reg-data)", "--reg-data",
                   "e.g. 1 or REG_SZ=sqlmap")
        self.value(keys, "Value type when adding (--reg-type)", "--reg-type",
                   "e.g. REG_DWORD / REG_SZ")
