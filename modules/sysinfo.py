"""
sysinfo.py - Modul System Information & Monitoring
Fitur: Info Sistem, Disk Space, Baterai, Uptime, Monitor Real-Time,
       GPU Info, User Info Detail, Hardware Summary
"""

import os
import sys
import time
import socket
import platform
import getpass
import datetime

import psutil
from colorama import Fore, Style

from utils.ui import (
    print_header, print_success, print_info, print_warning, print_error,
    get_color, get_accent, get_input, pause, print_progress_bar, print_section,
    print_key_value, print_divider, loading_animation,
)
from utils.helpers import run_command, is_windows

try:
    from prettytable import PrettyTable
except ImportError:
    PrettyTable = None


def system_info():
    """Tampilkan info sistem lengkap."""
    print_header("💻 INFO SISTEM KOMPUTER")

    loading_animation("Mengumpulkan info sistem", 0.8)
    print()

    c = get_color()
    a = get_accent()
    uname = platform.uname()

    info_items = [
        ("Nama Komputer", uname.node),
        ("Sistem Operasi", f"{uname.system} {uname.release}"),
        ("Versi OS", uname.version),
        ("Arsitektur", uname.machine),
        ("Processor", uname.processor or platform.processor()),
        ("Username", getpass.getuser()),
        ("Python Version", platform.python_version()),
    ]

    # CPU
    cpu_physical = psutil.cpu_count(logical=False)
    cpu_logical = psutil.cpu_count(logical=True)
    cpu_freq = psutil.cpu_freq()
    info_items.append(("CPU Cores (Fisik)", str(cpu_physical or "N/A")))
    info_items.append(("CPU Cores (Logical)", str(cpu_logical or "N/A")))
    if cpu_freq:
        max_freq = f" (Max: {cpu_freq.max:.0f} MHz)" if cpu_freq.max else ""
        info_items.append(("CPU Frequency", f"{cpu_freq.current:.0f} MHz{max_freq}"))

    # RAM
    ram = psutil.virtual_memory()
    info_items.append(("Total RAM", f"{ram.total / (1024**3):.2f} GB"))
    info_items.append(("RAM Terpakai", f"{ram.used / (1024**3):.2f} GB ({ram.percent}%)"))
    info_items.append(("RAM Tersedia", f"{ram.available / (1024**3):.2f} GB"))

    # Swap
    swap = psutil.swap_memory()
    info_items.append(("Total Swap", f"{swap.total / (1024**3):.2f} GB"))
    info_items.append(("Swap Terpakai", f"{swap.used / (1024**3):.2f} GB ({swap.percent}%)"))

    # Total Storage Summary
    total_storage = 0
    total_used = 0
    total_free = 0
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
            total_storage += usage.total
            total_used += usage.used
            total_free += usage.free
        except (PermissionError, OSError):
            pass
    info_items.append(("Total Storage", f"{total_storage / (1024**3):.2f} GB"))
    info_items.append(("Storage Terpakai", f"{total_used / (1024**3):.2f} GB"))
    info_items.append(("Storage Tersedia", f"{total_free / (1024**3):.2f} GB"))

    if PrettyTable:
        table = PrettyTable()
        table.field_names = ["Item", "Detail"]
        table.align["Item"] = "l"
        table.align["Detail"] = "l"
        for item, detail in info_items:
            table.add_row([item, detail])
        print(f"  {c}{table}{Style.RESET_ALL}")
    else:
        for item, detail in info_items:
            print_key_value(item, detail)

    pause()


