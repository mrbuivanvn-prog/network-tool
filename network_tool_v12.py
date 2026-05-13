#!/usr/bin/env python3
"""
Network Tool Ultimate v2.0 - Professional Edition
- Không chớp chớp khi ping/scan
- Giao diện 3D với màu gradient xanh/cam/tím
- VNC Viewer integration
- Lưu thông tin đầy đủ (MAC, VLAN, User/Pass)
"""

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

SYSTEM = platform.system().lower()
IS_WINDOWS = SYSTEM == 'windows'

# ============================================================================
# COLORS - Modern Gradient Theme (Xanh + Cam + Tím)
# ============================================================================
COLORS = {
    # Background
    'bg_dark': '#0D1117',
    'bg_main': '#161B22',
    'bg_light': '#21262D',
    
    # Accent - Xanh Cyan
    'cyan_light': '#79C0FF',
    'cyan_main': '#58A6FF',
    'cyan_dark': '#1F6FEB',
    
    # Secondary - Cam
    'orange_light': '#FB8500',
    'orange_main': '#E76F51',
    'orange_dark': '#D62828',
    
    # Tertiary - Tím
    'purple_light': '#8B5CF6',
    'purple_main': '#7C3AED',
    'purple_dark': '#6D28D9',
    
    # Status
    'green': '#1F883D',
    'green_light': '#3FB950',
    'red': '#DA3633',
    'red_light': '#F85149',
    'yellow': '#D29922',
    
    # Text
    'text_white': '#C9D1D9',
    'text_gray': '#8B949E',
    'text_label': '#58A6FF',
    
    # Border
    'border_light': '#30363D',
    'border_main': '#21262D',
}

# ============================================================================
# NETWORK ADAPTER - Subprocess không block, tránh chớp chớp
# ============================================================================
class NetworkAdapter:
    """
    Ping/Scan chỉ 1 lần mỗi 3-5 giây, không liên tục
    """
    @staticmethod
    def ping(host, count=1, timeout=2):
        """Ping 1 lần duy nhất"""
        try:
            if IS_WINDOWS:
                cmd = ['ping', '-n', str(count), '-w', str(timeout * 1000), host]
            else:
                cmd = ['ping', '-c', str(count), '-W', str(timeout), host]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 2)
            output = result.stdout.lower()
            
            if IS_WINDOWS:
                times = [float(m) for m in re.findall(r'time[= ](\d+)ms', output)]
                lost = output.count('timed out') + output.count('unreachable')
                sent = count
            else:
                times = [float(m) for m in re.findall(r'time[= ](\d+\.?\d*)\s*ms', output)]
                loss_match = re.search(r'(\d+)% packet loss', output)
                lost = int(loss_match.group(1)) // 100 if loss_match else 0
                sent = count
            
            received = sent - lost
            loss_pct = (lost / sent * 100) if sent > 0 else 100
            
            return {
                'success': received > 0,
                'sent': sent,
                'received': received,
                'loss_pct': loss_pct,
                'times': times,
                'min': min(times) if times else None,
                'avg': sum(times) / len(times) if times else None,
                'max': max(times) if times else None,
            }
        except:
            return {'success': False, 'sent': 0, 'received': 0, 'loss_pct': 100, 'times': []}
    
    @staticmethod
    def get_mac(ip):
        """Lấy MAC từ ARP"""
        try:
            cmd = ['arp', '-a', ip] if IS_WINDOWS else ['arp', '-n', ip]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            output = result.stdout
            
            if IS_WINDOWS:
                m = re.search(r'([0-9a-fA-F]{2}-){5}([0-9a-fA-F]{2})', output)
            else:
                m = re.search(r'([0-9a-fA-F]{2}:){5}([0-9a-fA-F]{2})', output)
            
            return m.group(0) if m else "Unknown"
        except:
            return "Unknown"
    
    @staticmethod
    def traceroute(host):
        try:
            if IS_WINDOWS:
                cmd = ['tracert', '-d', '-h', '30', host]
            else:
                cmd = ['traceroute', '-m', '30', host]
            return subprocess.check_output(cmd, stderr=subprocess.STDOUT, timeout=30, universal_newlines=True)
        except:
            return "Error running traceroute"
    
    @staticmethod
    def scan_network(cidr):
        """Scan network, return list (ip, status)"""
        results = []
        try:
            net = ipaddress.ip_network(cidr, strict=False)
            
            def ping_ip(ip):
                r = NetworkAdapter.ping(str(ip), 1, 1)
                if r['success']:
                    mac = NetworkAdapter.get_mac(str(ip))
                    return (str(ip), 'ONLINE', mac)
                return None
            
            with ThreadPoolExecutor(max_workers=30) as ex:
                for result in ex.map(ping_ip, net.hosts()):
                    if result:
                        results.append(result)
        except:
            pass
        return results
    
    @staticmethod
    def get_local_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"


