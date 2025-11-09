@echo off
REM Windows Desktop Launcher Batch File
REM Launches the PohLang-based desktop launcher

echo Starting Windows Desktop Launcher...
echo.

cd /d "%~dp0"

REM Check if plhub is in PATH
where plhub >nul 2>nul
if %errorlevel% equ 0 (
    plhub run src\main.poh
) else (
    REM Try using python + plhub.py
    if exist "..\plhub.py" (
        python ..\plhub.py run src\main.poh
    ) else (
        echo ERROR: Could not find plhub or plhub.py
        echo Please ensure PLHub is installed and in your PATH
        pause
        exit /b 1
    )
)

pause
