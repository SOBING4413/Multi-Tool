"""
network.py - Modul Jaringan & Internet
Fitur: Cek IP, IP Real Detail, Flush DNS, Ping, Traceroute, Info Jaringan,
       WiFi Toggle, WiFi Password, Speed Test, DNS Lookup
"""

import os
import re
import time
import socket
import subprocess

import psutil
from colorama import Fore, Style

from utils.ui import (
    print_header, print_success, print_info, print_warning, print_error,
    get_color, get_accent, get_input, pause, print_section, print_divider,
    print_key_value, loading_animation, print_menu_item,
)
from utils.helpers import run_command, is_windows

try:
    import requests as req_lib
except ImportError:
    req_lib = None

try:
    from prettytable import PrettyTable
except ImportError:
    PrettyTable = None


def _sanitize_host(host_input):
    """Sanitasi input hostname/IP untuk mencegah command injection.
    Hanya mengizinkan karakter alfanumerik, titik, strip, dan titik dua (IPv6).
    Returns sanitized string atau None jika tidak valid.
    """
    host = host_input.strip()
    if not host:
        return None
    # Hanya izinkan karakter yang valid untuk hostname/IP
    # a-z, A-Z, 0-9, ., -, : (untuk IPv6)
    if re.match(r'^[a-zA-Z0-9.\-:]+$', host):
        return host
    return None


def check_ip():
    """Cek IP Address lokal dan publik."""
    print_header("🌐 CEK IP ADDRESS")

    # IP Lokal
    print_section("IP ADDRESS LOKAL")
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print_key_value("Hostname", hostname)
        print_key_value("IP Lokal", local_ip)
    except Exception as e:
        print_error(f"Gagal mendapatkan IP lokal: {e}")

    print()

    # Semua Interface
    print_section("SEMUA NETWORK INTERFACE")
    addrs = psutil.net_if_addrs()
    for iface, addr_list in addrs.items():
        for addr in addr_list:
            if addr.family == socket.AF_INET:
                print(f"    {Fore.CYAN}{iface}{Style.RESET_ALL}: {addr.address} (Netmask: {addr.netmask})")

    print()

    # IP Publik
    print_section("IP ADDRESS PUBLIK")
    if req_lib:
        try:
            loading_animation("Mengambil IP publik", 0.5)
            response = req_lib.get("https://api.ipify.org?format=json", timeout=10)
            public_ip = response.json().get("ip", "Tidak ditemukan")
            print_key_value("IP Publik", public_ip)
        except req_lib.exceptions.ConnectionError:
            print_warning("Tidak ada koneksi internet.")
        except req_lib.exceptions.Timeout:
            print_warning("Timeout saat mengambil IP publik.")
        except Exception:
            print_warning("Gagal mendapatkan IP publik.")
    else:
        print_warning("Module 'requests' tidak tersedia.")

    pause()


