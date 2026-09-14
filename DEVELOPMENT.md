# Development Guide

Everything here is for working on sqlmap-gui itself. If you just want to use
the app, see the [README](README.md) -- `pip install sqlmap-gui` is all you need.

---

## Set Up a Development Environment

### Clone the Repository

```bash
git clone https://github.com/raselmandol/sqlmap-gui.git
cd sqlmap-gui
```

### Create a Virtual Environment

```bash
python -m venv sqlmap_env
sqlmap_env\Scripts\activate    # Windows
source sqlmap_env/bin/activate # Linux
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Install the Package (Editable)

```bash
pip install -e .
```

`pip install -e .` puts a `sqlmap-gui` launcher on your `PATH`, so it works from
any directory while your edits take effect immediately.

### Run the Application

```bash
sqlmap-gui
```

To launch with a console attached (handy for seeing tracebacks), run
`python -m sqlmap_gui` instead.

---

## Build Executable (Windows)

If you want to build a standalone `.exe`:

### Install PyInstaller:

   ```bash
   pip install pyinstaller
   ```

> [!Note]
> **Note:** Already added in `requirements.txt`. (If you want to ignore it, make sure to remove it from `requirements.txt`.)

### Run:
   ```bash
   pyinstaller --name sqlmap-gui --onefile --windowed --icon=icon.ico sqlmap_gui/main.py
   ```

---

## Builder Script (`builder.bat`)

###  Usage
Run the script with one of the following flags:

```bash
builder.bat --build
```
Builds the project using `pip install -e .`

```bash
builder.bat --run
```
Runs the main application using `sqlmap-gui`.

```bash
builder.bat --exe
```
Builds a standalone executable using **PyInstaller**. Configuration parameters are loaded from `config.txt`.

> [!Note]
> To use `--activate`, run `./builder.ps1 --activate` instead of `./builder.bat --activate`. The PowerShell script (`builder.ps1`) is more reliable and effective in PowerShell environments, which are commonly used as the default terminal in most IDEs (such as Visual Studio Code).

---

## Release Checklist

Releases are published to PyPI automatically by the
[CI/CD workflow](.github/workflows/ci-cd.yml) when a GitHub release is created.
Before tagging a release, make sure:

- `version` in `pyproject.toml` and `__version__` in `sqlmap_gui/__init__.py`
  match, and the version is not already on
  [PyPI](https://pypi.org/project/sqlmap-gui/).
- `requirements.txt` installs on Linux (the CI smoke job runs on `ubuntu-latest`
  -- avoid Windows-only pins such as `pywin32` without a
  `; platform_system == "Windows"` marker).
- A quick local sanity check builds and installs cleanly:

  ```bash
  rmdir /s /q build   # stale build/ can carry deleted files into new wheels
  pip wheel . --no-deps -w dist
  pip install dist/sqlmap_gui-*.whl
  sqlmap-gui
  ```

---

## To-Do

- [ ]  Enhance error handling.
- [ ]  AI Assistant Panel
- [ ]  Option Recommender (Auto-Suggest Best SQLMap Flags)
- [ ]  Auto Tamper Script Selector (Based on Response Patterns)
- [ ]  Vulnerability Summary Generator
- [x]  Builder.bat script
- [ ]  Option to load Sqlmap source/folder selection
- [ ]  Improve documentation with more examples.
- [ ]  More tabs/ more options
- [ ]  JSON import, export
- [ ]  History Tab
- [ ]  Optimization tab
- [ ]  Burp proxy
- [ ]  sqlmap web
- [ ]  Clean terminal/editor  
- [ ]  GitHub pages with documentation