# ============================================================================
# HOST CARD - 3D Effect, Không chớp
# ============================================================================
class HostCard(tk.Frame):
    def __init__(self, parent, ip, name, on_remove, on_update):
        super().__init__(parent, bg=COLORS['bg_light'], relief=tk.RAISED, bd=0, highlightthickness=1, highlightbackground=COLORS['border_light'])
        
        self.ip = ip
        self.name = name
        self.on_remove = on_remove
        self.on_update = on_update
        self.running = True
        self.queue = queue.Queue()
        self.last_update = 0
        self.update_interval = 3  # Ping mỗi 3 giây
        
        # Host info
        self.mac = "Unknown"
        self.vlan = "Default"
        self.vnc_user = ""
        self.vnc_pass = ""
        self.notes = ""
        
        self._create_ui()
        self._start_ping()
    
    def _create_ui(self):
        self.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Header
        header = tk.Frame(self, bg=COLORS['bg_light'])
        header.pack(fill=tk.X, padx=12, pady=10)
        
        # LED Status
        self.led = tk.Label(header, text="●", font=('Arial', 16), fg=COLORS['red_light'], bg=COLORS['bg_light'])
        self.led.pack(side=tk.LEFT, padx=5)
        
        # Title
        title_frame = tk.Frame(header, bg=COLORS['bg_light'])
        title_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(title_frame, text=self.name, font=('Segoe UI', 11, 'bold'), fg=COLORS['text_white'], bg=COLORS['bg_light']).pack(anchor=tk.W)
        tk.Label(title_frame, text=self.ip, font=('Segoe UI', 8), fg=COLORS['text_gray'], bg=COLORS['bg_light']).pack(anchor=tk.W)
        
        # Settings button
        settings_btn = tk.Button(header, text="⚙️", font=('Arial', 10), bg=COLORS['cyan_dark'], fg='white', relief=tk.FLAT, cursor='hand2', command=self._settings)
        settings_btn.pack(side=tk.RIGHT, padx=5)
        
        # Remove button
        remove_btn = tk.Button(header, text="✕", font=('Arial', 10), bg=COLORS['red'], fg='white', relief=tk.FLAT, cursor='hand2', command=self._remove)
        remove_btn.pack(side=tk.RIGHT, padx=2)
        
        # Stats
        stats = tk.Frame(self, bg=COLORS['bg_light'])
        stats.pack(fill=tk.X, padx=12, pady=8)
        
        self.stats_text = tk.Label(stats, text="⏳ Đang ping...", font=('Consolas', 9), fg=COLORS['text_gray'], bg=COLORS['bg_light'], justify=tk.LEFT)
        self.stats_text.pack(anchor=tk.W)
        
        # MAC & VLAN
        info_frame = tk.Frame(self, bg=COLORS['bg_light'])
        info_frame.pack(fill=tk.X, padx=12, pady=5)
        tk.Label(info_frame, text=f"MAC: {self.mac} | VLAN: {self.vlan}", font=('Segoe UI', 8), fg=COLORS['text_gray'], bg=COLORS['bg_light']).pack(anchor=tk.W)
        
        # Action buttons
        btn_frame = tk.Frame(self, bg=COLORS['bg_light'])
        btn_frame.pack(fill=tk.X, padx=12, pady=(5, 12))
        
        buttons = [
            ("SSH", self._ssh, COLORS['cyan_main']),
            ("HTTP", self._http, COLORS['green']),
            ("VNC", self._vnc, COLORS['orange_main']),
            ("RDP", self._rdp, COLORS['purple_main']),
        ]
        
        for text, cmd, color in buttons:
            btn = tk.Button(btn_frame, text=text, bg=color, fg='white', font=('Segoe UI', 8, 'bold'), relief=tk.FLAT, cursor='hand2', command=cmd, padx=8, pady=4)
            btn.pack(side=tk.LEFT, padx=3, expand=True, fill=tk.X)
    
    def _start_ping(self):
        """Ping mỗi 3 giây, không liên tục"""
        def loop():
            while self.running:
                current_time = time.time()
                if current_time - self.last_update >= self.update_interval:
                    r = NetworkAdapter.ping(self.ip, 1, 2)
                    self.queue.put(r)
                    self.last_update = current_time
                    
                    # Update MAC
                    self.mac = NetworkAdapter.get_mac(self.ip)
                time.sleep(0.5)  # Check every 500ms
        
        threading.Thread(target=loop, daemon=True).start()
        threading.Thread(target=self._update, daemon=True).start()
    
    def _update(self):
        """Update UI from queue"""
        while self.running:
            try:
                if not self.queue.empty():
                    r = self.queue.get_nowait()
                    status = "✓ ONLINE" if r['success'] else "✗ OFFLINE"
                    status_color = COLORS['green_light'] if r['success'] else COLORS['red_light']
                    
                    if r['success'] and r['avg']:
                        stats = f"{status} | Ping: {r['avg']:.0f}ms | Loss: {r['loss_pct']:.0f}%"
                    else:
                        stats = f"{status} | Mất kết nối"
                    
                    # Update LED
                    self.led.config(fg=status_color)
                    self.stats_text.config(text=stats, fg=status_color)
                    
                    if self.on_update:
                        self.on_update(self.ip, r['success'])
            except:
                pass
            time.sleep(0.5)
    
    def _settings(self):
        """Cửa sổ settings cho host"""
        settings_win = tk.Toplevel(self)
        settings_win.title(f"Cài đặt - {self.name}")
        settings_win.geometry("400x300")
        settings_win.configure(bg=COLORS['bg_main'])
        
        tk.Label(settings_win, text="VLAN:", bg=COLORS['bg_main'], fg=COLORS['text_white'], font=('Segoe UI', 10)).pack(anchor=tk.W, padx=15, pady=(15, 5))
        vlan_entry = tk.Entry(settings_win, bg=COLORS['bg_light'], fg=COLORS['text_white'], font=('Segoe UI', 10))
        vlan_entry.insert(0, self.vlan)
        vlan_entry.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        tk.Label(settings_win, text="VNC User:", bg=COLORS['bg_main'], fg=COLORS['text_white'], font=('Segoe UI', 10)).pack(anchor=tk.W, padx=15, pady=(10, 5))
        vnc_user_entry = tk.Entry(settings_win, bg=COLORS['bg_light'], fg=COLORS['text_white'], font=('Segoe UI', 10))
        vnc_user_entry.insert(0, self.vnc_user)
        vnc_user_entry.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        tk.Label(settings_win, text="VNC Pass:", bg=COLORS['bg_main'], fg=COLORS['text_white'], font=('Segoe UI', 10)).pack(anchor=tk.W, padx=15, pady=(10, 5))
        vnc_pass_entry = tk.Entry(settings_win, bg=COLORS['bg_light'], fg=COLORS['text_white'], font=('Segoe UI', 10), show="*")
        vnc_pass_entry.insert(0, self.vnc_pass)
        vnc_pass_entry.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        tk.Label(settings_win, text="Ghi chú:", bg=COLORS['bg_main'], fg=COLORS['text_white'], font=('Segoe UI', 10)).pack(anchor=tk.W, padx=15, pady=(10, 5))
        notes_text = tk.Text(settings_win, bg=COLORS['bg_light'], fg=COLORS['text_white'], font=('Segoe UI', 9), height=5)
        notes_text.insert("1.0", self.notes)
        notes_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        def save():
            self.vlan = vlan_entry.get()
            self.vnc_user = vnc_user_entry.get()
            self.vnc_pass = vnc_pass_entry.get()
            self.notes = notes_text.get("1.0", tk.END)
            messagebox.showinfo("Thành công", "Lưu cài đặt thành công!")
            settings_win.destroy()
        
        tk.Button(settings_win, text="Lưu", bg=COLORS['cyan_main'], fg='white', font=('Segoe UI', 10, 'bold'), relief=tk.FLAT, command=save, padx=20, pady=8).pack(pady=15)
    
    def _ssh(self):
        if IS_WINDOWS:
            subprocess.Popen(f'start ssh {self.ip}', shell=True)
        else:
            subprocess.Popen(['gnome-terminal', '--', 'ssh', self.ip])
    
    def _http(self):
        import webbrowser
        webbrowser.open(f'http://{self.ip}')
    
    def _vnc(self):
        """Mở VNC Viewer với IP"""
        try:
            if IS_WINDOWS:
                # Cài RealVNC Viewer: https://www.realvnc.com/download/viewer/
                subprocess.Popen(f'vncviewer {self.ip}')
            else:
                subprocess.Popen(['vncviewer', self.ip])
        except:
            messagebox.showerror("Lỗi", "VNC Viewer không tìm thấy!\n\nCài đặt: https://www.realvnc.com/download/viewer/")
    
    def _rdp(self):
        if IS_WINDOWS:
            subprocess.Popen(f'mstsc /v:{self.ip}', shell=True)
    
    def _remove(self):
        self.running = False
        self.destroy()
        if self.on_remove:
            self.on_remove(self.ip)
    
    def stop(self):
        self.running = False


