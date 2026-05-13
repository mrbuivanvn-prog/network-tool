import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import socket
import subprocess
import threading
import json
import platform
import re
import ipaddress
import time
import queue
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
import base64
from io import BytesIO

# ============================================================================
# ẢNH SỨA NHÚNG TRỰC TIẾP (BASE64) - KHÔNG CẦN FILE NGOÀI
# ============================================================================
JELLYFISH_BASE64 = """
iVBORw0KGgoAAAANSUhEUgAAAMgAAADICAYAAACtWK6eAAAACXBIWXMAAAsTAAALEwEAmpwYAAAF8GlUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4gPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iQWRvYmUgWE1QIENvcmUgNS42LWMxNDUgNzkuMTYzNDk5LCAyMDE4LzA4LzEzLTE2OjQwOjIyICAgICAgICAiPiA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPiA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIiB4bWxuczp4bXA9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8iIHhtbG5zOnhtcE1NPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvbW0vIiB4bWxuczpzdFJlZj0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL3NUeXBlL1Jlc291cmNlUmVmIyIgeG1wOkNyZWF0b3JUb29sPSJBZG9iZSBQaG90b3Nob3AgQ0MgMjAxOSAoV2luZG93cykiIHhtcE1NOkluc3RhbmNlSUQ9InhtcC5paWQ6M0I5MjI5RjQxQkFCMTFFQTgzMDhFODM5RkY5MjAzQzgiIHhtcE1NOkRvY3VtZW50SUQ9InhtcC5kaWQ6M0I5MjI5RjUxQkFCMTFFQTgzMDhFODM5RkY5MjAzQzgiPiA8eG1wTU06RGVyaXZlZEZyb20gc3RSZWY6aW5zdGFuY2VJRD0ieG1wLmlpZDozQjkyMjlGMjFCQUIxMUVBODMwOEU4MzlGRjkyMDNDOCIgc3RSZWY6ZG9jdW1lbnRJRD0ieG1wLmRpZDozQjkyMjlGMzFCQUIxMUVBODMwOEU4MzlGRjkyMDNDOCIvPiA8L3JkZjpEZXNjcmlwdGlvbj4gPC9yZGY6UkRGPiA8L3g6eG1wbWV0YT4gPD94cGFja2V0IGVuZD0iciI/Pk3I/YYAAAY5SURBVHic7dpPaBxVHMfx7yRtsu0f0pCm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
"""

# ============================================================================
# GIẢI MÃ ẢNH BASE64 THÀNH PHOTOIMAGE
# ============================================================================
def get_jellyfish_image():
    try:
        from PIL import Image, ImageTk
        img_data = base64.b64decode(JELLYFISH_BASE64)
        img = Image.open(BytesIO(img_data))
        img = img.resize((180, 180), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)
    except:
        return None

# ============================================================================
# PHẦN CÒN LẠI CỦA CODE (GIỮ NGUYÊN NHƯ BẢN PRO)
# ============================================================================
SYSTEM = platform.system().lower()
IS_WINDOWS = SYSTEM == 'windows'

COLORS = {
    'bg_deep': '#020617',
    'bg_mid': '#0F172A',
    'card_glass': '#1E293BCC',
    'border_neon': '#06B6D4',
    'neon_cyan': '#00F0FF',
    'neon_pink': '#FF007F',
    'neon_purple': '#A855F7',
    'neon_green': '#10B981',
    'text_glow': '#FFFFFF',
    'text_dim': '#94A3B8',
    'success': '#34D399',
    'error': '#F87171',
}

