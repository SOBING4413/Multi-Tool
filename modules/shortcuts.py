"""
shortcuts.py - Modul Shortcut & App Launcher
Fitur: Buka Kamera, Calculator, Notepad, Paint, Screenshot, dan lainnya
Shortcut cepat untuk membuka aplikasi bawaan Windows tanpa harus cari manual.
"""

import os
import time
import subprocess

from colorama import Fore, Style

from utils.ui import (
    print_header, print_success, print_info, print_warning, print_error,
    get_color, get_accent, get_input, pause, print_section, print_key_value,
    print_menu_category, print_menu_item, print_menu_end,
)
from utils.helpers import run_command, is_windows


def app_launcher():
    """Buka aplikasi bawaan Windows dengan cepat."""
    print_header("SHORTCUT BUKA APLIKASI")

    if not is_windows():
        print_warning("Fitur ini hanya tersedia di Windows.")
        pause()
        return

    c = get_color()

    apps = [
        ("KAMERA dan MEDIA", [
            ("1", "Kamera (Camera)", "start microsoft.windows.camera:"),
            ("2", "Voice Recorder", "start microsoft.windows.soundrecorder:"),
            ("3", "Media Player", "start mswindowsmusic:"),
            ("4", "Photos", "start ms-photos:"),
            ("5", "Movies dan TV", "start mswindowsvideo:"),
        ]),
        ("UTILITAS", [
            ("6", "Calculator", "calc"),
            ("7", "Notepad", "notepad"),
            ("8", "Paint", "mspaint"),
            ("9", "Snipping Tool", "snippingtool"),
            ("10", "Magnifier", "magnify"),
            ("11", "On-Screen Keyboard", "osk"),
            ("12", "Character Map", "charmap"),
            ("13", "Sticky Notes", "start ms-stickynotes:"),
        ]),
        ("SYSTEM TOOLS", [
            ("14", "Control Panel", "control"),
            ("15", "Settings", "start ms-settings:"),
            ("16", "Task Manager", "taskmgr"),
            ("17", "Device Manager", "devmgmt.msc"),
            ("18", "Disk Management", "diskmgmt.msc"),
            ("19", "System Information", "msinfo32"),
            ("20", "Registry Editor", "regedit"),
            ("21", "Resource Monitor", "resmon"),
            ("22", "Performance Monitor", "perfmon"),
            ("23", "Event Viewer", "eventvwr.msc"),
        ]),
        ("INTERNET dan LAINNYA", [
            ("24", "Microsoft Edge", "start msedge"),
            ("25", "Windows Explorer", "explorer"),
            ("26", "Command Prompt", "start cmd"),
            ("27", "PowerShell", "start powershell"),
            ("28", "Remote Desktop", "mstsc"),
            ("29", "WordPad", "write"),
        ]),
    ]

    for category, items in apps:
        print_menu_category(category)
        for num, label, _ in items:
            print_menu_item(num, label)
        print_menu_end()
        print()

    print(f"    {c}[ 0] Kembali ke Menu Utama{Style.RESET_ALL}")
    print()
    choice = get_input("Pilih aplikasi [0-29]: ")

    if choice == "0":
        return

    for _, items in apps:
        for num, label, cmd in items:
            if choice == num:
                print()
                print_info(f"Membuka {label}...")
                try:
                    if cmd.startswith("start "):
                        os.system(cmd)
                    else:
                        subprocess.Popen(cmd, shell=True)
                    print_success(f"{label} berhasil dibuka!")
                except Exception as e:
                    print_error(f"Gagal membuka {label}: {e}")
                    print_info("Aplikasi mungkin tidak tersedia di komputer ini.")
                pause()
                return

    print_error("Pilihan tidak valid!")
    pause()


