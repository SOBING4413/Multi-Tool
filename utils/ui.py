"""
ui.py - Modul tampilan & UI helper untuk MultiTool
Mengatur warna, header, input, dan elemen visual di terminal.
Versi 4.0 - UI Profesional dengan animasi, gradient, dan status bar.
"""

import os
import sys
import time
import datetime
import random

from colorama import Fore, Back, Style, init

init(autoreset=True)

# ============================================================
# GLOBAL SETTINGS
# ============================================================
SETTINGS = {
    "theme": "green",
    "animations": True,
}

# Lebar standar untuk semua elemen UI (konsisten)
UI_WIDTH = 62

THEME_COLORS = {
    "green": Fore.GREEN,
    "cyan": Fore.CYAN,
    "yellow": Fore.YELLOW,
    "red": Fore.RED,
    "magenta": Fore.MAGENTA,
    "white": Fore.WHITE,
}

THEME_ACCENT = {
    "green": Fore.LIGHTGREEN_EX,
    "cyan": Fore.LIGHTCYAN_EX,
    "yellow": Fore.LIGHTYELLOW_EX,
    "red": Fore.LIGHTRED_EX,
    "magenta": Fore.LIGHTMAGENTA_EX,
    "white": Fore.LIGHTWHITE_EX,
}

# Gradient colors for fancy effects
GRADIENT_COLORS = [
    Fore.LIGHTGREEN_EX, Fore.GREEN, Fore.CYAN,
    Fore.LIGHTCYAN_EX, Fore.LIGHTGREEN_EX,
]

# Category icons - used as fallback, main menu uses dynamic lookup
CATEGORY_ICONS = {
    "POWER dan SYSTEM": "⚡",
    "INFO dan MONITORING": "📊",
    "JARINGAN dan INTERNET": "🌐",
    "PEMBERSIHAN dan OPTIMASI": "🧹",
    "PROSES dan STARTUP": "⚙️",
    "KEAMANAN dan PRIVASI": "🛡️",
    "SHORTCUT dan TOOLS": "🔧",
    "LAINNYA": "📌",
}

# Icon keywords for dynamic category icon matching
_ICON_KEYWORDS = {
    "POWER": "⚡", "ENERGI": "⚡", "DAYA": "⚡", "GUC": "⚡", "ALIMENT": "⚡",
    "INFO": "📊", "MONITOR": "📊",
    "NETWORK": "🌐", "INTERNET": "🌐", "JARINGAN": "🌐", "RED": "🌐", "NETZ": "🌐", "RESEAU": "🌐", "MANG": "🌐",
    "CLEAN": "🧹", "OPTIM": "🧹", "BERSIH": "🧹", "LIMPI": "🧹", "BEREIN": "🧹", "NETTOY": "🧹", "RESIK": "🧹",
    "PROCESS": "⚙️", "STARTUP": "⚙️", "PROSES": "⚙️", "PROZESS": "⚙️",
    "SECUR": "🛡️", "PRIVAC": "🛡️", "KEAMANAN": "🛡️", "SEGUR": "🛡️", "SICHER": "🛡️",
    "SHORTCUT": "🔧", "TOOL": "🔧", "ATAJO": "🔧", "RACCOURC": "🔧",
    "OTHER": "📌", "LAIN": "📌", "OTRO": "📌", "SONST": "📌", "AUTRE": "📌", "KHAC": "📌",
}


def _get_category_icon(title):
    """Get icon for a category title by keyword matching."""
    # First try exact match
    icon = CATEGORY_ICONS.get(title)
    if icon:
        return icon
    # Then try keyword matching
    upper = title.upper()
    for keyword, ico in _ICON_KEYWORDS.items():
        if keyword in upper:
            return ico
    return "●"