def disk_space():
    """Tampilkan informasi ruang disk."""
    print_header("💾 CEK RUANG DISK")

    loading_animation("Mengambil info disk", 0.5)
    print()

    partitions = psutil.disk_partitions()

    total_all = 0
    used_all = 0
    free_all = 0

    if PrettyTable:
        table = PrettyTable()
        table.field_names = ["Drive", "Tipe", "Total (GB)", "Terpakai (GB)", "Sisa (GB)", "Pemakaian"]
        table.align = "r"
        table.align["Drive"] = "l"
        table.align["Tipe"] = "l"
        table.align["Pemakaian"] = "l"

        for part in partitions:
            try:
                usage = psutil.disk_usage(part.mountpoint)
                total_gb = usage.total / (1024**3)
                used_gb = usage.used / (1024**3)
                free_gb = usage.free / (1024**3)
                percent = usage.percent
                bar_len = 20
                filled = int(bar_len * percent / 100)
                bar = "█" * filled + "░" * (bar_len - filled)
                table.add_row([
                    part.mountpoint, part.fstype,
                    f"{total_gb:.1f}", f"{used_gb:.1f}", f"{free_gb:.1f}",
                    f"{bar} {percent}%",
                ])
                total_all += usage.total
                used_all += usage.used
                free_all += usage.free
            except (PermissionError, OSError):
                pass

        print(f"  {get_color()}{table}{Style.RESET_ALL}")
    else:
        for part in partitions:
            try:
                usage = psutil.disk_usage(part.mountpoint)
                total_gb = usage.total / (1024**3)
                used_gb = usage.used / (1024**3)
                free_gb = usage.free / (1024**3)
                pct = usage.percent
                bar_len = 15
                filled = int(bar_len * pct / 100)
                bar = "█" * filled + "░" * (bar_len - filled)
                color = Fore.RED if pct > 90 else (Fore.YELLOW if pct > 70 else Fore.GREEN)
                print(f"    {Fore.CYAN}{part.mountpoint}{Style.RESET_ALL} ({part.fstype})")
                print(f"      {color}[{bar}] {pct}%{Style.RESET_ALL} | Total: {total_gb:.1f}GB | Sisa: {free_gb:.1f}GB")
                total_all += usage.total
                used_all += usage.used
                free_all += usage.free
            except (PermissionError, OSError):
                pass

    # Total summary
    print()
    print_section("RINGKASAN TOTAL STORAGE")
    total_gb = total_all / (1024**3)
    used_gb = used_all / (1024**3)
    free_gb = free_all / (1024**3)
    pct = (used_all / total_all * 100) if total_all > 0 else 0
    bar_len = 30
    filled = int(bar_len * pct / 100)
    bar = "█" * filled + "░" * (bar_len - filled)

    if pct > 90:
        bar_color = Fore.RED
    elif pct > 70:
        bar_color = Fore.YELLOW
    else:
        bar_color = Fore.GREEN

    print_key_value("Total", f"{total_gb:.2f} GB")
    print_key_value("Terpakai", f"{used_gb:.2f} GB")
    print_key_value("Sisa", f"{free_gb:.2f} GB")
    print(f"  {bar_color}    [{bar}] {pct:.1f}%{Style.RESET_ALL}")

    if pct > 90:
        print()
        print_warning("⚠️  Storage hampir penuh! Pertimbangkan untuk membersihkan file.")

    pause()


def battery_status():
    """Tampilkan status baterai."""
    print_header("🔋 CEK STATUS BATERAI")

    battery = psutil.sensors_battery()
    if battery is None:
        print_warning("Baterai tidak terdeteksi. Mungkin ini komputer desktop.")
        pause()
        return

    percent = battery.percent
    plugged = battery.power_plugged
    secs_left = battery.secsleft

    bar_length = 30
    filled = int(bar_length * percent / 100)
    bar = "█" * filled + "░" * (bar_length - filled)

    if percent > 60:
        bar_color = Fore.GREEN
    elif percent > 20:
        bar_color = Fore.YELLOW
    else:
        bar_color = Fore.RED

    print(f"  {bar_color}  🔋 Baterai: [{bar}] {percent}%{Style.RESET_ALL}")
    print()
    print_key_value("Status", "🔌 Charging (sedang di-charge)" if plugged else "🔋 Discharging (tidak di-charge)")

    if secs_left not in (psutil.POWER_TIME_UNLIMITED, psutil.POWER_TIME_UNKNOWN) and secs_left > 0:
        hours = secs_left // 3600
        mins = (secs_left % 3600) // 60
        print_key_value("Sisa Waktu", f"{int(hours)} jam {int(mins)} menit")
    elif plugged:
        print_key_value("Sisa Waktu", "Sedang mengisi daya")
    else:
        print_key_value("Sisa Waktu", "Tidak diketahui")

    if is_windows():
        print()
        print_info("Membuat laporan detail baterai...")
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        report_path = os.path.join(desktop, "battery-report.html")
        os.system(f'powercfg /batteryreport /output "{report_path}" 2>nul')
        if os.path.exists(report_path):
            print_success(f"Laporan disimpan di: {report_path}")
        else:
            print_info("Laporan baterai tidak dapat dibuat (mungkin bukan laptop).")

    pause()


