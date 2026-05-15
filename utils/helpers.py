"""
helpers.py - Fungsi-fungsi helper umum untuk MultiTool
Berisi utilitas OS, command runner, cek admin, dan formatting.
"""

import os
import re
import ctypes
import subprocess
import sys


def is_admin():
    """Cek apakah program berjalan sebagai Administrator."""
    try:
        if os.name == "nt":
            return ctypes.windll.shell32.IsUserAnAdmin()
        else:
            return os.geteuid() == 0
    except Exception:
        return False


def run_command(cmd, shell=True, timeout=30):
    """Jalankan command dan return output."""
    try:
        result = subprocess.run(
            cmd, shell=shell, capture_output=True, text=True, timeout=timeout
        )
        output = result.stdout.strip()
        if not output and result.stderr.strip():
            return f"[Error: {result.stderr.strip()[:200]}]"
        return output
    except subprocess.TimeoutExpired:
        return "[Timeout - command terlalu lama]"
    except FileNotFoundError:
        return "[Error: Command tidak ditemukan]"
    except Exception as e:
        return f"[Error: {e}]"


def get_size_format(bytes_val, suffix="B"):
    """Konversi bytes ke format yang mudah dibaca (KB, MB, GB, dll)."""
    if bytes_val < 0:
        bytes_val = 0
    for unit in ["", "K", "M", "G", "T", "P"]:
        if abs(bytes_val) < 1024.0:
            return f"{bytes_val:.2f} {unit}{suffix}"
        bytes_val /= 1024.0
    return f"{bytes_val:.2f} E{suffix}"


def safe_int(value, default=0):
    """Konversi string ke integer dengan aman."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value, default=0.0):
    """Konversi string ke float dengan aman."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def is_windows():
    """Cek apakah OS adalah Windows."""
    return os.name == "nt"


def check_module(module_name):
    """Cek apakah sebuah module tersedia."""
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False


def sanitize_host(host_input):
    """Sanitasi input hostname/IP untuk mencegah command injection."""
    if not host_input:
        return None
    host = host_input.strip()
    if not host:
        return None
    # Hanya izinkan karakter yang valid untuk hostname/IP
    if re.match(r'^[a-zA-Z0-9.\-:]+$', host):
        return host
    return None