# Box drawing characters
BOX = {
    "tl": "╔", "tr": "╗", "bl": "╚", "br": "╝",
    "h": "═", "v": "║",
    "lt": "╠", "rt": "╣",
    "top_t": "╦", "bot_t": "╩",
    "cross": "╬",
    "thin_h": "─", "thin_v": "│",
    "thin_tl": "┌", "thin_tr": "┐",
    "thin_bl": "└", "thin_br": "┘",
    "thin_lt": "├", "thin_rt": "┤",
    "dot": "•", "arrow": "►", "diamond": "◆",
    "star": "★", "circle": "●",
    "tri_r": "▶", "tri_d": "▼",
    "block_full": "█", "block_light": "░",
    "block_med": "▒", "block_dark": "▓",
    "spark": "✦", "check": "✔", "cross_mark": "✘",
    "gear": "⚙", "bolt": "⚡", "shield": "🛡",
}

# Tips - now loaded from language module at runtime
# Kept as fallback for when language module is not available
TIPS = [
    "Tip: Run as Admin for full access to all features!",
    "Tip: Use menu [41] to change the color theme.",
    "Tip: Press Ctrl+C to stop a running process.",
    "Tip: Reduce startup programs to speed up boot time.",
    "Tip: Clean temp files regularly for optimal performance.",
    "Tip: Check your computer security regularly with menu [30].",
    "Tip: Use Speed Test [23] to check your internet speed.",
    "Tip: Privacy Cleaner [36] helps protect your privacy.",
]


def get_color():
    """Ambil warna tema saat ini."""
    return THEME_COLORS.get(SETTINGS["theme"], Fore.GREEN)


def get_accent():
    """Ambil warna aksen tema saat ini."""
    return THEME_ACCENT.get(SETTINGS["theme"], Fore.LIGHTGREEN_EX)


def get_gradient_color(index):
    """Ambil warna gradient berdasarkan index."""
    return GRADIENT_COLORS[index % len(GRADIENT_COLORS)]


def clear_screen():
    """Bersihkan layar terminal."""
    os.system("cls" if os.name == "nt" else "clear")


def get_greeting():
    """Dapatkan sapaan berdasarkan waktu."""
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        return "Selamat Pagi"
    elif 12 <= hour < 15:
        return "Selamat Siang"
    elif 15 <= hour < 18:
        return "Selamat Sore"
    else:
        return "Selamat Malam"


def get_random_tip():
    """Ambil tip random."""
    return random.choice(TIPS)


def type_text(text, delay=0.02, color=None):
    """Efek mengetik teks satu per satu karakter."""
    if not SETTINGS.get("animations", True):
        if color:
            print(f"  {color}{text}{Style.RESET_ALL}")
        else:
            print(f"  {text}")
        return
    prefix = f"  {color}" if color else "  "
    sys.stdout.write(prefix)
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    if color:
        sys.stdout.write(Style.RESET_ALL)
    sys.stdout.write("\n")
    sys.stdout.flush()


def animate_line(text, color=None, delay=0.005):
    """Animasi menampilkan satu baris dengan efek sweep."""
    if not SETTINGS.get("animations", True):
        c = color or get_color()
        print(f"  {c}{text}{Style.RESET_ALL}")
        return
    c = color or get_color()
    sys.stdout.write(f"  {c}")
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write(f"{Style.RESET_ALL}\n")
    sys.stdout.flush()


def print_gradient_text(text, center_width=0):
    """Cetak teks dengan efek gradient warna."""
    if center_width > 0:
        text = text.center(center_width)
    result = "  "
    for i, char in enumerate(text):
        color = get_gradient_color(i)
        result += f"{color}{char}"
    result += Style.RESET_ALL
    print(result)


def pause():
    """Wait for user to press Enter."""
    c = get_color()
    a = get_accent()
    dim = Style.DIM
    # Try to get translated text, fallback to English
    try:
        from utils.language import lang
        prompt_text = lang("press_enter")
    except Exception:
        prompt_text = "Press Enter to return to menu..."
    print()
    print(f"  {dim}{c}{'─' * UI_WIDTH}{Style.RESET_ALL}")
    input(f"  {a}{BOX['arrow']} {c}{prompt_text}{Style.RESET_ALL}")


