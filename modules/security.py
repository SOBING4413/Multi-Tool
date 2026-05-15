"""
security.py - Modul Keamanan & Privasi
Fitur: Cek Firewall, Cek Port Terbuka, Cek Antivirus, Scan Koneksi Mencurigakan,
       Cek User Account, Privacy Cleaner, Security Overview
"""

import os
import socket

import psutil
from colorama import Fore, Style

from utils.ui import (
    print_header, print_success, print_info, print_warning, print_error,
    get_color, get_accent, get_input, pause, print_section, print_divider,
    print_key_value, loading_animation, print_status_badge,
)
from utils.helpers import run_command, is_windows

try:
    from prettytable import PrettyTable
except ImportError:
    PrettyTable = None


def check_firewall():
    """Cek status Windows Firewall."""
    print_header("🛡️  CEK STATUS FIREWALL")

    if not is_windows():
        print_warning("Fitur ini hanya tersedia di Windows.")
        pause()
        return

    loading_animation("Mengecek Firewall", 0.8)
    print()

    profiles = {
        "Domain Profile": "domainprofile",
        "Private Profile": "privateprofile",
        "Public Profile": "publicprofile",
    }

    all_on = True
    for name, profile in profiles.items():
        result = run_command(f"netsh advfirewall show {profile} state")
        is_on = "ON" in result.upper() if result else False
        if not is_on:
            all_on = False
        status_icon = f"{Fore.GREEN}● AKTIF{Style.RESET_ALL}" if is_on else f"{Fore.RED}● TIDAK AKTIF{Style.RESET_ALL}"
        print(f"    {status_icon}  {name}")

    print()
    if all_on:
        print_success("Semua profil firewall aktif! 🛡️")
    else:
        print_warning("Beberapa profil firewall tidak aktif!")
        print_info("Untuk mengaktifkan: netsh advfirewall set allprofiles state on")

    pause()


def check_open_ports():
    """Scan port yang terbuka di komputer."""
    print_header("🔓 CEK PORT TERBUKA")

    loading_animation("Scanning port", 1.0)
    print()

    try:
        connections = psutil.net_connections(kind="inet")
    except psutil.AccessDenied:
        print_error("Akses ditolak! Jalankan sebagai Administrator untuk melihat semua port.")
        pause()
        return

    listening = []
    established = []

    for conn in connections:
        try:
            if conn.status == "LISTEN":
                prog_name = "Unknown"
                try:
                    if conn.pid:
                        prog_name = psutil.Process(conn.pid).name()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
                listening.append({
                    "port": conn.laddr.port,
                    "address": conn.laddr.ip,
                    "pid": conn.pid or 0,
                    "program": prog_name,
                })
            elif conn.status == "ESTABLISHED":
                prog_name = "Unknown"
                try:
                    if conn.pid:
                        prog_name = psutil.Process(conn.pid).name()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
                established.append({
                    "local_port": conn.laddr.port,
                    "remote_ip": conn.raddr.ip if conn.raddr else "N/A",
                    "remote_port": conn.raddr.port if conn.raddr else 0,
                    "pid": conn.pid or 0,
                    "program": prog_name,
                })
        except Exception:
            pass

    # Listening ports
    print_section("PORT YANG LISTENING (Terbuka)")
    if PrettyTable and listening:
        table = PrettyTable()
        table.field_names = ["Port", "Address", "PID", "Program"]
        table.align = "l"
        for p in sorted(listening, key=lambda x: x["port"]):
            table.add_row([p["port"], p["address"], p["pid"], p["program"][:25]])
        print(f"  {get_color()}{table}{Style.RESET_ALL}")
    elif listening:
        for p in sorted(listening, key=lambda x: x["port"]):
            port_val = p["port"]
            addr_val = p["address"]
            pid_val = p["pid"]
            prog_val = p["program"]
            print(f"    Port {port_val:>5} | {addr_val:<15} | PID {pid_val:<6} | {prog_val}")
    else:
        print_info("Tidak ada port yang listening.")

    print()

    # Known risky ports
    risky_ports = {21: "FTP", 23: "Telnet", 445: "SMB", 3389: "RDP", 5900: "VNC", 1433: "MSSQL", 3306: "MySQL"}
    open_risky = [p for p in listening if p["port"] in risky_ports]

    if open_risky:
        print()
        print_warning("⚠️  PORT BERISIKO TERDETEKSI:")
        for p in open_risky:
            service = risky_ports[p["port"]]
            port_val = p["port"]
            prog_val = p["program"]
            print(f"    {Fore.RED}● Port {port_val} ({service}) - Digunakan oleh: {prog_val}{Style.RESET_ALL}")
        print()
        print_info("Tips: Tutup port yang tidak diperlukan untuk meningkatkan keamanan.")
    else:
        print()
        print_success("Tidak ada port berisiko yang terbuka. 👍")

    # Established connections count
    print()
    print_section(f"KONEKSI AKTIF (ESTABLISHED): {len(established)}")
    if established:
        unique_remotes = set()
        for c in established:
            unique_remotes.add(c["remote_ip"])
        print(f"    Terhubung ke {len(unique_remotes)} IP unik")

    pause()


