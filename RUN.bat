@echo off
title MultiTool Utility v1.0 - Launcher
color 0A
cd /d "%~dp0"

echo.
echo  ╔════════════════════════════════════════════════════════════════╗
echo  ║                                                                ║
echo  ║            MULTI TOOL By.Sobing4413 v1.0 - LAUNCHER            ║
echo  ║     Program serbaguna untuk mempermudah hidupmu yang ribet     ║
echo  ║                                                                ║
echo  ║   GitHub  : https://github.com/SOBING4413                      ║
echo  ║   Discord : https://discord.gg/9nsub2yx4V                      ║
echo  ║                                                                ║
echo  ╚════════════════════════════════════════════════════════════════╝
echo.

:: Cek apakah Python terinstall
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [!] Python tidak ditemukan!
    echo.
    echo  Silakan install Python terlebih dahulu:
    echo  https://www.python.org/downloads/
    echo.
    echo  PENTING: Centang "Add Python to PATH" saat install!
    echo.
    pause
    exit /b
)

echo  [+] Python ditemukan.
echo.

:: Cek apakah dependencies sudah terinstall
python -c "import colorama; import psutil; import requests; import prettytable; import pyfiglet" >nul 2>&1
if %errorlevel% neq 0 (
    echo  [*] Menginstall dependencies...
    echo.
    pip install -r requirements.txt
    echo.
    if %errorlevel% neq 0 (
        echo  [!] Gagal menginstall dependencies!
        echo  Coba jalankan manual: pip install -r requirements.txt
        pause
        exit /b
    )
    echo  [+] Dependencies berhasil diinstall!
    echo.
)

echo  [+] Semua dependencies tersedia.
echo.
echo  [*] Menjalankan MultiTool v1.0...
echo.

:: Jalankan program utama
python multitool.py

:: Jika program selesai
echo.
echo  [*] MultiTool selesai.
pause