# ============================================================================
# LỚP NỀN SỨA BƠI (DÙNG ẢNH NHÚNG)
# ============================================================================
class JellyfishBackground(tk.Canvas):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.configure(bg=COLORS['bg_deep'], highlightthickness=0)
        self.jellyfish_photo = get_jellyfish_image()
        self.jellyfish_x = 100
        self.jellyfish_y = 300
        self.jellyfish_dx = 1.2
        self.is_moving_right = True
        self.draw_jellyfish()
        self.animate_jellyfish()
    
    def draw_jellyfish(self):
        if self.jellyfish_photo:
            self.create_image(self.jellyfish_x, self.jellyfish_y, image=self.jellyfish_photo, tags="jellyfish")
        else:
            # Fallback nếu không có PIL
            self.create_oval(80, 250, 160, 330, fill="#38BDF8", outline="#22D3EE", width=2, tags="jellyfish")
            for i in range(6):
                self.create_line(100 + i*10, 330, 90 + i*15, 400, fill="#22D3EE", width=2, tags="jellyfish")
    
    def animate_jellyfish(self):
        if self.jellyfish_photo:
            if self.is_moving_right:
                self.jellyfish_x += self.jellyfish_dx
                if self.jellyfish_x >= self.winfo_width() - 150:
                    self.is_moving_right = False
            else:
                self.jellyfish_x -= self.jellyfish_dx
                if self.jellyfish_x <= 150:
                    self.is_moving_right = True
            self.delete("jellyfish")
            if 0 < self.jellyfish_x < self.winfo_width():
                self.create_image(self.jellyfish_x, self.jellyfish_y, image=self.jellyfish_photo, tags="jellyfish")
        self.after(40, self.animate_jellyfish)

# ============================================================================
# NÚT NEON
# ============================================================================
class NeonButton(tk.Button):
    def __init__(self, parent, text="", command=None, color=COLORS['neon_cyan'], width=12):
        super().__init__(parent, text=text, command=command,
                        bg=COLORS['bg_mid'], fg=color, font=("Segoe UI", 10, "bold"),
                        relief=tk.FLAT, bd=0, padx=8, pady=5, activebackground=color,
                        activeforeground="black", cursor="hand2", width=width)
        self.default_fg = color
        self.bind("<Enter>", lambda e: self.config(bg=self.default_fg, fg="black"))
        self.bind("<Leave>", lambda e: self.config(bg=COLORS['bg_mid'], fg=self.default_fg))

# ============================================================================
# GLASS CARD
# ============================================================================
class GlassCard(tk.Frame):
    def __init__(self, parent, title="", **kwargs):
        super().__init__(parent, bg=COLORS['card_glass'], highlightbackground=COLORS['border_neon'], highlightthickness=1, **kwargs)
        if title:
            tk.Label(self, text=title, bg=COLORS['card_glass'], fg=COLORS['neon_cyan'], font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=12, pady=(8, 0))
        self.content = tk.Frame(self, bg=COLORS['card_glass'])
        self.content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# ============================================================================