def check_antivirus():
    """Cek status antivirus yang terinstall."""
    print_header("🦠 CEK STATUS ANTIVIRUS")

    if not is_windows():
        print_warning("Fitur ini hanya tersedia di Windows.")
        pause()
        return

    loading_animation("Mengecek antivirus", 0.8)
    print()

    # Check via WMI / CIM
    result = run_command(
        'powershell -Command "Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntiVirusProduct | '
        'Select-Object displayName, productState, pathToSignedProductExe | Format-List"'
    )

    if result and "displayName" in result:
        entries = result.split("\n\n")
        for entry in entries:
            if not entry.strip():
                continue
            lines = entry.strip().split("\n")
            name = ""
            state = ""
            path = ""
            for line in lines:
                if "displayName" in line:
                    name = line.split(":", 1)[-1].strip()
                elif "productState" in line:
                    state = line.split(":", 1)[-1].strip()
                elif "pathToSignedProductExe" in line:
                    path = line.split(":", 1)[-1].strip()

            if name:
                try:
                    state_int = int(state)
                    # productState is a bitmask:
                    # Byte 1 (bits 16-23): Product type
                    # Byte 2 (bits 8-15): Scanner state (0x10 = enabled)
                    # Byte 3 (bits 0-7): Definition state (0x00 = up to date)
                    scanner_state = (state_int >> 12) & 0xF
                    definition_state = (state_int >> 4) & 0xF

                    is_enabled = scanner_state in (1, 3)  # 1=enabled, 3=snoozed but enabled
                    is_updated = definition_state == 0  # 0 = up to date
                except (ValueError, TypeError):
                    is_enabled = None
                    is_updated = None

                print(f"    🛡️  {Fore.CYAN}{name}{Style.RESET_ALL}")
                if is_enabled is not None:
                    status = f"{Fore.GREEN}● Aktif{Style.RESET_ALL}" if is_enabled else f"{Fore.RED}● Tidak Aktif{Style.RESET_ALL}"
                    print(f"       Status   : {status}")
                if is_updated is not None:
                    update = f"{Fore.GREEN}● Terbaru{Style.RESET_ALL}" if is_updated else f"{Fore.YELLOW}● Perlu Update{Style.RESET_ALL}"
                    print(f"       Database : {update}")
                if path:
                    print(f"       Path     : {path}")
                print()
    else:
        print_warning("Tidak dapat mendeteksi antivirus via SecurityCenter2.")

    # Check Windows Defender
    print()
    print_section("WINDOWS DEFENDER STATUS")
    defender_result = run_command(
        'powershell -Command "Get-MpComputerStatus | Select-Object AntivirusEnabled, '
        'RealTimeProtectionEnabled, AntivirusSignatureLastUpdated | Format-List"'
    )
    if defender_result and "AntivirusEnabled" in defender_result:
        for line in defender_result.strip().split("\n"):
            line = line.strip()
            if ":" in line:
                key, val = line.split(":", 1)
                key = key.strip()
                val = val.strip()
                if val.lower() == "true":
                    val = f"{Fore.GREEN}● Ya{Style.RESET_ALL}"
                elif val.lower() == "false":
                    val = f"{Fore.RED}● Tidak{Style.RESET_ALL}"
                print(f"    {key}: {val}")
    else:
        print_info("Windows Defender info tidak tersedia.")

    pause()