def ip_real_detail():
    """Cek IP Real dengan detail lengkap (lokasi, ISP, timezone, dll)."""
    print_header("🌍 IP REAL - DETAIL LENGKAP")

    if not req_lib:
        print_error("Module 'requests' tidak tersedia. Install dulu: pip install requests")
        pause()
        return

    loading_animation("Mengambil informasi IP", 1.0)
    print()

    try:
        response = req_lib.get(
            "http://ip-api.com/json/?fields=status,message,continent,country,countryCode,"
            "region,regionName,city,district,zip,lat,lon,timezone,offset,currency,"
            "isp,org,as,asname,mobile,proxy,hosting,query",
            timeout=10,
        )
        data = response.json()

        if data.get("status") == "success":
            print_section("INFORMASI IP PUBLIK")
            print_key_value("🌐 IP Address", data.get("query", "N/A"))
            print()

            print_section("LOKASI")
            print_key_value("🌍 Benua", data.get("continent", "N/A"))
            print_key_value("🏳️  Negara", f"{data.get('country', 'N/A')} ({data.get('countryCode', '')})")
            print_key_value("📍 Provinsi", f"{data.get('regionName', 'N/A')} ({data.get('region', '')})")
            print_key_value("🏙️  Kota", data.get("city", "N/A"))
            district = data.get("district", "")
            if district:
                print_key_value("📌 Kecamatan", district)
            print_key_value("📮 Kode Pos", data.get("zip", "N/A"))
            print_key_value("📐 Koordinat", f"{data.get('lat', 'N/A')}, {data.get('lon', 'N/A')}")
            maps_url = f"https://www.google.com/maps?q={data.get('lat', 0)},{data.get('lon', 0)}"
            print_key_value("🗺️  Google Maps", maps_url)
            print()

            print_section("PROVIDER & JARINGAN")
            print_key_value("🏢 ISP", data.get("isp", "N/A"))
            print_key_value("🏛️  Organisasi", data.get("org", "N/A"))
            print_key_value("🔗 AS Number", data.get("as", "N/A"))
            print_key_value("📡 AS Name", data.get("asname", "N/A"))
            print()

            print_section("DETAIL TAMBAHAN")
            print_key_value("🕐 Timezone", data.get("timezone", "N/A"))
            offset_sec = data.get("offset", 0)
            offset_hours = offset_sec / 3600
            print_key_value("⏰ UTC Offset", f"UTC{'+' if offset_hours >= 0 else ''}{offset_hours:.1f}")
            print_key_value("💰 Mata Uang", data.get("currency", "N/A"))
            print_key_value("📱 Mobile", "Ya" if data.get("mobile") else "Tidak")
            proxy_status = f"{Fore.YELLOW}Ya ⚠️{Style.RESET_ALL}" if data.get("proxy") else f"{Fore.GREEN}Tidak ✅{Style.RESET_ALL}"
            print(f"    {'🔒 Proxy/VPN':<20}{proxy_status}")
            print_key_value("☁️  Hosting/DC", "Ya" if data.get("hosting") else "Tidak")
        else:
            print_error(f"Gagal: {data.get('message', 'Unknown error')}")

    except req_lib.exceptions.ConnectionError:
        print_error("Tidak ada koneksi internet!")
    except Exception as e:
        print_error(f"Error: {e}")

    # MAC Address
    print()
    print_section("MAC ADDRESS (Lokal)")
    addrs = psutil.net_if_addrs()
    for iface, addr_list in addrs.items():
        for addr in addr_list:
            if addr.family == psutil.AF_LINK:
                if addr.address and addr.address != "":
                    print(f"    {Fore.CYAN}{iface}{Style.RESET_ALL}: {addr.address}")

    pause()


def traceroute():
    """Traceroute ke sebuah alamat."""
    print_header("🔀 TRACEROUTE")

    target = get_input("Masukkan IP/Domain (contoh: google.com): ")
    target = _sanitize_host(target)
    if not target:
        print_error("Input tidak valid! Hanya huruf, angka, titik, dan strip yang diizinkan.")
        pause()
        return

    print()
    print_info(f"Traceroute ke {target}...")
    print_info("Ini mungkin memakan waktu beberapa menit...")
    print_divider()
    print()

    if is_windows():
        # Gunakan subprocess untuk keamanan lebih baik
        try:
            result = subprocess.run(
                ["tracert", target],
                capture_output=False, text=True, timeout=120
            )
        except subprocess.TimeoutExpired:
            print_warning("Traceroute timeout (lebih dari 2 menit).")
        except FileNotFoundError:
            print_error("Command tracert tidak ditemukan.")
        except Exception as e:
            print_error(f"Error: {e}")
    else:
        try:
            result = subprocess.run(
                ["traceroute", target],
                capture_output=False, text=True, timeout=120
            )
        except subprocess.TimeoutExpired:
            print_warning("Traceroute timeout (lebih dari 2 menit).")
        except FileNotFoundError:
            print_error("Command traceroute tidak ditemukan. Install: sudo apt install traceroute")
        except Exception as e:
            print_error(f"Error: {e}")

    pause()


def flush_dns():
    """Bersihkan DNS Cache."""
    print_header("🧹 FLUSH DNS CACHE")

    loading_animation("Membersihkan DNS Cache", 0.8)

    if is_windows():
        result = run_command("ipconfig /flushdns")
        if result:
            print(f"    {result}")
    else:
        os.system("sudo systemd-resolve --flush-caches 2>/dev/null || sudo dscacheutil -flushcache 2>/dev/null")

    print()
    print_success("DNS Cache berhasil dibersihkan!")
    print_info("Berguna jika kamu mengalami masalah akses website.")
    pause()


