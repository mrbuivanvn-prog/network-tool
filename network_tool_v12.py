#!/usr/bin/env python3
"""
Network Tool Ultimate v13.5 - Professional Edition
✨ 8 Features | 3D UI | No Flickering | Full Vietnamese
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog, scrolledtext
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
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================
SYSTEM = platform.system().lower()
IS_WINDOWS = SYSTEM == 'windows'

# ============================================================================
# ADVANCED COLORS - Modern Professional 3D
# ============================================================================
COLORS = {
    'bg_main': '#0D1117',
    'bg_dark': '#010409',
    'sidebar': '#161B22',
    'card': '#1C2128',
    'card_light': '#262C36',
    'accent': '#58A6FF',
    'accent_dark': '#3B82F6',
    'accent_light': '#79C0FF',
    'success': '#3FB950',
    'warning': '#D29922',
    'danger': '#F85149',
    'text_primary': '#C9D1D9',
    'text_secondary': '#8B949E',
    'border': '#30363D',
    'shadow': '#0D1117',
}

# ============================================================================
# NETWORK ADAPTER - ADVANCED
# ============================================================================
class NetworkAdapter:
    @staticmethod
    def ping(host, count=4, timeout=2):
        """Ping với timeout"""
        try:
            if IS_WINDOWS:
                cmd = ['ping', '-n', str(count), '-w', str(timeout * 1000), host]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 2)
                output = result.stdout.lower()
                times = [float(m) for m in re.findall(r'time[= ](\d+)ms', output)]
                lost = output.count('timed out') + output.count('unreachable')
                sent = count
                received = sent - lost
                loss_pct = (lost / sent * 100) if sent > 0 else 100
            else:
                cmd = ['ping', '-c', str(count), '-W', str(timeout), host]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 2)
                output = result.stdout.lower()
                times = [float(m) for m in re.findall(r'time[= ](\d+\.?\d*)\s*ms', output)]
                loss_match = re.search(r'(\d+)% packet loss', output)
                loss_pct = int(loss_match.group(1)) if loss_match else 0
                sent_match = re.search(r'(\d+) packets transmitted', output)
                sent = int(sent_match.group(1)) if sent_match else count
                received = sent - int(sent * loss_pct / 100)
            
            return {
                'success': received > 0,
                'sent': sent,
                'received': received,
                'loss_pct': loss_pct,
                'times': times,
                'min': min(times) if times else 0,
                'avg': sum(times) / len(times) if times else 0,
                'max': max(times) if times else 0,
            }
        except Exception as e:
            return {'success': False, 'sent': 0, 'received': 0, 'loss_pct': 100, 'times': [], 'error': str(e)}
    
    @staticmethod
    def traceroute(host):
        """Traceroute"""
        try:
            if IS_WINDOWS:
                cmd = ['tracert', '-d', '-h', '30', host]
            else:
                try:
                    cmd = ['traceroute', '-n', '-m', '30', host]
                    return subprocess.check_output(cmd, stderr=subprocess.STDOUT, timeout=60, universal_newlines=True)
                except FileNotFoundError:
                    cmd = ['tracepath', '-n', host]
                    return subprocess.check_output(cmd, stderr=subprocess.STDOUT, timeout=60, universal_newlines=True)
            return subprocess.check_output(cmd, stderr=subprocess.STDOUT, timeout=60, universal_newlines=True)
        except Exception as e:
            return f"❌ Lỗi: {str(e)}"
    
    @staticmethod
    def get_arp_table():
        """ARP table với MAC"""
        try:
            cmd = ['arp', '-a'] if IS_WINDOWS else ['arp', '-n']
            result = subprocess.check_output(cmd, universal_newlines=True, timeout=10)
            arp = {}
            for line in result.split('\n'):
                if IS_WINDOWS:
                    m = re.search(r'(\d+\.\d+\.\d+\.\d+)\s+([0-9a-fA-F-]{17})', line)
                else:
                    m = re.search(r'(\d+\.\d+\.\d+\.\d+).*?([0-9a-fA-F:]{17})', line)
                if m:
                    ip = m.group(1)
                    mac = m.group(2).upper()
                    arp[ip] = mac
            return arp
        except:
            return {}
    
    @staticmethod
    def get_local_ip():
        """Local IP"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    @staticmethod
    def scan_ports(host, ports):
        """Quét cổng"""
        results = {}
        def check(p):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.5)
                ok = s.connect_ex((host, p)) == 0
                s.close()
                return (p, ok)
            except:
                return (p, False)
        
        with ThreadPoolExecutor(max_workers=50) as ex:
            for p, ok in ex.map(check, ports):
                results[p] = ok
        return results


