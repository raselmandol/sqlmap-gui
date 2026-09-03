from sqlmap_gui.sections.widgets import OptionTab


class EnumerateTab(OptionTab):
    def __init__(self):
        super().__init__()
        self._build()

    def _build(self):
        quick = self.add_group("Quick facts", columns=3)
        self.flag(quick, "Everything (-a)", "-a",
                  tooltip="Retrieve everything in one go")
        self.flag(quick, "Banner (--banner)", "--banner")
        self.flag(quick, "Current user (--current-user)", "--current-user")
        self.flag(quick, "Current database (--current-db)", "--current-db")
        self.flag(quick, "Server hostname (--hostname)", "--hostname")
        self.flag(quick, "DBA check (--is-dba)", "--is-dba")
        self.flag(quick, "Users (--users)", "--users")
        self.flag(quick, "Passwords (--passwords)", "--passwords")
        self.flag(quick, "Privileges (--privileges)", "--privileges")
        self.flag(quick, "Roles (--roles)", "--roles")
        self.flag(quick, "Databases (--dbs)", "--dbs")

        schema = self.add_group("Structure & counting", columns=3)
        self.flag(schema, "Tables (--tables)", "--tables")
        self.flag(schema, "Columns (--columns)", "--columns")
        self.flag(schema, "Full DBMS schema (--schema)", "--schema")
        self.flag(schema, "Count entries (--count)", "--count")
        self.flag(schema, "Dump table data (--dump)", "--dump")
        self.flag(schema, "Dump everything (--dump-all)", "--dump-all")
        self.flag(schema, "Exclude system DBs (--exclude-sysdbs)",
                  "--exclude-sysdbs",
                  tooltip="Skip system databases when using --dump-all")
        self.flag(schema, "Search DBs/tables/columns (--search)", "--search")
        self.flag(schema, "Brute-force tables (--common-tables)",
                  "--common-tables")
        self.flag(schema, "Brute-force columns (--common-columns)",
                  "--common-columns")

        filters = self.add_group("Scope filters", columns=3)
        self.value(filters, "Database(s) to enumerate (-D)", "-D",
                   "e.g. testdb, information_schema")
        self.value(filters, "Table(s) to enumerate (-T)", "-T",
                   "e.g. users,sessions")
        self.value(filters, "Column(s) to enumerate (-C)", "-C",
                   "e.g. user,pass,id")
        self.value(filters, "Exclude identifiers (--exclude)", "--exclude",
                   "db/table/column names to skip")
        self.value(filters, "WHERE condition (--where)", "--where",
                   "e.g. id>3 AND name LIKE '%admin%'")
        self.value(filters, "Pivot column (--pivot-column)", "--pivot-column")
        self.number(filters, "First entry (--start)", "--start", low=0,
                    high=100000000)
        self.number(filters, "Last entry (--stop)", "--stop", low=0,
                    high=100000000)
        self.number(filters, "Chars from start (--first)", "--first",
                    low=1, high=1000000)
        self.number(filters, "Chars until (--last)", "--last", low=1,
                    high=1000000)

        query = self.add_group("Custom SQL", columns=2)
        self.value(query, "SQL statement (--sql-query)", "--sql-query",
                   "SELECT 'sqlmap' FROM dual")
        self.path(query, "SQL statements file (--sql-file)", "--sql-file")
        self.flag(query, "Interactive SQL shell (--sql-shell)", "--sql-shell")

        output = self.add_group("Dump formatting", columns=3)
        self.choice(output, "Dump format (--dump-format)", "--dump-format",
                    ["CSV", "HTML", "SQLITE"])
        self.value(output, "CSV field delimiter (--csv-del)", "--csv-del", ",")
