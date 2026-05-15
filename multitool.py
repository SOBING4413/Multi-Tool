"""
MultiTool GUI v2.0 - By Sobing4413
Premium dark GUI menggunakan CustomTkinter
Install dulu: pip install customtkinter psutil requests pillow
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import threading
import subprocess
import os
import sys
import socket
import time
import datetime
import platform

try:
    import customtkinter as ctk
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
except ImportError:
    print("[!] customtkinter tidak ditemukan!")
    print("    Install: pip install customtkinter")
    sys.exit(1)

try:
    import psutil
except ImportError:
    psutil = None

try:
    import requests as req_lib
except ImportError:
    req_lib = None

# ─────────────────────────────────────────────
# THEME / WARNA
# ─────────────────────────────────────────────
COLORS = {
    "bg_dark":     "#0d1117",
    "bg_panel":    "#161b22",
    "bg_card":     "#1c2128",
    "bg_hover":    "#21262d",
    "accent":      "#58a6ff",
    "accent2":     "#3fb950",
    "accent3":     "#f78166",
    "accent4":     "#d29922",
    "text_main":   "#e6edf3",
    "text_dim":    "#8b949e",
    "border":      "#30363d",
    "success":     "#3fb950",
    "warning":     "#d29922",
    "error":       "#f78166",
    "sidebar_sel": "#1f6feb",
}

AUTHOR  = "Sobing4413"
VERSION = "v2.0 GUI"
GITHUB  = "https://github.com/SOBING4413"
DISCORD = "https://discord.gg/9nsub2yx4V"

# ─────────────────────────────────────────────
# HELPER: jalankan perintah shell
# ─────────────────────────────────────────────
def run_cmd(cmd: str, timeout: int = 15) -> str:
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            timeout=timeout, encoding="utf-8", errors="replace"
        )
        return (result.stdout or "") + (result.stderr or "")
    except subprocess.TimeoutExpired:
        return "[Timeout]"
    except Exception as e:
        return f"[Error: {e}]"


def is_windows() -> bool:
    return platform.system() == "Windows"


# ─────────────────────────────────────────────
# OUTPUT BOX HELPER
# ─────────────────────────────────────────────
class OutputBox(ctk.CTkTextbox):
    """Textbox read-only dengan helper print."""

    def __init__(self, master, **kw):
        super().__init__(
            master,
            font=("Consolas", 12),
            text_color=COLORS["text_main"],
            fg_color=COLORS["bg_dark"],
            corner_radius=8,
            wrap="word",
            **kw,
        )
        self.configure(state="disabled")

    def clear(self):
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.configure(state="disabled")

    def write(self, text: str, tag: str = "normal"):
        color_map = {
            "normal":  COLORS["text_main"],
            "success": COLORS["success"],
            "warning": COLORS["warning"],
            "error":   COLORS["error"],
            "accent":  COLORS["accent"],
            "dim":     COLORS["text_dim"],
            "title":   COLORS["accent"],
        }
        color = color_map.get(tag, COLORS["text_main"])
        self.configure(state="normal")
        self.tag_config(tag, foreground=color)
        self.insert("end", text, tag)
        self.see("end")
        self.configure(state="disabled")

    def println(self, text: str = "", tag: str = "normal"):
        self.write(text + "\n", tag)

    def separator(self, char: str = "─", length: int = 60):
        self.println(char * length, "dim")


# ─────────────────────────────────────────────
# SIDEBAR BUTTON
# ─────────────────────────────────────────────
class SidebarBtn(ctk.CTkButton):
    def __init__(self, master, text, icon="", command=None, **kw):
        label = f"  {icon}  {text}" if icon else f"     {text}"
        super().__init__(
            master,
            text=label,
            anchor="w",
            height=38,
            corner_radius=6,
            fg_color="transparent",
            hover_color=COLORS["bg_hover"],
            text_color=COLORS["text_dim"],
            font=("Segoe UI", 12),
            command=command,
            **kw,
        )

    def set_active(self, active: bool):
        if active:
            self.configure(
                fg_color=COLORS["sidebar_sel"],
                text_color=COLORS["text_main"],
            )
        else:
            self.configure(
                fg_color="transparent",
                text_color=COLORS["text_dim"],
            )


# ─────────────────────────────────────────────
# STAT CARD (untuk dashboard)
# ─────────────────────────────────────────────
class StatCard(ctk.CTkFrame):
    def __init__(self, master, title, value, icon, color, **kw):
        super().__init__(
            master, fg_color=COLORS["bg_card"],
            corner_radius=10, border_width=1,
            border_color=COLORS["border"], **kw,
        )
        ctk.CTkLabel(self, text=icon, font=("Segoe UI Emoji", 22),
                     text_color=color).pack(anchor="w", padx=14, pady=(12, 0))
        self.val_lbl = ctk.CTkLabel(
            self, text=value,
            font=("Segoe UI", 18, "bold"),
            text_color=COLORS["text_main"],
        )
        self.val_lbl.pack(anchor="w", padx=14)
        ctk.CTkLabel(self, text=title, font=("Segoe UI", 11),
                     text_color=COLORS["text_dim"]).pack(anchor="w", padx=14, pady=(0, 12))

    def update_value(self, new_val: str):
        self.val_lbl.configure(text=new_val)


# ─────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────
class MultiToolApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"MultiTool {VERSION}  –  by {AUTHOR}")
        self.geometry("1100x680")
        self.minsize(900, 560)
        self.configure(fg_color=COLORS["bg_dark"])

        self._active_btn: SidebarBtn | None = None
        self._pages: dict[str, ctk.CTkFrame] = {}
        self._running_task = False

        self._build_layout()
        self._show_page("dashboard")

    # ── layout skeleton ──────────────────────
    def _build_layout(self):
        # Sidebar
        self.sidebar = ctk.CTkFrame(
            self, width=210, fg_color=COLORS["bg_panel"],
            corner_radius=0,
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Content area
        self.content = ctk.CTkFrame(self, fg_color=COLORS["bg_dark"], corner_radius=0)
        self.content.pack(side="left", fill="both", expand=True)

        self._build_sidebar()
        self._build_pages()

    def _build_sidebar(self):
        # Logo area
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(fill="x", pady=(16, 4), padx=10)

        ctk.CTkLabel(
            logo_frame,
            text="⚡ MultiTool",
            font=("Segoe UI", 16, "bold"),
            text_color=COLORS["accent"],
        ).pack(anchor="w")
        ctk.CTkLabel(
            logo_frame, text=f"by {AUTHOR}  {VERSION}",
            font=("Segoe UI", 9), text_color=COLORS["text_dim"],
        ).pack(anchor="w")

        ctk.CTkFrame(self.sidebar, height=1, fg_color=COLORS["border"]).pack(
            fill="x", padx=10, pady=8
        )

        # Sections
        menus = [
            ("Dashboard",    "🏠",  "dashboard"),
            ("─── POWER ──────────────", "", None),
            ("Shutdown Timer",  "⏻",  "shutdown"),
            ("Restart Timer",   "🔄", "restart"),
            ("Lock PC",         "🔒", "lock"),
            ("Sleep/Hibernate", "💤", "sleep"),
            ("─── INFO ───────────────", "", None),
            ("System Info",     "💻", "sysinfo"),
            ("Disk Space",      "💾", "disk"),
            ("Battery",         "🔋", "battery"),
            ("─── NETWORK ────────────", "", None),
            ("Cek IP",          "🌐", "checkip"),
            ("IP Detail",       "🌍", "ipdetail"),
            ("Ping Test",       "📡", "ping"),
            ("Speed Test",      "🚀", "speedtest"),
            ("Flush DNS",       "🧹", "flushdns"),
            ("─── PROSES ─────────────", "", None),
            ("Running Processes","📊", "processes"),
            ("Kill Process",    "💀", "kill"),
            ("─── CLEANUP ────────────", "", None),
            ("Clean Temp",      "🗑️",  "cleantemp"),
            ("Disk Benchmark",  "⚡", "benchmark"),
            ("─── SECURITY ───────────", "", None),
            ("Firewall Status", "🛡️",  "firewall"),
            ("Open Ports",      "🔓", "ports"),
            ("WiFi Passwords",  "🔑", "wifipass"),
        ]

        self._btns: dict[str, SidebarBtn] = {}
        scroll = ctk.CTkScrollableFrame(
            self.sidebar, fg_color="transparent", scrollbar_button_color=COLORS["border"]
        )
        scroll.pack(fill="both", expand=True, padx=4)

        for label, icon, page_key in menus:
            if page_key is None:
                # section divider label
                ctk.CTkLabel(
                    scroll, text=label,
                    font=("Segoe UI", 9, "bold"),
                    text_color=COLORS["text_dim"],
                    anchor="w",
                ).pack(fill="x", padx=8, pady=(8, 0))
                continue
            btn = SidebarBtn(
                scroll, text=label, icon=icon,
                command=lambda k=page_key: self._show_page(k),
            )
            btn.pack(fill="x", pady=1)
            self._btns[page_key] = btn

        # Bottom info
        ctk.CTkFrame(self.sidebar, height=1, fg_color=COLORS["border"]).pack(
            fill="x", padx=10, pady=8
        )
        ctk.CTkLabel(
            self.sidebar, text=f"GitHub: {GITHUB}",
            font=("Segoe UI", 8), text_color=COLORS["text_dim"],
            wraplength=190, justify="left",
        ).pack(anchor="w", padx=10, pady=(0, 6))

    # ── pages ────────────────────────────────
    def _build_pages(self):
        self._pages["dashboard"] = self._make_dashboard()
        self._pages["shutdown"]  = self._make_timer_page("shutdown")
        self._pages["restart"]   = self._make_timer_page("restart")
        self._pages["lock"]      = self._make_lock_page()
        self._pages["sleep"]     = self._make_sleep_page()
        self._pages["sysinfo"]   = self._make_output_page("💻 System Info",   self._run_sysinfo)
        self._pages["disk"]      = self._make_output_page("💾 Disk Space",     self._run_disk)
        self._pages["battery"]   = self._make_output_page("🔋 Battery Status", self._run_battery)
        self._pages["checkip"]   = self._make_output_page("🌐 Cek IP",         self._run_checkip)
        self._pages["ipdetail"]  = self._make_output_page("🌍 IP Detail",      self._run_ipdetail)
        self._pages["ping"]      = self._make_ping_page()
        self._pages["speedtest"] = self._make_output_page("🚀 Speed Test",     self._run_speedtest)
        self._pages["flushdns"]  = self._make_output_page("🧹 Flush DNS",      self._run_flushdns)
        self._pages["processes"] = self._make_output_page("📊 Running Processes", self._run_processes)
        self._pages["kill"]      = self._make_kill_page()
        self._pages["cleantemp"] = self._make_confirm_page(
            "🗑️  Clean Temp Files",
            "Hapus semua file temporary untuk menghemat ruang disk.",
            self._run_cleantemp,
        )
        self._pages["benchmark"] = self._make_output_page("⚡ Disk Benchmark", self._run_benchmark)
        self._pages["firewall"]  = self._make_output_page("🛡️  Firewall Status", self._run_firewall)
        self._pages["ports"]     = self._make_output_page("🔓 Open Ports",     self._run_ports)
        self._pages["wifipass"]  = self._make_output_page("🔑 WiFi Passwords", self._run_wifipass)

    def _show_page(self, key: str):
        if key not in self._pages:
            return
        for p in self._pages.values():
            p.pack_forget()
        self._pages[key].pack(fill="both", expand=True, padx=16, pady=16)

        if self._active_btn:
            self._active_btn.set_active(False)
        if key in self._btns:
            self._btns[key].set_active(True)
            self._active_btn = self._btns[key]

    # ── PAGE: Dashboard ───────────────────────
    def _make_dashboard(self) -> ctk.CTkFrame:
        p = ctk.CTkFrame(self.content, fg_color="transparent")

        # Title
        ctk.CTkLabel(
            p, text="Dashboard",
            font=("Segoe UI", 22, "bold"),
            text_color=COLORS["text_main"],
        ).pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(
            p, text="Selamat datang di MultiTool – ringkasan sistem kamu",
            font=("Segoe UI", 12), text_color=COLORS["text_dim"],
        ).pack(anchor="w", pady=(0, 16))

        # Stat cards grid
        cards_frame = ctk.CTkFrame(p, fg_color="transparent")
        cards_frame.pack(fill="x")
        cards_frame.columnconfigure((0, 1, 2, 3), weight=1)

        self._card_cpu  = StatCard(cards_frame, "CPU Usage",    "–",   "🖥️",  COLORS["accent"])
        self._card_ram  = StatCard(cards_frame, "RAM Usage",    "–",   "🧠", COLORS["accent2"])
        self._card_disk = StatCard(cards_frame, "Disk C: Used", "–",   "💾", COLORS["accent4"])
        self._card_bat  = StatCard(cards_frame, "Battery",      "–",   "🔋", COLORS["accent3"])

        for i, card in enumerate([self._card_cpu, self._card_ram, self._card_disk, self._card_bat]):
            card.grid(row=0, column=i, padx=6, pady=0, sticky="nsew")

        # Refresh button
        ctk.CTkButton(
            p, text="🔄  Refresh Stats",
            width=140, height=32,
            fg_color=COLORS["bg_card"],
            hover_color=COLORS["bg_hover"],
            text_color=COLORS["accent"],
            font=("Segoe UI", 12),
            border_width=1,
            border_color=COLORS["border"],
            command=self._refresh_dashboard,
        ).pack(anchor="w", pady=(12, 0))

        # System summary box
        ctk.CTkLabel(
            p, text="System Summary",
            font=("Segoe UI", 13, "bold"),
            text_color=COLORS["text_main"],
        ).pack(anchor="w", pady=(20, 6))

        self._dash_out = OutputBox(p)
        self._dash_out.pack(fill="both", expand=True)

        # Auto-load
        self.after(200, self._refresh_dashboard)
        return p

    def _refresh_dashboard(self):
        def task():
            # Cards
            if psutil:
                cpu  = psutil.cpu_percent(interval=0.5)
                ram  = psutil.virtual_memory()
                disk = psutil.disk_usage("C:\\" if is_windows() else "/")
                bat  = psutil.sensors_battery()

                self._card_cpu.update_value(f"{cpu:.1f}%")
                self._card_ram.update_value(
                    f"{ram.used / 1e9:.1f} / {ram.total / 1e9:.1f} GB"
                )
                self._card_disk.update_value(
                    f"{disk.used / 1e9:.1f} / {disk.total / 1e9:.1f} GB"
                )
                bat_txt = f"{bat.percent:.0f}% {'⚡' if bat.power_plugged else '🔋'}" if bat else "N/A"
                self._card_bat.update_value(bat_txt)

            # Summary
            self._dash_out.clear()
            out = self._dash_out
            out.separator("═")
            out.println(f"  Waktu    : {datetime.datetime.now().strftime('%A, %d %B %Y  %H:%M:%S')}", "accent")
            out.println(f"  OS       : {platform.system()} {platform.release()} ({platform.architecture()[0]})", "normal")
            out.println(f"  Hostname : {socket.gethostname()}", "normal")
            out.println(f"  Python   : {platform.python_version()}", "normal")
            out.separator()

            if psutil:
                cpu_count = psutil.cpu_count(logical=False)
                cpu_log   = psutil.cpu_count(logical=True)
                ram       = psutil.virtual_memory()
                swap      = psutil.swap_memory()

                out.println(f"\n  CPU Cores    : {cpu_count} physical, {cpu_log} logical", "normal")
                out.println(f"  CPU Usage    : {psutil.cpu_percent(interval=0.2):.1f}%", "normal")
                out.println(f"  RAM Total    : {ram.total / 1e9:.2f} GB", "normal")
                out.println(f"  RAM Used     : {ram.used / 1e9:.2f} GB  ({ram.percent:.1f}%)", "normal")
                out.println(f"  Swap Used    : {swap.used / 1e9:.2f} GB  ({swap.percent:.1f}%)", "normal")

                # Top 5 processes
                out.println()
                out.separator()
                out.println("  Top 5 Proses (RAM)", "accent")
                out.separator()
                procs = sorted(
                    psutil.process_iter(["name", "memory_info"]),
                    key=lambda p: p.info["memory_info"].rss if p.info["memory_info"] else 0,
                    reverse=True,
                )[:5]
                for i, pr in enumerate(procs, 1):
                    ram_mb = pr.info["memory_info"].rss / 1e6 if pr.info["memory_info"] else 0
                    out.println(f"  {i}. {pr.info['name'][:30]:<30}  {ram_mb:>8.1f} MB", "normal")
            out.separator("═")
        threading.Thread(target=task, daemon=True).start()

    # ── PAGE FACTORY: generic output ─────────
    def _make_output_page(self, title: str, run_fn) -> ctk.CTkFrame:
        p = ctk.CTkFrame(self.content, fg_color="transparent")

        header = ctk.CTkFrame(p, fg_color="transparent")
        header.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            header, text=title,
            font=("Segoe UI", 18, "bold"),
            text_color=COLORS["text_main"],
        ).pack(side="left")

        btn_run = ctk.CTkButton(
            header, text="▶  Jalankan",
            width=130, height=32,
            fg_color=COLORS["accent"],
            hover_color="#4493e0",
            font=("Segoe UI", 12, "bold"),
            command=lambda: self._threaded(run_fn, out, btn_run),
        )
        btn_run.pack(side="right")

        btn_clear = ctk.CTkButton(
            header, text="✕  Clear",
            width=90, height=32,
            fg_color=COLORS["bg_card"],
            hover_color=COLORS["bg_hover"],
            text_color=COLORS["text_dim"],
            border_width=1, border_color=COLORS["border"],
            font=("Segoe UI", 12),
            command=lambda: out.clear(),
        )
        btn_clear.pack(side="right", padx=(0, 8))

        out = OutputBox(p)
        out.pack(fill="both", expand=True)
        return p

    def _make_confirm_page(self, title: str, desc: str, run_fn) -> ctk.CTkFrame:
        p = ctk.CTkFrame(self.content, fg_color="transparent")

        ctk.CTkLabel(p, text=title,
                     font=("Segoe UI", 18, "bold"),
                     text_color=COLORS["text_main"]).pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(p, text=desc,
                     font=("Segoe UI", 12), text_color=COLORS["text_dim"]).pack(anchor="w", pady=(0, 14))

        header = ctk.CTkFrame(p, fg_color="transparent")
        header.pack(fill="x", pady=(0, 12))

        btn_run = ctk.CTkButton(
            header, text="⚠️  Jalankan Sekarang",
            width=180, height=36,
            fg_color=COLORS["accent4"],
            hover_color="#c08010",
            font=("Segoe UI", 12, "bold"),
            command=lambda: self._threaded(run_fn, out, btn_run),
        )
        btn_run.pack(side="left")

        btn_clear = ctk.CTkButton(
            header, text="✕  Clear",
            width=90, height=36,
            fg_color=COLORS["bg_card"],
            hover_color=COLORS["bg_hover"],
            text_color=COLORS["text_dim"],
            border_width=1, border_color=COLORS["border"],
            font=("Segoe UI", 12),
            command=lambda: out.clear(),
        )
        btn_clear.pack(side="left", padx=(8, 0))

        out = OutputBox(p)
        out.pack(fill="both", expand=True)
        return p

    # ── PAGE: Timer (shutdown / restart) ──────
    def _make_timer_page(self, mode: str) -> ctk.CTkFrame:
        p = ctk.CTkFrame(self.content, fg_color="transparent")
        icon  = "⏻" if mode == "shutdown" else "🔄"
        title = f"{icon}  {'Shutdown' if mode == 'shutdown' else 'Restart'} Timer"

        ctk.CTkLabel(p, text=title,
                     font=("Segoe UI", 18, "bold"),
                     text_color=COLORS["text_main"]).pack(anchor="w", pady=(0, 6))
        ctk.CTkLabel(p, text="Jadwalkan shutdown/restart otomatis setelah waktu tertentu.",
                     font=("Segoe UI", 12), text_color=COLORS["text_dim"]).pack(anchor="w", pady=(0, 20))

        row = ctk.CTkFrame(p, fg_color="transparent")
        row.pack(anchor="w")

        ctk.CTkLabel(row, text="Waktu (menit):", font=("Segoe UI", 12),
                     text_color=COLORS["text_main"]).pack(side="left", padx=(0, 10))
        entry = ctk.CTkEntry(row, width=100, height=36,
                             fg_color=COLORS["bg_card"],
                             border_color=COLORS["border"],
                             font=("Segoe UI", 13))
        entry.pack(side="left")
        entry.insert(0, "30")

        out = OutputBox(p, height=160)
        out.pack(fill="x", pady=(16, 0))

        def run():
            txt = entry.get().strip()
            if not txt.isdigit() or int(txt) <= 0:
                out.clear(); out.println("⚠️  Masukkan angka menit yang valid!", "error")
                return
            mnt = int(txt)
            sec = mnt * 60
            out.clear()
            if mode == "shutdown":
                if is_windows():
                    os.system(f'shutdown /s /t {sec} /c "Shutdown oleh MultiTool"')
                else:
                    os.system(f"sudo shutdown -h +{mnt}")
                out.println(f"✅  Shutdown dijadwalkan dalam {mnt} menit.", "success")
            else:
                if is_windows():
                    os.system(f'shutdown /r /t {sec} /c "Restart oleh MultiTool"')
                else:
                    os.system(f"sudo shutdown -r +{mnt}")
                out.println(f"✅  Restart dijadwalkan dalam {mnt} menit.", "success")
            out.println("Gunakan halaman ini lagi dan klik 'Batalkan' untuk membatalkan.", "dim")

        def cancel():
            out.clear()
            if is_windows():
                os.system("shutdown /a")
            else:
                os.system("sudo shutdown -c 2>/dev/null")
            out.println("❌  Jadwal dibatalkan.", "warning")

        btn_row = ctk.CTkFrame(p, fg_color="transparent")
        btn_row.pack(anchor="w", pady=(12, 0))

        ctk.CTkButton(
            btn_row, text="▶  Jadwalkan",
            width=140, height=36,
            fg_color=COLORS["accent3"],
            hover_color="#d06050",
            font=("Segoe UI", 12, "bold"),
            command=run,
        ).pack(side="left")

        ctk.CTkButton(
            btn_row, text="✕  Batalkan",
            width=120, height=36,
            fg_color=COLORS["bg_card"],
            hover_color=COLORS["bg_hover"],
            text_color=COLORS["text_dim"],
            border_width=1, border_color=COLORS["border"],
            font=("Segoe UI", 12),
            command=cancel,
        ).pack(side="left", padx=(8, 0))

        return p

    # ── PAGE: Lock ────────────────────────────
    def _make_lock_page(self) -> ctk.CTkFrame:
        p = ctk.CTkFrame(self.content, fg_color="transparent")
        ctk.CTkLabel(p, text="🔒  Lock PC",
                     font=("Segoe UI", 18, "bold"),
                     text_color=COLORS["text_main"]).pack(anchor="w", pady=(0, 6))
        ctk.CTkLabel(p, text="Kunci layar komputer segera.",
                     font=("Segoe UI", 12), text_color=COLORS["text_dim"]).pack(anchor="w", pady=(0, 20))

        out = OutputBox(p, height=100)
        out.pack(fill="x", pady=(0, 12))

        def do_lock():
            out.clear()
            out.println("🔒  Mengunci komputer...", "warning")
            if is_windows():
                import ctypes
                ctypes.windll.user32.LockWorkStation()
            else:
                os.system("loginctl lock-session 2>/dev/null")
            out.println("Komputer dikunci.", "success")

        ctk.CTkButton(
            p, text="🔒  Lock Sekarang",
            width=160, height=40,
            fg_color=COLORS["accent4"],
            hover_color="#c08010",
            font=("Segoe UI", 13, "bold"),
            command=do_lock,
        ).pack(anchor="w")
        return p

    # ── PAGE: Sleep ───────────────────────────
    def _make_sleep_page(self) -> ctk.CTkFrame:
        p = ctk.CTkFrame(self.content, fg_color="transparent")
        ctk.CTkLabel(p, text="💤  Sleep / Hibernate",
                     font=("Segoe UI", 18, "bold"),
                     text_color=COLORS["text_main"]).pack(anchor="w", pady=(0, 6))

        mode_var = ctk.StringVar(value="sleep")
        row_mode = ctk.CTkFrame(p, fg_color="transparent")
        row_mode.pack(anchor="w", pady=(0, 10))
        ctk.CTkRadioButton(row_mode, text="💤 Sleep", variable=mode_var, value="sleep",
                           text_color=COLORS["text_main"],
                           fg_color=COLORS["accent"]).pack(side="left", padx=(0, 20))
        ctk.CTkRadioButton(row_mode, text="❄️  Hibernate", variable=mode_var, value="hibernate",
                           text_color=COLORS["text_main"],
                           fg_color=COLORS["accent"]).pack(side="left")

        out = OutputBox(p, height=100)
        out.pack(fill="x", pady=(10, 12))

        def do_sleep():
            mode = mode_var.get()
            out.clear()
            out.println(f"Memulai {mode}...", "warning")
            if is_windows():
                if mode == "sleep":
                    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
                else:
                    os.system("shutdown /h")
            else:
                cmd = "systemctl suspend" if mode == "sleep" else "systemctl hibernate"
                os.system(cmd)

        ctk.CTkButton(
            p, text="▶  Jalankan",
            width=140, height=36,
            fg_color=COLORS["accent"],
            hover_color="#4493e0",
            font=("Segoe UI", 12, "bold"),
            command=do_sleep,
        ).pack(anchor="w")
        return p

    # ── PAGE: Ping ────────────────────────────
    def _make_ping_page(self) -> ctk.CTkFrame:
        p = ctk.CTkFrame(self.content, fg_color="transparent")
        ctk.CTkLabel(p, text="📡  Ping Test",
                     font=("Segoe UI", 18, "bold"),
                     text_color=COLORS["text_main"]).pack(anchor="w", pady=(0, 6))

        row = ctk.CTkFrame(p, fg_color="transparent")
        row.pack(anchor="w", pady=(0, 12))

        ctk.CTkLabel(row, text="Target:", font=("Segoe UI", 12),
                     text_color=COLORS["text_main"]).pack(side="left", padx=(0, 8))
        entry = ctk.CTkEntry(row, width=240, height=34,
                             fg_color=COLORS["bg_card"],
                             border_color=COLORS["border"],
                             font=("Segoe UI", 12),
                             placeholder_text="google.com atau IP")
        entry.pack(side="left")
        entry.insert(0, "google.com")

        out = OutputBox(p)
        out.pack(fill="both", expand=True)

        def run():
            target = entry.get().strip()
            if not target:
                return
            out.clear()
            out.println(f"Pinging {target}...\n", "accent")

            def task():
                cmd = f"ping {'-n' if is_windows() else '-c'} 4 {target}"
                result = run_cmd(cmd, timeout=20)
                out.println(result)
            threading.Thread(target=task, daemon=True).start()

        ctk.CTkButton(
            row, text="▶  Ping",
            width=100, height=34,
            fg_color=COLORS["accent"],
            hover_color="#4493e0",
            font=("Segoe UI", 12, "bold"),
            command=run,
        ).pack(side="left", padx=(10, 0))

        return p

    # ── PAGE: Kill process ────────────────────
    def _make_kill_page(self) -> ctk.CTkFrame:
        p = ctk.CTkFrame(self.content, fg_color="transparent")
        ctk.CTkLabel(p, text="💀  Kill Process",
                     font=("Segoe UI", 18, "bold"),
                     text_color=COLORS["text_main"]).pack(anchor="w", pady=(0, 6))

        row = ctk.CTkFrame(p, fg_color="transparent")
        row.pack(anchor="w", pady=(0, 12))

        ctk.CTkLabel(row, text="Nama proses:", font=("Segoe UI", 12),
                     text_color=COLORS["text_main"]).pack(side="left", padx=(0, 8))
        entry = ctk.CTkEntry(row, width=220, height=34,
                             fg_color=COLORS["bg_card"],
                             border_color=COLORS["border"],
                             font=("Segoe UI", 12),
                             placeholder_text="chrome, notepad, ...")
        entry.pack(side="left")

        out = OutputBox(p)
        out.pack(fill="both", expand=True)

        def search_and_kill():
            name = entry.get().strip().lower()
            if not name:
                return
            out.clear()
            out.println(f"Mencari proses dengan nama '{name}'...\n", "accent")

            if not psutil:
                out.println("psutil tidak tersedia.", "error")
                return

            found = []
            for proc in psutil.process_iter(["pid", "name", "memory_info"]):
                try:
                    if name in (proc.info["name"] or "").lower():
                        ram = proc.info["memory_info"].rss / 1e6 if proc.info["memory_info"] else 0
                        found.append(proc)
                        out.println(f"  PID {proc.info['pid']:>6}  {proc.info['name']:<30}  {ram:>8.1f} MB", "normal")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            if not found:
                out.println("Tidak ada proses ditemukan.", "warning")
                return

            out.println(f"\nDitemukan {len(found)} proses. Matikan semua?", "warning")

            def kill_all():
                killed = 0
                for proc in found:
                    try:
                        proc.terminate()
                        killed += 1
                    except Exception as e:
                        out.println(f"  Gagal: {e}", "error")
                out.println(f"\n✅  {killed} proses dihentikan.", "success")

            ctk.CTkButton(
                p, text="💀  Kill Semua",
                width=140, height=32,
                fg_color=COLORS["accent3"],
                hover_color="#d06050",
                font=("Segoe UI", 11, "bold"),
                command=kill_all,
            ).pack(anchor="w", pady=(8, 0))

        ctk.CTkButton(
            row, text="🔍  Cari",
            width=100, height=34,
            fg_color=COLORS["accent"],
            hover_color="#4493e0",
            font=("Segoe UI", 12, "bold"),
            command=search_and_kill,
        ).pack(side="left", padx=(10, 0))

        return p

    # ── THREAD HELPER ─────────────────────────
    def _threaded(self, fn, out: OutputBox, btn: ctk.CTkButton):
        out.clear()
        btn.configure(state="disabled", text="⏳  Running...")

        def task():
            fn(out)
            btn.configure(state="normal", text="▶  Jalankan")

        threading.Thread(target=task, daemon=True).start()

    # ─────────────────────────────────────────
    # RUN FUNCTIONS
    # ─────────────────────────────────────────
    def _run_sysinfo(self, out: OutputBox):
        out.println("═" * 60, "dim")
        out.println("  💻  SYSTEM INFORMATION", "title")
        out.println("═" * 60, "dim")

        out.println(f"\n  OS          : {platform.system()} {platform.release()}", "normal")
        out.println(f"  Version     : {platform.version()}", "normal")
        out.println(f"  Architecture: {platform.architecture()[0]}", "normal")
        out.println(f"  Hostname    : {socket.gethostname()}", "normal")
        out.println(f"  Machine     : {platform.machine()}", "normal")
        out.println(f"  Processor   : {platform.processor()}", "normal")

        if psutil:
            out.println("\n" + "─" * 60, "dim")
            out.println("  CPU", "accent")
            out.println("─" * 60, "dim")
            out.println(f"  Physical cores : {psutil.cpu_count(logical=False)}", "normal")
            out.println(f"  Logical cores  : {psutil.cpu_count(logical=True)}", "normal")
            out.println(f"  Usage          : {psutil.cpu_percent(interval=1):.1f}%", "normal")
            freq = psutil.cpu_freq()
            if freq:
                out.println(f"  Frequency      : {freq.current:.0f} MHz (max {freq.max:.0f} MHz)", "normal")

            out.println("\n" + "─" * 60, "dim")
            out.println("  MEMORY", "accent")
            out.println("─" * 60, "dim")
            ram = psutil.virtual_memory()
            out.println(f"  Total   : {ram.total / 1e9:.2f} GB", "normal")
            out.println(f"  Used    : {ram.used / 1e9:.2f} GB ({ram.percent:.1f}%)", "normal")
            out.println(f"  Free    : {ram.available / 1e9:.2f} GB", "normal")

            swap = psutil.swap_memory()
            out.println(f"\n  Swap Total : {swap.total / 1e9:.2f} GB", "normal")
            out.println(f"  Swap Used  : {swap.used / 1e9:.2f} GB ({swap.percent:.1f}%)", "normal")

        out.println("\n" + "═" * 60, "dim")

    def _run_disk(self, out: OutputBox):
        out.println("═" * 60, "dim")
        out.println("  💾  DISK SPACE", "title")
        out.println("═" * 60, "dim")

        if psutil:
            parts = psutil.disk_partitions()
            for part in parts:
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                except PermissionError:
                    continue
                pct = usage.percent
                color = "error" if pct > 85 else ("warning" if pct > 70 else "success")
                out.println(f"\n  Drive   : {part.device}", "accent")
                out.println(f"  Mount   : {part.mountpoint}", "normal")
                out.println(f"  FS Type : {part.fstype}", "normal")
                out.println(f"  Total   : {usage.total / 1e9:.2f} GB", "normal")
                out.println(f"  Used    : {usage.used / 1e9:.2f} GB", "normal")
                out.println(f"  Free    : {usage.free / 1e9:.2f} GB", "normal")
                bar_filled = int(pct / 5)
                bar = "█" * bar_filled + "░" * (20 - bar_filled)
                out.println(f"  Usage   : [{bar}] {pct:.1f}%", color)
        out.println("\n" + "═" * 60, "dim")

    def _run_battery(self, out: OutputBox):
        out.println("═" * 60, "dim")
        out.println("  🔋  BATTERY STATUS", "title")
        out.println("═" * 60, "dim")
        if psutil:
            bat = psutil.sensors_battery()
            if bat:
                out.println(f"\n  Percentage  : {bat.percent:.1f}%", "normal")
                out.println(f"  Plugged In  : {'Ya ⚡' if bat.power_plugged else 'Tidak 🔋'}", "normal")
                if bat.secsleft != psutil.POWER_TIME_UNLIMITED and not bat.power_plugged:
                    h, m = divmod(bat.secsleft // 60, 60)
                    out.println(f"  Time Left   : {h}j {m}m", "normal")
            else:
                out.println("\n  Tidak ada baterai terdeteksi.", "warning")
        out.println("\n" + "═" * 60, "dim")

    def _run_checkip(self, out: OutputBox):
        out.println("═" * 60, "dim")
        out.println("  🌐  CEK IP ADDRESS", "title")
        out.println("═" * 60, "dim")

        # Local
        out.println("\n  ── IP LOKAL ──", "accent")
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            out.println(f"  Hostname : {hostname}", "normal")
            out.println(f"  IP Lokal : {local_ip}", "normal")
        except Exception as e:
            out.println(f"  Error: {e}", "error")

        if psutil:
            out.println("\n  ── NETWORK INTERFACES ──", "accent")
            for iface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == socket.AF_INET:
                        out.println(f"  {iface:<18} {addr.address}", "normal")

        # Public
        out.println("\n  ── IP PUBLIK ──", "accent")
        if req_lib:
            try:
                r = req_lib.get("https://api.ipify.org?format=json", timeout=8)
                out.println(f"  IP Publik : {r.json().get('ip', 'N/A')}", "success")
            except Exception:
                out.println("  Tidak bisa mengambil IP publik.", "warning")
        else:
            out.println("  requests tidak tersedia.", "warning")
        out.println("\n" + "═" * 60, "dim")

    def _run_ipdetail(self, out: OutputBox):
        out.println("═" * 60, "dim")
        out.println("  🌍  IP REAL DETAIL", "title")
        out.println("═" * 60, "dim")
        if not req_lib:
            out.println("requests tidak tersedia.", "error")
            return
        try:
            r = req_lib.get(
                "http://ip-api.com/json/?fields=status,query,country,regionName,"
                "city,zip,lat,lon,timezone,isp,org,mobile,proxy,hosting",
                timeout=10,
            )
            d = r.json()
            if d.get("status") == "success":
                out.println(f"\n  IP Address  : {d.get('query','N/A')}", "success")
                out.println(f"  Negara      : {d.get('country','N/A')}", "normal")
                out.println(f"  Provinsi    : {d.get('regionName','N/A')}", "normal")
                out.println(f"  Kota        : {d.get('city','N/A')}", "normal")
                out.println(f"  Kode Pos    : {d.get('zip','N/A')}", "normal")
                out.println(f"  Koordinat   : {d.get('lat','N/A')}, {d.get('lon','N/A')}", "normal")
                out.println(f"  Timezone    : {d.get('timezone','N/A')}", "normal")
                out.println(f"  ISP         : {d.get('isp','N/A')}", "normal")
                out.println(f"  Organisasi  : {d.get('org','N/A')}", "normal")
                out.println(f"  Mobile      : {'Ya' if d.get('mobile') else 'Tidak'}", "normal")
                proxy = d.get("proxy")
                out.println(f"  Proxy/VPN   : {'⚠️  Ya' if proxy else '✅ Tidak'}", "warning" if proxy else "success")
            else:
                out.println("Gagal mendapatkan data.", "error")
        except Exception as e:
            out.println(f"Error: {e}", "error")
        out.println("\n" + "═" * 60, "dim")

    def _run_speedtest(self, out: OutputBox):
        out.println("═" * 60, "dim")
        out.println("  🚀  SPEED TEST", "title")
        out.println("═" * 60, "dim")
        if not req_lib:
            out.println("requests tidak tersedia.", "error")
            return

        test_urls = [
            ("https://speed.hetzner.de/10MB.bin", 10),
            ("http://speedtest.tele2.net/10MB.zip", 10),
            ("http://ipv4.download.thinkbroadband.com/10MB.zip", 10),
        ]

        for url, mb in test_urls:
            server = url.split("/")[2]
            out.println(f"\n  Mencoba server: {server}...", "dim")
            try:
                t0 = time.time()
                r = req_lib.get(url, timeout=25, stream=True)
                if r.status_code != 200:
                    out.println(f"  Status {r.status_code}, skip.", "warning")
                    continue
                total = 0
                for chunk in r.iter_content(8192):
                    total += len(chunk)
                elapsed = time.time() - t0
                if total < 1000:
                    continue
                mbps  = (total * 8) / (elapsed * 1e6)
                mbs   = total / (elapsed * 1e6)
                out.println(f"\n  ✅  Download selesai dari {server}", "success")
                out.println(f"  Ukuran   : {total / 1e6:.2f} MB", "normal")
                out.println(f"  Waktu    : {elapsed:.2f} detik", "normal")
                out.println(f"  Kecepatan: {mbps:.2f} Mbps ({mbs:.2f} MB/s)", "success" if mbps > 10 else "warning")
                if   mbps > 100: out.println("\n  🔥 SANGAT CEPAT!", "success")
                elif mbps > 50:  out.println("\n  ⚡ CEPAT!", "success")
                elif mbps > 10:  out.println("\n  👍 NORMAL", "normal")
                else:            out.println("\n  🐌 LAMBAT", "warning")
                break
            except Exception:
                out.println(f"  Server {server} gagal.", "warning")

        out.println("\n" + "═" * 60, "dim")

    def _run_flushdns(self, out: OutputBox):
        out.println("═" * 60, "dim")
        out.println("  🧹  FLUSH DNS CACHE", "title")
        out.println("═" * 60, "dim")
        if is_windows():
            result = run_cmd("ipconfig /flushdns")
        else:
            result = run_cmd("sudo systemd-resolve --flush-caches 2>&1 || sudo service nscd restart 2>&1")
        out.println("\n" + result, "normal")
        out.println("✅  Selesai.", "success")
        out.println("\n" + "═" * 60, "dim")

    def _run_processes(self, out: OutputBox):
        out.println("═" * 60, "dim")
        out.println("  📊  TOP 20 PROSES (RAM)", "title")
        out.println("═" * 60, "dim")
        if not psutil:
            out.println("psutil tidak tersedia.", "error")
            return

        procs = []
        for pr in psutil.process_iter(["pid", "name", "memory_info", "cpu_percent"]):
            try:
                ram = pr.info["memory_info"].rss / 1e6 if pr.info["memory_info"] else 0
                procs.append({"pid": pr.info["pid"], "name": pr.info["name"] or "?",
                               "ram": ram, "cpu": pr.info["cpu_percent"] or 0})
            except Exception:
                pass
        procs.sort(key=lambda x: x["ram"], reverse=True)

        out.println(f"\n  {'No':>3}  {'PID':>7}  {'Nama':<30}  {'RAM (MB)':>10}  {'CPU %':>7}", "accent")
        out.println("  " + "─" * 64, "dim")
        for i, pr in enumerate(procs[:20], 1):
            col = "error" if pr["ram"] > 500 else ("warning" if pr["ram"] > 200 else "normal")
            out.println(
                f"  {i:>3}  {pr['pid']:>7}  {pr['name'][:30]:<30}  {pr['ram']:>10.1f}  {pr['cpu']:>7.1f}",
                col,
            )
        out.println(f"\n  Total proses: {len(procs)}", "dim")
        out.println("═" * 60, "dim")

    def _run_cleantemp(self, out: OutputBox):
        out.println("═" * 60, "dim")
        out.println("  🗑️   CLEAN TEMP FILES", "title")
        out.println("═" * 60, "dim")

        temp_dirs = []
        if is_windows():
            temp_dirs = [
                os.environ.get("TEMP", ""),
                os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Temp"),
            ]
        else:
            temp_dirs = ["/tmp"]

        total_del, total_fail, total_size = 0, 0, 0
        for d in temp_dirs:
            if not d or not os.path.exists(d):
                continue
            out.println(f"\n  Membersihkan: {d}", "dim")
            for root, dirs, files in os.walk(d, topdown=False):
                for f in files:
                    fp = os.path.join(root, f)
                    try:
                        sz = os.path.getsize(fp)
                        os.remove(fp)
                        total_del += 1
                        total_size += sz
                    except Exception:
                        total_fail += 1
                for dn in dirs:
                    try:
                        os.rmdir(os.path.join(root, dn))
                    except Exception:
                        pass

        out.println(f"\n  ✅  {total_del} file dihapus ({total_size / 1e6:.2f} MB)", "success")
        if total_fail:
            out.println(f"  ⚠️   {total_fail} file tidak bisa dihapus (sedang dipakai)", "warning")
        out.println("\n" + "═" * 60, "dim")

    def _run_benchmark(self, out: OutputBox):
        out.println("═" * 60, "dim")
        out.println("  ⚡  DISK BENCHMARK", "title")
        out.println("═" * 60, "dim")

        test_file = os.path.join(os.environ.get("TEMP", "/tmp"), "multitool_bench.tmp")
        mb = 100
        size = mb * 1024 * 1024

        out.println(f"\n  Membuat file {mb}MB...", "dim")
        try:
            data = os.urandom(size)

            # Write
            t0 = time.time()
            with open(test_file, "wb") as f:
                f.write(data)
            wt = time.time() - t0
            ws = mb / wt if wt else 0

            # Read
            t0 = time.time()
            with open(test_file, "rb") as f:
                f.read()
            rt = time.time() - t0
            rs = mb / rt if rt else 0

            try:
                os.remove(test_file)
            except Exception:
                pass

            wcolor = "success" if ws > 500 else ("warning" if ws > 100 else "error")
            rcolor = "success" if rs > 500 else ("warning" if rs > 100 else "error")

            out.println(f"\n  Write Speed : {ws:.2f} MB/s  ({wt:.2f}s)", wcolor)
            out.println(f"  Read Speed  : {rs:.2f} MB/s  ({rt:.2f}s)", rcolor)

            avg = (ws + rs) / 2
            if   avg > 1000: rating = "EXCELLENT (NVMe SSD)"
            elif avg > 400:  rating = "SANGAT CEPAT (SSD)"
            elif avg > 100:  rating = "NORMAL (SSD/HDD)"
            else:             rating = "LAMBAT (HDD)"

            out.println(f"\n  Rating  : {rating}", "accent")
        except Exception as e:
            out.println(f"  Error: {e}", "error")
        out.println("\n" + "═" * 60, "dim")

    def _run_firewall(self, out: OutputBox):
        out.println("═" * 60, "dim")
        out.println("  🛡️   FIREWALL STATUS", "title")
        out.println("═" * 60, "dim")
        if is_windows():
            r = run_cmd('netsh advfirewall show allprofiles state', timeout=10)
        else:
            r = run_cmd("sudo ufw status 2>/dev/null || iptables -L --line-numbers 2>/dev/null", timeout=10)
        out.println("\n" + r, "normal")
        out.println("═" * 60, "dim")

    def _run_ports(self, out: OutputBox):
        out.println("═" * 60, "dim")
        out.println("  🔓  OPEN PORTS (Listening)", "title")
        out.println("═" * 60, "dim")

        if psutil:
            conns = psutil.net_connections(kind="inet")
            listening = [c for c in conns if c.status == "LISTEN"]
            out.println(f"\n  {'Proto':<8} {'Local Address':<25} {'PID':>8}", "accent")
            out.println("  " + "─" * 44, "dim")
            for c in sorted(listening, key=lambda x: x.laddr.port):
                addr = f"{c.laddr.ip}:{c.laddr.port}"
                proto = "TCP" if c.type.name == "SOCK_STREAM" else "UDP"
                out.println(f"  {proto:<8} {addr:<25} {c.pid or '-':>8}", "normal")
            out.println(f"\n  Total listening: {len(listening)}", "dim")
        else:
            r = run_cmd("netstat -an | findstr LISTENING" if is_windows() else "ss -tlnp", timeout=15)
            out.println("\n" + r, "normal")
        out.println("\n" + "═" * 60, "dim")

    def _run_wifipass(self, out: OutputBox):
        out.println("═" * 60, "dim")
        out.println("  🔑  WIFI PASSWORDS TERSIMPAN", "title")
        out.println("═" * 60, "dim")

        if not is_windows():
            out.println("Fitur ini hanya tersedia di Windows.", "warning")
            return

        r = run_cmd("netsh wlan show profiles", timeout=10)
        profiles = []
        for line in r.split("\n"):
            if "All User Profile" in line or "Semua Profil Pengguna" in line:
                profile = line.split(":")[-1].strip()
                if profile:
                    profiles.append(profile)

        if not profiles:
            out.println("\n  Tidak ada WiFi tersimpan.", "warning")
            out.println("═" * 60, "dim")
            return

        out.println(f"\n  Ditemukan {len(profiles)} profil WiFi\n", "accent")
        out.println(f"  {'No':>3}  {'SSID':<30}  Password", "accent")
        out.println("  " + "─" * 55, "dim")

        for i, p in enumerate(profiles, 1):
            detail = run_cmd(f'netsh wlan show profile name="{p}" key=clear', timeout=8)
            pw = ""
            for line in detail.split("\n"):
                if "Key Content" in line or "Konten Kunci" in line:
                    pw = line.split(":")[-1].strip()
                    break
            color = "normal" if pw else "dim"
            out.println(f"  {i:>3}  {p[:30]:<30}  {pw or '(tidak ada / hidden)'}", color)

        out.println("\n" + "═" * 60, "dim")


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = MultiToolApp()
    app.mainloop()