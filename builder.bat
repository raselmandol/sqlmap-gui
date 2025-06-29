@echo off
setlocal enabledelayedexpansion

:: Load configuration from config.txt
for /f "tokens=1,* delims==" %%A in (config.txt) do (
    set "%%A=%%B"
)

:: Parse arguments
if "%1"=="--build" (
    echo Running: pip install -e .
    pip install -e .
    goto :eof
)

if "%1"=="--run" (
    echo Running: python sqlmap_gui
    python sqlmap_gui
    goto :eof
)

if "%1"=="--exe" (
    set "CMD=pyinstaller"

    :: Required
    if defined name set "CMD=!CMD! --name !name!"
    if defined icon set "CMD=!CMD! --icon=!icon!"

    :: Optional
    if defined distpath set "CMD=!CMD! --distpath !distpath!"
    if defined workpath set "CMD=!CMD! --workpath !workpath!"
    if defined add-data set "CMD=!CMD! --add-data !add-data!"
    if defined paths set "CMD=!CMD! --paths !paths!"

    :: Default flags
    set "CMD=!CMD! --onefile --windowed sqlmap_gui/main.py"

    echo Running: !CMD!
    call !CMD!
    goto :eof
)

if "%1"=="--activate" (
    echo Activating virtual environment: sqlmap_env\Scripts\activate
    call sqlmap_env\Scripts\activate
    goto :eof
)

:: Default help message
echo Usage:
echo   builder.bat --build         ^(pip install -e .^)
echo   builder.bat --run           ^(python sqlmap_gui^)
echo   builder.bat --exe           ^(build executable with pyinstaller^)
