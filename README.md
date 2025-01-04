# sqlmap-gui

![GUI Preview](https://raw.githubusercontent.com/raselmandol/sqlmap-gui/refs/heads/main/sqlmap_gui/resources/icon.png)


`sqlmap-gui` is a Python-based graphical user interface (GUI) for interacting with the powerful [sqlmap](https://github.com/sqlmapproject/sqlmap) penetration testing tool. This GUI simplifies the use of sqlmap, enabling users to execute SQL injection tests and analyze vulnerabilities without requiring extensive command-line experience.

---

[![GitHub release date](https://img.shields.io/github/release-date/raselmandol/sqlmap-gui)](#)

[![GitHub last commit](https://img.shields.io/github/last-commit/raselmandol/sqlmap-gui)](#)


## Features

- **User-Friendly Interface**: Simplified navigation for sqlmap functionalities.
- **Comprehensive Options**: Access to all popular sqlmap commands with categorized tabs.
- **Results Display**: Real-time output display for executed sqlmap commands.
- **Cross-Platform**: Runs on Windows and Linux.
- **Customizable**: Easily add new features or extend the interface.

---

## Screenshots

![GUI Preview](https://raw.githubusercontent.com/raselmandol/sqlmap-gui/refs/heads/main/screenshots/1.png)

![GUI Preview](https://raw.githubusercontent.com/raselmandol/sqlmap-gui/refs/heads/main/screenshots/2.png)

---

## Installation

Follow these steps to set up the project locally:

### Clone the Repository

```bash
git clone https://github.com/raselmandol/sqlmap-gui.git
cd sqlmap-gui
```

### Create a Virtual Environment

```bash
python -m venv sqlmap_env
source sqlmap_env/bin/activate   # On Linux/Mac
sqlmap_env\Scripts\activate    # On Windows
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

###  Build

```bash
pip install -e .
```
### Run the Application

```bash
python sqlmap_gui
```
---

## How to Use

 1. Launch the GUI (`python sqlmap_gui`).
 2. Navigate through the tabs to explore sqlmap commands:
   - **Injection Tests**: Enter a target URL and customize sqlmap options.
   - **Advanced Options**: Configure sqlmap payloads and settings.
 3. Execute the command and view results in the output console.

---

## Folder Structure

```plaintext
sqlmap-gui/
├── build/                     # Auto-generated build files (ignored)
├── sqlmap/                    # sqlmap tool integration
├── sqlmap_env/                # Virtual environment (ignored)
├── sqlmap_gui/                # Main GUI source code
│   ├── sections/              # Modular GUI sections
│   ├── __init__.py            # Initialization script
│   ├── main.py                # Main application entry point
├── sqlmap_gui.egg-info/       # Metadata files (ignored)
├── setup.py                   # Setup script
├── README.md                  # Project documentation
```

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

## Requirements

- Python 3.8+
- PyQt5
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
   git commit -m "Add new feature"
   ```

4. Push to your branch:

   ```bash
   git push origin feature-name
   ```

5. Open a pull request.

---

## License

This project is licensed under the MIT License, [sqlmap license](https://raw.githubusercontent.com/sqlmapproject/sqlmap/refs/heads/master/LICENSE).
---

## To-Do

- [ ]  Add more screenshots of the GUI in action.
- [ ]  Enhance error handling.
- [ ]  Improve documentation with more examples.
- [ ]  More tabs
- [ ]  Background Process
- [ ]  JSON import, export
- [ ]  History Tab