def suspicious_connections():
    """Scan koneksi jaringan yang mencurigakan."""
    print_header("🔍 SCAN KONEKSI MENCURIGAKAN")

    loading_animation("Menganalisis koneksi jaringan", 1.0)
    print()

    try:
        connections = psutil.net_connections(kind="inet")
    except psutil.AccessDenied:
        print_error("Akses ditolak! Jalankan sebagai Administrator untuk scan koneksi.")
        pause()
        return

    suspicious = []

    sus_ports = {
        4444: "Metasploit default",
        5555: "Android ADB exploit",
        6666: "IRC Botnet",
        6667: "IRC Botnet",
        31337: "Back Orifice",
        12345: "NetBus",
        27374: "SubSeven",
        1234: "Common backdoor",
        9999: "Common backdoor",
    }

    for conn in connections:
        try:
            if conn.status == "ESTABLISHED" and conn.raddr:
                remote_port = conn.raddr.port
                remote_ip = conn.raddr.ip
                program = ""
                try:
                    if conn.pid:
                        program = psutil.Process(conn.pid).name()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    program = "Unknown"

                reason = ""
                if remote_port in sus_ports:
                    reason = f"Port mencurigakan ({sus_ports[remote_port]})"
                elif remote_ip.startswith("10.") or remote_ip.startswith("192.168.") or remote_ip.startswith("172."):
                    continue
                elif program.lower() in ["cmd.exe", "powershell.exe", "wscript.exe", "cscript.exe", "mshta.exe"]:
                    reason = "Program mencurigakan membuat koneksi keluar"

                if reason:
                    suspicious.append({
                        "remote_ip": remote_ip,
                        "remote_port": remote_port,
                        "local_port": conn.laddr.port,
                        "program": program,
                        "pid": conn.pid,
                        "reason": reason,
                    })
        except Exception:
            pass

    if suspicious:
        print_warning(f"Ditemukan {len(suspicious)} koneksi mencurigakan!")
        print()
        for i, s in enumerate(suspicious, 1):
            s_ip = s["remote_ip"]
            s_port = s["remote_port"]
            s_prog = s["program"]
            s_pid = s["pid"]
            s_reason = s["reason"]
            print(f"    {Fore.RED}[{i}] {s_ip}:{s_port}")
            print(f"       Program : {s_prog} (PID: {s_pid})")
            print(f"       Alasan  : {s_reason}{Style.RESET_ALL}")
            print()
    else:
        print_success("Tidak ada koneksi mencurigakan terdeteksi! 🎉")
        print()

    # Stats
    total = len(connections)
    est = sum(1 for c in connections if c.status == "ESTABLISHED")
    listen = sum(1 for c in connections if c.status == "LISTEN")

    print_section("RINGKASAN KONEKSI")
    print_key_value("Total Koneksi", str(total))
    print_key_value("Established", str(est))
    print_key_value("Listening", str(listen))

    pause()


def check_user_accounts():
    """Cek akun user di komputer."""
    print_header("👤 CEK AKUN USER")

    if not is_windows():
        print_warning("Fitur ini hanya tersedia di Windows.")
        pause()
        return

    loading_animation("Mengecek akun user", 0.8)
    print()

    print_section("DAFTAR AKUN USER")
    result = run_command(
        'powershell -Command "Get-LocalUser | Select-Object Name, Enabled, LastLogon, '
        'PasswordRequired, PasswordLastSet | Format-Table -AutoSize"'
    )

    if result and "[Error" not in result:
        print(f"  {get_color()}{result}{Style.RESET_ALL}")
    else:
        result = run_command("net user")
        if result:
            print(f"  {result}")

    print()
    print_section("AKUN DENGAN HAK ADMINISTRATOR")
    admin_result = run_command(
        'powershell -Command "Get-LocalGroupMember -Group Administrators | Select-Object Name, ObjectClass | Format-Table -AutoSize"'
    )
    if admin_result and "[Error" not in admin_result:
        print(f"  {admin_result}")
    else:
        admin_result = run_command("net localgroup Administrators")
        if admin_result:
            print(f"  {admin_result}")

    print()
    print_info("Tips: Nonaktifkan akun yang tidak digunakan untuk keamanan.")
    print_info("Tips: Pastikan semua akun admin punya password yang kuat.")
    pause()