def check_uptime():
    """Tampilkan uptime komputer."""
    print_header("⏱️  CEK UPTIME KOMPUTER")

    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
    now = datetime.datetime.now()
    uptime = now - boot_time

    days = uptime.days
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    print_key_value("🕐 Boot Terakhir", boot_time.strftime('%d %B %Y, %H:%M:%S'))
    print_key_value("⏱️  Uptime", f"{days} hari, {hours} jam, {minutes} menit, {seconds} detik")
    print()

    total_hours = uptime.total_seconds() / 3600
    bar_pct = min(total_hours / 24 * 100, 100)
    bar_len = 30
    filled = int(bar_len * bar_pct / 100)
    bar = "█" * filled + "░" * (bar_len - filled)

    color = Fore.GREEN if total_hours < 12 else (Fore.YELLOW if total_hours < 48 else Fore.RED)
    print(f"    {color}Uptime (24h): [{bar}] {total_hours:.1f} jam{Style.RESET_ALL}")

    if total_hours > 72:
        print()
        print_warning("Komputer sudah menyala lebih dari 3 hari. Pertimbangkan untuk restart.")

    pause()


def realtime_monitor():
    """Monitor CPU, RAM, Network secara real-time."""
    print_header("📊 MONITOR REAL-TIME (CPU, RAM, NETWORK)")

    print_info("Tekan Ctrl+C untuk berhenti")
    print_divider()
    print()

    try:
        while True:
            cpu_percent = psutil.cpu_percent(interval=1)
            ram = psutil.virtual_memory()
            net = psutil.net_io_counters()

            cpu_bar_len = 20
            cpu_filled = int(cpu_bar_len * cpu_percent / 100)
            cpu_bar = "█" * cpu_filled + "░" * (cpu_bar_len - cpu_filled)
            cpu_color = Fore.RED if cpu_percent > 80 else (Fore.YELLOW if cpu_percent > 50 else Fore.GREEN)

            ram_bar_len = 20
            ram_filled = int(ram_bar_len * ram.percent / 100)
            ram_bar = "█" * ram_filled + "░" * (ram_bar_len - ram_filled)
            ram_color = Fore.RED if ram.percent > 80 else (Fore.YELLOW if ram.percent > 50 else Fore.GREEN)

            sent_mb = net.bytes_sent / (1024**2)
            recv_mb = net.bytes_recv / (1024**2)
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")

            sys.stdout.write(f"\r  [{timestamp}]  ")
            sys.stdout.write(f"{cpu_color}CPU [{cpu_bar}] {cpu_percent:5.1f}%{Style.RESET_ALL}  ")
            sys.stdout.write(f"{ram_color}RAM [{ram_bar}] {ram.percent:5.1f}%{Style.RESET_ALL}  ")
            sys.stdout.write(f"{Fore.CYAN}↑{sent_mb:.0f}MB ↓{recv_mb:.0f}MB{Style.RESET_ALL}  ")
            sys.stdout.flush()

    except KeyboardInterrupt:
        print("\n")
        print_info("Monitor dihentikan.")
        pause()


