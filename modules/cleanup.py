"""
cleanup.py - Modul Pembersihan & Optimasi
Fitur: Bersihkan Temp, Recycle Bin, Disk Benchmark
"""

import os
import time

from colorama import Fore, Style

from utils.ui import (
    print_header, print_success, print_info, print_warning, print_error,
    get_input, pause, print_section, print_key_value, loading_animation,
    print_divider,
)
from utils.helpers import is_windows, get_size_format


def clean_temp():
    """Bersihkan file temporary."""
    print_header("🧹 BERSIHKAN FILE TEMPORARY")

    print_warning("File temporary akan dihapus untuk menghemat ruang disk.")
    print()
    confirm = get_input("Lanjutkan? (Y/N): ")
    if confirm.upper() != "Y":
        print_info("Dibatalkan.")
        pause()
        return

    print()
    total_deleted = 0
    total_failed = 0
    total_size = 0

    temp_dirs = []
    if is_windows():
        temp_dirs = [
            os.environ.get("TEMP", ""),
            os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Temp"),
            os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Prefetch"),
        ]
    else:
        temp_dirs = ["/tmp"]

    for temp_dir in temp_dirs:
        if not temp_dir or not os.path.exists(temp_dir):
            continue

        print_info(f"Membersihkan: {temp_dir}")
        dir_deleted = 0
        dir_size = 0

        for root, dirs, files in os.walk(temp_dir, topdown=False):
            for name in files:
                filepath = os.path.join(root, name)
                try:
                    size = os.path.getsize(filepath)
                    os.remove(filepath)
                    dir_deleted += 1
                    dir_size += size
                except (PermissionError, OSError):
                    total_failed += 1
            for name in dirs:
                dirpath = os.path.join(root, name)
                try:
                    os.rmdir(dirpath)
                except (PermissionError, OSError):
                    pass

        total_deleted += dir_deleted
        total_size += dir_size
        print(f"      {Fore.GREEN}* {dir_deleted} file ({get_size_format(dir_size)}) dihapus{Style.RESET_ALL}")

    print()
    print_divider("=")
    print()
    print_success(f"Total: {total_deleted} file berhasil dihapus ({get_size_format(total_size)})")
    if total_failed > 0:
        print_warning(f"{total_failed} file tidak bisa dihapus (sedang digunakan/dilindungi)")
    print_info("Ini membantu menghemat ruang disk dan mempercepat komputer.")
    pause()


def clean_recycle_bin():
    """Bersihkan Recycle Bin."""
    print_header("BERSIHKAN RECYCLE BIN")

    print_warning("Semua file di Recycle Bin akan dihapus PERMANEN!")
    print_warning("Aksi ini tidak bisa dibatalkan.")
    print()
    confirm = get_input("Yakin ingin melanjutkan? (Y/N): ")

    if confirm.upper() == "Y":
        loading_animation("Membersihkan Recycle Bin", 1.0)
        if is_windows():
            os.system('powershell -Command "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"')
        print()
        print_success("Recycle Bin berhasil dikosongkan!")
    else:
        print_info("Dibatalkan.")

    pause()


def disk_benchmark():
    """Benchmark kecepatan disk sederhana."""
    print_header("BENCHMARK DISK SEDERHANA")

    test_file = os.path.join(os.environ.get("TEMP", "/tmp"), "disk_benchmark_test.tmp")
    test_size_mb = 100
    test_size_bytes = test_size_mb * 1024 * 1024

    print_info(f"Membuat file test {test_size_mb}MB untuk benchmark...")
    print_info("Ini mungkin memakan waktu beberapa detik...")
    print()

    try:
        # Write test
        print_section("WRITE SPEED TEST")
        data = os.urandom(test_size_bytes)
        start = time.time()
        with open(test_file, "wb") as f:
            f.write(data)
        write_time = time.time() - start
        write_speed = test_size_mb / write_time if write_time > 0 else 0

        write_color = Fore.GREEN if write_speed > 500 else (Fore.YELLOW if write_speed > 100 else Fore.RED)
        print(f"    {write_color}Write Speed: {write_speed:.2f} MB/s{Style.RESET_ALL}")
        print(f"    Waktu: {write_time:.2f} detik")
        print()

        # Read test
        print_section("READ SPEED TEST")
        start = time.time()
        with open(test_file, "rb") as f:
            _ = f.read()
        read_time = time.time() - start
        read_speed = test_size_mb / read_time if read_time > 0 else 0

        read_color = Fore.GREEN if read_speed > 500 else (Fore.YELLOW if read_speed > 100 else Fore.RED)
        print(f"    {read_color}Read Speed: {read_speed:.2f} MB/s{Style.RESET_ALL}")
        print(f"    Waktu: {read_time:.2f} detik")

        # Cleanup
        try:
            os.remove(test_file)
        except (PermissionError, OSError):
            pass

        # Summary
        print()
        print_divider("=")
        print()
        print_section("RINGKASAN BENCHMARK")

        # Speed rating
        avg_speed = (write_speed + read_speed) / 2
        if avg_speed > 1000:
            rating = f"{Fore.GREEN}EXCELLENT (NVMe SSD){Style.RESET_ALL}"
        elif avg_speed > 400:
            rating = f"{Fore.GREEN}SANGAT CEPAT (SSD){Style.RESET_ALL}"
        elif avg_speed > 100:
            rating = f"{Fore.YELLOW}NORMAL (SSD/HDD){Style.RESET_ALL}"
        else:
            rating = f"{Fore.RED}LAMBAT (HDD){Style.RESET_ALL}"

        print(f"    Write: {write_speed:.2f} MB/s | Read: {read_speed:.2f} MB/s")
        print(f"    Rating: {rating}")

    except Exception as e:
        print_error(f"Benchmark gagal: {e}")
        try:
            os.remove(test_file)
        except (PermissionError, OSError):
            pass

    print()
    print_success("Benchmark selesai! File test sudah dihapus.")
    pause()