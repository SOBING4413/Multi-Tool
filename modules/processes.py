"""
processes.py - Modul Manajemen Proses & Startup
Fitur: Lihat Proses, Kill Proses, Startup Manager
"""

import os

import psutil
from colorama import Fore, Style

from utils.ui import (
    print_header, print_success, print_info, print_warning, print_error,
    get_color, get_accent, get_input, pause, print_section, print_divider,
    loading_animation,
)
from utils.helpers import run_command, is_windows

try:
    from prettytable import PrettyTable
except ImportError:
    PrettyTable = None


def running_programs():
    """Tampilkan 20 program yang paling banyak memakai RAM."""
    print_header("📊 PROGRAM BERJALAN (TOP 20 RAM)")

    loading_animation("Mengambil data proses", 0.8)
    print()

    processes = []
    for proc in psutil.process_iter(["pid", "name", "memory_info", "cpu_percent"]):
        try:
            info = proc.info
            ram_mb = info["memory_info"].rss / (1024 * 1024) if info["memory_info"] else 0
            processes.append({
                "pid": info["pid"],
                "name": info["name"] or "Unknown",
                "ram_mb": ram_mb,
                "cpu": info["cpu_percent"] or 0,
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    processes.sort(key=lambda x: x["ram_mb"], reverse=True)
    top_20 = processes[:20]

    if PrettyTable:
        table = PrettyTable()
        table.field_names = ["No", "PID", "Nama Program", "RAM (MB)", "CPU %"]
        table.align["Nama Program"] = "l"
        table.align["RAM (MB)"] = "r"
        table.align["CPU %"] = "r"
        for i, p in enumerate(top_20, 1):
            table.add_row([i, p["pid"], p["name"][:30], f"{p['ram_mb']:.1f}", f"{p['cpu']:.1f}"])
        print(f"  {get_color()}{table}{Style.RESET_ALL}")
    else:
        c = get_color()
        a = get_accent()
        print(f"  {a}{'No':>3} {'PID':>8} {'Nama Program':<30} {'RAM (MB)':>10} {'CPU %':>8}{Style.RESET_ALL}")
        print(f"  {c}{'─' * 63}{Style.RESET_ALL}")
        for i, p in enumerate(top_20, 1):
            ram_color = Fore.RED if p["ram_mb"] > 500 else (Fore.YELLOW if p["ram_mb"] > 200 else Fore.GREEN)
            print(f"  {c}{i:>3} {p['pid']:>8} {p['name'][:30]:<30} {ram_color}{p['ram_mb']:>10.1f}{c}{p['cpu']:>8.1f}{Style.RESET_ALL}")

    # Total RAM usage
    total_ram = sum(p["ram_mb"] for p in processes)
    print()
    print_info(f"Total RAM digunakan oleh semua proses: {total_ram / 1024:.2f} GB")
    print_info(f"Total proses berjalan: {len(processes)}")

    pause()


def kill_process():
    """Cari dan matikan proses."""
    print_header("💀 CARI & MATIKAN PROSES")

    nama = get_input("Masukkan nama program (contoh: chrome): ")
    if not nama.strip():
        print_error("Input tidak boleh kosong!")
        pause()
        return

    print()
    loading_animation("Mencari proses", 0.5)
    print()

    found = []
    for proc in psutil.process_iter(["pid", "name", "memory_info"]):
        try:
            proc_name = proc.info["name"] or ""
            if nama.lower() in proc_name.lower():
                ram_mb = proc.info["memory_info"].rss / (1024 * 1024) if proc.info["memory_info"] else 0
                found.append({"pid": proc.info["pid"], "name": proc_name, "ram_mb": ram_mb})
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    if not found:
        print_warning(f"Tidak ada proses dengan nama '{nama}'.")
        pause()
        return

    print_info(f"Ditemukan {len(found)} proses:")
    print()
    c = get_color()
    for i, p in enumerate(found, 1):
        print(f"    {c}[{i}]{Style.RESET_ALL} PID: {Fore.CYAN}{p['pid']}{Style.RESET_ALL} | {p['name']} | RAM: {p['ram_mb']:.1f} MB")

    print()
    print(f"    {c}[A] Matikan semua")
    print(f"    [N] Batalkan{Style.RESET_ALL}")
    print()
    choice = get_input("Pilih nomor atau [A/N]: ")

    if choice.upper() == "A":
        print()
        for p in found:
            try:
                proc = psutil.Process(p["pid"])
                proc.terminate()
                print_success(f"PID {p['pid']} ({p['name']}) dihentikan.")
            except psutil.NoSuchProcess:
                print_warning(f"PID {p['pid']} sudah tidak ada.")
            except psutil.AccessDenied:
                print_error(f"Akses ditolak untuk PID {p['pid']}. Jalankan sebagai Admin.")
            except Exception as e:
                print_error(f"Gagal menghentikan PID {p['pid']}: {e}")
    elif choice.upper() != "N":
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(found):
                try:
                    proc = psutil.Process(found[idx]["pid"])
                    proc.terminate()
                    print()
                    print_success(f"PID {found[idx]['pid']} ({found[idx]['name']}) dihentikan.")
                except psutil.NoSuchProcess:
                    print_warning(f"Proses sudah tidak ada.")
                except psutil.AccessDenied:
                    print_error("Akses ditolak. Jalankan sebagai Administrator.")
            else:
                print_error("Nomor tidak valid!")
        except ValueError:
            print_error("Input tidak valid!")
    else:
        print_info("Dibatalkan.")

    pause()


def startup_manager():
    """Lihat program startup."""
    print_header("🚀 STARTUP MANAGER")

    if not is_windows():
        print_warning("Fitur ini hanya tersedia di Windows.")
        pause()
        return

    loading_animation("Mengambil data startup", 0.8)
    print()

    print_section("STARTUP FOLDER")
    startup_folder = os.path.join(
        os.environ.get("APPDATA", ""),
        "Microsoft", "Windows", "Start Menu", "Programs", "Startup"
    )

    if os.path.exists(startup_folder):
        items = os.listdir(startup_folder)
        if items:
            for item in items:
                print(f"    📁 {item}")
        else:
            print_info("Startup folder kosong.")
    else:
        print_info("Startup folder tidak ditemukan.")

    print()
    print_section("REGISTRY STARTUP")

    # Gunakan PowerShell (pengganti wmic yang deprecated)
    result = run_command(
        'powershell -Command "'
        '$startupItems = @(); '
        '$paths = @('
        '  \'HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run\','
        '  \'HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\RunOnce\','
        '  \'HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run\','
        '  \'HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\RunOnce\''
        '); '
        'foreach ($path in $paths) { '
        '  if (Test-Path $path) { '
        '    $items = Get-ItemProperty $path -ErrorAction SilentlyContinue; '
        '    if ($items) { '
        '      $items.PSObject.Properties | Where-Object { $_.Name -notlike \'PS*\' } | '
        '      ForEach-Object { Write-Output (\\\"$($_.Name) = $($_.Value)\\\") } '
        '    } '
        '  } '
        '}"'
    )

    if result and "[Error" not in result:
        entries = result.strip().split("\n")
        count = 0
        for entry in entries:
            entry = entry.strip()
            if entry and "=" in entry:
                name, cmd = entry.split("=", 1)
                name = name.strip()
                cmd = cmd.strip()
                if name and cmd:
                    print(f"    {Fore.CYAN}{name}{Style.RESET_ALL}")
                    print(f"      Command: {cmd}")
                    print()
                    count += 1

        if count == 0:
            print_info("Tidak ada entry startup yang ditemukan di Registry.")
    else:
        # Fallback: coba cara lain
        result2 = run_command(
            'powershell -Command "Get-CimInstance Win32_StartupCommand | '
            'Select-Object Name, Command, Location | Format-List"'
        )
        if result2 and "[Error" not in result2:
            entries = result2.split("\n\n")
            count = 0
            for entry in entries:
                lines = [l.strip() for l in entry.strip().split("\n") if l.strip()]
                if lines:
                    has_content = False
                    for line in lines:
                        if ":" in line:
                            key, val = line.split(":", 1)
                            if val.strip():
                                print(f"    {Fore.CYAN}{key.strip()}{Style.RESET_ALL}: {val.strip()}")
                                has_content = True
                    if has_content:
                        count += 1
                        print()

            if count == 0:
                print_info("Tidak ada entry startup yang ditemukan.")
        else:
            print_info("Tidak dapat mengambil data startup.")

    print()
    print_info("Tips: Kurangi program startup untuk mempercepat boot komputer.")
    pause()