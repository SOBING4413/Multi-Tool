"""
MultiTool GUI v2.1.0 - By Sobing4413
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
    ctk.set_default_color_theme("green")
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
    "bg_dark":     "#080e09",   # very deep forest black
    "bg_panel":    "#0b1210",   # sidebar dark green-black
    "bg_card":     "#0f1a12",   # card bg
    "bg_card2":    "#121f15",   # card alt
    "bg_hover":    "#172418",   # hover state
    "accent":      "#4ade80",   # leaf green
    "accent_glow": "#16a34a",   # deep green glow
    "accent_soft": "#22c55e",   # mid green
    "accent2":     "#86efac",   # light green (secondary)
    "accent3":     "#f87171",   # red (error/danger)
    "accent4":     "#fbbf24",   # amber (warning)
    "accent5":     "#a3e635",   # lime (highlight)
    "text_main":   "#e2f5e6",   # soft green-white
    "text_dim":    "#5d7a62",   # muted green-grey
    "text_muted":  "#2e4030",   # very muted
    "border":      "#1a2e1c",   # subtle border
    "border2":     "#223424",   # slightly stronger
    "success":     "#4ade80",
    "warning":     "#fbbf24",
    "error":       "#f87171",
    "sidebar_sel": "#0f2e14",   # selected bg
    "sidebar_sel2":"#143319",
    "grad_start":  "#0c1a0e",
    "grad_end":    "#080e09",
}

AUTHOR  = "Exter Interactive"
VERSION = "v2.1.0 GUI"
GITHUB  = "https://github.com/SOBING4413"
DISCORD = "https://discord.gg/9nsub2yx4V"

# ─────────────────────────────────────────────
# LOGO LOADER
# ─────────────────────────────────────────────
_BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
_LOGO_PATH = os.path.join(_BASE_DIR, "logo.png")

def _load_logo(size=(40, 40)):
    """Return CTkImage dari logo.png. None kalau gagal."""
    try:
        from PIL import Image
        img = Image.open(_LOGO_PATH).convert("RGBA").resize(size, Image.LANCZOS)
        return ctk.CTkImage(light_image=img, dark_image=img, size=size)
    except Exception:
        return None

def _load_logo_tk(size=(64, 64)):
    """Return PhotoImage untuk tkinter Canvas. None kalau gagal."""
    try:
        from PIL import Image, ImageTk
        img = Image.open(_LOGO_PATH).convert("RGBA").resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception:
        return None

def _set_icon(root):
    """Set window icon dari logo.png. Silent fail."""
    try:
        from PIL import Image, ImageTk
        img = Image.open(_LOGO_PATH).convert("RGBA").resize((32, 32), Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        root.iconphoto(True, photo)
        root._icon_ref = photo   # cegah garbage collector
    except Exception:
        pass

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


def _measure_download_speed(test_urls, timeout=25):
    """Return tuple (ok, message_lines, mbps)."""
    if not req_lib:
        return False, ["requests tidak tersedia."], 0.0

    headers = {"User-Agent": "MultiTool/2.1.0 (+speedtest)"}
    for url in test_urls:
        server = url.split("/")[2]
        lines = [f"  Mencoba server: {server}..."]
        try:
            t0 = time.time()
            r = req_lib.get(url, timeout=timeout, stream=True, headers=headers)
            if r.status_code != 200:
                lines.append(f"  Status {r.status_code}, skip.")
                continue
            total = 0
            for chunk in r.iter_content(65536):
                if chunk:
                    total += len(chunk)
            elapsed = max(time.time() - t0, 0.001)
            if total < 1_000_000:
                lines.append("  Data terlalu kecil untuk pengukuran valid, skip.")
                continue
            mbps = (total * 8) / (elapsed * 1_000_000)
            lines.extend([
                f"  ✅ Download selesai dari {server}",
                f"  Ukuran   : {total / (1024**2):.2f} MB",
                f"  Waktu    : {elapsed:.2f} detik",
                f"  Kecepatan: {mbps:.2f} Mbps",
            ])
            return True, lines, mbps
        except Exception:
            lines.append(f"  Server {server} gagal.")
    return False, ["  Semua server gagal."], 0.0


# ─────────────────────────────────────────────
# OUTPUT BOX HELPER
# ─────────────────────────────────────────────
class OutputBox(ctk.CTkTextbox):
    """Textbox read-only dengan helper print — dark premium style."""

    def __init__(self, master, **kw):
        super().__init__(
            master,
            font=("Cascadia Code", 12) if os.name == "nt" else ("Monospace", 12),
            text_color=COLORS["text_main"],
            fg_color="#060a10",
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"],
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["border2"],
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
            "dim":     COLORS["text_muted"],
            "title":   COLORS["accent5"],
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
            height=40,
            corner_radius=8,
            fg_color="transparent",
            hover_color=COLORS["bg_hover"],
            text_color=COLORS["text_dim"],
            font=("Segoe UI", 12),
            border_width=0,
            command=command,
            **kw,
        )
        self._is_active = False

    def set_active(self, active: bool):
        self._is_active = active
        if active:
            self.configure(
                fg_color=COLORS["sidebar_sel"],
                text_color=COLORS["accent"],
                border_width=1,
                border_color=COLORS["accent_glow"],
            )
        else:
            self.configure(
                fg_color="transparent",
                text_color=COLORS["text_dim"],
                border_width=0,
            )


# ─────────────────────────────────────────────
# ANIMATED PROGRESS BAR
# ─────────────────────────────────────────────
class AnimatedProgressBar(tk.Canvas):
    """Custom animated progress bar with color transitions."""

    def __init__(self, master, width=200, height=6, **kw):
        super().__init__(master, width=width, height=height,
                         bg=COLORS["bg_dark"], bd=0, highlightthickness=0, **kw)
        self._current = 0.0
        self._target  = 0.0
        self._width   = width
        self._height  = height
        self._animating = False
        self._draw(0.0)

    def _get_color(self, pct: float) -> str:
        if pct < 0.5:
            r = int(52 + (227-52) * (pct / 0.5))
            g = int(208 - (208-179) * (pct / 0.5))
            b = int(88  - (88-10) * (pct / 0.5))
        else:
            r = int(227 + (249-227) * ((pct-0.5)/0.5))
            g = int(179 - (179-117) * ((pct-0.5)/0.5))
            b = int(10)
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        return f"#{r:02x}{g:02x}{b:02x}"

    def _draw(self, pct: float):
        self.delete("all")
        # Track
        self.create_rounded_rect(0, 0, self._width, self._height,
                                  radius=3, fill=COLORS["border"], outline="")
        # Fill
        fill_w = max(0, int(self._width * pct))
        if fill_w > 0:
            color = self._get_color(pct)
            self.create_rounded_rect(0, 0, fill_w, self._height,
                                      radius=3, fill=color, outline="")
            # Shine
            shine_y = max(1, self._height // 3)
            self.create_rounded_rect(2, 1, max(2, fill_w - 2), shine_y,
                                      radius=2, fill="#1a5c2e", outline="")

    def create_rounded_rect(self, x1, y1, x2, y2, radius=4, **kw):
        pts = [x1+radius, y1, x2-radius, y1, x2, y1,
               x2, y1+radius, x2, y2-radius, x2, y2,
               x2-radius, y2, x1+radius, y2, x1, y2,
               x1, y2-radius, x1, y1+radius, x1, y1]
        self.create_polygon(pts, smooth=True, **kw)

    def set_value(self, pct: float):
        self._target = max(0.0, min(1.0, pct))
        if not self._animating:
            self._animate()

    def _animate(self):
        self._animating = True
        diff = self._target - self._current
        if abs(diff) < 0.005:
            self._current = self._target
            self._draw(self._current)
            self._animating = False
            return
        self._current += diff * 0.15
        self._draw(self._current)
        self.after(16, self._animate)


# ─────────────────────────────────────────────
# STAT CARD (untuk dashboard) — animated
# ─────────────────────────────────────────────
class StatCard(ctk.CTkFrame):
    def __init__(self, master, title, value, icon, color, **kw):
        super().__init__(
            master,
            fg_color=COLORS["bg_card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border2"],
            **kw,
        )
        # Top row: icon + title
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=14, pady=(12, 0))

        self._icon_lbl = ctk.CTkLabel(top, text=icon,
                                       font=("Segoe UI Emoji", 18),
                                       text_color=color)
        self._icon_lbl.pack(side="left")

        ctk.CTkLabel(top, text=title, font=("Segoe UI", 10),
                     text_color=COLORS["text_dim"]).pack(side="right", anchor="e")

        # Value
        self.val_lbl = ctk.CTkLabel(
            self, text=value,
            font=("Segoe UI", 20, "bold"),
            text_color=COLORS["text_main"],
            anchor="w",
        )
        self.val_lbl.pack(anchor="w", padx=14, pady=(4, 0))

        # Progress bar
        bar_frame = ctk.CTkFrame(self, fg_color="transparent")
        bar_frame.pack(fill="x", padx=14, pady=(6, 12))
        self._bar = AnimatedProgressBar(bar_frame, height=5)
        self._bar.pack(fill="x")

        self._color = color
        self._pct   = 0.0

    def update_value(self, new_val: str, pct: float = None):
        self.val_lbl.configure(text=new_val)
        if pct is not None:
            self._bar.set_value(pct)



# ─────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────
class MultiToolApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"MultiTool {VERSION}  –  by {AUTHOR}")
        self.geometry("1160x720")
        self.minsize(960, 600)
        self.configure(fg_color=COLORS["bg_dark"])

        # Window icon
        _set_icon(self)

        try:
            self.wm_attributes("-alpha", 1.0)
        except Exception:
            pass

        self._active_btn: SidebarBtn | None = None
        self._pages: dict[str, ctk.CTkFrame] = {}
        self._running_task = False
        self._dot_anim_id  = None

        self._build_layout()
        self._show_page("dashboard")

    # ── layout skeleton ──────────────────────
    def _build_layout(self):
        # Thin accent line at very top (like VSCode)
        accent_bar = tk.Frame(self, bg=COLORS["accent"], height=2)
        accent_bar.pack(side="top", fill="x")

        body = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        body.pack(side="top", fill="both", expand=True)

        # Sidebar
        self.sidebar = ctk.CTkFrame(
            body, width=220, fg_color=COLORS["bg_panel"],
            corner_radius=0,
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Separator line between sidebar and content
        sep = tk.Frame(body, bg=COLORS["border"], width=1)
        sep.pack(side="left", fill="y")

        # Content area
        self.content = ctk.CTkFrame(body, fg_color=COLORS["bg_dark"], corner_radius=0)
        self.content.pack(side="left", fill="both", expand=True)

        self._build_sidebar()
        self._build_pages()

    def _build_sidebar(self):
        # Logo area with pulsing glow effect
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(fill="x", pady=(20, 6), padx=14)

        logo_inner = ctk.CTkFrame(logo_frame,
                                   fg_color=COLORS["bg_card"],
                                   corner_radius=10,
                                   border_width=1,
                                   border_color=COLORS["accent_glow"])
        logo_inner.pack(fill="x")

        # Row: logo image (if available) + text
        row = ctk.CTkFrame(logo_inner, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=(10, 2))

        logo_img = _load_logo(size=(32, 32))
        if logo_img:
            ctk.CTkLabel(row, text="", image=logo_img,
                         fg_color="transparent").pack(side="left", padx=(0, 8))

        self._logo_lbl = ctk.CTkLabel(
            row,
            text="MultiTool",
            font=("Segoe UI", 14, "bold"),
            text_color=COLORS["accent"],
        )
        self._logo_lbl.pack(side="left", anchor="w")

        ctk.CTkLabel(
            logo_inner, text=f"{AUTHOR}  ·  {VERSION}",
            font=("Segoe UI", 9), text_color=COLORS["text_muted"],
        ).pack(anchor="w", padx=12, pady=(0, 10))

        # Start logo pulse animation
        self._logo_pulse_state = 0
        self._pulse_logo()

        ctk.CTkFrame(self.sidebar, height=1, fg_color=COLORS["border"]).pack(
            fill="x", padx=10, pady=(10, 6)
        )

        # Sections
        menus = [
            ("Dashboard",    "🏠",  "dashboard"),
            ("─── POWER", "", None),
            ("Shutdown Timer",  "⏻",  "shutdown"),
            ("Restart Timer",   "🔄", "restart"),
            ("Lock PC",         "🔒", "lock"),
            ("Sleep/Hibernate", "💤", "sleep"),
            ("─── INFO", "", None),
            ("System Info",     "💻", "sysinfo"),
            ("Disk Space",      "💾", "disk"),
            ("Battery",         "🔋", "battery"),
            ("─── NETWORK", "", None),
            ("Cek IP",          "🌐", "checkip"),
            ("IP Detail",       "🌍", "ipdetail"),
            ("Ping Test",       "📡", "ping"),
            ("Speed Test",      "🚀", "speedtest"),
            ("Flush DNS",       "🧹", "flushdns"),
            ("─── PROSES", "", None),
            ("Running Processes","📊", "processes"),
            ("Kill Process",    "💀", "kill"),
            ("─── CLEANUP", "", None),
            ("Clean Temp",      "🗑️",  "cleantemp"),
            ("Disk Benchmark",  "⚡", "benchmark"),
            ("─── SECURITY", "", None),
            ("Firewall Status", "🛡️",  "firewall"),
            ("Open Ports",      "🔓", "ports"),
            ("WiFi Passwords",  "🔑", "wifipass"),
        ]

        self._btns: dict[str, SidebarBtn] = {}
        scroll = ctk.CTkScrollableFrame(
            self.sidebar, fg_color="transparent",
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["border2"],
        )
        scroll.pack(fill="both", expand=True, padx=6)

        # Smooth mousewheel scroll
        self._smooth_scroll_vel  = 0.0
        self._smooth_scroll_anim = False
        self._scroll_frame_ref   = scroll

        def on_scroll(event):
            delta = -1 if (event.delta > 0 or event.num == 4) else 1
            self._smooth_scroll_vel += delta * 0.04
            if not self._smooth_scroll_anim:
                self._smooth_scroll_tick()

        scroll.bind("<MouseWheel>", on_scroll)
        scroll.bind("<Button-4>",   on_scroll)
        scroll.bind("<Button-5>",   on_scroll)
        for child in scroll.winfo_children():
            child.bind("<MouseWheel>", on_scroll)


        for label, icon, page_key in menus:
            if page_key is None:
                # section header — clean minimal look
                sec_frame = ctk.CTkFrame(scroll, fg_color="transparent")
                sec_frame.pack(fill="x", padx=4, pady=(12, 2))
                ctk.CTkLabel(
                    sec_frame, text=label,
                    font=("Segoe UI", 9, "bold"),
                    text_color=COLORS["text_muted"],
                    anchor="w",
                ).pack(fill="x")
                continue
            btn = SidebarBtn(
                scroll, text=label, icon=icon,
                command=lambda k=page_key: self._show_page(k),
            )
            btn.pack(fill="x", pady=1)
            self._btns[page_key] = btn

        # Bottom — social links
        ctk.CTkFrame(self.sidebar, height=1, fg_color=COLORS["border"]).pack(
            fill="x", padx=10, pady=(6, 6)
        )
        bottom = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        bottom.pack(fill="x", padx=12, pady=(0, 12))
        ctk.CTkLabel(
            bottom, text="github.com/SOBING4413  ·  Exter Interactive",
            font=("Segoe UI", 8), text_color=COLORS["text_muted"],
            anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(
            bottom, text="discord.gg/9nsub2yx4V",
            font=("Segoe UI", 8), text_color=COLORS["text_muted"],
            anchor="w",
        ).pack(anchor="w")

    def _pulse_logo(self):
        """Subtle pulsing border color on logo card."""
        try:
            colors = [COLORS["accent_glow"], "#15803d", "#166534", "#15803d"]
            c = colors[self._logo_pulse_state % len(colors)]
            # find logo inner frame and update border
            logo_frame = self.sidebar.winfo_children()[0]
            logo_inner = logo_frame.winfo_children()[0]
            logo_inner.configure(border_color=c)
            self._logo_pulse_state += 1
            self.after(800, self._pulse_logo)
        except Exception:
            pass

    def _smooth_scroll_tick(self):
        """Inertia-based smooth scroll for sidebar."""
        self._smooth_scroll_anim = True
        try:
            sf = self._scroll_frame_ref
            # Get the internal scrollable canvas from CTkScrollableFrame
            inner = sf._parent_canvas  # CTk internal
            inner.yview_moveto(inner.yview()[0] + self._smooth_scroll_vel)
        except Exception:
            pass
        self._smooth_scroll_vel *= 0.78  # friction
        if abs(self._smooth_scroll_vel) > 0.001:
            self.after(16, self._smooth_scroll_tick)
        else:
            self._smooth_scroll_vel = 0.0
            self._smooth_scroll_anim = False

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
        # Hide all pages
        for p in self._pages.values():
            p.pack_forget()

        target = self._pages[key]
        target.pack(fill="both", expand=True, padx=20, pady=20)

        # Update sidebar state
        if self._active_btn:
            self._active_btn.set_active(False)
        if key in self._btns:
            self._btns[key].set_active(True)
            self._active_btn = self._btns[key]

        # Smooth fade-in overlay animation
        self._fade_in_page(target)

    def _fade_in_page(self, frame: ctk.CTkFrame):
        """Overlay a transparent canvas that fades from dark to clear."""
        try:
            overlay = tk.Canvas(self.content,
                                 bg=COLORS["bg_dark"],
                                 bd=0, highlightthickness=0)
            overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

            step = [0]  # mutable for closure
            total = 8

            def tick():
                step[0] += 1
                if step[0] >= total:
                    overlay.destroy()
                    return
                alpha_frac = step[0] / total          # 0→1
                # Darken = high alpha at start, transparent at end
                darkness = int(200 * (1 - alpha_frac))
                r = int(8   * (1 - alpha_frac) + 8)
                g = int(14  * (1 - alpha_frac) + 14)
                b = int(9   * (1 - alpha_frac) + 9)
                col = f"#{max(0,r):02x}{max(0,g):02x}{max(0,b):02x}"
                # Resize canvas to match content area
                w = self.content.winfo_width()
                h = self.content.winfo_height()
                overlay.configure(width=w, height=h, bg=col)
                self.after(14, tick)

            tick()
        except Exception:
            pass

    # ── PAGE: Dashboard ───────────────────────
    def _make_dashboard(self) -> ctk.CTkFrame:
        p = ctk.CTkFrame(self.content, fg_color="transparent")

        # Header row: title + live clock
        hdr = ctk.CTkFrame(p, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 4))

        left_hdr = ctk.CTkFrame(hdr, fg_color="transparent")
        left_hdr.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            left_hdr, text="Dashboard",
            font=("Segoe UI", 24, "bold"),
            text_color=COLORS["text_main"],
        ).pack(anchor="w")
        ctk.CTkLabel(
            left_hdr, text="Ringkasan sistem realtime",
            font=("Segoe UI", 12), text_color=COLORS["text_dim"],
        ).pack(anchor="w")

        # Live clock label
        self._clock_lbl = ctk.CTkLabel(
            hdr, text="",
            font=("Segoe UI", 11),
            text_color=COLORS["text_muted"],
        )
        self._clock_lbl.pack(side="right", anchor="ne")
        self._update_clock()

        # Thin separator
        ctk.CTkFrame(p, height=1, fg_color=COLORS["border"]).pack(fill="x", pady=(8, 16))

        # Stat cards grid
        cards_frame = ctk.CTkFrame(p, fg_color="transparent")
        cards_frame.pack(fill="x")
        cards_frame.columnconfigure((0, 1, 2, 3), weight=1)

        self._card_cpu  = StatCard(cards_frame, "CPU Usage",    "–", "🖥️",  COLORS["accent"])
        self._card_ram  = StatCard(cards_frame, "RAM Usage",    "–", "🧠",  COLORS["accent2"])
        self._card_disk = StatCard(cards_frame, "Disk C: Used", "–", "💾",  COLORS["accent4"])
        self._card_bat  = StatCard(cards_frame, "Battery",      "–", "🔋",  COLORS["accent3"])

        for i, card in enumerate([self._card_cpu, self._card_ram, self._card_disk, self._card_bat]):
            card.grid(row=0, column=i, padx=5, pady=0, sticky="nsew")

        # Refresh button — subtle style
        btn_row = ctk.CTkFrame(p, fg_color="transparent")
        btn_row.pack(fill="x", pady=(14, 0))

        self._refresh_btn = ctk.CTkButton(
            btn_row, text="↻  Refresh Stats",
            width=140, height=32,
            fg_color=COLORS["bg_card2"],
            hover_color=COLORS["bg_hover"],
            text_color=COLORS["accent"],
            font=("Segoe UI", 11, "bold"),
            border_width=1,
            border_color=COLORS["border2"],
            corner_radius=8,
            command=self._refresh_dashboard,
        )
        self._refresh_btn.pack(side="left")
        self._report_btn = ctk.CTkButton(
            btn_row, text="📝  Generate Health Report",
            width=210, height=32,
            fg_color=COLORS["bg_card2"],
            hover_color=COLORS["bg_hover"],
            text_color=COLORS["accent2"],
            font=("Segoe UI", 11, "bold"),
            border_width=1,
            border_color=COLORS["border2"],
            corner_radius=8,
            command=self._generate_health_report,
        )
        self._report_btn.pack(side="left", padx=(8, 0))

        # Auto-refresh toggle
        self._auto_refresh_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            btn_row, text="Auto refresh (30s)",
            variable=self._auto_refresh_var,
            font=("Segoe UI", 11),
            text_color=COLORS["text_dim"],
            fg_color=COLORS["accent_glow"],
            hover_color=COLORS["accent"],
            checkbox_width=16, checkbox_height=16,
        ).pack(side="left", padx=14)

        # Section title
        sec = ctk.CTkFrame(p, fg_color="transparent")
        sec.pack(fill="x", pady=(20, 8))
        ctk.CTkLabel(
            sec, text="System Summary",
            font=("Segoe UI", 13, "bold"),
            text_color=COLORS["text_main"],
        ).pack(side="left")

        self._dash_out = OutputBox(p)
        self._dash_out.pack(fill="both", expand=True)

        # Auto-load
        self.after(300, self._refresh_dashboard)
        self._schedule_auto_refresh()
        return p

    def _update_clock(self):
        now = datetime.datetime.now().strftime("%a %d %b  %H:%M:%S")
        try:
            self._clock_lbl.configure(text=now)
            self.after(1000, self._update_clock)
        except Exception:
            pass

    def _schedule_auto_refresh(self):
        def loop():
            try:
                if self._auto_refresh_var.get():
                    self._refresh_dashboard()
                self.after(30_000, loop)
            except Exception:
                pass
        self.after(30_000, loop)

    def _refresh_dashboard(self):
        def task():
            # Cards
            if psutil:
                cpu  = psutil.cpu_percent(interval=0.5)
                ram  = psutil.virtual_memory()
                disk = psutil.disk_usage("C:\\" if is_windows() else "/")
                bat  = psutil.sensors_battery()

                self._card_cpu.update_value(f"{cpu:.1f}%", pct=cpu/100)
                self._card_ram.update_value(
                    f"{ram.used / 1e9:.1f} / {ram.total / 1e9:.1f} GB",
                    pct=ram.percent/100,
                )
                self._card_disk.update_value(
                    f"{disk.used / 1e9:.1f} / {disk.total / 1e9:.1f} GB",
                    pct=disk.percent/100,
                )
                if bat:
                    bat_txt = f"{bat.percent:.0f}% {'⚡' if bat.power_plugged else '🔋'}"
                    self._card_bat.update_value(bat_txt, pct=bat.percent/100)
                else:
                    self._card_bat.update_value("N/A", pct=0)

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

    def _generate_health_report(self):
        """Buat file laporan kesehatan sistem."""
        try:
            reports_dir = os.path.join(_BASE_DIR, "reports")
            os.makedirs(reports_dir, exist_ok=True)
            stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(reports_dir, f"health_report_{stamp}.txt")

            lines = [
                "MULTITOOL SYSTEM HEALTH REPORT",
                "=" * 42,
                f"Generated : {datetime.datetime.now().isoformat(sep=' ', timespec='seconds')}",
                f"Hostname  : {socket.gethostname()}",
                f"OS        : {platform.platform()}",
                f"Python    : {platform.python_version()}",
                "",
            ]
            if psutil:
                cpu = psutil.cpu_percent(interval=0.5)
                ram = psutil.virtual_memory()
                disk = psutil.disk_usage("C:\\" if is_windows() else "/")
                uptime = str(datetime.timedelta(seconds=int(time.time() - psutil.boot_time())))
                lines += [
                    "RESOURCE USAGE",
                    "-" * 42,
                    f"CPU       : {cpu:.1f}%",
                    f"RAM       : {ram.percent:.1f}% ({ram.used / 1e9:.2f}/{ram.total / 1e9:.2f} GB)",
                    f"DISK      : {disk.percent:.1f}% ({disk.used / 1e9:.2f}/{disk.total / 1e9:.2f} GB)",
                    f"Uptime    : {uptime}",
                    "",
                    "TOP 5 PROCESSES BY RAM",
                    "-" * 42,
                ]
                procs = sorted(
                    psutil.process_iter(["pid", "name", "memory_info"]),
                    key=lambda p: p.info["memory_info"].rss if p.info["memory_info"] else 0,
                    reverse=True,
                )[:5]
                for pr in procs:
                    if not pr.info["memory_info"]:
                        continue
                    rss_mb = pr.info["memory_info"].rss / (1024 ** 2)
                    name = str(pr.info["name"] or "unknown")[:30]
                    lines.append(f"PID {pr.info['pid']:>6} | {name:<30} | {rss_mb:8.1f} MB")
            else:
                lines.append("psutil tidak tersedia. Install dependency untuk detail report.")

            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")

            messagebox.showinfo("Report Generated", f"Laporan berhasil dibuat:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuat report:\n{e}")

    # ── PAGE FACTORY: generic output ─────────
    def _make_output_page(self, title: str, run_fn) -> ctk.CTkFrame:
        p = ctk.CTkFrame(self.content, fg_color="transparent")

        # Title row
        title_lbl = ctk.CTkLabel(
            p, text=title,
            font=("Segoe UI", 18, "bold"),
            text_color=COLORS["text_main"],
        )
        title_lbl.pack(anchor="w", pady=(0, 10))

        ctk.CTkFrame(p, height=1, fg_color=COLORS["border"]).pack(fill="x", pady=(0, 12))

        header = ctk.CTkFrame(p, fg_color="transparent")
        header.pack(fill="x", pady=(0, 12))

        btn_run = ctk.CTkButton(
            header, text="▶  Jalankan",
            width=130, height=34,
            fg_color=COLORS["accent_glow"],
            hover_color=COLORS["accent"],
            text_color="#ffffff",
            font=("Segoe UI", 12, "bold"),
            corner_radius=8,
            command=lambda: self._threaded(run_fn, out, btn_run),
        )
        btn_run.pack(side="right")

        btn_clear = ctk.CTkButton(
            header, text="✕  Clear",
            width=90, height=34,
            fg_color=COLORS["bg_card"],
            hover_color=COLORS["bg_hover"],
            text_color=COLORS["text_dim"],
            border_width=1, border_color=COLORS["border"],
            font=("Segoe UI", 12),
            corner_radius=8,
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
            hover_color="#b8960e",
            text_color="#000000",
            font=("Segoe UI", 12, "bold"),
            corner_radius=8,
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
            corner_radius=8,
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
                     text_color=COLORS["text_main"]).pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(p, text="Jadwalkan shutdown/restart otomatis setelah waktu tertentu.",
                     font=("Segoe UI", 12), text_color=COLORS["text_dim"]).pack(anchor="w", pady=(0, 8))
        ctk.CTkFrame(p, height=1, fg_color=COLORS["border"]).pack(fill="x", pady=(0, 16))

        row = ctk.CTkFrame(p, fg_color="transparent")
        row.pack(anchor="w")

        ctk.CTkLabel(row, text="Waktu (menit):", font=("Segoe UI", 12),
                     text_color=COLORS["text_main"]).pack(side="left", padx=(0, 10))
        entry = ctk.CTkEntry(row, width=100, height=36,
                             fg_color=COLORS["bg_card"],
                             border_color=COLORS["border2"],
                             corner_radius=8,
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
            hover_color="#22c55e",
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
            hover_color="#22c55e",
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
            hover_color="#22c55e",
            font=("Segoe UI", 12, "bold"),
            command=search_and_kill,
        ).pack(side="left", padx=(10, 0))

        return p

    # ── THREAD HELPER ─────────────────────────
    def _threaded(self, fn, out: OutputBox, btn: ctk.CTkButton):
        out.clear()
        btn.configure(state="disabled")
        self._start_btn_anim(btn)

        def task():
            fn(out)
            self._stop_btn_anim(btn)

        threading.Thread(target=task, daemon=True).start()

    def _start_btn_anim(self, btn: ctk.CTkButton):
        """Animated loading dots on button."""
        self._btn_anim_running = True
        self._btn_anim_frame   = 0
        frames = ["⠋ Running", "⠙ Running", "⠹ Running", "⠸ Running",
                  "⠼ Running", "⠴ Running", "⠦ Running", "⠧ Running",
                  "⠇ Running", "⠏ Running"]

        def tick():
            if not self._btn_anim_running:
                return
            try:
                btn.configure(text=frames[self._btn_anim_frame % len(frames)])
                self._btn_anim_frame += 1
                self.after(80, tick)
            except Exception:
                pass
        tick()

    def _stop_btn_anim(self, btn: ctk.CTkButton):
        self._btn_anim_running = False
        try:
            btn.configure(state="normal", text="▶  Jalankan")
        except Exception:
            pass

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
            "https://proof.ovh.net/files/10Mb.dat",
            "https://speed.hetzner.de/10MB.bin",
            "https://bouygues.testdebit.info/10M.iso",
        ]
        ok, lines, mbps = _measure_download_speed(test_urls, timeout=30)
        for line in lines:
            tag = "success" if "✅" in line else ("warning" if "gagal" in line or "skip" in line else "dim")
            out.println(f"\n{line}" if line.startswith("  Mencoba") else line, tag)
        if ok:
            if mbps > 100:
                out.println("\n  🔥 SANGAT CEPAT!", "success")
            elif mbps > 50:
                out.println("\n  ⚡ CEPAT!", "success")
            elif mbps > 10:
                out.println("\n  👍 NORMAL", "normal")
            else:
                out.println("\n  🐌 LAMBAT", "warning")
        else:
            out.println("\n  ❌ Speed test gagal: semua server tidak merespons dengan baik.", "error")

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
# SPLASH SCREEN
# ─────────────────────────────────────────────
class SplashScreen(tk.Tk):
    """
    Full-screen animated loading splash before main GUI.
    Draws on a tk.Canvas with:
      - Animated particle field (floating dots)
      - Glowing title text animation
      - Typing effect for subtitle
      - Smooth progress bar with pulse
      - Fade-out before launching main app
    """

    W, H = 720, 420
    FPS  = 30

    def __init__(self):
        super().__init__()
        self.overrideredirect(True)          # borderless
        self.configure(bg="#080e09")
        self.resizable(False, False)
        self.attributes("-topmost", True)

        # Center window
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x  = (sw - self.W) // 2
        y  = (sh - self.H) // 2
        self.geometry(f"{self.W}x{self.H}+{x}+{y}")

        self.canvas = tk.Canvas(self, width=self.W, height=self.H,
                                 bg="#080e09", bd=0, highlightthickness=0)
        self.canvas.pack()

        # Window icon
        _set_icon(self)

        # State
        self._frame        = 0
        self._progress     = 0.0      # 0.0 → 1.0
        self._alpha        = 255      # for fade-out (canvas hack via wm alpha)
        self._done         = False
        self._typing_idx   = 0
        self._typing_text  = "by Exter Interactive"
        self._title_glow   = 0

        # Particles: (x, y, vx, vy, radius, alpha_offset)
        import random
        rng = random.Random(42)
        self._particles = [
            [rng.randint(0, self.W), rng.randint(0, self.H),
             rng.uniform(-0.4, 0.4), rng.uniform(-0.3, 0.3),
             rng.randint(1, 3), rng.uniform(0, 6.28)]
            for _ in range(55)
        ]

        # Loading steps
        self._steps = [
            (0.08,  "Initializing core modules..."),
            (0.22,  "Loading system interfaces..."),
            (0.38,  "Connecting to hardware sensors..."),
            (0.55,  "Building UI components..."),
            (0.70,  "Applying Exter design system..."),
            (0.85,  "Preparing network tools..."),
            (1.00,  "Launch!"),
        ]
        self._step_idx    = 0
        self._step_label  = self._steps[0][1]

        # Load logo for splash
        self._splash_logo = _load_logo_tk(size=(72, 72))

        self._tick()

    # ── helpers ──────────────────────────────
    @staticmethod
    def _hex_color(r, g, b, a=255) -> str:
        r = max(0, min(255, int(r)))
        g = max(0, min(255, int(g)))
        b = max(0, min(255, int(b)))
        return f"#{r:02x}{g:02x}{b:02x}"

    def _lerp_color(self, c1, c2, t):
        def h(c): return (int(c[1:3],16), int(c[3:5],16), int(c[5:7],16))
        r1,g1,b1 = h(c1); r2,g2,b2 = h(c2)
        return self._hex_color(r1+(r2-r1)*t, g1+(g2-g1)*t, b1+(b2-b1)*t)

    # ── main tick ────────────────────────────
    def _tick(self):
        if self._done:
            return

        self._frame += 1
        dt = 1 / self.FPS

        # Advance progress
        target_prog = self._steps[min(self._step_idx, len(self._steps)-1)][0]
        if self._progress < target_prog:
            self._progress = min(self._progress + 0.008, target_prog)

        # Advance step
        if self._progress >= target_prog and self._step_idx < len(self._steps) - 1:
            self._step_idx   += 1
            self._step_label  = self._steps[self._step_idx][1]

        # Typing effect for subtitle
        full = self._typing_text
        if self._typing_idx < len(full) and self._frame % 3 == 0:
            self._typing_idx += 1

        # Title glow pulse
        import math
        self._title_glow = (math.sin(self._frame * 0.08) + 1) / 2

        # Launch when done
        if self._progress >= 1.0 and self._frame > 80:
            self._fade_out()
            return

        self._draw()
        self.after(1000 // self.FPS, self._tick)

    def _fade_out(self):
        """Fade window alpha to 0, then destroy and launch main app."""
        alpha = getattr(self, "_fade_alpha", 1.0)
        alpha -= 0.07
        if alpha <= 0:
            self._done = True
            self.destroy()
            _launch_main()
            return
        self._fade_alpha = alpha
        try:
            self.attributes("-alpha", alpha)
        except Exception:
            pass
        self.after(18, self._fade_out)

    # ── draw frame ───────────────────────────
    def _draw(self):
        import math, random
        c   = self.canvas
        W, H = self.W, self.H
        c.delete("all")

        # ── Background gradient (faked with horizontal bands) ──
        band_h = 4
        for i in range(0, H, band_h):
            t  = i / H
            r  = int(8  + 6  * t)
            g  = int(14 + 12 * t)
            b  = int(9  + 8  * t)
            col = self._hex_color(r, g, b)
            c.create_rectangle(0, i, W, i + band_h, fill=col, outline="")

        # ── Radial glow behind title ──
        glow_r  = 180 + int(20 * self._title_glow)
        glow_cx = W // 2
        glow_cy = H // 2 - 40
        for ri in range(glow_r, 0, -8):
            alpha_t = (1 - ri / glow_r) * 0.15 * (0.6 + 0.4 * self._title_glow)
            r = int(74  * alpha_t)
            g = int(222 * alpha_t)
            b = int(128 * alpha_t)
            col = self._hex_color(8 + r, 14 + g, 9 + b)
            c.create_oval(glow_cx - ri, glow_cy - ri,
                          glow_cx + ri, glow_cy + ri,
                          fill=col, outline="")

        # ── Particles ──
        for p in self._particles:
            p[0] = (p[0] + p[2]) % W
            p[1] = (p[1] + p[3]) % H
            p[5] += 0.04
            alpha_t = (math.sin(p[5]) + 1) / 2
            ri  = p[4]
            bright = int(40 + 80 * alpha_t)
            col = self._hex_color(0, bright, int(bright * 0.6))
            x, y = int(p[0]), int(p[1])
            c.create_oval(x - ri, y - ri, x + ri, y + ri,
                          fill=col, outline="")

        # ── Horizontal scan line (moving) ──
        scan_y = int((self._frame * 2.5) % H)
        # scan line — use a very dark green instead of alpha
        c.create_line(0, scan_y, W, scan_y, fill="#0f2a12", width=1)

        # ── Corner brackets decoration ──
        blen = 30
        pad  = 18
        bclr = "#22c55e"
        # top-left
        c.create_line(pad, pad+blen, pad, pad, pad+blen, pad, fill=bclr, width=2)
        # top-right
        c.create_line(W-pad-blen, pad, W-pad, pad, W-pad, pad+blen, fill=bclr, width=2)
        # bottom-left
        c.create_line(pad, H-pad-blen, pad, H-pad, pad+blen, H-pad, fill=bclr, width=2)
        # bottom-right
        c.create_line(W-pad-blen, H-pad, W-pad, H-pad, W-pad, H-pad-blen, fill=bclr, width=2)

        # ── Logo image (above title) ──
        if self._splash_logo:
            logo_y = H // 2 - 115
            c.create_image(W // 2, logo_y, image=self._splash_logo, anchor="center")

        # ── Title ──
        glow_brightness = int(180 + 75 * self._title_glow)
        title_color = self._hex_color(0, glow_brightness, int(glow_brightness * 0.55))
        c.create_text(W//2 + 2, H//2 - 62,   # shadow
                      text="MULTI TOOLS",
                      font=("Segoe UI", 38, "bold"),
                      fill="#001a04", anchor="center")
        c.create_text(W//2, H//2 - 64,
                      text="MULTI TOOLS",
                      font=("Segoe UI", 38, "bold"),
                      fill=title_color, anchor="center")

        # ── Subtitle typing ──
        shown = self._typing_text[:self._typing_idx]
        cursor = "▌" if self._frame % 16 < 8 else ""
        c.create_text(W//2, H//2 - 20,
                      text=shown + cursor,
                      font=("Segoe UI", 14),
                      fill="#2d8a4e" if len(shown) < len(self._typing_text) else "#4ade80",
                      anchor="center")

        # ── Progress bar track ──
        bar_x1, bar_y  = 80, H//2 + 40
        bar_x2, bar_h  = W - 80, 6
        # track
        c.create_rectangle(bar_x1, bar_y, bar_x2, bar_y + bar_h,
                            fill="#1a2e1c", outline="")
        # fill
        fill_x = bar_x1 + int((bar_x2 - bar_x1) * self._progress)
        if fill_x > bar_x1:
            # gradient fill
            seg_w = max(1, fill_x - bar_x1)
            for xi in range(bar_x1, fill_x, 2):
                t = (xi - bar_x1) / seg_w
                r = int(22  + (74 - 22) * t)
                g = int(197 + (222 - 197) * t)
                b = int(88  + (128 - 88) * t)
                col = self._hex_color(r, g, b)
                c.create_rectangle(xi, bar_y, xi + 2, bar_y + bar_h,
                                   fill=col, outline="")
            # pulse glow at tip
            pulse = 0.5 + 0.5 * math.sin(self._frame * 0.25)
            tip_r = int(4 + 3 * pulse)
            tc = self._hex_color(74, 222, 128)
            c.create_oval(fill_x - tip_r, bar_y - tip_r + 3,
                          fill_x + tip_r, bar_y + bar_h + tip_r - 3,
                          fill=tc, outline="")
        # progress percent
        pct_txt = f"{int(self._progress * 100)}%"
        c.create_text(W//2, bar_y + 22,
                      text=self._step_label,
                      font=("Segoe UI", 10),
                      fill="#5d7a62", anchor="center")
        c.create_text(bar_x2, bar_y - 14,
                      text=pct_txt,
                      font=("Segoe UI", 10, "bold"),
                      fill="#4ade80", anchor="e")

        # ── Version tag ──
        c.create_text(W//2, H - 28,
                      text="v2.1.0  ·  Exter Interactive",
                      font=("Segoe UI", 9),
                      fill="#2e4030", anchor="center")


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────
def _launch_main():
    app = MultiToolApp()
    app.mainloop()


if __name__ == "__main__":
    splash = SplashScreen()
    splash.mainloop()