def print_header(title):
    """Cetak header dengan border yang rapi, sejajar, dan profesional."""
    c = get_color()
    a = get_accent()
    clear_screen()
    w = UI_WIDTH

    print()
    print(f"  {c}{BOX['tl']}{BOX['h'] * w}{BOX['tr']}")
    print(f"  {BOX['v']}{' ' * w}{BOX['v']}")
    # Center the title with diamond icon
    title_display = f"{BOX['diamond']} {title}"
    padding_left = (w - len(title_display) - 2) // 2
    padding_right = w - len(title_display) - 2 - padding_left
    print(f"  {BOX['v']}  {' ' * padding_left}{a}{title_display}{c}{' ' * padding_right}{BOX['v']}")
    print(f"  {BOX['v']}{' ' * w}{BOX['v']}")
    print(f"  {BOX['bl']}{BOX['h'] * w}{BOX['br']}{Style.RESET_ALL}")
    print()


def print_sub_header(title):
    """Cetak sub-header yang lebih kecil."""
    c = get_color()
    a = get_accent()
    w = UI_WIDTH - 2
    print()
    print(f"  {c}{BOX['thin_tl']}{BOX['thin_h'] * w}{BOX['thin_tr']}")
    title_padded = f"  {title}"
    remaining = w - len(title_padded)
    print(f"  {BOX['thin_v']}{a}{title_padded}{c}{' ' * max(0, remaining)}{BOX['thin_v']}")
    print(f"  {BOX['thin_bl']}{BOX['thin_h'] * w}{BOX['thin_br']}{Style.RESET_ALL}")
    print()


def print_success(msg):
    """Cetak pesan sukses."""
    print(f"  {Fore.GREEN}{BOX['check']} [✓] {msg}{Style.RESET_ALL}")


def print_info(msg):
    """Cetak pesan info."""
    print(f"  {Fore.CYAN}{BOX['dot']} [*] {msg}{Style.RESET_ALL}")


def print_warning(msg):
    """Cetak pesan warning."""
    print(f"  {Fore.YELLOW}{BOX['star']} [!] {msg}{Style.RESET_ALL}")


def print_error(msg):
    """Cetak pesan error."""
    print(f"  {Fore.RED}{BOX['cross_mark']} [✗] {msg}{Style.RESET_ALL}")


def get_input(prompt):
    """Ambil input dari user dengan warna tema."""
    c = get_color()
    a = get_accent()
    return input(f"  {a}{BOX['tri_r']} {c}{prompt}{Style.RESET_ALL}")


def print_section(title):
    """Cetak judul section dengan dekorasi."""
    c = get_color()
    a = get_accent()
    w = UI_WIDTH - 6 - len(title)
    print(f"  {c}{BOX['thin_lt']}{BOX['thin_h'] * 3} {a}{title} {c}{BOX['thin_h'] * max(0, w)}{BOX['thin_rt']}{Style.RESET_ALL}")


def print_divider(char="─", length=None):
    """Cetak garis pemisah."""
    c = get_color()
    if length is None:
        length = UI_WIDTH
    print(f"  {Style.DIM}{c}{char * length}{Style.RESET_ALL}")


def print_menu_category(title):
    """Print menu category with icon and professional style."""
    c = get_color()
    a = get_accent()
    icon = _get_category_icon(title)
    display_title = f"{icon} {title}"
    # Account for emoji width (most emoji are 2 chars wide in terminal)
    visible_len = len(title) + 2  # icon + space
    w = UI_WIDTH - 5 - visible_len
    print(f"  {c}{BOX['thin_tl']}{BOX['thin_h']} {a}{display_title} {c}{BOX['thin_h'] * max(0, w)}{BOX['thin_tr']}{Style.RESET_ALL}")