def privacy_cleaner():
    """Bersihkan jejak privasi (browser cache, recent files, dll)."""
    print_header("🔒 PRIVACY CLEANER")

    print_warning("Fitur ini akan membersihkan jejak aktivitas di komputer.")
    print()

    c = get_color()
    print(f"    {c}[1] 📂 Bersihkan Recent Files (Windows)")
    print(f"    [2] 🖼️  Bersihkan Thumbnail Cache")
    print(f"    [3] 🌐 Bersihkan DNS Cache")
    print(f"    [4] 🗑️  Bersihkan Windows Temp + Prefetch")
    print(f"    [5] 🧹 Bersihkan SEMUA di atas{Style.RESET_ALL}")
    print()
    choice = get_input("Pilih [1-5]: ")

    if choice not in ("1", "2", "3", "4", "5"):
        print_error("Pilihan tidak valid!")
        pause()
        return
    items_cleaned = 0

    # Recent Files
    if choice in ("1", "5"):
        print()
        print_info("Membersihkan Recent Files...")
        recent_path = os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows", "Recent")
        if os.path.exists(recent_path):
            for f in os.listdir(recent_path):
                try:
                    filepath = os.path.join(recent_path, f)
                    if os.path.isfile(filepath):
                        os.remove(filepath)
                        items_cleaned += 1
                except Exception:
                    pass
            print_success("Recent Files dibersihkan.")
        else:
            print_info("Folder Recent tidak ditemukan.")

    # Thumbnail Cache
    if choice in ("2", "5"):
        print()
        print_info("Membersihkan Thumbnail Cache...")
        thumb_path = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Windows", "Explorer")
        if os.path.exists(thumb_path):
            for f in os.listdir(thumb_path):
                if f.startswith("thumbcache"):
                    try:
                        filepath = os.path.join(thumb_path, f)
                        if os.path.isfile(filepath):
                            os.remove(filepath)
                            items_cleaned += 1
                    except Exception:
                        pass
            print_success("Thumbnail Cache dibersihkan.")
        else:
            print_info("Folder Thumbnail tidak ditemukan.")

    # DNS Cache
    if choice in ("3", "5"):
        print()
        print_info("Membersihkan DNS Cache...")
        if is_windows():
            os.system("ipconfig /flushdns >nul 2>&1")
        print_success("DNS Cache dibersihkan.")
        items_cleaned += 1

    # Temp + Prefetch
    if choice in ("4", "5"):
        print()
        print_info("Membersihkan Temp & Prefetch...")
        temp_dirs = [
            os.environ.get("TEMP", ""),
            os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Temp"),
            os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Prefetch"),
        ]
        for temp_dir in temp_dirs:
            if not temp_dir or not os.path.exists(temp_dir):
                continue
            for root, dirs, files in os.walk(temp_dir, topdown=False):
                for name in files:
                    try:
                        os.remove(os.path.join(root, name))
                        items_cleaned += 1
                    except Exception:
                        pass
                for name in dirs:
                    try:
                        os.rmdir(os.path.join(root, name))
                    except Exception:
                        pass
        print_success("Temp & Prefetch dibersihkan.")

    print()
    print_divider("═")
    print()
    print_success(f"Total item dibersihkan: {items_cleaned}")
    print_info("Privasi kamu lebih terjaga sekarang! 🔒")
    pause()


