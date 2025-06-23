@echo off
setlocal enabledelayedexpansion

# PS > where.exe python
set "PYTHON_EXEC=C:\path\to\python.exe" 
set "SRC_DIR=%~dp0src"
set "RUN_DIR=%~dp0run"

echo [%date%%time%] [DEBUG] Python Executable: %PYTHON_EXEC%
echo [%date%%time%] [DEBUG] Source Directory: %SRC_DIR%
echo [%date%%time%] [DEBUG] Run Directory: %RUN_DIR%

if not exist "%RUN_DIR%" mkdir "%RUN_DIR%"

echo.
for %%F in ("%SRC_DIR%\*.py") do (
    set "FILENAME=%%~nF"
    set "SCRIPT_RUNNER=%RUN_DIR%\!FILENAME!.cmd"
    echo [%date%%time%] [INFO] Processing: %%F
    (
        echo @echo off
        echo "%PYTHON_EXEC%" "%%F" %%*
    ) > "!SCRIPT_RUNNER!"
    echo [%date%%time%] [INFO] Created: !SCRIPT_RUNNER!
    echo.
)

echo [DEBUG] Scripts generated in "run" folder.