def gpu_info():
    """Tampilkan info GPU / VGA."""
    print_header("🎮 INFO GPU / VGA")

    if not is_windows():
        print_warning("Fitur ini hanya tersedia di Windows.")
        pause()
        return

    loading_animation("Mengambil info GPU", 0.8)
    print()

    # Gunakan PowerShell Get-CimInstance (pengganti wmic yang deprecated)
    result = run_command(
        'powershell -Command "Get-CimInstance Win32_VideoController | '
        'Select-Object Name, DriverVersion, AdapterRAM, VideoModeDescription, '
        'CurrentRefreshRate, Status | Format-List"'
    )

    if result and "[Error" not in result:
        entries = result.split("\n\n")
        gpu_num = 0
        for entry in entries:
            lines = [l.strip() for l in entry.strip().split("\n") if l.strip() and ":" in l]
            if not lines:
                continue
            gpu_num += 1
            print_section(f"GPU #{gpu_num}")
            for line in lines:
                key, val = line.split(":", 1)
                key = key.strip()
                val = val.strip()
                if key == "AdapterRAM" and val.isdigit():
                    ram_bytes = int(val)
                    if ram_bytes > 0:
                        ram_gb = ram_bytes / (1024**3)
                        val = f"{ram_gb:.2f} GB ({val} bytes)"
                    else:
                        val = "N/A (shared memory)"
                print_key_value(key, val)
            print()

        if gpu_num == 0:
            print_warning("Tidak ada GPU yang terdeteksi.")
    else:
        print_warning("Gagal mendapatkan info GPU.")

    # NVIDIA specific
    nvidia_result = run_command(
        "nvidia-smi --query-gpu=name,memory.total,memory.used,memory.free,temperature.gpu,utilization.gpu "
        "--format=csv,noheader,nounits"
    )
    if nvidia_result and "[Error" not in nvidia_result and "not recognized" not in nvidia_result.lower() and "NVIDIA-SMI" not in nvidia_result:
        print()
        print_section("NVIDIA GPU Detail (nvidia-smi)")
        for gpu_line in nvidia_result.strip().split("\n"):
            parts = gpu_line.split(",")
            if len(parts) >= 6:
                print_key_value("GPU Name", parts[0].strip())
                print_key_value("VRAM Total", f"{parts[1].strip()} MB")
                print_key_value("VRAM Used", f"{parts[2].strip()} MB")
                print_key_value("VRAM Free", f"{parts[3].strip()} MB")
                print_key_value("Temperature", f"{parts[4].strip()}°C")
                print_key_value("GPU Usage", f"{parts[5].strip()}%")

    pause()


def _get_folder_size_fast(path, max_depth=2):
    """Hitung ukuran folder dengan batas kedalaman untuk menghindari hang."""
    total_size = 0
    base_depth = path.rstrip(os.sep).count(os.sep)
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            # Batasi kedalaman scan
            current_depth = dirpath.rstrip(os.sep).count(os.sep) - base_depth
            if current_depth >= max_depth:
                dirnames.clear()
                continue
            for f in filenames:
                try:
                    fp = os.path.join(dirpath, f)
                    if not os.path.islink(fp):
                        total_size += os.path.getsize(fp)
                except (OSError, PermissionError):
                    pass
    except (PermissionError, OSError):
        pass
    return total_size


