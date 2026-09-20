# sqlmap-gui

![GUI Preview](https://raw.githubusercontent.com/raselmandol/sqlmap-gui/refs/heads/main/screenshots/v200_1_preview1.png)


`sqlmap-gui` is a Python-based graphical user interface (GUI) for interacting with the powerful [sqlmap](https://github.com/sqlmapproject/sqlmap) penetration testing tool. This GUI simplifies the use of sqlmap, enabling users to execute SQL injection tests and analyze vulnerabilities without requiring extensive command-line experience.

---

[![PyPI version](https://img.shields.io/pypi/v/sqlmap-gui)](https://pypi.org/project/sqlmap-gui/) [![GitHub release](https://img.shields.io/github/v/release/raselmandol/sqlmap-gui)](https://github.com/raselmandol/sqlmap-gui/releases) [![GitHub release date](https://img.shields.io/github/release-date/raselmandol/sqlmap-gui)](https://github.com/raselmandol/sqlmap-gui/releases) [![GitHub last commit](https://img.shields.io/github/last-commit/raselmandol/sqlmap-gui)](https://github.com/raselmandol/sqlmap-gui/commits/main) [![CI/CD](https://github.com/raselmandol/sqlmap-gui/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/raselmandol/sqlmap-gui/actions/workflows/ci-cd.yml)


## Features

- **User-Friendly Interface**: Simplified navigation for sqlmap functionalities.
- **Comprehensive Options**: Access to all popular sqlmap commands with categorized tabs.
- **Results Display**: Real-time output display for executed sqlmap commands.
- **Cross-Platform**: Runs on Windows and ~~Linux~~ (working).
- **Customizable**: Easily add new features or extend the interface.

---

## Screenshots

![GUI Preview](https://raw.githubusercontent.com/raselmandol/sqlmap-gui/refs/heads/main/screenshots/v200_1_preview2.png)

![GUI Preview](https://raw.githubusercontent.com/raselmandol/sqlmap-gui/refs/heads/main/screenshots/v200_1_preview4.png)

![GUI Preview](https://raw.githubusercontent.com/raselmandol/sqlmap-gui/refs/heads/main/screenshots/v200_1_preview3.png)

---

## Installation

```bash
pip install sqlmap-gui
```

That single command pulls in everything the GUI needs, including the
`pywinpty` terminal backend on Windows. Run it with:

```bash
sqlmap-gui
```

`pip install` puts a `sqlmap-gui` launcher on your `PATH`, so this works from
any directory. If you installed into a virtual environment, activate it first --
the launcher lives in that environment's `Scripts`/`bin` folder, not on the
system `PATH`.

To launch with a console attached (handy for seeing tracebacks), run
`python -m sqlmap_gui` instead.

> [!Tip]
> sqlmap itself is not bundled. On first use, point the GUI at an existing
> sqlmap checkout or let it download the latest sqlmap for you from the
> Environment settings.

Setting up a development environment, building a standalone `.exe`, or using
the builder scripts is covered in [DEVELOPMENT.md](DEVELOPMENT.md).

---

## How to Use

 1. Launch the GUI (`sqlmap-gui`).
 2. Navigate through the tabs to explore sqlmap commands:
   - **Injection Tests**: Enter a target URL and customize sqlmap options.
   - **Advanced Options**: Configure sqlmap payloads and settings.
 3. Execute the command and view results in the output console.

---


## Example

Here is a sample workflow for detecting vulnerabilities on a target website:

1. Enter the target URL: `http://example.com/page?id=1`.
2. Select detection options like:
   - **Technique**: `--technique=T`
   - **DBMS**: `--dbms=mysql`
3. Click `Run` to execute sqlmap.
4. View results in the output console.

---

## More

To get a list of basic options and switches use:

```bash
-h
```
To get a list of all options and switches use:
```bash
-hh
```

To get an overview of sqlmap capabilities, a list of supported features, and a description of all options and switches, along with examples, you are advised to consult the [user's manual](https://github.com/sqlmapproject/sqlmap/wiki/Usage). Use extra/optional command input option to use those extra options and switches. You can find Custom Query option in Enumerate tab.

---

## Requirements

- Python 3.8+
- PyQt5 (installed automatically by pip)
- [sqlmap](https://github.com/sqlmapproject/sqlmap) source

---

## Contribution

Contributions are welcome! To contribute:

1. Fork this repository.
2. Create a new branch:

   ```bash
   git checkout -b feature-name
   ```

3. Commit your changes:

   ```bash
   git commit -m "Add feature"
   ```

4. Push to your branch:

   ```bash
   git push origin feature-name
   ```

5. Open a pull request.

---

## License

This project is licensed under the MIT License, [sqlmap license](https://raw.githubusercontent.com/sqlmapproject/sqlmap/refs/heads/master/LICENSE).