# HOST CARD
# ============================================================================
class HostCard(tk.Frame):
    def __init__(self, parent, ip, name, on_remove, on_update):
        super().__init__(parent, bg=COLORS['bg_mid'], bd=1, relief=tk.FLAT, highlightbackground=COLORS['border_neon'], highlightthickness=1)
        self.ip = ip
        self.name = name
        self.on_remove = on_remove
        self.on_update = on_update
        self.running = True
        self.queue = queue.Queue()
        self.last_update = 0
        self.update_interval = 3
        self.mac = "Unknown"
        self.vlan = "Default"
        self.vnc_user = ""
        self.vnc_pass = ""
        self._create_ui()
        self._start_ping()
    
    def _create_ui(self):
        self.pack(side=tk.LEFT, padx=8, pady=8, fill=tk.BOTH, expand=True)
        header = tk.Frame(self, bg=COLORS['bg_mid'])
        header.pack(fill=tk.X, padx=10, pady=8)
        self.led = tk.Label(header, text="●", font=('Arial', 12), fg=COLORS['error'], bg=COLORS['bg_mid'])
        self.led.pack(side=tk.LEFT, padx=5)
        tk.Label(header, text=self.name, font=('Segoe UI', 10, 'bold'), fg=COLORS['text_glow'], bg=COLORS['bg_mid']).pack(side=tk.LEFT, padx=5)
        tk.Label(header, text=self.ip, font=('Segoe UI', 8), fg=COLORS['text_dim'], bg=COLORS['bg_mid']).pack(side=tk.LEFT, padx=5)
        btn_frame = tk.Frame(header, bg=COLORS['bg_mid'])
        btn_frame.pack(side=tk.RIGHT)
        tk.Button(btn_frame, text="⚙️", command=self._settings, bg=COLORS['bg_mid'], fg=COLORS['text_glow'], relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT)
        tk.Button(btn_frame, text="✕", command=self._remove, bg=COLORS['bg_mid'], fg=COLORS['error'], relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        self.stats_text = tk.Label(self, text="⏳ Đang kiểm tra...", font=('Consolas', 8), fg=COLORS['text_dim'], bg=COLORS['bg_mid'])
        self.stats_text.pack(anchor=tk.W, padx=10, pady=2)
        tk.Label(self, text=f"MAC: {self.mac} | VLAN: {self.vlan}", font=('Segoe UI', 7), fg=COLORS['text_dim'], bg=COLORS['bg_mid']).pack(anchor=tk.W, padx=10)
        
        btn_row = tk.Frame(self, bg=COLORS['bg_mid'])
        btn_row.pack(fill=tk.X, padx=10, pady=8)
        for text, cmd, color in [("SSH", self._ssh, COLORS['neon_cyan']), ("HTTP", self._http, COLORS['neon_green']), ("VNC", self._vnc, COLORS['neon_pink']), ("RDP", self._rdp, COLORS['neon_purple'])]:
            btn = tk.Button(btn_row, text=text, bg=COLORS['bg_deep'], fg=color, font=('Segoe UI', 8, 'bold'), relief=tk.FLAT, command=cmd)
            btn.pack(side=tk.LEFT, padx=4, expand=True, fill=tk.X)
    
    def _ping_once(self):
        try:
            param = '-n' if IS_WINDOWS else '-c'
            cmd = ['ping', param, '1', '-W', '1', self.ip]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
            success = result.returncode == 0
            times = re.findall(r'time[= ](\d+\.?\d*)\s*ms', result.stdout.lower())
            avg = float(times[0]) if times else None
            return {'success': success, 'avg': avg, 'loss': 0 if success else 100}
        except: return {'success': False, 'avg': None, 'loss': 100}
    
    def _get_mac(self):
        try:
            cmd = ['arp', '-a', self.ip] if IS_WINDOWS else ['arp', '-n', self.ip]
            out = subprocess.check_output(cmd, universal_newlines=True, timeout=3)
            mac = re.search(r'([0-9a-fA-F]{2}[:-]){5}([0-9a-fA-F]{2})', out)
            return mac.group(0) if mac else "Unknown"
        except: return "Unknown"
    
    def _start_ping(self):
        def loop():
            while self.running:
                current_time = time.time()
                if current_time - self.last_update >= self.update_interval:
                    r = self._ping_once()
                    self.queue.put(r)
                    self.mac = self._get_mac()
                    self.last_update = current_time
                time.sleep(0.5)
        threading.Thread(target=loop, daemon=True).start()
        threading.Thread(target=self._update, daemon=True).start()
    
    def _update(self):
        while self.running:
            try:
                if not self.queue.empty():
                    r = self.queue.get_nowait()
                    if r['success']:
                        self.led.config(fg=COLORS['success'])
                        self.stats_text.config(text=f"✓ ONLINE | Ping: {r['avg']:.0f}ms", fg=COLORS['success'])
                    else:
                        self.led.config(fg=COLORS['error'])
                        self.stats_text.config(text="✗ OFFLINE | Mất kết nối", fg=COLORS['error'])
            except: pass
            time.sleep(0.5)
    
    def _settings(self):
        win = tk.Toplevel(self)
        win.title(f"Cài đặt {self.name}")
        win.geometry("400x300")
        win.configure(bg=COLORS['bg_mid'])
        tk.Label(win, text="VLAN:", bg=COLORS['bg_mid'], fg='white').pack(anchor=tk.W, padx=15, pady=(15,0))
        vlan_e = tk.Entry(win, bg=COLORS['bg_deep'], fg='white')
        vlan_e.insert(0, self.vlan)
        vlan_e.pack(fill=tk.X, padx=15, pady=5)
        tk.Label(win, text="VNC User:", bg=COLORS['bg_mid'], fg='white').pack(anchor=tk.W, padx=15, pady=(10,0))
        user_e = tk.Entry(win, bg=COLORS['bg_deep'], fg='white')
        user_e.insert(0, self.vnc_user)
        user_e.pack(fill=tk.X, padx=15, pady=5)
        tk.Label(win, text="VNC Pass:", bg=COLORS['bg_mid'], fg='white').pack(anchor=tk.W, padx=15, pady=(10,0))
        pass_e = tk.Entry(win, bg=COLORS['bg_deep'], fg='white', show="*")
        pass_e.insert(0, self.vnc_pass)
        pass_e.pack(fill=tk.X, padx=15, pady=5)
        def save():
            self.vlan, self.vnc_user, self.vnc_pass = vlan_e.get(), user_e.get(), pass_e.get()
            win.destroy()
        tk.Button(win, text="Lưu", command=save, bg=COLORS['neon_cyan'], fg='black').pack(pady=15)
    
    def _ssh(self): subprocess.Popen(['ssh', self.ip])
    def _http(self): import webbrowser; webbrowser.open(f'http://{self.ip}')
    def _rdp(self): subprocess.Popen(['mstsc', '/v', self.ip]) if IS_WINDOWS else None
    def _vnc(self): subprocess.Popen(['vncviewer', self.ip])
    def _remove(self): self.running = False; self.destroy(); self.on_remove(self.ip)
    def stop(self): self.running = False


# ============================================================================
# ỨNG DỤNG CHÍNH (RÚT GỌN NHƯNG ĐẦY ĐỦ CHỨC NĂNG)
# ============================================================================
class NetToolApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🐙 Network Pro | Jellyfish 3D")
        self.root.geometry("1500x900")
        
        self.bg_canvas = JellyfishBackground(self.root)
        self.bg_canvas.pack(fill=tk.BOTH, expand=True)
        
        self.main_container = tk.Frame(self.bg_canvas, bg='')
        self.main_container.place(relwidth=1, relheight=1)
        
        self.hosts = {}
        self.groups = {"Default": []}
        self.config_file = Path.home() / ".network_pro.json"
        
        self._create_ui()
        self._load_config()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _create_ui(self):
        # Header
        header = tk.Frame(self.main_container, bg=COLORS['card_glass'], highlightbackground=COLORS['border_neon'], highlightthickness=1)
        header.pack(fill=tk.X, pady=10, padx=15)
        tk.Label(header, text="🌊 NETWORK PRO TOOL", bg=COLORS['card_glass'], fg=COLORS['neon_cyan'], font=('Segoe UI', 18, 'bold')).pack(side=tk.LEFT, padx=20)
        tk.Label(header, text="🐙 Jellyfish 3D", bg=COLORS['card_glass'], fg=COLORS['neon_pink']).pack(side=tk.LEFT)
        
        # Sidebar
        sidebar = tk.Frame(self.main_container, bg=COLORS['card_glass'], width=140, highlightbackground=COLORS['border_neon'], highlightthickness=1)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=15, pady=10)
        sidebar.pack_propagate(False)
        
        nav = [("📡 PING", self.show_ping), ("🗺️ TRACE", self.show_trace), ("🔍 SCAN", self.show_scan),
               ("🔌 PORT", self.show_ports), ("📊 ANALYSIS", self.show_analysis), ("📋 GROUPS", self.show_groups),
               ("💾 BACKUP", self.show_backup), ("ℹ️ INFO", self.show_info)]
        for text, cmd in nav:
            NeonButton(sidebar, text=text, command=cmd, width=12).pack(pady=6, padx=10)
        
        self.content = tk.Frame(self.main_container, bg=COLORS['card_glass'])
        self.content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.pages = {}
        self._build_ping()
        self._build_trace()
        self._build_scan()
        self._build_ports()
        self._build_analysis()
        self._build_groups()
        self._build_backup()
        self._build_info()
        self.show_ping()
    
    def _build_ping(self):
        page = tk.Frame(self.content, bg=COLORS['card_glass'])
        GlassCard(page, "🐙 Live Monitoring").pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        top = tk.Frame(page, bg=COLORS['card_glass'])
        top.pack(fill=tk.X, padx=20, pady=10)
        self.search_ip = tk.Entry(top, bg=COLORS['bg_mid'], fg='white', insertbackground=COLORS['neon_cyan'])
        self.search_ip.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0,10))
        NeonButton(top, "➕ Add Host", self._add_host, COLORS['neon_green']).pack(side=tk.LEFT)
        NeonButton(top, "⏹ Stop All", self._stop_all, COLORS['error']).pack(side=tk.LEFT, padx=10)
        self.hosts_container = tk.Frame(page, bg=COLORS['card_glass'])
        self.hosts_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        self.pages["ping"] = page
    
    def _build_trace(self):
        page = tk.Frame(self.content, bg=COLORS['card_glass'])
        card = GlassCard(page, "🐙 Traceroute")
        card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        frame = tk.Frame(card.content, bg=COLORS['card_glass'])
        frame.pack(fill=tk.X)
        self.trace_target = tk.Entry(frame, bg=COLORS['bg_mid'], fg='white', width=40)
        self.trace_target.insert(0, "8.8.8.8")
        self.trace_target.pack(side=tk.LEFT, padx=(0,10))
        NeonButton(frame, "Trace", self._run_trace).pack(side=tk.LEFT)
        self.trace_text = tk.Text(card.content, bg=COLORS['bg_mid'], fg='white', font=('Consolas', 9))
        self.trace_text.pack(fill=tk.BOTH, expand=True, pady=10)
        self.pages["trace"] = page
    
    def _build_scan(self):
        page = tk.Frame(self.content, bg=COLORS['card_glass'])
        card = GlassCard(page, "🐙 Network Scan")
        card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        frame = tk.Frame(card.content, bg=COLORS['card_glass'])
        frame.pack(fill=tk.X)
        self.cidr_entry = tk.Entry(frame, bg=COLORS['bg_mid'], fg='white', width=30)
        self.cidr_entry.insert(0, "192.168.1.0/24")
        self.cidr_entry.pack(side=tk.LEFT, padx=(0,10))
        NeonButton(frame, "Scan", self._run_scan, COLORS['neon_purple']).pack(side=tk.LEFT)
        self.scan_tree = ttk.Treeview(card.content, columns=('IP','Status','MAC'), height=15)
        self.scan_tree.heading('#0', text=''); self.scan_tree.heading('IP', text='IP'); self.scan_tree.heading('Status', text='Status'); self.scan_tree.heading('MAC', text='MAC')
        self.scan_tree.column('#0', width=0); self.scan_tree.column('IP', width=150); self.scan_tree.column('Status', width=100); self.scan_tree.column('MAC', width=180)
        self.scan_tree.pack(fill=tk.BOTH, expand=True, pady=10)
        self.pages["scan"] = page
    
    def _build_ports(self):
        page = tk.Frame(self.content, bg=COLORS['card_glass'])
        card = GlassCard(page, "🐙 Port Scanner")
        card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        frame = tk.Frame(card.content, bg=COLORS['card_glass'])
        frame.pack(fill=tk.X)
        self.port_target = tk.Entry(frame, bg=COLORS['bg_mid'], fg='white', width=15)
        self.port_target.insert(0, "127.0.0.1")
        self.port_target.pack(side=tk.LEFT, padx=(0,10))
        self.port_range = tk.Entry(frame, bg=COLORS['bg_mid'], fg='white', width=30)
        self.port_range.insert(0, "22,80,443,3306")
        self.port_range.pack(side=tk.LEFT, padx=(0,10))
        NeonButton(frame, "Scan", self._scan_ports, COLORS['neon_pink']).pack(side=tk.LEFT)
        self.port_tree = ttk.Treeview(card.content, columns=('Port','Status','Service'), height=15)
        self.port_tree.heading('#0', text=''); self.port_tree.heading('Port', text='Port'); self.port_tree.heading('Status', text='Status'); self.port_tree.heading('Service', text='Service')
        self.port_tree.column('#0', width=0); self.port_tree.column('Port', width=100); self.port_tree.column('Status', width=100); self.port_tree.column('Service', width=150)
        self.port_tree.pack(fill=tk.BOTH, expand=True, pady=10)
        self.pages["ports"] = page
    
    def _build_analysis(self):
        page = tk.Frame(self.content, bg=COLORS['card_glass'])
        card = GlassCard(page, "🐙 Analysis")
        card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        NeonButton(card.content, "Analyze", self._analyze, COLORS['neon_cyan']).pack(pady=10)
        self.analysis_text = tk.Text(card.content, bg=COLORS['bg_mid'], fg='white', font=('Consolas', 9), height=20)
        self.analysis_text.pack(fill=tk.BOTH, expand=True)
        self.pages["analysis"] = page
    
    def _build_groups(self):
        page = tk.Frame(self.content, bg=COLORS['card_glass'])
        card = GlassCard(page, "🐙 Groups")
        card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        top = tk.Frame(card.content, bg=COLORS['card_glass'])
        top.pack(fill=tk.X)
        self.new_group_name = tk.Entry(top, bg=COLORS['bg_mid'], fg='white', width=20)
        self.new_group_name.pack(side=tk.LEFT, padx=(0,10))
        NeonButton(top, "Create", self._create_group, COLORS['neon_green']).pack(side=tk.LEFT)
        mid = tk.Frame(card.content, bg=COLORS['card_glass'])
        mid.pack(fill=tk.BOTH, expand=True, pady=10)
        left = tk.Frame(mid, bg=COLORS['bg_mid'])
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        tk.Label(left, text="Groups", bg=COLORS['bg_mid'], fg='white').pack()
        self.groups_listbox = tk.Listbox(left, bg=COLORS['bg_deep'], fg='white')
        self.groups_listbox.pack(fill=tk.BOTH, expand=True)
        self.groups_listbox.bind('<<ListboxSelect>>', self._show_group_ips)
        right = tk.Frame(mid, bg=COLORS['bg_mid'])
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        tk.Label(right, text="IPs", bg=COLORS['bg_mid'], fg='white').pack()
        self.ips_listbox = tk.Listbox(right, bg=COLORS['bg_deep'], fg='white')
        self.ips_listbox.pack(fill=tk.BOTH, expand=True)
        btn_frame = tk.Frame(card.content, bg=COLORS['card_glass'])
        btn_frame.pack(fill=tk.X)
        NeonButton(btn_frame, "Add IP", self._add_ip_group, COLORS['neon_cyan']).pack(side=tk.LEFT, padx=5)
        NeonButton(btn_frame, "Remove IP", self._remove_ip_group, COLORS['error']).pack(side=tk.LEFT, padx=5)
        NeonButton(btn_frame, "Load to Ping", self._load_group_to_ping, COLORS['neon_green']).pack(side=tk.LEFT, padx=5)
        self.pages["groups"] = page
        self._refresh_groups()
    
    def _build_backup(self):
        page = tk.Frame(self.content, bg=COLORS['card_glass'])
        card = GlassCard(page, "🐙 Backup")
        card.pack(expand=True, padx=20, pady=20)
        NeonButton(card.content, "Export", self._export, COLORS['neon_cyan']).pack(pady=10)
        NeonButton(card.content, "Import", self._import, COLORS['neon_purple']).pack(pady=10)
        NeonButton(card.content, "Reset", self._reset_all, COLORS['error']).pack(pady=10)
        self.pages["backup"] = page
    
    def _build_info(self):
        page = tk.Frame(self.content, bg=COLORS['card_glass'])
        card = GlassCard(page, "🐙 Info")
        card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        txt = f"Host: {socket.gethostname()}\nIP: {self._get_local_ip()}\nOS: {platform.system()}\n\n✨ Features:\n- Ping Monitor\n- VNC/SSH/RDP\n- Groups\n- VLAN & Notes"
        tk.Label(card.content, text=txt, bg=COLORS['card_glass'], fg='white', justify=tk.LEFT, font=('Consolas', 10)).pack(pady=20)
        self.pages["info"] = page
    
    # ========== LOGIC ==========
    def _get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80)); ip = s.getsockname()[0]; s.close()
            return ip
        except: return "127.0.0.1"
    
    def _add_host(self):
        ip = self.search_ip.get().strip()
        if ip and ip not in self.hosts:
            HostCard(self.hosts_container, ip, ip, self._remove_host, None)
            self.hosts[ip] = True
            self._save_config()
    
    def _remove_host(self, ip):
        if ip in self.hosts: del self.hosts[ip]; self._save_config()
    
    def _stop_all(self):
        for w in self.hosts_container.winfo_children():
            if hasattr(w, 'stop'): w.stop(); w.destroy()
        self.hosts.clear()
    
    def _run_trace(self):
        host = self.trace_target.get()
        self.trace_text.delete(1.0, tk.END)
        self.trace_text.insert(1.0, "Tracing...\n")
        def do():
            try:
                cmd = ['tracert' if IS_WINDOWS else 'traceroute', host]
                out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, universal_newlines=True, timeout=30)
                self.trace_text.delete(1.0, tk.END); self.trace_text.insert(1.0, out)
            except Exception as e: self.trace_text.insert(1.0, f"Error: {e}")
        threading.Thread(target=do, daemon=True).start()
    
    def _run_scan(self):
        cidr = self.cidr_entry.get()
        self.scan_tree.delete(*self.scan_tree.get_children())
        def scan():
            try:
                net = ipaddress.ip_network(cidr)
                def ping(ip):
                    r = subprocess.run(['ping', '-n', '1', '-w', '500', str(ip)], capture_output=True) if IS_WINDOWS else subprocess.run(['ping', '-c', '1', '-W', '1', str(ip)], capture_output=True)
                    if r.returncode == 0:
                        mac = self._get_mac_from_arp(str(ip))
                        self.root.after(0, lambda i=str(ip), m=mac: self.scan_tree.insert('', tk.END, values=(i, "ONLINE", m)))
                with ThreadPoolExecutor(max_workers=30) as ex:
                    ex.map(ping, net.hosts())
            except Exception as e: messagebox.showerror("Error", str(e))
        threading.Thread(target=scan, daemon=True).start()
    
    def _get_mac_from_arp(self, ip):
        try:
            cmd = ['arp', '-a', ip] if IS_WINDOWS else ['arp', '-n', ip]
            out = subprocess.check_output(cmd, universal_newlines=True)
            mac = re.search(r'([0-9a-fA-F]{2}[:-]){5}([0-9a-fA-F]{2})', out)
            return mac.group(0) if mac else "Unknown"
        except: return "Unknown"
    
    def _scan_ports(self):
        target = self.port_target.get()
        ports = [int(p.strip()) for p in self.port_range.get().split(',') if p.strip().isdigit()]
        self.port_tree.delete(*self.port_tree.get_children())
        services = {22:'SSH',80:'HTTP',443:'HTTPS',3306:'MySQL'}
        def check(p):
            try:
                s = socket.socket(); s.settimeout(0.3)
                if s.connect_ex((target, p)) == 0:
                    self.root.after(0, lambda: self.port_tree.insert('', tk.END, values=(p, "OPEN", services.get(p, "Unknown"))))
                s.close()
            except: pass
        threading.Thread(target=lambda: [check(p) for p in ports], daemon=True).start()
    
    def _analyze(self):
        self.analysis_text.delete(1.0, tk.END)
        self.analysis_text.insert(1.0, f"Local IP: {self._get_local_ip()}\nActive Hosts: {len(self.hosts)}\n\n🐙 Jellyfish watching over your network...")
    
    def _refresh_groups(self):
        self.groups_listbox.delete(0, tk.END)
        for g in self.groups: self.groups_listbox.insert(tk.END, g)
    
    def _show_group_ips(self, e):
        sel = self.groups_listbox.curselection()
        if sel:
            name = self.groups_listbox.get(sel[0])
            self.ips_listbox.delete(0, tk.END)
            for ip in self.groups.get(name, []): self.ips_listbox.insert(tk.END, ip)
    
    def _create_group(self):
        name = self.new_group_name.get()
        if name and name not in self.groups:
            self.groups[name] = []; self._refresh_groups(); self._save_config()
    
    def _add_ip_group(self):
        sel = self.groups_listbox.curselection()
        if sel:
            name = self.groups_listbox.get(sel[0])
            ip = simpledialog.askstring("Add IP", "IP:")
            if ip: self.groups[name].append(ip); self._save_config(); self._show_group_ips(None)
    
    def _remove_ip_group(self):
        sel = self.groups_listbox.curselection(); isel = self.ips_listbox.curselection()
        if sel and isel:
            name = self.groups_listbox.get(sel[0]); ip = self.ips_listbox.get(isel[0])
            if ip in self.groups[name]: self.groups[name].remove(ip); self._save_config(); self._show_group_ips(None)
    
    def _load_group_to_ping(self):
        sel = self.groups_listbox.curselection()
        if sel:
            for ip in self.groups[self.groups_listbox.get(sel[0])]:
                if ip not in self.hosts:
                    HostCard(self.hosts_container, ip, ip, self._remove_host, None)
                    self.hosts[ip] = True
            self.show_ping()
    
    def _export(self):
        f = filedialog.asksaveasfilename(defaultextension=".json")
        if f:
            with open(f, 'w') as fp: json.dump({'hosts': list(self.hosts.keys()), 'groups': self.groups}, fp, indent=2)
            messagebox.showinfo("Done", "Exported")
    
    def _import(self):
        f = filedialog.askopenfilename()
        if f:
            with open(f) as fp: data = json.load(fp)
            for ip in data.get('hosts', []):
                if ip not in self.hosts:
                    HostCard(self.hosts_container, ip, ip, self._remove_host, None); self.hosts[ip] = True
            self.groups = data.get('groups', {"Default":[]}); self._refresh_groups(); self._save_config()
    
    def _reset_all(self):
        if messagebox.askyesno("Confirm", "Reset all?"):
            self._stop_all(); self.groups = {"Default": []}; self._refresh_groups(); self._save_config()
    
    def _save_config(self):
        with open(self.config_file, 'w') as f: json.dump({'hosts': list(self.hosts.keys()), 'groups': self.groups}, f)
    
    def _load_config(self):
        if self.config_file.exists():
            try:
                with open(self.config_file) as f: data = json.load(f)
                for ip in data.get('hosts', []):
                    HostCard(self.hosts_container, ip, ip, self._remove_host, None); self.hosts[ip] = True
                self.groups = data.get('groups', {"Default":[]}); self._refresh_groups()
            except: pass
    
    def show_ping(self): self._show_page("ping")
    def show_trace(self): self._show_page("trace")
    def show_scan(self): self._show_page("scan")
    def show_ports(self): self._show_page("ports")
    def show_analysis(self): self._show_page("analysis")
    def show_groups(self): self._show_page("groups")
    def show_backup(self): self._show_page("backup")
    def show_info(self): self._show_page("info")
    
    def _show_page(self, name):
        for p in self.pages.values(): p.pack_forget()
        self.pages[name].pack(fill=tk.BOTH, expand=True)
    
    def _on_close(self): self._stop_all(); self.root.destroy()
    
    def run(self): self.root.mainloop()


if __name__ == "__main__":
    app = NetToolApp()
    app.run()
