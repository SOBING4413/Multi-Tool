"""
power.py - Modul Power Management
Fitur: Shutdown Timer, Restart Timer, Batalkan Jadwal, Lock PC, Sleep/Hibernate
"""

import os
import sys
import time
import ctypes
import threading

from utils.ui import (
    print_header, print_success, print_info, print_warning, print_error,
    get_input, pause, get_color, print_key_value, print_divider,
    loading_animation,
)
from utils.helpers import is_windows, safe_int

from colorama import Fore, Style


def shutdown_timer():
    """Shutdown otomatis dengan timer."""
    print_header("⏻  SHUTDOWN OTOMATIS (TIMER)")

    print_info("Komputer akan dimatikan setelah waktu yang ditentukan.")
    print()
    menit = get_input("Masukkan waktu dalam MENIT: ")
    menit = safe_int(menit, -1)

    if menit <= 0:
        print_error("Waktu harus berupa angka lebih dari 0!")
        pause()
        return

    detik = menit * 60
    print()
    loading_animation("Menjadwalkan shutdown", 0.5)

    if is_windows():
        os.system(
            f'shutdown /s /t {detik} /c "Komputer akan shutdown dalam {menit} menit - MultiTool"'
        )
    else:
        os.system(f"sudo shutdown -h +{menit}")

    print()
    print_success(f"Komputer akan SHUTDOWN dalam {menit} menit ({detik} detik).")
    print_info("Gunakan menu 'Batalkan Shutdown/Restart' untuk membatalkan.")
    pause()


def restart_timer():
    """Restart otomatis dengan timer."""
    print_header("🔄 RESTART OTOMATIS (TIMER)")

    print_info("Komputer akan direstart setelah waktu yang ditentukan.")
    print()
    menit = get_input("Masukkan waktu dalam MENIT: ")
    menit = safe_int(menit, -1)

    if menit <= 0:
        print_error("Waktu harus berupa angka lebih dari 0!")
        pause()
        return

    detik = menit * 60
    print()
    loading_animation("Menjadwalkan restart", 0.5)

    if is_windows():
        os.system(
            f'shutdown /r /t {detik} /c "Komputer akan restart dalam {menit} menit - MultiTool"'
        )
    else:
        os.system(f"sudo shutdown -r +{menit}")

    print()
    print_success(f"Komputer akan RESTART dalam {menit} menit ({detik} detik).")
    print_info("Gunakan menu 'Batalkan Shutdown/Restart' untuk membatalkan.")
    pause()


def cancel_schedule():
    """Batalkan jadwal shutdown/restart."""
    print_header("❌ BATALKAN SHUTDOWN / RESTART")

    loading_animation("Membatalkan jadwal", 0.5)

    if is_windows():
        os.system("shutdown /a")
    else:
        os.system("sudo shutdown -c 2>/dev/null")

    print()
    print_success("Jadwal shutdown/restart telah DIBATALKAN.")
    pause()


def lock_pc():
    """Kunci layar komputer."""
    print_header("🔒 LOCK KOMPUTER")

    print_info("Mengunci komputer dalam 3 detik...")
    print()
    c = get_color()
    for i in range(3, 0, -1):
        print(f"    {c}{Fore.LIGHTYELLOW_EX}⏳ {i}...{Style.RESET_ALL}")
        time.sleep(1)

    if is_windows():
        ctypes.windll.user32.LockWorkStation()
    else:
        os.system("loginctl lock-session 2>/dev/null || xdg-screensaver lock 2>/dev/null")


def sleep_timer():
    """Sleep/Hibernate otomatis dengan timer."""
    print_header("💤 SLEEP / HIBERNATE (TIMER)")

    c = get_color()
    print(f"    {c}[1] 💤 Sleep (Standby)")
    print(f"    [2] ❄️  Hibernate{Style.RESET_ALL}")
    print()
    choice = get_input("Pilih [1-2]: ")

    if choice not in ("1", "2"):
        print_error("Pilihan tidak valid!")
        pause()
        return

    mode_name = "sleep" if choice == "1" else "hibernate"

    menit = get_input("Masukkan waktu dalam MENIT (0 = langsung): ")
    menit = safe_int(menit, -1)

    if menit < 0:
        print_error("Waktu harus berupa angka 0 atau lebih!")
        pause()
        return

    if menit > 0:
        detik = menit * 60
        print()
        print_info(f"Komputer akan {mode_name} dalam {menit} menit...")
        print_info("Tekan Ctrl+C untuk membatalkan.")
        print()

        # Use a non-blocking countdown display
        try:
            for remaining in range(detik, 0, -1):
                mins_left = remaining // 60
                secs_left = remaining % 60
                sys.stdout.write(f"\r    ⏳ Sisa waktu: {mins_left:02d}:{secs_left:02d}  ")
                sys.stdout.flush()
                time.sleep(1)
            print()
        except KeyboardInterrupt:
            print()
            print()
            print_info("Timer dibatalkan oleh user.")
            pause()
            return

    print()
    loading_animation(f"Memulai {mode_name}", 0.5)

    if is_windows():
        if choice == "1":
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        else:
            os.system("shutdown /h")
    else:
        if choice == "1":
            os.system("systemctl suspend")
        else:
            os.system("systemctl hibernate")

    pause()