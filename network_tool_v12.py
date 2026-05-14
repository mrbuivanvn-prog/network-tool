#!/usr/bin/env python3
"""
NETWORK SCANNER PRO - FIXED SCAN
Scan IP hiển thị kết quả ngay lập tức
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
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
import base64
from io import BytesIO

SYSTEM = platform.system().lower()
IS_WINDOWS = SYSTEM == 'windows'

# ============================================================================
# ẢNH SỨA BASE64
# ============================================================================
JELLYFISH_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAAMgAAADICAYAAACtWK6eAAAACXBIWXMAAAsTAAALEwEAmpwYAAAF8GlUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4gPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iQWRvYmUgWE1QIENvcmUgNS42LWMxNDUgNzkuMTYzNDk5LCAyMDE4LzA4LzEzLTE2OjQwOjIyICAgICAgICAiPiA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPiA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIiB4bWxuczp4bXA9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8iIHhtbG5zOnhtcE1NPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvbW0vIiB4bWxuczpzdFJlZj0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL3NUeXBlL1Jlc291cmNlUmVmIyIgeG1wOkNyZWF0b3JUb29sPSJBZG9iZSBQaG90b3Nob3AgQ0MgMjAxOSAoV2luZG93cykiIHhtcE1NOkluc3RhbmNlSUQ9InhtcC5paWQ6M0I5MjI5RjQxQkFCMTFFQTgzMDhFODM5RkY5MjAzQzgiIHhtcE1NOkRvY3VtZW50SUQ9InhtcC5kaWQ6M0I5MjI5RjUxQkFCMTFFQTgzMDhFODM5RkY5MjAzQzgiPiA8eG1wTU06RGVyaXZlZEZyb20gc3RSZWY6aW5zdGFuY2VJRD0ieG1wLmlpZDozQjkyMjlGMjFCQUIxMUVBODMwOEU4MzlGRjkyMDNDOCIgc3RSZWY6ZG9jdW1lbnRJRD0ieG1wLmRpZDozQjkyMjlGMzFCQUIxMUVBODMwOEU4MzlGRjkyMDNDOCIvPiA8L3JkZjpEZXNjcmlwdGlvbj4gPC9yZGY6UkRGPiA8L3g6eG1wbWV0YT4gPD94cGFja2V0IGVuZD0iciI/Pk3I/YYAAAY5SURBVHic7dpPaBxVHMfx7yRtsu0f0pCm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"

def get_jellyfish_icon(size=(32, 32)):
    try:
        from PIL import Image, ImageTk
        img_data = base64.b64decode(JELLYFISH_BASE64)
        img = Image.open(BytesIO(img_data))
        img = img.resize(size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)
    except:
        return None

# ============================================================================
# MÀU SẮC
# ============================================================================
COLORS = {
    'bg': '#1E1E1E',
    'sidebar': '#252526',
    'card': '#2D2D2D',
    'accent': '#007ACC',
    'text': '#FFFFFF',
    'text_sec': '#CCCCCC',
    'success': '#6A9955',
    'error': '#F48771',
}


class NetworkScanner:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Network Scanner Pro - Ultimate Edition")
        self.root.geometry("1300x750")
        self.root.configure(bg=COLORS['bg'])
        
        # Dữ liệu
        self.ping_hosts = []
        self.groups = {"Default": []}
        self.config_file = Path.home() / ".net_scanner.json"
        self.scanning = False
        
        self._create_ui()
        self._load_config()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _create_ui(self):
        # Header
        header = tk.Frame(self.root, bg=COLORS['accent'], height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        jelly = get_jellyfish_icon((24, 24))
        if jelly:
            tk.Label(header, image=jelly, bg=COLORS['accent']).pack(side=tk.LEFT, padx=(10, 5))
        
        tk.Label(header, text="Network Scanner Pro", bg=COLORS['accent'], 
                fg='white', font=('Segoe UI', 14, 'bold')).pack(side=tk.LEFT)
        
        tk.Label(header, text="mrbuivanvn@gmail.com", bg=COLORS['accent'], 
                fg='white', font=('Segoe UI', 9)).pack(side=tk.RIGHT, padx=15)
        
        self.status = tk.Label(header, text="✓ Ready", bg=COLORS['accent'], fg='white')
        self.status.pack(side=tk.RIGHT, padx=15)
        
        # Main
        main = tk.Frame(self.root, bg=COLORS['bg'])
        main.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # Sidebar
        sidebar = tk.Frame(main, bg=COLORS['sidebar'], width=150)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        jelly_big = get_jellyfish_icon((48, 48))
        if jelly_big:
            tk.Label(sidebar, image=jelly_big, bg=COLORS['sidebar']).pack(pady=(15, 5))
        
        buttons = [
            ("📡 Scan IP", self._show_scan),
            ("🔌 Port Scan", self._show_port),
            ("🔍 Ping", self._show_ping),
            ("🗺️ Traceroute", self._show_trace),
            ("🖥️ VNC", self._show_vnc),
            ("📋 Groups", self._show_groups),
            ("💾 Backup", self._show_backup),
        ]
        
        for text, cmd in buttons:
            btn = tk.Button(sidebar, text=text, bg=COLORS['sidebar'], fg=COLORS['text'],
                          font=('Segoe UI', 10), relief=tk.FLAT, command=cmd,
                          anchor=tk.W, padx=15, pady=10)
            btn.pack(fill=tk.X, padx=5, pady=3)
            btn.bind('<Enter>', lambda e, b=btn: b.config(bg=COLORS['accent']))
            btn.bind('<Leave>', lambda e, b=btn: b.config(bg=COLORS['sidebar']))
        
        # Content
        self.content = tk.Frame(main, bg=COLORS['bg'])
        self.content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self._show_scan()
    
    def _clear(self):
        for w in self.content.winfo_children():
            w.destroy()
    
    # ==================== SCAN IP (FIXED - HIỂN THỊ NGAY) ====================
    def _show_scan(self):
        self._clear()
        
        # Toolbar
        toolbar = tk.Frame(self.content, bg=COLORS['bg'])
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(toolbar, text="IP Range:", bg=COLORS['bg'], fg=COLORS['text']).pack(side=tk.LEFT, padx=5)
        self.scan_range = tk.Entry(toolbar, bg=COLORS['card'], fg=COLORS['text'], 
                                   width=22, font=('Consolas', 10))
        self.scan_range.pack(side=tk.LEFT, padx=5)
        self.scan_range.insert(0, "192.168.1.1-192.168.1.254")
        
        tk.Label(toolbar, text="CIDR:", bg=COLORS['bg'], fg=COLORS['text']).pack(side=tk.LEFT, padx=5)
        self.scan_cidr = tk.Entry(toolbar, bg=COLORS['card'], fg=COLORS['text'], 
                                  width=18, font=('Consolas', 10))
        self.scan_cidr.pack(side=tk.LEFT, padx=5)
        self.scan_cidr.insert(0, "192.168.1.0/24")
        
        self.scan_btn = tk.Button(toolbar, text="▶ Scan Now", bg=COLORS['accent'], fg='white',
                                  font=('Segoe UI', 10, 'bold'), padx=15, pady=5,
                                  command=self._do_scan)
        self.scan_btn.pack(side=tk.LEFT, padx=10)
        
        # Progress label
        self.scan_progress = tk.Label(self.content, text="", bg=COLORS['bg'], 
                                      fg=COLORS['text_sec'], font=('Segoe UI', 9))
        self.scan_progress.pack(fill=tk.X, pady=(0, 5))
        
        # Treeview frame
        tree_frame = tk.Frame(self.content, bg=COLORS['bg'])
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        scroll_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        
        # Treeview
        columns = ('IP', 'Name', 'Status', 'MAC', 'Response')
        self.scan_tree = ttk.Treeview(tree_frame, columns=columns,
                                       yscrollcommand=scroll_y.set,
                                       xscrollcommand=scroll_x.set)
        
        scroll_y.config(command=self.scan_tree.yview)
        scroll_x.config(command=self.scan_tree.xview)
        
        self.scan_tree.heading('#0', text='')
        self.scan_tree.heading('IP', text='IP Address')
        self.scan_tree.heading('Name', text='Host Name')
        self.scan_tree.heading('Status', text='Status')
        self.scan_tree.heading('MAC', text='MAC Address')
        self.scan_tree.heading('Response', text='Response (ms)')
        
        self.scan_tree.column('#0', width=0)
        self.scan_tree.column('IP', width=140)
        self.scan_tree.column('Name', width=180)
        self.scan_tree.column('Status', width=70)
        self.scan_tree.column('MAC', width=160)
        self.scan_tree.column('Response', width=80)
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', background=COLORS['card'], foreground=COLORS['text'],
                       fieldbackground=COLORS['card'], rowheight=24)
        style.configure('Treeview.Heading', background=COLORS['sidebar'], 
                       foreground=COLORS['text'], font=('Segoe UI', 9, 'bold'))
        
        self.scan_tree.grid(row=0, column=0, sticky='nsew')
        scroll_y.grid(row=0, column=1, sticky='ns')
        scroll_x.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Right-click menu
        self.scan_menu = tk.Menu(self.scan_tree, tearoff=0, bg=COLORS['card'], fg=COLORS['text'])
        self.scan_menu.add_command(label="▶ Ping", command=self._scan_ping)
        self.scan_menu.add_command(label="🗺️ Traceroute", command=self._scan_trace)
        self.scan_menu.add_command(label="🖥️ VNC Connect", command=self._scan_vnc)
        self.scan_menu.add_separator()
        self.scan_menu.add_command(label="📋 Copy IP", command=self._copy_ip)
        self.scan_tree.bind("<Button-3>", self._show_menu)
    
    def _get_ips_from_input(self):
        range_str = self.scan_range.get().strip()
        cidr_str = self.scan_cidr.get().strip()
        ips = []
        
        if range_str and '-' in range_str:
            try:
                parts = range_str.split('-')
                start = parts[0].strip()
                end = parts[1].strip()
                start_ip = ipaddress.ip_address(start)
                end_ip = ipaddress.ip_address(end)
                current = int(start_ip)
                end_int = int(end_ip)
                while current <= end_int:
                    ips.append(str(ipaddress.ip_address(current)))
                    current += 1
            except:
                pass
        elif cidr_str:
            try:
                net = ipaddress.ip_network(cidr_str, strict=False)
                ips = [str(ip) for ip in net.hosts()]
            except:
                pass
        return ips
    
    def _do_scan(self):
        # Xóa kết quả cũ
        for item in self.scan_tree.get_children():
            self.scan_tree.delete(item)
        
        ips = self._get_ips_from_input()
        if not ips:
            messagebox.showerror("Error", "Invalid IP range or CIDR!")
            return
        
        if self.scanning:
            return
        
        self.scanning = True
        self.scan_btn.config(state=tk.DISABLED, text="⏹ Scanning...")
        self.scan_progress.config(text=f"Scanning {len(ips)} IPs...")
        self.status.config(text=f"Scanning {len(ips)} IPs...")
        
        def scan_single_ip(ip):
            try:
                param = '-n' if IS_WINDOWS else '-c'
                start = time.time()
                result = subprocess.run(['ping', param, '1', '-W', '1', ip],
                                       capture_output=True, text=True, timeout=2)
                response = int((time.time() - start) * 1000)
                
                if result.returncode == 0:
                    # Lấy hostname
                    try:
                        hostname = socket.gethostbyaddr(ip)[0]
                    except:
                        hostname = ""
                    # Lấy MAC
                    mac = self._get_mac(ip)
                    return (ip, hostname, "● Online", mac, f"{response}ms")
                return None
            except:
                return None
        
        def update_result(result):
            if result:
                self.scan_tree.insert('', tk.END, values=result)
                self.scan_tree.yview_moveto(1)
        
        def scan_complete(found):
            self.scanning = False
            self.scan_btn.config(state=tk.NORMAL, text="▶ Scan Now")
            self.scan_progress.config(text=f"✓ Scan completed - Found {found} devices")
            self.status.config(text=f"✓ Found {found} devices")
        
        def do_scan():
            found = 0
            with ThreadPoolExecutor(max_workers=50) as executor:
                futures = {executor.submit(scan_single_ip, ip): ip for ip in ips}
                for future in as_completed(futures):
                    result = future.result()
                    if result:
                        found += 1
                        self.root.after(0, update_result, result)
                    # Cập nhật progress
                    self.root.after(0, lambda: self.scan_progress.config(
                        text=f"Scanning... {found} found so far"))
            self.root.after(0, scan_complete, found)
        
        threading.Thread(target=do_scan, daemon=True).start()
    
    def _get_mac(self, ip):
        try:
            cmd = ['arp', '-a', ip] if IS_WINDOWS else ['arp', '-n', ip]
            out = subprocess.check_output(cmd, universal_newlines=True, timeout=3)
            mac = re.search(r'([0-9a-fA-F]{2}[:-]){5}([0-9a-fA-F]{2})', out, re.IGNORECASE)
            return mac.group(0).upper() if mac else "Unknown"
        except:
            return "Unknown"
    
    def _show_menu(self, event):
        item = self.scan_tree.identify_row(event.y)
        if item:
            self.scan_tree.selection_set(item)
            self.scan_menu.post(event.x_root, event.y_root)
    
    def _scan_ping(self):
        sel = self.scan_tree.selection()
        if sel:
            ip = self.scan_tree.item(sel[0], 'values')[0]
            open_cmd(f'ping {ip} -t' if IS_WINDOWS else f'ping {ip}')
    
    def _scan_trace(self):
        sel = self.scan_tree.selection()
        if sel:
            ip = self.scan_tree.item(sel[0], 'values')[0]
            cmd = f'tracert {ip}' if IS_WINDOWS else f'traceroute {ip}'
            open_cmd(cmd)
    
    def _scan_vnc(self):
        sel = self.scan_tree.selection()
        if sel:
            ip = self.scan_tree.item(sel[0], 'values')[0]
            self._vnc_connect(ip)
    
    def _copy_ip(self):
        sel = self.scan_tree.selection()
        if sel:
            ip = self.scan_tree.item(sel[0], 'values')[0]
            self.root.clipboard_clear()
            self.root.clipboard_append(ip)
            self.status.config(text=f"Copied {ip}")
    
    # ==================== PORT SCAN ====================
    def _show_port(self):
        self._clear()
        
        toolbar = tk.Frame(self.content, bg=COLORS['bg'])
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(toolbar, text="Target:", bg=COLORS['bg'], fg=COLORS['text']).pack(side=tk.LEFT, padx=5)
        self.port_target = tk.Entry(toolbar, bg=COLORS['card'], fg=COLORS['text'], width=18)
        self.port_target.pack(side=tk.LEFT, padx=5)
        self.port_target.insert(0, "192.168.1.1")
        
        tk.Label(toolbar, text="Ports:", bg=COLORS['bg'], fg=COLORS['text']).pack(side=tk.LEFT, padx=5)
        self.port_list = tk.Entry(toolbar, bg=COLORS['card'], fg=COLORS['text'], width=35)
        self.port_list.pack(side=tk.LEFT, padx=5)
        self.port_list.insert(0, "22,80,443,3389,5900,8080")
        
        tk.Button(toolbar, text="Scan", bg=COLORS['accent'], fg='white',
                 padx=15, pady=5, command=self._do_port_scan).pack(side=tk.LEFT, padx=10)
        
        # Treeview
        tree_frame = tk.Frame(self.content, bg=COLORS['bg'])
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        self.port_tree = ttk.Treeview(tree_frame, columns=('Port', 'Status', 'Service'),
                                       yscrollcommand=scroll_y.set, height=20)
        scroll_y.config(command=self.port_tree.yview)
        
        self.port_tree.heading('#0', text='')
        self.port_tree.heading('Port', text='Port')
        self.port_tree.heading('Status', text='Status')
        self.port_tree.heading('Service', text='Service')
        self.port_tree.column('#0', width=0)
        self.port_tree.column('Port', width=100)
        self.port_tree.column('Status', width=80)
        self.port_tree.column('Service', width=150)
        
        self.port_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.services = {22:'SSH',80:'HTTP',443:'HTTPS',3389:'RDP',5900:'VNC',8080:'HTTP-Alt'}
    
    def _do_port_scan(self):
        target = self.port_target.get().strip()
        ports_str = self.port_list.get().strip()
        
        if not target:
            return
        
        ports = [int(p.strip()) for p in ports_str.split(',') if p.strip().isdigit()]
        if not ports:
            return
        
        for item in self.port_tree.get_children():
            self.port_tree.delete(item)
        
        self.status.config(text=f"Scanning {len(ports)} ports...")
        
        def check_port(p):
            try:
                s = socket.socket()
                s.settimeout(0.3)
                if s.connect_ex((target, p)) == 0:
                    return p
                s.close()
            except:
                pass
            return None
        
        def do():
            open_ports = []
            with ThreadPoolExecutor(max_workers=100) as ex:
                for p in ex.map(check_port, ports):
                    if p:
                        open_ports.append(p)
                        self.root.after(0, lambda x=p: self.port_tree.insert('', tk.END,
                            values=(x, "● OPEN", self.services.get(x, "Unknown"))))
            self.root.after(0, lambda: self.status.config(text=f"✓ Found {len(open_ports)} open ports"))
        
        threading.Thread(target=do, daemon=True).start()
    
    # ==================== PING ====================
    def _show_ping(self):
        self._clear()
        
        add_frame = tk.Frame(self.content, bg=COLORS['bg'])
        add_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(add_frame, text="IP:", bg=COLORS['bg'], fg=COLORS['text']).pack(side=tk.LEFT, padx=5)
        self.ping_ip = tk.Entry(add_frame, bg=COLORS['card'], fg=COLORS['text'], width=18)
        self.ping_ip.pack(side=tk.LEFT, padx=5)
        
        tk.Label(add_frame, text="Name:", bg=COLORS['bg'], fg=COLORS['text']).pack(side=tk.LEFT, padx=5)
        self.ping_name = tk.Entry(add_frame, bg=COLORS['card'], fg=COLORS['text'], width=15)
        self.ping_name.pack(side=tk.LEFT, padx=5)
        
        tk.Button(add_frame, text="Add", bg=COLORS['accent'], fg='white',
                 padx=15, pady=5, command=self._add_ping).pack(side=tk.LEFT, padx=10)
        tk.Button(add_frame, text="Remove All", bg=COLORS['error'], fg='white',
                 padx=15, pady=5, command=self._remove_all_ping).pack(side=tk.LEFT)
        
        list_frame = tk.LabelFrame(self.content, text="Saved Hosts", bg=COLORS['card'], fg=COLORS['text'])
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.ping_list = tk.Listbox(list_frame, bg=COLORS['bg'], fg=COLORS['text'],
                                    selectbackground=COLORS['accent'], font=('Consolas', 10))
        self.ping_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        btn_frame = tk.Frame(list_frame, bg=COLORS['card'])
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Button(btn_frame, text="▶ Ping Selected", bg=COLORS['success'], fg='white',
                 padx=15, pady=5, command=self._ping_selected).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="❌ Remove Selected", bg=COLORS['error'], fg='white',
                 padx=15, pady=5, command=self._remove_selected_ping).pack(side=tk.LEFT, padx=5)
        
        self._refresh_ping_list()
    
    def _add_ping(self):
        ip = self.ping_ip.get().strip()
        name = self.ping_name.get().strip()
        if not ip:
            return
        if not name:
            name = ip
        self.ping_hosts.append({'ip': ip, 'name': name})
        self._refresh_ping_list()
        self.ping_ip.delete(0, tk.END)
        self.ping_name.delete(0, tk.END)
        self._save_config()
    
    def _ping_selected(self):
        sel = self.ping_list.curselection()
        if sel:
            host = self.ping_hosts[sel[0]]
            open_cmd(f'ping {host["ip"]} -t' if IS_WINDOWS else f'ping {host["ip"]}')
    
    def _remove_selected_ping(self):
        sel = self.ping_list.curselection()
        if sel:
            del self.ping_hosts[sel[0]]
            self._refresh_ping_list()
            self._save_config()
    
    def _remove_all_ping(self):
        self.ping_hosts.clear()
        self._refresh_ping_list()
        self._save_config()
    
    def _refresh_ping_list(self):
        self.ping_list.delete(0, tk.END)
        for h in self.ping_hosts:
            self.ping_list.insert(tk.END, f"{h['name']} ({h['ip']})")
    
    # ==================== TRACEROUTE ====================
    def _show_trace(self):
        self._clear()
        
        frame = tk.Frame(self.content, bg=COLORS['bg'])
        frame.pack(fill=tk.X, pady=30)
        
        tk.Label(frame, text="Target:", bg=COLORS['bg'], fg=COLORS['text']).pack(side=tk.LEFT, padx=5)
        self.trace_ip = tk.Entry(frame, bg=COLORS['card'], fg=COLORS['text'], width=25)
        self.trace_ip.pack(side=tk.LEFT, padx=5)
        self.trace_ip.insert(0, "8.8.8.8")
        
        tk.Button(frame, text="Trace Route", bg=COLORS['accent'], fg='white',
                 padx=20, pady=8, command=self._do_trace).pack(side=tk.LEFT, padx=10)
    
    def _do_trace(self):
        ip = self.trace_ip.get().strip()
        if ip:
            cmd = f'tracert {ip}' if IS_WINDOWS else f'traceroute {ip}'
            open_cmd(cmd)
    
    # ==================== VNC ====================
    def _show_vnc(self):
        self._clear()
        
        frame = tk.Frame(self.content, bg=COLORS['bg'])
        frame.pack(fill=tk.X, pady=30)
        
        tk.Label(frame, text="IP:", bg=COLORS['bg'], fg=COLORS['text']).pack(side=tk.LEFT, padx=5)
        self.vnc_ip = tk.Entry(frame, bg=COLORS['card'], fg=COLORS['text'], width=18)
        self.vnc_ip.pack(side=tk.LEFT, padx=5)
        self.vnc_ip.insert(0, "192.168.1.10")
        
        tk.Label(frame, text="Port:", bg=COLORS['bg'], fg=COLORS['text']).pack(side=tk.LEFT, padx=5)
        self.vnc_port = tk.Entry(frame, bg=COLORS['card'], fg=COLORS['text'], width=8)
        self.vnc_port.pack(side=tk.LEFT, padx=5)
        self.vnc_port.insert(0, "5900")
        
        tk.Button(frame, text="Connect VNC", bg=COLORS['accent'], fg='white',
                 padx=20, pady=8, command=self._vnc_connect_input).pack(side=tk.LEFT, padx=10)
    
    def _vnc_connect_input(self):
        ip = self.vnc_ip.get().strip()
        port = self.vnc_port.get().strip()
        self._vnc_connect(ip, port)
    
    def _vnc_connect(self, ip, port="5900"):
        if not ip:
            return
        
        def do():
            try:
                if IS_WINDOWS:
                    vnc_paths = [
                        r"C:\Program Files\RealVNC\VNC Viewer\vncviewer.exe",
                        r"C:\Program Files\TightVNC\tightvncviewer.exe",
                    ]
                    found = False
                    for path in vnc_paths:
                        if Path(path).exists():
                            subprocess.Popen([path, f'{ip}:{port}'])
                            found = True
                            break
                    if not found:
                        subprocess.Popen(f'start vncviewer {ip}:{port}', shell=True)
                else:
                    subprocess.Popen(['vncviewer', f'{ip}:{port}'])
                self.root.after(0, lambda: self.status.config(text=f"VNC launched for {ip}"))
            except:
                pass
        threading.Thread(target=do, daemon=True).start()
    
    # ==================== GROUPS ====================
    def _show_groups(self):
        self._clear()
        
        top = tk.Frame(self.content, bg=COLORS['bg'])
        top.pack(fill=tk.X, pady=(0, 10))
        
        self.new_group = tk.Entry(top, bg=COLORS['card'], fg=COLORS['text'], width=20)
        self.new_group.pack(side=tk.LEFT, padx=5)
        tk.Button(top, text="Create Group", bg=COLORS['accent'], fg='white',
                 padx=15, pady=5, command=self._create_group).pack(side=tk.LEFT, padx=10)
        
        list_frame = tk.Frame(self.content, bg=COLORS['bg'])
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        left = tk.LabelFrame(list_frame, text="Groups", bg=COLORS['card'], fg=COLORS['text'])
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.groups_list = tk.Listbox(left, bg=COLORS['bg'], fg=COLORS['text'], selectbackground=COLORS['accent'])
        self.groups_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.groups_list.bind('<<ListboxSelect>>', self._on_group_select)
        
        right = tk.LabelFrame(list_frame, text="IPs in Group", bg=COLORS['card'], fg=COLORS['text'])
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        self.ips_list = tk.Listbox(right, bg=COLORS['bg'], fg=COLORS['text'], selectbackground=COLORS['accent'])
        self.ips_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        btn_frame = tk.Frame(self.content, bg=COLORS['bg'])
        btn_frame.pack(fill=tk.X, pady=10)
        tk.Button(btn_frame, text="Add IP", bg=COLORS['accent'], fg='white',
                 padx=15, pady=5, command=self._add_ip_group).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Remove IP", bg=COLORS['error'], fg='white',
                 padx=15, pady=5, command=self._remove_ip_group).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Load to Ping", bg=COLORS['success'], fg='white',
                 padx=15, pady=5, command=self._load_group).pack(side=tk.LEFT, padx=5)
        
        self._refresh_groups()
    
    def _refresh_groups(self):
        self.groups_list.delete(0, tk.END)
        for g in self.groups:
            self.groups_list.insert(tk.END, f"{g} ({len(self.groups[g])})")
    
    def _on_group_select(self, e):
        sel = self.groups_list.curselection()
        if sel:
            name = self.groups_list.get(sel[0]).split(' (')[0]
            self.ips_list.delete(0, tk.END)
            for ip in self.groups.get(name, []):
                self.ips_list.insert(tk.END, ip)
    
    def _create_group(self):
        name = self.new_group.get().strip()
        if name and name not in self.groups:
            self.groups[name] = []
            self._refresh_groups()
            self._save_config()
            self.new_group.delete(0, tk.END)
    
    def _add_ip_group(self):
        sel = self.groups_list.curselection()
        if not sel:
            return
        name = self.groups_list.get(sel[0]).split(' (')[0]
        ip = simpledialog.askstring("Add IP", "Enter IP:")
        if ip and ip not in self.groups[name]:
            self.groups[name].append(ip)
            self._refresh_groups()
            self._save_config()
            self._on_group_select(None)
    
    def _remove_ip_group(self):
        sel = self.groups_list.curselection()
        isel = self.ips_list.curselection()
        if not sel or not isel:
            return
        name = self.groups_list.get(sel[0]).split(' (')[0]
        ip = self.ips_list.get(isel[0])
        if ip in self.groups[name]:
            self.groups[name].remove(ip)
            self._refresh_groups()
            self._save_config()
            self._on_group_select(None)
    
    def _load_group(self):
        sel = self.groups_list.curselection()
        if not sel:
            return
        name = self.groups_list.get(sel[0]).split(' (')[0]
        ips = self.groups.get(name, [])
        for ip in ips:
            if not any(h['ip'] == ip for h in self.ping_hosts):
                self.ping_hosts.append({'ip': ip, 'name': ip})
        self._refresh_ping_list()
        self._save_config()
    
    # ==================== BACKUP ====================
    def _show_backup(self):
        self._clear()
        
        frame = tk.Frame(self.content, bg=COLORS['bg'])
        frame.pack(expand=True, pady=50)
        
        tk.Button(frame, text="📤 Export Config", bg=COLORS['accent'], fg='white',
                 padx=40, pady=12, command=self._export).pack(pady=10)
        tk.Button(frame, text="📥 Import Config", bg=COLORS['accent'], fg='white',
                 padx=40, pady=12, command=self._import).pack(pady=10)
        tk.Button(frame, text="🔄 Reset All", bg=COLORS['error'], fg='white',
                 padx=40, pady=12, command=self._reset).pack(pady=10)
    
    def _export(self):
        f = filedialog.asksaveasfilename(defaultextension=".json")
        if f:
            with open(f, 'w') as fp:
                json.dump({'ping_hosts': self.ping_hosts, 'groups': self.groups}, fp, indent=2)
            messagebox.showinfo("Success", "Exported!")
    
    def _import(self):
        f = filedialog.askopenfilename()
        if f:
            try:
                with open(f, 'r') as fp:
                    data = json.load(fp)
                    self.ping_hosts = data.get('ping_hosts', [])
                    self.groups = data.get('groups', {"Default": []})
                    self._refresh_ping_list()
                    self._refresh_groups()
                    self._save_config()
                messagebox.showinfo("Success", "Imported!")
            except:
                messagebox.showerror("Error", "Invalid file!")
    
    def _reset(self):
        if messagebox.askyesno("Confirm", "Reset all?"):
            self.ping_hosts.clear()
            self.groups = {"Default": []}
            self._refresh_ping_list()
            self._refresh_groups()
            self._save_config()
    
    def _save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump({'ping_hosts': self.ping_hosts, 'groups': self.groups}, f)
    
    def _load_config(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    self.ping_hosts = data.get('ping_hosts', [])
                    self.groups = data.get('groups', {"Default": []})
            except:
                pass
    
    def _on_close(self):
        self._save_config()
        self.root.destroy()
    
    def run(self):
        self.root.mainloop()


def open_cmd(command):
    if IS_WINDOWS:
        subprocess.Popen(f'start cmd /k "{command}"', shell=True)
    else:
        subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', f'{command}; exec bash'])


if __name__ == "__main__":
    app = NetworkScanner()
    app.run()