def user_info_detail():
    """Tampilkan info user lengkap."""
    print_header("👤 INFO USER DETAIL")

    loading_animation("Mengambil info user", 0.8)
    print()

    print_section("INFO USER SAAT INI")
    print_key_value("Username", getpass.getuser())
    print_key_value("Home Directory", os.path.expanduser("~"))
    print_key_value("Temp Directory", os.environ.get("TEMP", os.environ.get("TMPDIR", "/tmp")))

    if is_windows():
        print_key_value("Computer Name", os.environ.get("COMPUTERNAME", "N/A"))
        print_key_value("User Domain", os.environ.get("USERDOMAIN", "N/A"))
        print_key_value("User Profile", os.environ.get("USERPROFILE", "N/A"))

        from utils.helpers import is_admin
        admin_status = f"{Fore.GREEN}● Ya{Style.RESET_ALL}" if is_admin() else f"{Fore.YELLOW}● Tidak{Style.RESET_ALL}"
        print(f"    {'Administrator':<20}{admin_status}")

    print()
    print_section("UKURAN FOLDER USER")
    print_info("Menghitung ukuran folder (scan cepat, kedalaman terbatas)...")
    print()

    home = os.path.expanduser("~")
    folders_to_check = [
        ("Desktop", os.path.join(home, "Desktop")),
        ("Documents", os.path.join(home, "Documents")),
        ("Downloads", os.path.join(home, "Downloads")),
        ("Pictures", os.path.join(home, "Pictures")),
        ("Videos", os.path.join(home, "Videos")),
        ("Music", os.path.join(home, "Music")),
    ]

    # AppData di-scan terpisah dengan kedalaman lebih dangkal karena sangat besar
    appdata_path = os.path.join(home, "AppData")

    total_user_size = 0
    for name, path in folders_to_check:
        if os.path.exists(path):
            size = _get_folder_size_fast(path, max_depth=3)
            total_user_size += size
            size_gb = size / (1024**3)
            size_mb = size / (1024**2)

            if size_gb >= 1:
                size_str = f"{size_gb:.2f} GB"
            else:
                size_str = f"{size_mb:.1f} MB"

            bar_pct = min(size_gb / 50 * 100, 100)
            bar_len = 15
            filled = int(bar_len * bar_pct / 100)
            bar = "█" * filled + "░" * (bar_len - filled)

            print(f"    {Fore.CYAN}{name:<12}{Style.RESET_ALL} [{bar}] {size_str}")
        else:
            print(f"    {name:<12} (tidak ditemukan)")

    # AppData - scan dangkal (kedalaman 1 saja)
    if os.path.exists(appdata_path):
        size = _get_folder_size_fast(appdata_path, max_depth=1)
        total_user_size += size
        size_gb = size / (1024**3)
        size_str = f"{size_gb:.2f} GB" if size_gb >= 1 else f"{size / (1024**2):.1f} MB"
        bar_pct = min(size_gb / 50 * 100, 100)
        bar_len = 15
        filled = int(bar_len * bar_pct / 100)
        bar = "█" * filled + "░" * (bar_len - filled)
        print(f"    {Fore.CYAN}{'AppData':<12}{Style.RESET_ALL} [{bar}] {size_str} (estimasi)")

    print()
    total_gb = total_user_size / (1024**3)
    print(f"    {Fore.LIGHTYELLOW_EX}{'TOTAL':<12} {total_gb:.2f} GB (estimasi){Style.RESET_ALL}")

    # All user accounts
    if is_windows():
        print()
        print_section("SEMUA AKUN USER DI KOMPUTER INI")
        result = run_command(
            'powershell -Command "Get-LocalUser | Select-Object Name, Enabled, LastLogon | Format-Table -AutoSize"'
        )
        if result and "[Error" not in result:
            for line in result.split("\n"):
                if line.strip():
                    print(f"    {line}")
        else:
            result = run_command("net user")
            if result and "[Error" not in result:
                for line in result.split("\n"):
                    if line.strip():
                        print(f"    {line}")

    pause()