def take_screenshot():
    """Ambil screenshot layar."""
    print_header("AMBIL SCREENSHOT")

    if not is_windows():
        print_warning("Fitur ini hanya tersedia di Windows.")
        pause()
        return

    c = get_color()
    print(f"    {c}[1] Buka Snipping Tool (pilih area manual)")
    print(f"    [2] Screenshot seluruh layar (simpan ke Desktop)")
    print(f"    [3] Buka Snip dan Sketch (Win+Shift+S){Style.RESET_ALL}")
    print()
    choice = get_input("Pilih [1-3]: ")

    if choice == "1":
        print_info("Membuka Snipping Tool...")
        os.system("snippingtool 2>nul || start ms-screenclip: 2>nul")
        print_success("Snipping Tool dibuka!")
    elif choice == "2":
        print_info("Mengambil screenshot seluruh layar...")
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        filepath = os.path.join(desktop, filename)

        # Escape backslash untuk PowerShell
        filepath_escaped = filepath.replace("'", "''")
        ps_cmd = (
            'powershell -Command "'
            'Add-Type -AssemblyName System.Windows.Forms;'
            'Add-Type -AssemblyName System.Drawing;'
            '$screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds;'
            '$bitmap = New-Object System.Drawing.Bitmap($screen.Width, $screen.Height);'
            '$graphics = [System.Drawing.Graphics]::FromImage($bitmap);'
            '$graphics.CopyFromScreen($screen.Location, [System.Drawing.Point]::Empty, $screen.Size);'
            f"$bitmap.Save('{filepath_escaped}');"
            '$graphics.Dispose();'
            '$bitmap.Dispose()"'
        )
        os.system(ps_cmd)
        if os.path.exists(filepath):
            print_success(f"Screenshot disimpan di: {filepath}")
        else:
            print_warning("Gagal mengambil screenshot. Coba gunakan Snipping Tool.")
    elif choice == "3":
        print_info("Membuka Snip dan Sketch...")
        os.system("start ms-screenclip: 2>nul")
        print_success("Snip dan Sketch dibuka! Pilih area yang ingin di-screenshot.")
    else:
        print_error("Pilihan tidak valid!")

    pause()


def quick_settings():
    """Shortcut ke berbagai pengaturan Windows."""
    print_header("SHORTCUT PENGATURAN WINDOWS")

    if not is_windows():
        print_warning("Fitur ini hanya tersedia di Windows.")
        pause()
        return

    c = get_color()
    settings_list = [
        ("1", "WiFi dan Internet", "ms-settings:network-wifi"),
        ("2", "Bluetooth", "ms-settings:bluetooth"),
        ("3", "Sound (Suara)", "ms-settings:sound"),
        ("4", "Display (Layar)", "ms-settings:display"),
        ("5", "Battery (Baterai)", "ms-settings:batterysaver"),
        ("6", "Storage (Penyimpanan)", "ms-settings:storagesense"),
        ("7", "Privacy", "ms-settings:privacy"),
        ("8", "Windows Update", "ms-settings:windowsupdate"),
        ("9", "Personalization", "ms-settings:personalization"),
        ("10", "Keyboard", "ms-settings:easeofaccess-keyboard"),
        ("11", "Mouse", "ms-settings:mousetouchpad"),
        ("12", "Phone (Hubungkan HP)", "ms-settings:mobile-devices"),
        ("13", "Date dan Time", "ms-settings:dateandtime"),
        ("14", "Language dan Region", "ms-settings:regionlanguage"),
        ("15", "Email dan Accounts", "ms-settings:emailandaccounts"),
        ("16", "Sign-in Options", "ms-settings:signinoptions"),
        ("17", "Gaming", "ms-settings:gaming-gamebar"),
        ("18", "Accessibility", "ms-settings:easeofaccess"),
        ("19", "Apps dan Features", "ms-settings:appsfeatures"),
        ("20", "Notifications", "ms-settings:notifications"),
    ]

    for num, label, _ in settings_list:
        print(f"    {c}[{num:>2}] {label}{Style.RESET_ALL}")

    print()
    print(f"    {c}[ 0] Kembali{Style.RESET_ALL}")
    print()
    choice = get_input("Pilih [0-20]: ")

    if choice == "0":
        return

    for num, label, uri in settings_list:
        if choice == num:
            print()
            print_info(f"Membuka {label}...")
            os.system(f"start {uri}")
            print_success(f"{label} berhasil dibuka!")
            pause()
            return

    print_error("Pilihan tidak valid!")
    pause()