def ping_test():
    """Tes koneksi dengan ping."""
    print_header("📡 TES KECEPATAN KONEKSI (PING)")

    c = get_color()
    print(f"    {c}[1] 🌐 Ping Google (8.8.8.8)")
    print(f"    [2] ☁️  Ping Cloudflare (1.1.1.1)")
    print(f"    [3] 🎯 Ping Custom{Style.RESET_ALL}")
    print()
    choice = get_input("Pilih [1-3]: ")

    targets = {"1": "8.8.8.8", "2": "1.1.1.1"}
    target = targets.get(choice)

    if choice == "3":
        raw_target = get_input("Masukkan IP/Domain: ")
        target = _sanitize_host(raw_target)
        if not target:
            print_error("Input tidak valid! Hanya huruf, angka, titik, dan strip yang diizinkan.")
            pause()
            return
    elif not target:
        print_error("Pilihan tidak valid!")
        pause()
        return

    print()
    print_info(f"Ping ke {target} (10 paket)...")
    print_divider()
    print()

    # Gunakan subprocess untuk keamanan
    try:
        if is_windows():
            subprocess.run(["ping", "-n", "10", target], timeout=60)
        else:
            subprocess.run(["ping", "-c", "10", target], timeout=60)
    except subprocess.TimeoutExpired:
        print_warning("Ping timeout.")
    except FileNotFoundError:
        print_error("Command ping tidak ditemukan.")
    except Exception as e:
        print_error(f"Error: {e}")

    pause()


def network_info():
    """Tampilkan info jaringan lengkap."""
    print_header("📊 INFO JARINGAN LENGKAP")

    print_section("NETWORK INTERFACES")
    net_io = psutil.net_io_counters(pernic=True)
    addrs = psutil.net_if_addrs()

    for iface, addr_list in addrs.items():
        for addr in addr_list:
            if addr.family == socket.AF_INET:
                io = net_io.get(iface)
                sent = f"{io.bytes_sent / (1024**2):.1f} MB" if io else "N/A"
                recv = f"{io.bytes_recv / (1024**2):.1f} MB" if io else "N/A"
                print(f"    {Fore.CYAN}▸ {iface}{Style.RESET_ALL}")
                print(f"      IP: {addr.address} | Netmask: {addr.netmask}")
                print(f"      ↑ Sent: {sent} | ↓ Received: {recv}")
                print()

    if is_windows():
        print_section("WIFI TERSIMPAN")
        result = run_command("netsh wlan show profiles")
        profiles_found = False
        if result and "[Error" not in result:
            for line in result.split("\n"):
                if "All User Profile" in line or "Semua Profil Pengguna" in line:
                    profile = line.split(":")[-1].strip()
                    if profile:
                        print(f"    📶 {profile}")
                        profiles_found = True
        if not profiles_found:
            print_info("Tidak ada WiFi tersimpan atau WiFi adapter tidak tersedia.")
        print()

        print_section("WIFI TERHUBUNG SAAT INI")
        result = run_command("netsh wlan show interfaces")
        connected = False
        if result and "[Error" not in result:
            for line in result.split("\n"):
                line = line.strip()
                if any(key in line for key in ["SSID", "Signal", "Radio type", "Channel", "Authentication"]):
                    print(f"    {line}")
                    connected = True
        if not connected:
            print_info("Tidak terhubung ke WiFi atau WiFi adapter tidak tersedia.")

    pause()