# ============================================================================
# CARD 3D STYLE
# ============================================================================
class Card3D(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.config(bg=COLORS['card'], relief=tk.RAISED, bd=1, highlightthickness=2, 
                   highlightbackground=COLORS['border'], highlightcolor=COLORS['accent'])


# ============================================================================
# HOST CARD ADVANCED
# ============================================================================
class HostCardAdvanced(tk.Frame):
    def __init__(self, parent, ip, name="", on_remove=None):
        super().__init__(parent, bg=COLORS['card'], relief=tk.RAISED, bd=2, 
                        highlightthickness=1, highlightbackground=COLORS['border'])
        self.ip = ip
        self.name = name or ip
        self.on_remove = on_remove
        self.running = True
        self.queue = queue.Queue()
        
        # Host data
        self.mac = "N/A"
        self.vlan = "0"
        self.vnc_user = ""
        self.vnc_pass = ""
        self.notes = ""
        
        self.update_pending = False
        self._create_ui()
        self._start_ping()
    
    def _create_ui(self):
        self.pack(fill=tk.BOTH, padx=6, pady=6)
        
        # Top bar
        top = tk.Frame(self, bg=COLORS['card'])
        top.pack(fill=tk.X, padx=8, pady=8)
        
        # LED
        self.led = tk.Label(top, text="●", bg=COLORS['card'], fg=COLORS['danger'], 
                           font=('Arial', 16))
        self.led.pack(side=tk.LEFT)
        
        # Name & IP
        info = tk.Frame(top, bg=COLORS['card'])
        info.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))
        tk.Label(info, text=self.name, bg=COLORS['card'], fg=COLORS['text_primary'],
                font=('Segoe UI', 11, 'bold')).pack(anchor=tk.W)
        tk.Label(info, text=self.ip, bg=COLORS['card'], fg=COLORS['text_secondary'],
                font=('Segoe UI', 8)).pack(anchor=tk.W)
        
        # Buttons
        btn_frame = tk.Frame(top, bg=COLORS['card'])
        btn_frame.pack(side=tk.RIGHT)
        
        tk.Button(btn_frame, text="⚙️", bg=COLORS['card_light'], fg=COLORS['text_primary'],
                 font=('Arial', 10), relief=tk.FLAT, command=self._settings,
                 width=3, padx=2).pack(side=tk.LEFT, padx=2)
        
        tk.Button(btn_frame, text="✕", bg=COLORS['danger'], fg='white',
                 font=('Arial', 10, 'bold'), relief=tk.FLAT, command=self._remove,
                 width=3, padx=2).pack(side=tk.LEFT, padx=2)
        
        # Divider
        tk.Frame(self, bg=COLORS['border'], height=1).pack(fill=tk.X, padx=8, pady=4)
        
        # Stats
        stats = tk.Frame(self, bg=COLORS['card'])
        stats.pack(fill=tk.X, padx=8, pady=4)
        
        self.time_lbl = tk.Label(stats, text="⏱️ ---ms", bg=COLORS['card'], 
                               fg=COLORS['text_secondary'], font=('Segoe UI', 9))
        self.time_lbl.pack(anchor=tk.W)
        
        self.loss_lbl = tk.Label(stats, text="📉 Loss: --%", bg=COLORS['card'], 
                               fg=COLORS['text_secondary'], font=('Segoe UI', 9))
        self.loss_lbl.pack(anchor=tk.W)
        
        self.mac_lbl = tk.Label(stats, text="🔗 MAC: N/A", bg=COLORS['card'], 
                              fg=COLORS['text_secondary'], font=('Segoe UI', 8))
        self.mac_lbl.pack(anchor=tk.W)
        
        self.vlan_lbl = tk.Label(stats, text="🏷️ VLAN: 0", bg=COLORS['card'], 
                               fg=COLORS['text_secondary'], font=('Segoe UI', 8))
        self.vlan_lbl.pack(anchor=tk.W)
        
        # Divider
        tk.Frame(self, bg=COLORS['border'], height=1).pack(fill=tk.X, padx=8, pady=4)
        
        # Remote tools
        tools = tk.Frame(self, bg=COLORS['card'])
        tools.pack(fill=tk.X, padx=8, pady=(4, 8))
        
        btns = [("SSH", self._ssh, COLORS['accent']), 
                ("HTTP", self._http, COLORS['success']),
                ("RDP", self._rdp, COLORS['warning']),
                ("VNC", self._vnc, COLORS['danger'])]
        
        for text, cmd, color in btns:
            btn = tk.Button(tools, text=text, bg=COLORS['card_light'], fg=color,
                          font=('Segoe UI', 8, 'bold'), relief=tk.FLAT, command=cmd)
            btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
            btn.bind('<Enter>', lambda e, b=btn: b.config(bg=color, fg='white'))
            btn.bind('<Leave>', lambda e, b=btn: b.config(bg=COLORS['card_light'], fg=e.widget.cget('fg')))
    
    def _start_ping(self):
        def ping_loop():
            while self.running:
                r = NetworkAdapter.ping(self.ip, 1, 2)
                self.queue.put(r)
                time.sleep(3)  # 3 giây 1 lần - không chớp
        
        def update_loop():
            while self.running:
                try:
                    while not self.queue.empty():
                        r = self.queue.get_nowait()
                        if r['success']:
                            self.led.config(fg=COLORS['success'])
                            avg = r['avg']
                            self.time_lbl.config(text=f"⏱️ {avg:.0f}ms", fg=COLORS['success'])
                        else:
                            self.led.config(fg=COLORS['danger'])
                            self.time_lbl.config(text="⏱️ Offline", fg=COLORS['danger'])
                        
                        loss = r['loss_pct']
                        loss_color = COLORS['danger'] if loss > 0 else COLORS['success']
                        self.loss_lbl.config(text=f"📉 Loss: {loss:.0f}%", fg=loss_color)
                        
                        # Get MAC
                        arp = NetworkAdapter.get_arp_table()
                        if self.ip in arp:
                            self.mac = arp[self.ip]
                            self.mac_lbl.config(text=f"🔗 MAC: {self.mac}")
                except:
                    pass
                time.sleep(0.1)
        
        threading.Thread(target=ping_loop, daemon=True).start()
        threading.Thread(target=update_loop, daemon=True).start()
    
    def _settings(self):
        """Cửa sổ cài đặt"""
        win = tk.Toplevel(self)
        win.title(f"⚙️ Cài đặt - {self.name}")
        win.geometry("400x350")
        win.config(bg=COLORS['bg_main'])
        
        tk.Label(win, text="MAC Address", bg=COLORS['bg_main'], fg=COLORS['text_primary'],
                font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W, padx=10, pady=(10, 2))
        mac_entry = tk.Entry(win, bg=COLORS['card'], fg=COLORS['text_primary'], font=('Courier', 9))
        mac_entry.pack(fill=tk.X, padx=10, pady=(0, 10))
        mac_entry.insert(0, self.mac)
        
        tk.Label(win, text="VLAN ID", bg=COLORS['bg_main'], fg=COLORS['text_primary'],
                font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W, padx=10, pady=(0, 2))
        vlan_entry = tk.Entry(win, bg=COLORS['card'], fg=COLORS['text_primary'])
        vlan_entry.pack(fill=tk.X, padx=10, pady=(0, 10))
        vlan_entry.insert(0, self.vlan)
        
        tk.Label(win, text="VNC User", bg=COLORS['bg_main'], fg=COLORS['text_primary'],
                font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W, padx=10, pady=(0, 2))
        vnc_user_entry = tk.Entry(win, bg=COLORS['card'], fg=COLORS['text_primary'])
        vnc_user_entry.pack(fill=tk.X, padx=10, pady=(0, 10))
        vnc_user_entry.insert(0, self.vnc_user)
        
        tk.Label(win, text="VNC Password", bg=COLORS['bg_main'], fg=COLORS['text_primary'],
                font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W, padx=10, pady=(0, 2))
        vnc_pass_entry = tk.Entry(win, bg=COLORS['card'], fg=COLORS['text_primary'], show="*")
        vnc_pass_entry.pack(fill=tk.X, padx=10, pady=(0, 10))
        vnc_pass_entry.insert(0, self.vnc_pass)
        
        tk.Label(win, text="Ghi chú", bg=COLORS['bg_main'], fg=COLORS['text_primary'],
                font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W, padx=10, pady=(0, 2))
        notes_text = tk.Text(win, bg=COLORS['card'], fg=COLORS['text_primary'], height=4, font=('Segoe UI', 9))
        notes_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        notes_text.insert('1.0', self.notes)
        
        def save():
            self.mac = mac_entry.get()
            self.vlan = vlan_entry.get()
            self.vnc_user = vnc_user_entry.get()
            self.vnc_pass = vnc_pass_entry.get()
            self.notes = notes_text.get('1.0', tk.END)
            self.mac_lbl.config(text=f"🔗 MAC: {self.mac}")
            self.vlan_lbl.config(text=f"🏷️ VLAN: {self.vlan}")
            messagebox.showinfo("✅", "Đã lưu!")
            win.destroy()
        
        tk.Button(win, text="💾 Lưu", bg=COLORS['accent'], fg='white', command=save,
                 font=('Segoe UI', 10, 'bold'), relief=tk.FLAT).pack(fill=tk.X, padx=10, pady=10)
    
    def _ssh(self):
        if IS_WINDOWS:
            subprocess.Popen(f'start cmd /k ssh {self.ip}', shell=True)
        else:
            subprocess.Popen(['gnome-terminal', '--', 'ssh', self.ip])
    
    def _http(self):
        import webbrowser
        webbrowser.open(f'http://{self.ip}')
    
    def _rdp(self):
        if IS_WINDOWS:
            subprocess.Popen(f'mstsc /v:{self.ip}', shell=True)
    
    def _vnc(self):
        if IS_WINDOWS:
            cmd = f'vncviewer {self.ip}'
            if self.vnc_user and self.vnc_pass:
                cmd += f' -user {self.vnc_user} -passwd {self.vnc_pass}'
            subprocess.Popen(cmd, shell=True)
    
    def _remove(self):
        self.running = False
        self.destroy()
        if self.on_remove:
            self.on_remove(self.ip)
    
    def stop(self):
        self.running = False