def print_menu_item(num, label, icon=""):
    """Cetak item menu dengan format yang rapi dan sejajar."""
    c = get_color()
    a = get_accent()
    dim = Style.DIM
    icon_str = f"{icon} " if icon else ""
    # Nomor rata kanan 2 digit, label rata kiri
    num_display = f"{num:>2}"
    item_text = f"  {dim}{c}[{a}{num_display}{dim}{c}]{Style.RESET_ALL} {c}{icon_str}{label}"
    # Calculate visible length (without ANSI codes) for padding
    visible_len = 2 + 1 + len(num_display) + 1 + 1 + len(icon_str) + len(label)
    remaining = UI_WIDTH - visible_len - 3
    print(f"  {c}{BOX['thin_v']}{item_text}{' ' * max(0, remaining)}{c}{BOX['thin_v']}{Style.RESET_ALL}")


def print_menu_end():
    """Cetak penutup kategori menu."""
    c = get_color()
    w = UI_WIDTH - 2
    print(f"  {c}{BOX['thin_bl']}{BOX['thin_h'] * w}{BOX['thin_br']}{Style.RESET_ALL}")


def print_progress_bar(label, percent, bar_length=25):
    """Cetak progress bar visual yang lebih menarik."""
    percent = max(0, min(100, percent))
    filled = int(bar_length * percent / 100)
    bar = "█" * filled + "░" * (bar_length - filled)

    if percent > 80:
        color = Fore.RED
    elif percent > 50:
        color = Fore.YELLOW
    else:
        color = Fore.GREEN

    print(f"  {color}  {label}: [{bar}] {percent:.1f}%{Style.RESET_ALL}")


def print_key_value(key, value, indent=4):
    """Cetak pasangan key-value dengan format rapi."""
    c = get_color()
    a = get_accent()
    spaces = " " * indent
    print(f"  {spaces}{a}{key:<20}{c}{value}{Style.RESET_ALL}")


def print_table_row(cols, widths, colors=None):
    """Cetak baris tabel sederhana."""
    c = get_color()
    row = "  "
    for i, (col, width) in enumerate(zip(cols, widths)):
        color = colors[i] if colors and i < len(colors) else c
        row += f"{color}{str(col):<{width}}{Style.RESET_ALL}"
    print(row)


def print_table_header(cols, widths):
    """Cetak header tabel."""
    a = get_accent()
    c = get_color()
    header = "  "
    for col, width in zip(cols, widths):
        header += f"{a}{str(col):<{width}}{Style.RESET_ALL}"
    print(header)
    total_width = sum(widths)
    print(f"  {c}{'─' * total_width}{Style.RESET_ALL}")


def loading_animation(text="Memproses", duration=1.0, steps=10):
    """Tampilkan animasi loading dengan spinner dan progress bar."""
    c = get_color()
    a = get_accent()
    spinners = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    for i in range(steps):
        spinner = spinners[i % len(spinners)]
        bar_filled = int(20 * (i + 1) / steps)
        bar = "█" * bar_filled + "░" * (20 - bar_filled)
        pct = int((i + 1) / steps * 100)
        sys.stdout.write(f"\r  {a}{spinner} {c}{text} [{bar}] {pct}%{Style.RESET_ALL}")
        sys.stdout.flush()
        time.sleep(duration / steps)
    sys.stdout.write(f"\r  {Fore.GREEN}✔ {c}{text} [{'█' * 20}] 100%{Style.RESET_ALL}\n")
    sys.stdout.flush()