def wifi_toggle():
    """Matikan atau nyalakan WiFi."""
    print_header("📶 MATIKAN / NYALAKAN WIFI")

    if not is_windows():
        print_warning("Fitur ini hanya tersedia di Windows.")
        pause()
        return

    c = get_color()
    print(f"    {c}[1] 📴 Matikan WiFi")
    print(f"    [2] 📶 Nyalakan WiFi")
    print(f"    [3] 📊 Lihat Status Network{Style.RESET_ALL}")
    print()
    choice = get_input("Pilih [1-3]: ")

    if choice == "1":
        loading_animation("Mematikan WiFi", 0.8)
        os.system('netsh interface set interface "Wi-Fi" disabled 2>nul')
        os.system('netsh interface set interface "WiFi" disabled 2>nul')
        print_success("WiFi dimatikan.")
    elif choice == "2":
        loading_animation("Menyalakan WiFi", 0.8)
        os.system('netsh interface set interface "Wi-Fi" enabled 2>nul')
        os.system('netsh interface set interface "WiFi" enabled 2>nul')
        print_success("WiFi dinyalakan.")
    elif choice == "3":
        print()
        result = run_command("netsh interface show interface")
        if result and "[Error" not in result:
            print(f"    {result}")
        else:
            print_warning("Tidak dapat mengambil status network.")
    else:
        print_error("Pilihan tidak valid!")

    pause()


def wifi_passwords():
    """Lihat password WiFi yang tersimpan."""
    print_header("🔑 LIHAT PASSWORD WIFI TERSIMPAN")

    if not is_windows():
        print_warning("Fitur ini hanya tersedia di Windows.")
        pause()
        return

    loading_animation("Mengambil daftar WiFi", 1.0)
    print()

    result = run_command("netsh wlan show profiles")
    profiles = []

    if result and "[Error" not in result:
        for line in result.split("\n"):
            if "All User Profile" in line or "Semua Profil Pengguna" in line:
                profile = line.split(":")[-1].strip()
                if profile:
                    profiles.append(profile)

    if not profiles:
        print_warning("Tidak ada WiFi yang tersimpan atau WiFi adapter tidak tersedia.")
        pause()
        return

    if PrettyTable:
        table = PrettyTable()
        table.field_names = ["No", "Nama WiFi (SSID)", "Password"]
        table.align["Nama WiFi (SSID)"] = "l"
        table.align["Password"] = "l"

        for i, profile in enumerate(profiles, 1):
            detail = run_command(f'netsh wlan show profile name="{profile}" key=clear')
            password = ""
            if detail and "[Error" not in detail:
                for line in detail.split("\n"):
                    if "Key Content" in line or "Konten Kunci" in line:
                        password = line.split(":")[-1].strip()
                        break
            table.add_row([i, profile, password or "(Tidak tersedia)"])

        print(f"  {get_color()}{table}{Style.RESET_ALL}")
    else:
        c = get_color()
        a = get_accent()
        print(f"  {a}{'No':>3} {'Nama WiFi (SSID)':<30} {'Password'}{Style.RESET_ALL}")
        print(f"  {c}{'─' * 60}{Style.RESET_ALL}")
        for i, profile in enumerate(profiles, 1):
            detail = run_command(f'netsh wlan show profile name="{profile}" key=clear')
            password = ""
            if detail and "[Error" not in detail:
                for line in detail.split("\n"):
                    if "Key Content" in line or "Konten Kunci" in line:
                        password = line.split(":")[-1].strip()
                        break
            print(f"  {c}{i:>3} {profile:<30} {password or '(Tidak tersedia)'}{Style.RESET_ALL}")

    pause()