def security_overview():
    """Ringkasan keamanan komputer."""
    print_header("🛡️  RINGKASAN KEAMANAN KOMPUTER")

    checks = []

    # 1. Check Firewall
    print_info("Mengecek Firewall...")
    if is_windows():
        fw_result = run_command("netsh advfirewall show allprofiles state")
        if fw_result and "[Error" not in fw_result:
            fw_on = fw_result.upper().count("ON")
            if fw_on >= 3:
                checks.append(("Firewall", True, "Semua profil aktif"))
            elif fw_on > 0:
                checks.append(("Firewall", False, f"Hanya {fw_on}/3 profil aktif"))
            else:
                checks.append(("Firewall", False, "Tidak aktif!"))
        else:
            checks.append(("Firewall", None, "Tidak dapat dicek"))
    else:
        checks.append(("Firewall", None, "Tidak dapat dicek (bukan Windows)"))

    # 2. Check Antivirus
    print_info("Mengecek Antivirus...")
    if is_windows():
        av_result = run_command(
            'powershell -Command "(Get-MpComputerStatus).AntivirusEnabled"'
        )
        if av_result and "True" in av_result:
            checks.append(("Antivirus", True, "Windows Defender aktif"))
        elif av_result and "False" in av_result:
            checks.append(("Antivirus", False, "Antivirus tidak aktif"))
        else:
            # Fallback: cek via SecurityCenter2
            av_result2 = run_command(
                'powershell -Command "(Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntiVirusProduct).displayName"'
            )
            if av_result2 and "[Error" not in av_result2 and av_result2.strip():
                checks.append(("Antivirus", True, f"Terdeteksi: {av_result2.strip().split(chr(10))[0]}"))
            else:
                checks.append(("Antivirus", False, "Antivirus tidak terdeteksi aktif"))

    # 3. Check Risky Ports
    print_info("Mengecek port berisiko...")
    risky_ports = {21, 23, 445, 3389, 5900, 1433, 3306}
    try:
        connections = psutil.net_connections(kind="inet")
        open_risky = set()
        for conn in connections:
            if conn.status == "LISTEN" and conn.laddr.port in risky_ports:
                open_risky.add(conn.laddr.port)
        if open_risky:
            risky_str = ", ".join(map(str, open_risky))
            checks.append(("Port Berisiko", False, f"Port terbuka: {risky_str}"))
        else:
            checks.append(("Port Berisiko", True, "Tidak ada port berisiko terbuka"))
    except psutil.AccessDenied:
        checks.append(("Port Berisiko", None, "Akses ditolak (perlu Admin)"))

    # 4. Check Password Policy
    print_info("Mengecek kebijakan password...")
    if is_windows():
        pwd_result = run_command("net accounts")
        if pwd_result and "[Error" not in pwd_result:
            min_length = "0"
            for line in pwd_result.split("\n"):
                if "Minimum password length" in line or "Panjang minimum kata sandi" in line:
                    min_length = line.split(":")[-1].strip()
                    break
            try:
                if int(min_length) >= 8:
                    checks.append(("Password Policy", True, f"Minimum {min_length} karakter"))
                else:
                    checks.append(("Password Policy", False, f"Minimum hanya {min_length} karakter (disarankan 8+)"))
            except ValueError:
                checks.append(("Password Policy", None, "Tidak dapat dicek"))
        else:
            checks.append(("Password Policy", None, "Tidak dapat dicek"))

    # 5. Check UAC
    print_info("Mengecek UAC...")
    if is_windows():
        uac_result = run_command(
            'powershell -Command "(Get-ItemProperty HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System).EnableLUA"'
        )
        if uac_result and "1" in uac_result:
            checks.append(("UAC (User Account Control)", True, "Aktif"))
        elif uac_result and "0" in uac_result:
            checks.append(("UAC (User Account Control)", False, "Tidak aktif!"))
        else:
            checks.append(("UAC (User Account Control)", None, "Tidak dapat dicek"))

    # Display results
    print()
    c = get_color()
    a = get_accent()
    print(f"  {c}╔{'═' * 56}╗")
    print(f"  ║  {a}{'HASIL PENGECEKAN KEAMANAN':^52}{c}  ║")
    print(f"  ╚{'═' * 56}╝{Style.RESET_ALL}")
    print()

    score = 0
    total = 0

    for name, status, detail in checks:
        total += 1
        print_status_badge(name, status, detail)
        if status is True:
            score += 1
        print()

    # Security Score
    if total > 0:
        pct = int(score / total * 100)
        bar_len = 30
        filled = int(bar_len * pct / 100)
        bar = "█" * filled + "░" * (bar_len - filled)

        if pct >= 80:
            bar_color = Fore.GREEN
            grade = "BAIK ✅"
        elif pct >= 50:
            bar_color = Fore.YELLOW
            grade = "PERLU PERHATIAN ⚠️"
        else:
            bar_color = Fore.RED
            grade = "BERISIKO ❌"

        print_divider("═")
        print()
        print(f"  {bar_color}  Skor Keamanan: [{bar}] {pct}% - {grade}{Style.RESET_ALL}")

    pause()