@echo off
setlocal enabledelayedexpansion

:: Set project base
set "BASE_DIR=%~dp0blogger_autopost"
echo Creating minimal bot tool in: %BASE_DIR%

:: Confirm overwrite
if exist "%BASE_DIR%" (
    echo WARNING: Directory already exists.
    set /p "confirm=Continue and overwrite structure? (y/N): "
    if /i not "!confirm!"=="y" (
        echo Aborting.
        exit /b 1
    )
)

:: === Create minimal folders ===
mkdir "%BASE_DIR%"
mkdir "%BASE_DIR%\templates"
mkdir "%BASE_DIR%\static"
mkdir "%BASE_DIR%\static\css"
mkdir "%BASE_DIR%\static\js"
mkdir "%BASE_DIR%\static\images"

:: === Create minimal files ===
type NUL > "%BASE_DIR%\main.py"
type NUL > "%BASE_DIR%\requirements.txt"
type NUL > "%BASE_DIR%\auth_config.txt"
type NUL > "%BASE_DIR%\templates\index.html"
type NUL > "%BASE_DIR%\static\css\style.css"
type NUL > "%BASE_DIR%\static\js\app.js"

echo.
echo ✅ blogger_autopost minimal bot structure created as per flask_bot_manager standards.
echo.
pause
