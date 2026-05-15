@echo off
:: Batch file ini akan menjalankan MultiTool sebagai Administrator
:: Berguna untuk fitur yang membutuhkan akses admin (WiFi, Firewall, dll)

title MultiTool Utility v1.0 - Admin Launcher

:: Cek apakah sudah admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo  [*] Meminta akses Administrator...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:: Sudah admin, jalankan program
cd /d "%~dp0"
color 0A

echo.
echo  ╔════════════════════════════════════════════════════════════════╗
echo  ║                                                                ║
echo  ║        MULTI TOOL By.Sobing4413 v1.0 - ADMIN LAUNCHER         ║
echo  ║               Berjalan sebagai Administrator                   ║
echo  ║                                                                ║
echo  ║   GitHub  : https://github.com/SOBING4413                     ║
echo  ║   Discord : https://discord.gg/9nsub2yx4V                     ║
echo  ║                                                                ║
echo  ╚════════════════════════════════════════════════════════════════╝
echo.

:: Cek Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [!] Python tidak ditemukan!
    echo  Silakan install Python: https://www.python.org/downloads/
    echo  PENTING: Centang "Add Python to PATH" saat install!
    pause
    exit /b
)

echo  [+] Python ditemukan.
echo  [+] Berjalan sebagai Administrator.
echo.

:: Install dependencies jika belum
python -c "import colorama; import psutil; import requests; import prettytable; import pyfiglet" >nul 2>&1
if %errorlevel% neq 0 (
    echo  [*] Menginstall dependencies...
    pip install -r requirements.txt
    echo.
)

echo  [*] Menjalankan MultiTool v1.0...
echo.

python multitool.py

echo.
pause