def loading_spinner(text="Memproses", duration=1.5):
    """Tampilkan animasi spinner saja (tanpa progress bar)."""
    c = get_color()
    a = get_accent()
    spinners = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]
    steps = int(duration / 0.1)
    for i in range(steps):
        spinner = spinners[i % len(spinners)]
        dots = "." * ((i // 3) % 4)
        sys.stdout.write(f"\r  {a}{spinner} {c}{text}{dots:<4}{Style.RESET_ALL}")
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write(f"\r  {Fore.GREEN}✔ {c}{text}    {Style.RESET_ALL}\n")
    sys.stdout.flush()


def print_box(lines, width=None):
    """Cetak teks dalam box dengan lebar konsisten."""
    if width is None:
        width = UI_WIDTH - 4
    c = get_color()
    a = get_accent()
    print(f"  {c}{BOX['tl']}{BOX['h'] * (width + 2)}{BOX['tr']}")
    for line in lines:
        padding = width - len(line)
        left_pad = padding // 2
        right_pad = padding - left_pad
        print(f"  {BOX['v']} {a}{' ' * left_pad}{line}{' ' * right_pad}{c} {BOX['v']}")
    print(f"  {BOX['bl']}{BOX['h'] * (width + 2)}{BOX['br']}{Style.RESET_ALL}")


def print_fancy_box(lines, title="", width=None):
    """Cetak teks dalam box dengan judul di border atas."""
    if width is None:
        width = UI_WIDTH - 4
    c = get_color()
    a = get_accent()
    if title:
        title_display = f" {title} "
        remaining = width + 2 - len(title_display) - 1
        left_h = 1
        right_h = max(0, remaining)
        print(f"  {c}{BOX['tl']}{BOX['h'] * left_h}{a}{title_display}{c}{BOX['h'] * right_h}{BOX['tr']}")
    else:
        print(f"  {c}{BOX['tl']}{BOX['h'] * (width + 2)}{BOX['tr']}")
    for line in lines:
        padding = width - len(line)
        left_pad = padding // 2
        right_pad = padding - left_pad
        print(f"  {BOX['v']} {a}{' ' * left_pad}{line}{' ' * right_pad}{c} {BOX['v']}")
    print(f"  {BOX['bl']}{BOX['h'] * (width + 2)}{BOX['br']}{Style.RESET_ALL}")


def print_status_badge(label, is_ok, detail=""):
    """Cetak badge status (OK/FAIL)."""
    if is_ok is True:
        icon = f"{Fore.GREEN}● AMAN{Style.RESET_ALL}"
    elif is_ok is False:
        icon = f"{Fore.RED}● PERHATIAN{Style.RESET_ALL}"
    else:
        icon = f"{Fore.YELLOW}● N/A{Style.RESET_ALL}"

    c = get_color()
    print(f"  {c}  {icon}  {c}{label}")
    if detail:
        print(f"  {c}         {Style.DIM}{detail}{Style.RESET_ALL}")


def print_system_status_bar():
    """Cetak status bar sistem (CPU, RAM, Waktu) di bagian atas."""
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=0)
        ram = psutil.virtual_memory()
        ram_pct = ram.percent
    except Exception:
        cpu = 0
        ram_pct = 0

    now = datetime.datetime.now().strftime("%H:%M:%S")
    date_str = datetime.datetime.now().strftime("%d/%m/%Y")

    c = get_color()
    a = get_accent()
    dim = Style.DIM

    # CPU color
    if cpu > 80:
        cpu_color = Fore.RED
    elif cpu > 50:
        cpu_color = Fore.YELLOW
    else:
        cpu_color = Fore.GREEN

    # RAM color
    if ram_pct > 80:
        ram_color = Fore.RED
    elif ram_pct > 50:
        ram_color = Fore.YELLOW
    else:
        ram_color = Fore.GREEN

    # Build status bar
    cpu_bar_len = 8
    cpu_filled = int(cpu_bar_len * cpu / 100)
    cpu_bar = "█" * cpu_filled + "░" * (cpu_bar_len - cpu_filled)

    ram_bar_len = 8
    ram_filled = int(ram_bar_len * ram_pct / 100)
    ram_bar = "█" * ram_filled + "░" * (ram_bar_len - ram_filled)

    w = UI_WIDTH
    print(f"  {dim}{c}┌{'─' * w}┐{Style.RESET_ALL}")
    status_line = (
        f" {dim}📅 {date_str}  🕐 {now}  "
        f"{cpu_color}CPU[{cpu_bar}]{cpu:.0f}%{Style.RESET_ALL}{dim}  "
        f"{ram_color}RAM[{ram_bar}]{ram_pct:.0f}%{Style.RESET_ALL}"
    )
    # Simple approach: just print the status content
    print(f"  {dim}{c}│{Style.RESET_ALL}{status_line}{dim}{c} │{Style.RESET_ALL}")
    print(f"  {dim}{c}└{'─' * w}┘{Style.RESET_ALL}")


def splash_screen():
    """Tampilkan splash screen animasi saat pertama kali buka."""
    clear_screen()
    c = get_color()
    a = get_accent()
    dim = Style.DIM

    # Animated border
    w = UI_WIDTH
    print()

    # Top border animation
    sys.stdout.write(f"  {c}{BOX['tl']}")
    sys.stdout.flush()
    for i in range(w):
        sys.stdout.write(f"{BOX['h']}")
        sys.stdout.flush()
        time.sleep(0.005)
    sys.stdout.write(f"{BOX['tr']}\n")
    sys.stdout.flush()

    # Empty line
    print(f"  {c}{BOX['v']}{' ' * w}{BOX['v']}")

    # Animated title
    title_lines = [
        "███╗   ███╗██╗   ██╗██╗  ████████╗██╗",
        "████╗ ████║██║   ██║██║  ╚══██╔══╝██║",
        "██╔████╔██║██║   ██║██║     ██║   ██║",
        "██║╚██╔╝██║██║   ██║██║     ██║   ██║",
        "██║ ╚═╝ ██║╚██████╔╝███████╗██║   ██║",
        "╚═╝     ╚═╝ ╚═════╝ ╚══════╝╚═╝   ╚═╝",
    ]

    for line in title_lines:
        if len(line) > w - 4:
            line = line[:w - 4]
        pad_l = (w - len(line)) // 2
        pad_r = w - len(line) - pad_l
        # Gradient effect per line
        colored_line = ""
        for j, ch in enumerate(line):
            colored_line += f"{get_gradient_color(j)}{ch}"
        print(f"  {c}{BOX['v']}{' ' * pad_l}{colored_line}{Style.RESET_ALL}{c}{' ' * pad_r}{BOX['v']}")
        time.sleep(0.05)

    # Subtitle
    print(f"  {c}{BOX['v']}{' ' * w}{BOX['v']}")
    subtitle = "T O O L"
    pad_l = (w - len(subtitle)) // 2
    pad_r = w - len(subtitle) - pad_l
    print(f"  {c}{BOX['v']}{' ' * pad_l}{a}{subtitle}{c}{' ' * pad_r}{BOX['v']}")
    print(f"  {c}{BOX['v']}{' ' * w}{BOX['v']}")

    # Separator
    print(f"  {c}{BOX['lt']}{BOX['h'] * w}{BOX['rt']}")

    # Loading bar animation
    try:
        from utils.language import lang as _lang
        loading_text = _lang("loading_components")
    except Exception:
        loading_text = "Loading components"
    print(f"  {c}{BOX['v']}{' ' * w}{BOX['v']}")
    bar_w = 40
    for i in range(bar_w + 1):
        bar = "█" * i + "░" * (bar_w - i)
        pct = int(i / bar_w * 100)
        pad_l = (w - bar_w - 8) // 2
        pad_r = w - bar_w - 8 - pad_l
        line_content = f"{' ' * pad_l}{a}[{bar}] {pct:>3}%{c}{' ' * pad_r}"
        sys.stdout.write(f"\r  {c}{BOX['v']}{line_content}{BOX['v']}")
        sys.stdout.flush()
        time.sleep(0.015)
    print()

    print(f"  {c}{BOX['v']}{' ' * w}{BOX['v']}")

    # Bottom border animation
    sys.stdout.write(f"  {c}{BOX['bl']}")
    sys.stdout.flush()
    for i in range(w):
        sys.stdout.write(f"{BOX['h']}")
        sys.stdout.flush()
        time.sleep(0.005)
    sys.stdout.write(f"{BOX['br']}\n")
    sys.stdout.flush()

    print()
    try:
        from utils.language import get_greeting_text as _get_greeting_text, lang as _lang
        greeting = _get_greeting_text()
        welcome = _lang("welcome")
    except Exception:
        greeting = get_greeting()
        welcome = "Welcome to MultiTool"
    type_text(f"  {greeting}! {welcome}...", delay=0.03, color=a)
    time.sleep(0.5)