def hardware_summary():
    """Ringkasan hardware lengkap dalam satu halaman."""
    print_header("🖥️  RINGKASAN HARDWARE LENGKAP")

    loading_animation("Mengumpulkan data hardware", 1.0)
    print()

    uname = platform.uname()

    # OS
    print_section("SISTEM OPERASI")
    print_key_value("OS", f"{uname.system} {uname.release}")
    print_key_value("Versi", uname.version)
    print_key_value("Arsitektur", uname.machine)
    print()

    # CPU
    print_section("PROCESSOR (CPU)")
    print_key_value("Nama", uname.processor or platform.processor())
    print_key_value("Cores Fisik", str(psutil.cpu_count(logical=False) or "N/A"))
    print_key_value("Cores Logical", str(psutil.cpu_count(logical=True) or "N/A"))
    freq = psutil.cpu_freq()
    if freq:
        max_freq = f" (Max: {freq.max:.0f} MHz)" if freq.max else ""
        print_key_value("Frequency", f"{freq.current:.0f} MHz{max_freq}")
    cpu_pct = psutil.cpu_percent(interval=0.5)
    print_key_value("Usage", f"{cpu_pct}%")
    print()

    # RAM
    print_section("MEMORY (RAM)")
    ram = psutil.virtual_memory()
    print_key_value("Total", f"{ram.total / (1024**3):.2f} GB")
    print_key_value("Terpakai", f"{ram.used / (1024**3):.2f} GB ({ram.percent}%)")
    print_key_value("Tersedia", f"{ram.available / (1024**3):.2f} GB")
    bar_len = 25
    filled = int(bar_len * ram.percent / 100)
    bar = "█" * filled + "░" * (bar_len - filled)
    ram_color = Fore.RED if ram.percent > 80 else (Fore.YELLOW if ram.percent > 50 else Fore.GREEN)
    print(f"    {ram_color}[{bar}] {ram.percent}%{Style.RESET_ALL}")
    print()

    # Storage
    print_section("STORAGE (DISK)")
    total_storage = 0
    total_used = 0
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
            total_gb = usage.total / (1024**3)
            free_gb = usage.free / (1024**3)
            total_storage += usage.total
            total_used += usage.used
            pct = usage.percent
            bar_filled = int(15 * pct / 100)
            bar = "█" * bar_filled + "░" * (15 - bar_filled)
            color = Fore.RED if pct > 90 else (Fore.YELLOW if pct > 70 else Fore.GREEN)
            print(f"    {Fore.CYAN}{part.mountpoint}{Style.RESET_ALL} ({part.fstype}): {color}[{bar}]{Style.RESET_ALL} {total_gb:.1f}GB, {free_gb:.1f}GB free ({pct}%)")
        except (PermissionError, OSError):
            pass
    if total_storage > 0:
        print(f"    {Fore.LIGHTYELLOW_EX}Total Storage: {total_storage / (1024**3):.2f} GB{Style.RESET_ALL}")
    print()

    # GPU
    print_section("GPU / VGA")
    if is_windows():
        gpu_result = run_command(
            'powershell -Command "Get-CimInstance Win32_VideoController | Select-Object Name, AdapterRAM | Format-List"'
        )
        if gpu_result and "[Error" not in gpu_result:
            for line in gpu_result.strip().split("\n"):
                line = line.strip()
                if ":" in line:
                    key, val = line.split(":", 1)
                    key = key.strip()
                    val = val.strip()
                    if key == "AdapterRAM" and val.isdigit():
                        ram_bytes = int(val)
                        if ram_bytes > 0:
                            val = f"{ram_bytes / (1024**3):.2f} GB"
                        else:
                            val = "N/A (shared memory)"
                    print_key_value(key, val)
        else:
            print_info("GPU info tidak tersedia.")
    else:
        print_info("GPU info hanya tersedia di Windows.")
    print()

    # Battery
    print_section("BATERAI")
    battery = psutil.sensors_battery()
    if battery:
        pct = battery.percent
        bar_filled = int(15 * pct / 100)
        bar = "█" * bar_filled + "░" * (15 - bar_filled)
        bat_color = Fore.GREEN if pct > 60 else (Fore.YELLOW if pct > 20 else Fore.RED)
        status = "🔌 Charging" if battery.power_plugged else "🔋 Discharging"
        print(f"    {bat_color}[{bar}] {pct}% - {status}{Style.RESET_ALL}")
    else:
        print(f"    Desktop (tidak ada baterai)")
    print()

    # Network
    print_section("NETWORK")
    addrs = psutil.net_if_addrs()
    for iface, addr_list in addrs.items():
        for addr in addr_list:
            if addr.family == socket.AF_INET and addr.address != "127.0.0.1":
                print(f"    {Fore.CYAN}{iface}{Style.RESET_ALL}: {addr.address}")

    # Identitas Perangkat - gunakan PowerShell (bukan wmic yang deprecated)
    if is_windows():
        print()
        print_section("IDENTITAS PERANGKAT")

        # Serial Number via PowerShell
        sn_result = run_command(
            'powershell -Command "(Get-CimInstance Win32_BIOS).SerialNumber"'
        )
        if sn_result and "[Error" not in sn_result:
            print_key_value("Serial Number", sn_result.strip())

        # Model via PowerShell
        model_result = run_command(
            'powershell -Command "(Get-CimInstance Win32_ComputerSystem).Model"'
        )
        if model_result and "[Error" not in model_result:
            print_key_value("Model", model_result.strip())

        # Manufacturer via PowerShell
        mfg_result = run_command(
            'powershell -Command "(Get-CimInstance Win32_ComputerSystem).Manufacturer"'
        )
        if mfg_result and "[Error" not in mfg_result:
            print_key_value("Manufacturer", mfg_result.strip())

    pause()