param (
    [string]$arg
)

switch ($arg) {
    "--build" {
        Write-Host "Running: pip install -e ."
        pip install -e .
    }
    "--run" {
        Write-Host "Running: sqlmap-gui"
        sqlmap-gui
    }
    "--activate" {
        Write-Host "Activating virtual environment"
        .\sqlmap_env\Scripts\Activate.ps1
    }
    "--exe" {
        $cmd = "pyinstaller --onefile --windowed sqlmap_gui/main.py"
        Write-Host "Running: $cmd"
        Invoke-Expression $cmd
    }
    Default {
        Write-Host "Usage:"
        Write-Host "  builder.ps1 --build      (pip install -e .)"
        Write-Host "  builder.ps1 --run        (sqlmap-gui)"
        Write-Host "  builder.ps1 --activate   (activate virtualenv)"
        Write-Host "  builder.ps1 --exe        (build executable)"
    }
}