# ============================================================================
# MAIN APP - 8 FEATURES
# ============================================================================
class NetworkToolPro:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Network Tool Pro v1.2.6 - Developed by Yuri")
        self.root.geometry("1600x900")
        self.root.config(bg=COLORS['bg_main'])
        
        self.hosts = {}
        self.config_file = Path.home() / ".network_tool_pro.json"
        self._load_config()
        
        self._create_ui()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _create_ui(self):
        # ============ HEADER ============
        header = tk.Frame(self.root, bg=COLORS['bg_dark'], height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Logo area
        logo_frame = tk.Frame(header, bg=COLORS['accent'], width=80, height=70)
        logo_frame.pack(side=tk.LEFT)
        logo_frame.pack_propagate(False)
        tk.Label(logo_frame, text="🌐", bg=COLORS['accent'], fg='white',
                font=('Arial', 28)).pack(expand=True)
        
        # Title
        tk.Label(header, text="Network Tool", bg=COLORS['bg_dark'], fg=COLORS['accent'],
                font=('Segoe UI', 18, 'bold')).pack(side=tk.LEFT, padx=20, pady=15)
        
        tk.Label(header, text="v1.2.6 Developed by Yuri", bg=COLORS['bg_dark'], 
                fg=COLORS['text_secondary'], font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=(0, 20))
        
        # Search bar
        search_frame = tk.Frame(header, bg=COLORS['bg_dark'])
        search_frame.pack(side=tk.RIGHT, padx=20, pady=15)
        
        tk.Label(search_frame, text="🔍", bg=COLORS['bg_dark'], fg=COLORS['accent']).pack(side=tk.LEFT, padx=(0, 8))
        self.search_entry = tk.Entry(search_frame, bg=COLORS['card'], fg=COLORS['text_primary'],
                                    font=('Segoe UI', 10), width=30, relief=tk.FLAT,
                                    insertbackground=COLORS['accent'], insertwidth=2)
        self.search_entry.pack(side=tk.LEFT, ipady=8, ipadx=8)
        self.search_entry.insert(0, "Nhập IP...")
        
        # Action buttons
        btn_frame = tk.Frame(header, bg=COLORS['bg_dark'])
        btn_frame.pack(side=tk.RIGHT, padx=10, pady=15)
        
        tk.Button(btn_frame, text="▶️", bg=COLORS['accent'], fg='white', font=('Arial', 12),
                 relief=tk.FLAT, width=3, command=self._quick_add).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="⏹️", bg=COLORS['danger'], fg='white', font=('Arial', 12),
                 relief=tk.FLAT, width=3, command=self._stop_all).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="≡", bg=COLORS['card_light'], fg=COLORS['text_primary'],
                 font=('Arial', 12), relief=tk.FLAT, width=3).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="⚙️", bg=COLORS['card_light'], fg=COLORS['text_primary'],
                 font=('Arial', 12), relief=tk.FLAT, width=3).pack(side=tk.LEFT, padx=2)
        
        # ============ SIDEBAR ============
        sidebar = tk.Frame(self.root, bg=COLORS['sidebar'], width=120)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        nav_items = [
            ("🔍 PING", self._show_ping),
            ("🗺️ TRACERT", self._show_tracert),
            ("🔍 SCAN IP", self._show_scan),
            ("🔌 PORT SCAN", self._show_ports),
            ("📊 ANALYSIS", self._show_analysis),
            ("📋 GROUPS", self._show_groups),
            ("💾 BACKUP", self._show_backup),
            ("ℹ️ INFO", self._show_info),
        ]
        
        self.nav_btns = {}
        for text, cmd in nav_items:
            btn = tk.Button(sidebar, text=text, bg=COLORS['sidebar'], fg=COLORS['text_secondary'],
                          font=('Segoe UI', 9), relief=tk.FLAT, command=cmd, width=14,
                          wraplength=100, padx=5, pady=10)
            btn.pack(fill=tk.X, padx=5, pady=3)
            btn.bind('<Enter>', lambda e, b=btn: b.config(bg=COLORS['card_light'], fg=COLORS['accent']))
            btn.bind('<Leave>', lambda e, b=btn: b.config(bg=COLORS['sidebar'], fg=COLORS['text_secondary']))
            self.nav_btns[text] = btn
        
        # Language buttons
        tk.Frame(sidebar, bg=COLORS['sidebar'], height=1).pack(fill=tk.X, pady=10)
        lang_frame = tk.Frame(sidebar, bg=COLORS['sidebar'])
        lang_frame.pack(fill=tk.X, padx=5)
        tk.Button(lang_frame, text="VN", bg=COLORS['accent'], fg='white', font=('Segoe UI', 8, 'bold'),
                 relief=tk.FLAT, width=3).pack(side=tk.LEFT, padx=2)
        tk.Button(lang_frame, text="EN", bg=COLORS['card_light'], fg=COLORS['text_secondary'],
                 font=('Segoe UI', 8), relief=tk.FLAT, width=3).pack(side=tk.LEFT, padx=2)
        tk.Button(lang_frame, text="CH", bg=COLORS['card_light'], fg=COLORS['text_secondary'],
                 font=('Segoe UI', 8), relief=tk.FLAT, width=3).pack(side=tk.LEFT, padx=2)
        
        # ============ CONTENT ============
        self.content = tk.Frame(self.root, bg=COLORS['bg_main'])
        self.content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Pages
        self.pages = {}
        self._create_ping_page()
        self._create_tracert_page()
        self._create_scan_page()
        self._create_ports_page()
        self._create_analysis_page()
        self._create_groups_page()
        self._create_backup_page()
        self._create_info_page()
        
        self._show_ping()
    
    # ========== PAGE: PING ==========
    def _create_ping_page(self):
        page = tk.Frame(self.content, bg=COLORS['bg_main'])
        
        # Title
        tk.Label(page, text="🔍 PING MONITORING", bg=COLORS['bg_main'], fg=COLORS['accent'],
                font=('Segoe UI', 14, 'bold')).pack(anchor=tk.W, padx=20, pady=15)
        
        # Hosts container with scrollbar
        canvas = tk.Canvas(page, bg=COLORS['bg_main'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(page, orient=tk.VERTICAL, command=canvas.yview)
        
        self.hosts_frame = tk.Frame(canvas, bg=COLORS['bg_main'])
        self.hosts_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=self.hosts_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=15)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 15))
        
        # Empty state
        self.empty_label = tk.Label(self.hosts_frame, text="Chưa thêm host nào", 
                                   bg=COLORS['bg_main'], fg=COLORS['text_secondary'],
                                   font=('Segoe UI', 14))
        self.empty_label.pack(expand=True, pady=100)
        
        self.pages["ping"] = page
    
    def _quick_add(self):
        ip = self.search_entry.get().strip()
        if not ip or ip == "Nhập IP...":
            messagebox.showwarning("⚠️", "Nhập IP!")
            return
        if ip in self.hosts:
            messagebox.showwarning("⚠️", "IP đã tồn tại!")
            return
        
        self._add_host(ip)
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, "Nhập IP...")
    
    def _add_host(self, ip, name=""):
        if not name:
            name = ip
        if ip in self.hosts:
            return
        
        # Remove empty label
        if self.empty_label.winfo_exists():
            self.empty_label.pack_forget()
        
        card = HostCardAdvanced(self.hosts_frame, ip, name, self._remove_host)
        self.hosts[ip] = card
        self._save_config()
    
    def _remove_host(self, ip):
        if ip in self.hosts:
            del self.hosts[ip]
            if not self.hosts:
                self.empty_label.pack(expand=True, pady=100)
            self._save_config()
    
    def _stop_all(self):
        for card in self.hosts.values():
            card.stop()
            card.destroy()
        self.hosts.clear()
        self.empty_label.pack(expand=True, pady=100)
    
    # ========== PAGE: TRACERT ==========
    def _create_tracert_page(self):
        page = tk.Frame(self.content, bg=COLORS['bg_main'])
        
        tk.Label(page, text="🗺️ TRACEROUTE", bg=COLORS['bg_main'], fg=COLORS['accent'],
                font=('Segoe UI', 14, 'bold')).pack(anchor=tk.W, padx=20, pady=15)
        
        frame = Card3D(page, bg=COLORS['card'])
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Input
        input_frame = tk.Frame(frame, bg=COLORS['card'])
        input_frame.pack(fill=tk.X, padx=15, pady=15)
        
        self.tracert_entry = tk.Entry(input_frame, bg=COLORS['bg_dark'], fg=COLORS['text_primary'],
                                     font=('Segoe UI', 10), relief=tk.FLAT, insertbackground=COLORS['accent'])
        self.tracert_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, ipadx=10)
        self.tracert_entry.insert(0, "8.8.8.8")
        
        tk.Button(input_frame, text="▶️ Trace", bg=COLORS['accent'], fg='white',
                 font=('Segoe UI', 10, 'bold'), relief=tk.FLAT, command=self._run_tracert,
                 padx=20).pack(side=tk.LEFT, padx=(10, 0), ipady=6)
        
        # Output
        self.tracert_text = scrolledtext.ScrolledText(frame, bg=COLORS['bg_dark'], 
                                                     fg=COLORS['text_primary'],
                                                     font=('Courier', 9), relief=tk.FLAT)
        self.tracert_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        self.pages["tracert"] = page
    
    def _run_tracert(self):
        host = self.tracert_entry.get().strip()
        if not host:
            return
        
        self.tracert_text.delete('1.0', tk.END)
        self.tracert_text.insert('1.0', f"⏳ Tracing {host}...\n")
        
        def do():
            result = NetworkAdapter.traceroute(host)
            self.root.after(0, lambda: self.tracert_text.delete('1.0', tk.END))
            self.root.after(0, lambda: self.tracert_text.insert('1.0', result))
        
        threading.Thread(target=do, daemon=True).start()
    
    # ========== PAGE: SCAN IP ==========
    def _create_scan_page(self):
        page = tk.Frame(self.content, bg=COLORS['bg_main'])
        
        tk.Label(page, text="🔍 SCAN IP NETWORK", bg=COLORS['bg_main'], fg=COLORS['accent'],
                font=('Segoe UI', 14, 'bold')).pack(anchor=tk.W, padx=20, pady=15)
        
        frame = Card3D(page, bg=COLORS['card'])
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Input
        input_frame = tk.Frame(frame, bg=COLORS['card'])
        input_frame.pack(fill=tk.X, padx=15, pady=15)
        
        self.scan_entry = tk.Entry(input_frame, bg=COLORS['bg_dark'], fg=COLORS['text_primary'],
                                  font=('Segoe UI', 10), relief=tk.FLAT, insertbackground=COLORS['accent'])
        self.scan_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, ipadx=10)
        self.scan_entry.insert(0, "192.168.1.0/24")
        
        tk.Button(input_frame, text="▶️ Scan", bg=COLORS['accent'], fg='white',
                 font=('Segoe UI', 10, 'bold'), relief=tk.FLAT, command=self._run_scan,
                 padx=20).pack(side=tk.LEFT, padx=(10, 0), ipady=6)
        
        # Tree
        tree_frame = tk.Frame(frame, bg=COLORS['card'])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        self.scan_tree = ttk.Treeview(tree_frame, columns=('IP', 'MAC', 'Status'), height=20)
        self.scan_tree.column('#0', width=0)
        self.scan_tree.column('IP', width=150)
        self.scan_tree.column('MAC', width=150)
        self.scan_tree.column('Status', width=100)
        self.scan_tree.heading('IP', text='IP Address')
        self.scan_tree.heading('MAC', text='MAC Address')
        self.scan_tree.heading('Status', text='Status')
        
        style = ttk.Style()
        style.configure('Treeview', background=COLORS['bg_dark'], foreground=COLORS['text_primary'])
        style.configure('Treeview.Heading', background=COLORS['card_light'], foreground=COLORS['accent'])
        
        self.scan_tree.pack(fill=tk.BOTH, expand=True)
        
        self.pages["scan"] = page
    
    def _run_scan(self):
        cidr = self.scan_entry.get().strip()
        if not cidr:
            return
        
        self.scan_tree.delete(*self.scan_tree.get_children())
        
        def do():
            try:
                net = ipaddress.ip_network(cidr, strict=False)
                arp = NetworkAdapter.get_arp_table()
                
                def ping_ip(ip):
                    r = NetworkAdapter.ping(str(ip), 1, 1)
                    return (str(ip), r['success'])
                
                with ThreadPoolExecutor(max_workers=50) as ex:
                    for ip, ok in ex.map(ping_ip, net.hosts()):
                        if ok:
                            mac = arp.get(ip, "N/A")
                            self.root.after(0, lambda x=ip, m=mac: self.scan_tree.insert('', 'end', 
                                                                                         values=(x, m, "✓ ONLINE")))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("❌", str(e)))
        
        threading.Thread(target=do, daemon=True).start()
    
    # ========== PAGE: PORT SCAN ==========
    def _create_ports_page(self):
        page = tk.Frame(self.content, bg=COLORS['bg_main'])
        
        tk.Label(page, text="🔌 PORT SCANNER", bg=COLORS['bg_main'], fg=COLORS['accent'],
                font=('Segoe UI', 14, 'bold')).pack(anchor=tk.W, padx=20, pady=15)
        
        frame = Card3D(page, bg=COLORS['card'])
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Input
        input_frame = tk.Frame(frame, bg=COLORS['card'])
        input_frame.pack(fill=tk.X, padx=15, pady=15)
        
        tk.Label(input_frame, text="Host:", bg=COLORS['card'], fg=COLORS['text_primary'],
                font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=(0, 10))
        
        self.port_host = tk.Entry(input_frame, bg=COLORS['bg_dark'], fg=COLORS['text_primary'],
                                 font=('Segoe UI', 10), relief=tk.FLAT, insertbackground=COLORS['accent'],
                                 width=20)
        self.port_host.pack(side=tk.LEFT, ipady=6, ipadx=10, padx=(0, 20))
        self.port_host.insert(0, "127.0.0.1")
        
        tk.Label(input_frame, text="Ports:", bg=COLORS['card'], fg=COLORS['text_primary'],
                font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=(0, 10))
        
        self.port_list = tk.Entry(input_frame, bg=COLORS['bg_dark'], fg=COLORS['text_primary'],
                                 font=('Segoe UI', 10), relief=tk.FLAT, insertbackground=COLORS['accent'])
        self.port_list.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, ipadx=10, padx=(0, 10))
        self.port_list.insert(0, "22,80,443,3306,5432,8080,9000")
        
        tk.Button(input_frame, text="▶️ Scan", bg=COLORS['accent'], fg='white',
                 font=('Segoe UI', 10, 'bold'), relief=tk.FLAT, command=self._run_ports,
                 padx=20).pack(side=tk.LEFT, ipady=6)
        
        # Tree
        tree_frame = tk.Frame(frame, bg=COLORS['card'])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        self.port_tree = ttk.Treeview(tree_frame, columns=('Port', 'Service', 'Status'), height=20)
        self.port_tree.column('#0', width=0)
        self.port_tree.column('Port', width=100)
        self.port_tree.column('Service', width=150)
        self.port_tree.column('Status', width=100)
        self.port_tree.heading('Port', text='Port')
        self.port_tree.heading('Service', text='Service')
        self.port_tree.heading('Status', text='Status')
        
        style = ttk.Style()
        style.configure('Treeview', background=COLORS['bg_dark'], foreground=COLORS['text_primary'])
        style.configure('Treeview.Heading', background=COLORS['card_light'], foreground=COLORS['accent'])
        
        self.port_tree.pack(fill=tk.BOTH, expand=True)
        
        self.pages["ports"] = page
    
    def _run_ports(self):
        host = self.port_host.get().strip()
        ports_str = self.port_list.get().strip()
        if not host or not ports_str:
            return
        
        ports = []
        for p in ports_str.split(','):
            p = p.strip()
            if '-' in p:
                s, e = p.split('-')
                ports.extend(range(int(s), int(e) + 1))
            else:
                ports.append(int(p))
        
        self.port_tree.delete(*self.port_tree.get_children())
        services = {22: 'SSH', 80: 'HTTP', 443: 'HTTPS', 3306: 'MySQL', 5432: 'PostgreSQL',
                   3389: 'RDP', 5900: 'VNC', 8080: 'HTTP-ALT', 9000: 'SonarQube'}
        
        def do():
            results = NetworkAdapter.scan_ports(host, ports)
            for p, ok in sorted(results.items()):
                if ok:
                    service = services.get(p, 'Unknown')
                    self.root.after(0, lambda x=p, s=service: self.port_tree.insert('', 'end', 
                                                                                    values=(x, s, "✓ OPEN")))
        
        threading.Thread(target=do, daemon=True).start()
    
    # ========== PAGE: ANALYSIS ==========
    def _create_analysis_page(self):
        page = tk.Frame(self.content, bg=COLORS['bg_main'])
        
        tk.Label(page, text="📊 NETWORK ANALYSIS", bg=COLORS['bg_main'], fg=COLORS['accent'],
                font=('Segoe UI', 14, 'bold')).pack(anchor=tk.W, padx=20, pady=15)
        
        frame = Card3D(page, bg=COLORS['card'])
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Info display
        self.analysis_text = scrolledtext.ScrolledText(frame, bg=COLORS['bg_dark'], 
                                                      fg=COLORS['text_primary'],
                                                      font=('Segoe UI', 10), relief=tk.FLAT)
        self.analysis_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Buttons
        btn_frame = tk.Frame(page, bg=COLORS['bg_main'])
        btn_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        tk.Button(btn_frame, text="🔄 Refresh ARP", bg=COLORS['accent'], fg='white',
                 font=('Segoe UI', 10, 'bold'), relief=tk.FLAT, command=self._refresh_analysis,
                 padx=20).pack(side=tk.LEFT, ipady=6)
        
        self.pages["analysis"] = page
    
    def _refresh_analysis(self):
        self.analysis_text.delete('1.0', tk.END)
        
        def do():
            arp = NetworkAdapter.get_arp_table()
            local_ip = NetworkAdapter.get_local_ip()
            
            text = f"📍 Local IP: {local_ip}\n\n"
            text += f"📊 ARP Table ({len(arp)} entries):\n"
            text += "=" * 50 + "\n"
            
            for ip, mac in sorted(arp.items()):
                text += f"{ip:<15} | {mac}\n"
            
            self.root.after(0, lambda: self.analysis_text.delete('1.0', tk.END))
            self.root.after(0, lambda: self.analysis_text.insert('1.0', text))
        
        threading.Thread(target=do, daemon=True).start()
    
    # ========== PAGE: GROUPS ==========
    def _create_groups_page(self):
        page = tk.Frame(self.content, bg=COLORS['bg_main'])
        
        tk.Label(page, text="📋 GROUPS", bg=COLORS['bg_main'], fg=COLORS['accent'],
                font=('Segoe UI', 14, 'bold')).pack(anchor=tk.W, padx=20, pady=15)
        
        frame = Card3D(page, bg=COLORS['card'])
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        tk.Label(frame, text="Groups Management (Sắp có)", bg=COLORS['card'], 
                fg=COLORS['text_secondary'], font=('Segoe UI', 12)).pack(expand=True)
        
        self.pages["groups"] = page
    
    # ========== PAGE: BACKUP ==========
    def _create_backup_page(self):
        page = tk.Frame(self.content, bg=COLORS['bg_main'])
        
        tk.Label(page, text="💾 BACKUP & EXPORT", bg=COLORS['bg_main'], fg=COLORS['accent'],
                font=('Segoe UI', 14, 'bold')).pack(anchor=tk.W, padx=20, pady=15)
        
        frame = tk.Frame(page, bg=COLORS['bg_main'])
        frame.pack(expand=True)
        
        tk.Button(frame, text="📤 Export Config", bg=COLORS['accent'], fg='white',
                 font=('Segoe UI', 11, 'bold'), relief=tk.FLAT, command=self._export,
                 padx=30, pady=10).pack(pady=10)
        
        tk.Button(frame, text="📥 Import Config", bg=COLORS['success'], fg='white',
                 font=('Segoe UI', 11, 'bold'), relief=tk.FLAT, command=self._import,
                 padx=30, pady=10).pack(pady=10)
        
        self.pages["backup"] = page
    
    def _export(self):
        f = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if f:
            with open(f, 'w') as fp:
                json.dump(self.hosts, fp, indent=2, default=str)
            messagebox.showinfo("✅", "Exported!")
    
    def _import(self):
        f = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if f:
            with open(f, 'r') as fp:
                data = json.load(fp)
            messagebox.showinfo("✅", "Imported!")
    
    # ========== PAGE: INFO ==========
    def _create_info_page(self):
        page = tk.Frame(self.content, bg=COLORS['bg_main'])
        
        tk.Label(page, text="ℹ️ INFORMATION", bg=COLORS['bg_main'], fg=COLORS['accent'],
                font=('Segoe UI', 14, 'bold')).pack(anchor=tk.W, padx=20, pady=15)
        
        frame = Card3D(page, bg=COLORS['card'])
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        info_text = """
🌐 Network Tool Pro v1.2.6
👨‍💻 Developed by Yuri
📅 2024-2026

Features:
  ✓ PING Monitoring
  ✓ Traceroute
  ✓ IP Scanner
  ✓ Port Scanner
  ✓ Network Analysis
  ✓ ARP Table
  ✓ MAC Detection
  ✓ VLAN Management

Technology:
  • Python 3.10+
  • Tkinter UI
  • Threading
  • Socket

Contact: github.com/mrbuivanvn-prog
        """
        
        tk.Label(frame, text=info_text, bg=COLORS['card'], fg=COLORS['text_primary'],
                font=('Segoe UI', 11), justify=tk.LEFT).pack(expand=True, padx=20, pady=20)
        
        self.pages["info"] = page
    
    # ========== NAVIGATION ==========
    def _show_ping(self):
        self._show_page("ping")
    
    def _show_tracert(self):
        self._show_page("tracert")
    
    def _show_scan(self):
        self._show_page("scan")
    
    def _show_ports(self):
        self._show_page("ports")
    
    def _show_analysis(self):
        self._show_page("analysis")
        self._refresh_analysis()
    
    def _show_groups(self):
        self._show_page("groups")
    
    def _show_backup(self):
        self._show_page("backup")
    
    def _show_info(self):
        self._show_page("info")
    
    def _show_page(self, page_name):
        for p in self.pages.values():
            p.pack_forget()
        self.pages[page_name].pack(fill=tk.BOTH, expand=True)
    
    # ========== CONFIG ==========
    def _save_config(self):
        try:
            config = {
                'hosts': {ip: {
                    'name': card.name,
                    'mac': card.mac,
                    'vlan': card.vlan,
                    'vnc_user': card.vnc_user,
                    'vnc_pass': card.vnc_pass,
                    'notes': card.notes
                } for ip, card in self.hosts.items()}
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except:
            pass
    
    def _load_config(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Load later after UI created
                    self.saved_config = config.get('hosts', {})
            except:
                self.saved_config = {}
        else:
            self.saved_config = {}
    
    def _on_close(self):
        self._stop_all()
        self._save_config()
        self.root.destroy()
    
    def run(self):
        # Load saved hosts
        for ip, data in self.saved_config.items():
            self._add_host(ip, data.get('name', ip))
            if ip in self.hosts:
                card = self.hosts[ip]
                card.mac = data.get('mac', 'N/A')
                card.vlan = data.get('vlan', '0')
                card.vnc_user = data.get('vnc_user', '')
                card.vnc_pass = data.get('vnc_pass', '')
                card.notes = data.get('notes', '')
        
        self.root.mainloop()


# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    app = NetworkToolPro()
    app.run()