def speed_test():
    """Tes kecepatan internet sederhana."""
    print_header("🚀 TES KECEPATAN INTERNET")

    if not req_lib:
        print_error("Module 'requests' tidak tersedia.")
        pause()
        return

    print_info("Mengunduh file test untuk mengukur kecepatan download...")
    print_info("Ini mungkin memakan waktu beberapa detik...")
    print()

    # Multiple test URLs for reliability - diurutkan dari yang paling reliable
    test_urls = [
        ("https://speed.hetzner.de/10MB.bin", 10),
        ("http://speedtest.tele2.net/10MB.zip", 10),
        ("http://ipv4.download.thinkbroadband.com/10MB.zip", 10),
        ("https://proof.ovh.net/files/10Mb.dat", 10),
    ]

    success = False
    for test_url, expected_mb in test_urls:
        try:
            server_name = test_url.split('/')[2]
            print_info(f"Mencoba server: {server_name}...")
            start = time.time()
            response = req_lib.get(test_url, timeout=30, stream=True)

            # Cek HTTP status
            if response.status_code != 200:
                print_warning(f"Server {server_name} mengembalikan status {response.status_code}")
                continue

            total_bytes = 0
            for chunk in response.iter_content(chunk_size=8192):
                total_bytes += len(chunk)
            elapsed = time.time() - start

            if total_bytes < 1000:
                print_warning(f"File terlalu kecil dari {server_name}, skip...")
                continue

            speed_mbps = (total_bytes * 8) / (elapsed * 1_000_000)
            speed_mbytes = total_bytes / (elapsed * 1_000_000)

            print()
            print_success("Download selesai!")
            print()
            print_key_value("📥 Ukuran File", f"{total_bytes / (1024**2):.2f} MB")
            print_key_value("⏱️  Waktu", f"{elapsed:.2f} detik")
            print_key_value("🚀 Kecepatan", f"{speed_mbps:.2f} Mbps ({speed_mbytes:.2f} MB/s)")

            # Visual speed indicator
            print()
            if speed_mbps > 100:
                print_success("Kecepatan internet kamu SANGAT CEPAT! 🔥")
            elif speed_mbps > 50:
                print_success("Kecepatan internet kamu CEPAT! ⚡")
            elif speed_mbps > 10:
                print_info("Kecepatan internet kamu NORMAL. 👍")
            elif speed_mbps > 1:
                print_warning("Kecepatan internet kamu LAMBAT. 🐌")
            else:
                print_error("Kecepatan internet kamu SANGAT LAMBAT! 🐢")

            success = True
            break

        except req_lib.exceptions.ConnectionError:
            print_warning(f"Tidak bisa terhubung ke {server_name}")
            continue
        except req_lib.exceptions.Timeout:
            print_warning(f"Timeout saat menghubungi {server_name}")
            continue
        except Exception as e:
            print_warning(f"Server gagal: {e}")
            continue

    if not success:
        print_error("Semua server test gagal. Periksa koneksi internet kamu.")

    pause()


def dns_lookup():
    """DNS Lookup - Cek DNS record dari sebuah domain."""
    print_header("🔍 DNS LOOKUP")

    domain = get_input("Masukkan domain (contoh: google.com): ")
    domain = _sanitize_host(domain)
    if not domain:
        print_error("Input tidak valid! Hanya huruf, angka, titik, dan strip yang diizinkan.")
        pause()
        return

    print()
    loading_animation(f"DNS Lookup untuk {domain}", 0.8)
    print()

    # A Record
    print_section("A Record (IPv4)")
    try:
        ips = socket.getaddrinfo(domain, None, socket.AF_INET)
        seen = set()
        for ip in ips:
            addr = ip[4][0]
            if addr not in seen:
                print(f"    {Fore.GREEN}►{Style.RESET_ALL} {addr}")
                seen.add(addr)
        if not seen:
            print_warning("    Tidak ditemukan.")
    except socket.gaierror:
        print_warning("    Tidak ditemukan.")

    # AAAA Record (IPv6)
    print()
    print_section("AAAA Record (IPv6)")
    try:
        ips = socket.getaddrinfo(domain, None, socket.AF_INET6)
        seen = set()
        for ip in ips:
            addr = ip[4][0]
            if addr not in seen:
                print(f"    {Fore.GREEN}►{Style.RESET_ALL} {addr}")
                seen.add(addr)
        if not seen:
            print_warning("    Tidak ditemukan.")
    except socket.gaierror:
        print_warning("    Tidak ditemukan.")

    # nslookup - gunakan subprocess untuk keamanan
    print()
    print_section("NSLookup Detail")
    try:
        result = subprocess.run(
            ["nslookup", domain],
            capture_output=True, text=True, timeout=15
        )
        output = result.stdout.strip()
        if output:
            for line in output.split("\n"):
                if line.strip():
                    print(f"    {line}")
        else:
            print_warning("    NSLookup tidak menghasilkan output.")
    except subprocess.TimeoutExpired:
        print_warning("    NSLookup timeout.")
    except FileNotFoundError:
        print_warning("    NSLookup tidak tersedia.")
    except Exception:
        print_warning("    NSLookup gagal.")

    pause()