def system_shortcuts():
    """Shortcut aksi sistem cepat."""
    print_header("AKSI SISTEM CEPAT")

    if not is_windows():
        print_warning("Fitur ini hanya tersedia di Windows.")
        pause()
        return

    c = get_color()
    print(f"    {c}[ 1] Mute/Unmute Volume")
    print(f"    [ 2] Set Volume ke Level Tertentu")
    print(f"    [ 3] Aktifkan Night Light")
    print(f"    [ 4] Airplane Mode")
    print(f"    [ 5] Ganti Resolusi Layar")
    print(f"    [ 6] Buka Clipboard History")
    print(f"    [ 7] Bersihkan Clipboard")
    print(f"    [ 8] Cek Serial Number / Product Key")
    print(f"    [ 9] Buka DirectX Diagnostic (dxdiag)")
    print(f"    [10] System File Checker (SFC)")
    print(f"    [11] Buka God Mode{Style.RESET_ALL}")
    print()
    print(f"    {c}[ 0] Kembali{Style.RESET_ALL}")
    print()
    choice = get_input("Pilih [0-11]: ")

    if choice == "0":
        return

    if choice == "1":
        print_info("Mute/Unmute Volume...")
        ps = 'powershell -Command "(New-Object -ComObject WScript.Shell).SendKeys([char]173)"'
        os.system(ps)
        print_success("Volume di-toggle (mute/unmute)!")

    elif choice == "2":
        level = get_input("Masukkan level volume (0-100): ")
        try:
            level = int(level)
            if 0 <= level <= 100:
                # Gunakan PowerShell dengan nircmd-style approach via SendKeys
                # Pertama mute, lalu set ke level yang diinginkan
                steps = level // 2
                ps = (
                    'powershell -Command "'
                    '$wshShell = New-Object -ComObject WScript.Shell;'
                    f'for ($i = 0; $i -lt 50; $i++) {{ $wshShell.SendKeys([char]174) }};'
                    f'$steps = {steps};'
                    'for ($i = 0; $i -lt $steps; $i++) { $wshShell.SendKeys([char]175) }"'
                )
                os.system(ps)
                print_success(f"Volume diatur ke ~{level}%")
                print_info("Catatan: Metode ini menggunakan simulasi tombol, hasilnya mungkin tidak 100% akurat.")
            else:
                print_error("Level harus antara 0-100!")
        except ValueError:
            print_error("Input tidak valid!")

    elif choice == "3":
        print_info("Membuka pengaturan Night Light...")
        os.system("start ms-settings:nightlight")
        print_success("Pengaturan Night Light dibuka!")

    elif choice == "4":
        print_info("Membuka pengaturan Airplane Mode...")
        os.system("start ms-settings:network-airplanemode")
        print_success("Pengaturan Airplane Mode dibuka!")

    elif choice == "5":
        print_info("Membuka pengaturan Display...")
        os.system("start ms-settings:display")
        print_success("Pengaturan Display dibuka!")

    elif choice == "6":
        print_info("Membuka Clipboard History...")
        print_info("Tips: Tekan Win+V untuk membuka Clipboard History")
        os.system("start ms-settings:clipboard")
        print_success("Pengaturan Clipboard dibuka!")

    elif choice == "7":
        print_info("Membersihkan Clipboard...")
        os.system('powershell -Command "Set-Clipboard -Value $null"')
        print_success("Clipboard berhasil dibersihkan!")

    elif choice == "8":
        print_info("Mengambil Serial Number dan Product Key...")
        print()

        # Serial Number - gunakan PowerShell (bukan wmic yang deprecated)
        print_section("Serial Number (BIOS)")
        sn = run_command(
            'powershell -Command "(Get-CimInstance Win32_BIOS).SerialNumber"'
        )
        if sn and "[Error" not in sn:
            print_key_value("Serial Number", sn.strip())
        else:
            print_info("Serial Number tidak tersedia.")

        print()
        print_section("Product Key Windows")
        pk = run_command(
            'powershell -Command "(Get-CimInstance SoftwareLicensingService).OA3xOriginalProductKey"'
        )
        if pk and "[Error" not in pk and pk.strip():
            print_key_value("Product Key", pk.strip())
        else:
            print_info("Product Key tidak tersedia (mungkin digital license).")

        print()
        print_section("Model Komputer")
        model = run_command(
            'powershell -Command "$cs = Get-CimInstance Win32_ComputerSystem; '
            'Write-Output (\\\"Manufacturer=$($cs.Manufacturer)\\\"); '
            'Write-Output (\\\"Model=$($cs.Model)\\\")"'
        )
        if model and "[Error" not in model:
            for line in model.split("\n"):
                line = line.strip()
                if "=" in line and line.split("=", 1)[1].strip():
                    print(f"    {line}")

    elif choice == "9":
        print_info("Membuka DirectX Diagnostic...")
        os.system("dxdiag")
        print_success("DxDiag dibuka!")

    elif choice == "10":
        print_info("Menjalankan System File Checker (SFC)...")
        print_warning("Ini memerlukan akses Administrator dan mungkin memakan waktu lama.")
        confirm = get_input("Lanjutkan? (Y/N): ")
        if confirm.upper() == "Y":
            os.system("sfc /scannow")
        else:
            print_info("Dibatalkan.")

    elif choice == "11":
        print_info("Membuat shortcut God Mode di Desktop...")
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        god_mode = os.path.join(desktop, "GodMode.{ED7BA470-8E54-465E-825C-99712043E01C}")
        try:
            if not os.path.exists(god_mode):
                os.makedirs(god_mode)
            print_success("God Mode folder dibuat di Desktop!")
            print_info("Buka folder 'GodMode' di Desktop untuk akses semua settings.")
        except Exception as e:
            print_error(f"Gagal membuat God Mode: {e}")

    else:
        print_error("Pilihan tidak valid!")

    pause()