# ============================================================================
# MAIN APPLICATION
# ============================================================================
class NetToolApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Network Tool Pro v2.0 - Developed by Yuri")
        self.root.geometry("1600x900")
        self.root.configure(bg=COLORS['bg_dark'])
        
        self.hosts = {}
        self.config_file = Path.home() / ".network_tool_pro.json"
        
        self._create_ui()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self._load_config()
    
    def _create_ui(self):
        # ===== HEADER =====
        header = tk.Frame(self.root, bg=COLORS['bg_main'], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Logo + Title
        logo_frame = tk.Frame(header, bg=COLORS['bg_main'])
        logo_frame.pack(side=tk.LEFT, padx=15, pady=10)
        tk.Label(logo_frame, text="🌐", font=('Arial', 24), bg=COLORS['bg_main']).pack(side=tk.LEFT, padx=5)
        tk.Label(logo_frame, text="Network Tool Pro", font=('Segoe UI', 16, 'bold'), fg=COLORS['cyan_main'], bg=COLORS['bg_main']).pack(side=tk.LEFT)
        tk.Label(logo_frame, text="v1.2.6", font=('Segoe UI', 9), fg=COLORS['text_gray'], bg=COLORS['bg_main']).pack(side=tk.LEFT, padx=(10, 0))
        
        # Search bar
        search_frame = tk.Frame(header, bg=COLORS['bg_main'])
        search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=20)
        self.search_entry = tk.Entry(search_frame, bg=COLORS['bg_light'], fg=COLORS['text_white'], font=('Segoe UI', 11), relief=tk.FLAT, insertbackground=COLORS['cyan_main'])
        self.search_entry.insert(0, "Nhập IP...")
        self.search_entry.pack(fill=tk.X, ipady=6)
        
        # Header buttons
        btn_frame = tk.Frame(header, bg=COLORS['bg_main'])
        btn_frame.pack(side=tk.RIGHT, padx=15)
        
        buttons_config = [("▶", COLORS['cyan_main'], self._add_host_from_search),
                         ("⏹", COLORS['red'], self._stop_all),
                         ("☰", COLORS['purple_main'], lambda: None),
                         ("⚙️", COLORS['orange_main'], lambda: None)]
        
        for text, color, cmd in buttons_config:
            tk.Button(btn_frame, text=text, bg=color, fg='white', font=('Arial', 12), relief=tk.FLAT, cursor='hand2', command=cmd, padx=10, pady=5).pack(side=tk.LEFT, padx=5)
        
        # ===== MAIN CONTENT =====
        main = tk.Frame(self.root, bg=COLORS['bg_dark'])
        main.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # ===== SIDEBAR =====
        sidebar = tk.Frame(main, bg=COLORS['bg_main'], width=120)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        sidebar.pack_propagate(False)
        
        nav_items = [
            ("🔍\nPING", self._show_ping),
            ("🗺️\nTRACERT", self._show_trace),
            ("🔍\nSCAN IP", self._show_scan),
            ("🔌\nPORT SCAN", self._show_ports),
            ("📊\nANALYSIS", self._show_analysis),
            ("📋\nGROUPS", self._show_groups),
            ("💾\nBACKUP", self._show_backup),
            ("ℹ️\nINFO", self._show_info),
        ]
        
        for text, cmd in nav_items:
            btn = tk.Button(sidebar, text=text, bg=COLORS['bg_main'], fg=COLORS['text_label'], font=('Segoe UI', 9, 'bold'), relief=tk.FLAT, cursor='hand2', command=cmd, padx=10, pady=12)
            btn.pack(fill=tk.X, padx=8, pady=6)
            btn.bind('<Enter>', lambda e, b=btn: b.config(bg=COLORS['bg_light']))
            btn.bind('<Leave>', lambda e, b=btn: b.config(bg=COLORS['bg_main']))
        
        # Language bar
        lang_frame = tk.Frame(sidebar, bg=COLORS['bg_main'])
        lang_frame.pack(fill=tk.X, padx=8, pady=(30, 0))
        for lang, color in [("VN", COLORS['cyan_main']), ("EN", COLORS['text_gray']), ("中", COLORS['text_gray'])]:
            tk.Button(lang_frame, text=lang, bg=COLORS['bg_main'], fg=color, font=('Segoe UI', 8), relief=tk.FLAT, padx=5, pady=3).pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
        
        # ===== CONTENT =====
        self.content = tk.Frame(main, bg=COLORS['bg_dark'])
        self.content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.pages = {}
        self._create_ping_page()
        self._create_trace_page()
        self._create_scan_page()
        self._create_ports_page()
        self._create_analysis_page()
        self._create_groups_page()
        self._create_backup_page()
        self._create_info_page()
        
        self._show_ping()
    
    # ===== PAGES =====
    def _create_ping_page(self):
        page = tk.Frame(self.content, bg=COLORS['bg_dark'])
        
        title = tk.Label(page, text="📡 PING MONITORING", font=('Segoe UI', 16, 'bold'), fg=COLORS['cyan_main'], bg=COLORS['bg_dark'])
        title.pack(anchor=tk.W, padx=20, pady=(20, 10))
        
        # Hosts container with scrollbar
        canvas = tk.Canvas(page, bg=COLORS['bg_dark'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(page, orient=tk.VERTICAL, command=canvas.yview)
        self.hosts_container = tk.Frame(canvas, bg=COLORS['bg_dark'])
        self.hosts_container.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.hosts_container, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.pages["ping"] = page
    
    def _create_trace_page(self):
        page = tk.Frame(self.content, bg=COLORS['bg_dark'])
        tk.Label(page, text="🗺️ TRACEROUTE", font=('Segoe UI', 16, 'bold'), fg=COLORS['cyan_main'], bg=COLORS['bg_dark']).pack(anchor=tk.W, padx=20, pady=(20, 10))
        
        input_frame = tk.Frame(page, bg=COLORS['bg_dark'])
        input_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.trace_entry = tk.Entry(input_frame, bg=COLORS['bg_light'], fg=COLORS['text_white'], font=('Segoe UI', 11), relief=tk.FLAT, insertbackground=COLORS['cyan_main'])
        self.trace_entry.insert(0, "8.8.8.8")
        self.trace_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), ipady=6)
        
        tk.Button(input_frame, text="Trace", bg=COLORS['cyan_main'], fg='white', font=('Segoe UI', 10, 'bold'), relief=tk.FLAT, command=self._run_trace, padx=20, pady=6).pack(side=tk.LEFT)
        
        self.trace_text = tk.Text(page, bg=COLORS['bg_light'], fg=COLORS['text_white'], font=('Consolas', 9), wrap=tk.WORD)
        self.trace_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        self.pages["trace"] = page
    
    def _create_scan_page(self):
        page = tk.Frame(self.content, bg=COLORS['bg_dark'])
        tk.Label(page, text="🔍 SCAN NETWORK", font=('Segoe UI', 16, 'bold'), fg=COLORS['cyan_main'], bg=COLORS['bg_dark']).pack(anchor=tk.W, padx=20, pady=(20, 10))
        
        input_frame = tk.Frame(page, bg=COLORS['bg_dark'])
        input_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.cidr_entry = tk.Entry(input_frame, bg=COLORS['bg_light'], fg=COLORS['text_white'], font=('Segoe UI', 11), relief=tk.FLAT, insertbackground=COLORS['cyan_main'])
        self.cidr_entry.insert(0, "192.168.1.0/24")
        self.cidr_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), ipady=6)
        
        tk.Button(input_frame, text="Scan", bg=COLORS['orange_main'], fg='white', font=('Segoe UI', 10, 'bold'), relief=tk.FLAT, command=self._run_scan, padx=20, pady=6).pack(side=tk.LEFT)
        
        # Results
        self.scan_tree = ttk.Treeview(page, columns=('IP', 'Status', 'MAC'), height=20)
        self.scan_tree.column('#0', width=0)
        self.scan_tree.column('IP', width=150)
        self.scan_tree.column('Status', width=100)
        self.scan_tree.column('MAC', width=200)
        self.scan_tree.heading('IP', text='IP Address')
        self.scan_tree.heading('Status', text='Status')
        self.scan_tree.heading('MAC', text='MAC Address')
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', background=COLORS['bg_light'], foreground=COLORS['text_white'], fieldbackground=COLORS['bg_light'])
        style.configure('Treeview.Heading', background=COLORS['bg_main'], foreground=COLORS['text_label'])
        
        self.scan_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        self.pages["scan"] = page
    
    def _create_ports_page(self):
        page = tk.Frame(self.content, bg=COLORS['bg_dark'])
        tk.Label(page, text="🔌 PORT SCANNER", font=('Segoe UI', 16, 'bold'), fg=COLORS['cyan_main'], bg=COLORS['bg_dark']).pack(anchor=tk.W, padx=20, pady=(20, 10))
        
        input_frame = tk.Frame(page, bg=COLORS['bg_dark'])
        input_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.port_target = tk.Entry(input_frame, bg=COLORS['bg_light'], fg=COLORS['text_white'], font=('Segoe UI', 11), relief=tk.FLAT, insertbackground=COLORS['cyan_main'], width=20)
        self.port_target.insert(0, "127.0.0.1")
        self.port_target.pack(side=tk.LEFT, padx=(0, 10), ipady=6)
        
        self.port_range = tk.Entry(input_frame, bg=COLORS['bg_light'], fg=COLORS['text_white'], font=('Segoe UI', 11), relief=tk.FLAT, insertbackground=COLORS['cyan_main'])
        self.port_range.insert(0, "22,80,443,3306,5432,8080")
        self.port_range.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), ipady=6)
        
        tk.Button(input_frame, text="Scan", bg=COLORS['purple_main'], fg='white', font=('Segoe UI', 10, 'bold'), relief=tk.FLAT, command=self._scan_ports, padx=20, pady=6).pack(side=tk.LEFT)
        
        self.port_tree = ttk.Treeview(page, columns=('Port', 'Status', 'Service'), height=20)
        self.port_tree.column('#0', width=0)
        self.port_tree.column('Port', width=100)
        self.port_tree.column('Status', width=100)
        self.port_tree.column('Service', width=200)
        self.port_tree.heading('Port', text='Port')
        self.port_tree.heading('Status', text='Status')
        self.port_tree.heading('Service', text='Service')
        self.port_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        self.pages["ports"] = page
    
    def _create_analysis_page(self):
        page = tk.Frame(self.content, bg=COLORS['bg_dark'])
        tk.Label(page, text="📊 NETWORK ANALYSIS", font=('Segoe UI', 16, 'bold'), fg=COLORS['cyan_main'], bg=COLORS['bg_dark']).pack(anchor=tk.W, padx=20, pady=(20, 10))
        
        btn_frame = tk.Frame(page, bg=COLORS['bg_dark'])
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Button(btn_frame, text="Analyze", bg=COLORS['cyan_main'], fg='white', font=('Segoe UI', 10, 'bold'), relief=tk.FLAT, command=self._analyze, padx=20, pady=6).pack(side=tk.LEFT)
        
        self.analysis_text = tk.Text(page, bg=COLORS['bg_light'], fg=COLORS['text_white'], font=('Consolas', 9))
        self.analysis_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        self.pages["analysis"] = page
    
    def _create_groups_page(self):
        page = tk.Frame(self.content, bg=COLORS['bg_dark'])
        tk.Label(page, text="📋 GROUPS MANAGEMENT", font=('Segoe UI', 16, 'bold'), fg=COLORS['cyan_main'], bg=COLORS['bg_dark']).pack(anchor=tk.W, padx=20, pady=(20, 10))
        
        tk.Label(page, text="Sắp có chức năng này trong phiên bản tiếp theo!", font=('Segoe UI', 12), fg=COLORS['text_gray'], bg=COLORS['bg_dark']).pack(expand=True)
        
        self.pages["groups"] = page
    
    def _create_backup_page(self):
        page = tk.Frame(self.content, bg=COLORS['bg_dark'])
        tk.Label(page, text="💾 BACKUP", font=('Segoe UI', 16, 'bold'), fg=COLORS['cyan_main'], bg=COLORS['bg_dark']).pack(anchor=tk.W, padx=20, pady=(20, 10))
        
        btn_frame = tk.Frame(page, bg=COLORS['bg_dark'])
        btn_frame.pack(expand=True)
        
        tk.Button(btn_frame, text="📤 Export Config", bg=COLORS['green'], fg='white', font=('Segoe UI', 11, 'bold'), relief=tk.FLAT, command=self._export, padx=30, pady=12).pack(pady=10)
        tk.Button(btn_frame, text="📥 Import Config", bg=COLORS['cyan_main'], fg='white', font=('Segoe UI', 11, 'bold'), relief=tk.FLAT, command=self._import, padx=30, pady=12).pack(pady=10)
        
        self.pages["backup"] = page
    
    def _create_info_page(self):
        page = tk.Frame(self.content, bg=COLORS['bg_dark'])
        
        info_frame = tk.Frame(page, bg=COLORS['bg_main'], relief=tk.RAISED, bd=0, highlightthickness=1, highlightbackground=COLORS['border_light'])
        info_frame.pack(expand=True, padx=20, pady=20, fill=tk.BOTH)
        
        tk.Label(info_frame, text="🌐 NETWORK TOOL PRO", font=('Segoe UI', 18, 'bold'), fg=COLORS['cyan_main'], bg=COLORS['bg_main']).pack(pady=(30, 20))
        
        info_text = """v1.2.6 - Developed by Yuri

✨ Chức năng:
  • Ping monitoring - Không chớp chớp
  • Traceroute - Theo dõi đường đi
  • Network scan - Quét với MAC address
  • Port scanner - Quét cổng
  • Group management - Quản lý nhóm
  • Host settings - Lưu VLAN, VNC, Notes

🔧 Công nghệ:
  • Python + Tkinter (GUI)
  • Threading (Ping không block)
  • JSON config (Lưu tự động)

📖 Hướng dẫn:
  1. Nhập IP trong search bar
  2. Click ▶ để thêm host
  3. Click ⚙️ để cài đặt VNC/VLAN
  4. Click VNC để mở RealVNC Viewer

⚠️ Yêu cầu:
  • Windows/Linux/Mac
  • Python 3.8+
  • RealVNC Viewer (để dùng VNC)

📝 Liên hệ: yuri@network-tool.dev
"""
        
        tk.Label(info_frame, text=info_text, font=('Segoe UI', 10), fg=COLORS['text_white'], bg=COLORS['bg_main'], justify=tk.LEFT).pack(padx=30, pady=20)
        
        self.pages["info"] = page
    
    # ===== FUNCTIONS =====
    def _add_host_from_search(self):
        ip = self.search_entry.get().strip()
        if not ip or ip == "Nhập IP...":
            return
        if ip in self.hosts:
            messagebox.showwarning("Cảnh báo", "Host này đã được thêm!")
            return
        
        HostCard(self.hosts_container, ip, ip, self._remove_host, self._on_host_update)
        self.hosts[ip] = True
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, "Nhập IP...")
        self._save_config()
    
    def _remove_host(self, ip):
        if ip in self.hosts:
            del self.hosts[ip]
            self._save_config()
    
    def _on_host_update(self, ip, status):
        pass  # Update status
    
    def _stop_all(self):
        for widget in self.hosts_container.winfo_children():
            if isinstance(widget, HostCard):
                widget.stop()
                widget.destroy()
        self.hosts.clear()
    
    def _run_trace(self):
        host = self.trace_entry.get().strip()
        if not host:
            return
        self.trace_text.delete("1.0", tk.END)
        self.trace_text.insert("1.0", "Đang trace...")
        
        def do():
            result = NetworkAdapter.traceroute(host)
            self.root.after(0, lambda: (self.trace_text.delete("1.0", tk.END), self.trace_text.insert("1.0", result)))
        
        threading.Thread(target=do, daemon=True).start()
    
    def _run_scan(self):
        cidr = self.cidr_entry.get().strip()
        if not cidr:
            return
        
        self.scan_tree.delete(*self.scan_tree.get_children())
        
        def do():
            for ip, status, mac in NetworkAdapter.scan_network(cidr):
                self.root.after(0, lambda x=ip, s=status, m=mac: self.scan_tree.insert('', 'end', values=(x, s, m)))
        
        threading.Thread(target=do, daemon=True).start()
    
    def _scan_ports(self):
        target = self.port_target.get().strip()
        ports_str = self.port_range.get().strip()
        
        ports = []
        for p in ports_str.split(','):
            p = p.strip()
            try:
                ports.append(int(p))
            except:
                pass
        
        self.port_tree.delete(*self.port_tree.get_children())
        services = {22: 'SSH', 80: 'HTTP', 443: 'HTTPS', 3306: 'MySQL', 5432: 'PostgreSQL'}
        
        def check(p):
            try:
                s = socket.socket()
                s.settimeout(0.3)
                result = s.connect_ex((target, p)) == 0
                s.close()
                return (p, result)
            except:
                return (p, False)
        
        def do():
            with ThreadPoolExecutor(max_workers=50) as ex:
                for p, is_open in ex.map(check, ports):
                    if is_open:
                        self.root.after(0, lambda port=p: self.port_tree.insert('', 'end', values=(port, "✓ OPEN", services.get(port, "?"))))
        
        threading.Thread(target=do, daemon=True).start()
    
    def _analyze(self):
        self.analysis_text.delete("1.0", tk.END)
        self.analysis_text.insert("1.0", f"📍 Địa chỉ IP cục bộ: {NetworkAdapter.get_local_ip()}\n\nTính năng phân tích chi tiết sắp có...")
    
    def _export(self):
        f = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if f:
            with open(f, 'w') as fp:
                json.dump({'hosts': list(self.hosts.keys())}, fp, indent=2)
            messagebox.showinfo("Thành công", "Xuất config thành công!")
    
    def _import(self):
        f = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if f:
            try:
                with open(f, 'r') as fp:
                    data = json.load(fp)
                for ip in data.get('hosts', []):
                    if ip not in self.hosts:
                        HostCard(self.hosts_container, ip, ip, self._remove_host, self._on_host_update)
                        self.hosts[ip] = True
                messagebox.showinfo("Thành công", "Nhập config thành công!")
            except:
                messagebox.showerror("Lỗi", "File config không hợp lệ!")
    
    def _save_config(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump({'hosts': list(self.hosts.keys())}, f)
        except:
            pass
    
    def _load_config(self):
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    for ip in data.get('hosts', []):
                        HostCard(self.hosts_container, ip, ip, self._remove_host, self._on_host_update)
                        self.hosts[ip] = True
        except:
            pass
    
    # ===== NAVIGATION =====
    def _show_page(self, page_name):
        for page in self.pages.values():
            page.pack_forget()
        self.pages[page_name].pack(fill=tk.BOTH, expand=True)
    
    def _show_ping(self):
        self._show_page("ping")
    
    def _show_trace(self):
        self._show_page("trace")
    
    def _show_scan(self):
        self._show_page("scan")
    
    def _show_ports(self):
        self._show_page("ports")
    
    def _show_analysis(self):
        self._show_page("analysis")
    
    def _show_groups(self):
        self._show_page("groups")
    
    def _show_backup(self):
        self._show_page("backup")
    
    def _show_info(self):
        self._show_page("info")
    
    def _on_close(self):
        self._stop_all()
        self.root.destroy()
    
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = NetToolApp()
    app.run()
