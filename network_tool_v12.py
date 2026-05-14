#!/usr/bin/env python3
"""
NETWORK SCANNER PRO - ULTIMATE EDITION
Scan IP | Port Scan | Ping | Traceroute | VNC | Groups | Backup
Email: mrbuivanvn@gmail.com | Jellyfish Logo
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
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
import base64
from io import BytesIO

SYSTEM = platform.system().lower()
IS_WINDOWS = SYSTEM == 'windows'

# ============================================================================
# ẢNH SỨA BASE64
# ============================================================================
JELLYFISH_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAAMgAAADICAYAAACtWK6eAAAACXBIWXMAAAsTAAALEwEAmpwYAAAF8GlUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQi[...]

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
# MÀU SẮC - MODERN & ELEGANT
# ============================================================================
COLORS = {
    'bg': '#0D1117',          # GitHub dark
    'sidebar': '#161B22',     # Sidebar
    'card': '#21262D',        # Card bg
    'accent': '#1F6FEB',      # Modern blue
    'accent_hover': '#388BFD',
    'text': '#E6EDF3',        # Light text
    'text_sec': '#8B949E',    # Secondary text
    'success': '#3FB950',     # Green
    'error': '#DA3633',       # Red
    'warning': '#D29922',     # Orange
    'border': '#30363D',      # Border
}


class NetworkScanner:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Network Scanner Pro - Ultimate Edition")
        self.root.geometry("1400x800")
        self.root.configure(bg=COLORS['bg'])
        self.root.minsize(1100, 650)
        
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
        header = tk.Frame(self.root, bg=COLORS['accent'], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Logo
        self.jellyfish_icon = get_jellyfish_icon((32, 32))
        if self.jellyfish_icon:
            logo_label = tk.Label(header, image=self.jellyfish_icon, bg=COLORS['accent'])
            logo_label.pack(side=tk.LEFT, padx=(15, 8), pady=10)
        
        tk.Label(header, text="Network Scanner Pro", bg=COLORS['accent'], 
                fg='white', font=('Segoe UI', 15, 'bold')).pack(side=tk.LEFT)
        
        # Email + Status
        right_frame = tk.Frame(header, bg=COLORS['accent'])
        right_frame.pack(side=tk.RIGHT, padx=15)
        
        self.status = tk.Label(right_frame, text="✓ Ready", bg=COLORS['accent'], 
                               fg='#C9D1D9', font=('Segoe UI', 10))
        self.status.pack()
        
        tk.Label(right_frame, text="mrbuivanvn@gmail.com", bg=COLORS['accent'], 
                fg='#8B949E', font=('Segoe UI', 8)).pack()
        
        # Main
        main = tk.Frame(self.root, bg=COLORS['bg'])
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Sidebar
        sidebar = tk.Frame(main, bg=COLORS['sidebar'], width=180)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        sidebar.pack_propagate(False)
        
        # Logo in sidebar
        logo_big = get_jellyfish_icon((52, 52))
        if logo_big:
            tk.Label(sidebar, image=logo_big, bg=COLORS['sidebar']).pack(pady=(20, 10))
        
        tk.Label(sidebar, text="TOOLS", bg=COLORS['sidebar'], 
                fg=COLORS['accent'], font=('Segoe UI', 10, 'bold')).pack(pady=(10, 20))
        
        # Buttons
        buttons = [
            ("🔍 Scan IP", self._show_scan),
            ("🔌 Port Scan", self._show_port),
            ("📡 Ping", self._show_ping),
            ("🗺️ Traceroute", self._show_trace),
            ("🖥️ VNC", self._show_vnc),
            ("📋 Groups", self._show_groups),
            ("💾 Backup", self._show_backup),
        ]
        
        for text, cmd in buttons:
            btn = tk.Button(sidebar, text=text, bg=COLORS['sidebar'], fg=COLORS['text'],
                          font=('Segoe UI', 9), relief=tk.FLAT, command=cmd,
                          anchor=tk.W, padx=12, pady=12, bd=0, activebackground=COLORS['accent'],
                          activeforeground='white', cursor='hand2')
            btn.pack(fill=tk.X, padx=8, pady=3)
            btn.bind('<Enter>', lambda e, b=btn: b.config(bg=COLORS['accent'], fg='white'))
            btn.bind('<Leave>', lambda e, b=btn: b.config(bg=COLORS['sidebar'], fg=COLORS['text']))
        
        # Content
        self.content = tk.Frame(main, bg=COLORS['bg'])
        self.content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self._show_scan()
    
    def _clear(self):
        for w in self.content.winfo_children():
            w.destroy()
    
    # ==================== SCAN IP ====================
    def _show_scan(self):
        self._clear()
        
        # Toolbar
        toolbar = tk.Frame(self.content, bg=COLORS['bg'])
        toolbar.pack(fill=tk.X, pady=(0, 15))
        
        # Range input
        range_frame = tk.Frame(toolbar, bg=COLORS['bg'])
        range_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(range_frame, text="IP Range:", bg=COLORS['bg'], 
                fg=COLORS['text_sec'], font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=(0, 5))
        self.scan_range = tk.Entry(range_frame, bg=COLORS['card'], fg=COLORS['text'], 
                                   width=22, font=('Consolas', 10), relief=tk.FLAT, bd=1,
                                   insertbackground=COLORS['accent'])
        self.scan_range.pack(side=tk.LEFT, padx=(0, 15))
        self.scan_range.insert(0, "192.168.1.1-192.168.1.254")
        
        tk.Label(range_frame, text="CIDR:", bg=COLORS['bg'], 
                fg=COLORS['text_sec'], font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=(0, 5))
        self.scan_cidr = tk.Entry(range_frame, bg=COLORS['card'], fg=COLORS['text'], 
                                  width=18, font=('Consolas', 10), relief=tk.FLAT, bd=1,
                                  insertbackground=COLORS['accent'])
        self.scan_cidr.pack(side=tk.LEFT, padx=(0, 15))
        self.scan_cidr.insert(0, "192.168.1.0/24")
        
        # Scan button
        scan_btn = tk.Button(toolbar, text="▶ Scan Now", bg=COLORS['accent'], fg='white',
                            font=('Segoe UI', 10, 'bold'), padx=20, pady=6,
                            command=self._do_scan, cursor='hand2', relief=tk.FLAT, bd=0,
                            activebackground=COLORS['accent_hover'], activeforeground='white')
        scan_btn.pack(side=tk.RIGHT)
        
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
                                       xscrollcommand=scroll_x.set, height=20)
        
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
        self.scan_tree.column('Name', width=200)
        self.scan_tree.column('Status', width=80)
        self.scan_tree.column('MAC', width=160)
        self.scan_tree.column('Response', width=100)
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', background=COLORS['card'], foreground=COLORS['text'], 
                       fieldbackground=COLORS['card'], rowheight=26, font=('Segoe UI', 9))
        style.configure('Treeview.Heading', background=COLORS['sidebar'], 
                       foreground=COLORS['text'], font=('Segoe UI', 9, 'bold'))
        style.map('Treeview', background=[('selected', COLORS['accent'])])
        
        self.scan_tree.grid(row=0, column=0, sticky='nsew')
        scroll_y.grid(row=0, column=1, sticky='ns')
        scroll_x.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Context menu
        self.scan_menu = tk.Menu(self.scan_tree, tearoff=0, bg=COLORS['card'], 
                                 fg=COLORS['text'], font=('Segoe UI', 9))
        self.scan_menu.add_command(label="▶ Ping", command=self._scan_ping_selected)
        self.scan_menu.add_command(label="🗺️ Traceroute", command=self._scan_trace_selected)
        self.scan_menu.add_command(label="🖥️ VNC Connect", command=self._scan_vnc_selected)
        self.scan_menu.add_separator()
        self.scan_menu.add_command(label="📋 Copy IP", command=self._copy_ip)
        self.scan_menu.add_command(label="📋 Copy Name", command=self._copy_name)
        self.scan_tree.bind("<Button-3>", self._show_scan_menu)
        
        # Info label
        self.scan_info = tk.Label(self.content, text="Ready to scan...", bg=COLORS['bg'], 
                                  fg=COLORS['text_sec'], font=('Segoe UI', 8))
        self.scan_info.pack(fill=tk.X, pady=(8, 0))
    
    def _do_scan(self):
        if self.scanning:
            messagebox.showwarning("Warning", "Scan already in progress!")
            return
        
        for item in self.scan_tree.get_children():
            self.scan_tree.delete(item)
        
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
            except Exception as e:
                messagebox.showerror("Error", f"Invalid IP range: {e}")
                return
        elif cidr_str:
            try:
                net = ipaddress.ip_network(cidr_str, strict=False)
                ips = [str(ip) for ip in net.hosts()]
            except Exception as e:
                messagebox.showerror("Error", f"Invalid CIDR: {e}")
                return
        
        if not ips:
            messagebox.showerror("Error", "Please enter valid IP range or CIDR!")
            return
        
        self.scanning = True
        self.scan_info.config(text=f"Scanning {len(ips)} IPs...")
        self.status.config(text=f"⏳ Scanning {len(ips)} IPs...")
        
        def scan_ip(ip):
            try:
                param = '-n' if IS_WINDOWS else '-c'
                start = time.time()
                
                # Ping command
                result = subprocess.run(['ping', param, '1', '-w', '500' if IS_WINDOWS else '1', ip], 
                                       capture_output=True, text=True, timeout=2)
                response = int((time.time() - start) * 1000)
                
                if result.returncode == 0:
                    # Resolve hostname
                    try:
                        hostname = socket.gethostbyaddr(ip)[0]
                    except:
                        hostname = ""
                    
                    # Get MAC
                    mac = self._get_mac(ip)
                    return (ip, hostname, "● Online", mac, f"{response}ms")
                return None
            except:
                return None
        
        def do():
            results = []
            with ThreadPoolExecutor(max_workers=50) as ex:
                futures = [ex.submit(scan_ip, ip) for ip in ips]
                for future in futures:
                    try:
                        r = future.result(timeout=3)
                        if r:
                            results.append(r)
                    except:
                        pass
            
            def update():
                for ip, name, status, mac, resp in results:
                    self.scan_tree.insert('', tk.END, values=(ip, name, status, mac, resp))
                
                self.scan_info.config(text=f"✓ Scan completed - Found {len(results)}/{len(ips)} online devices")
                self.status.config(text=f"✓ Found {len(results)} devices")
                self.scanning = False
            
            self.root.after(0, update)
        
        threading.Thread(target=do, daemon=True).start()
    
    def _get_mac(self, ip):
        try:
            if IS_WINDOWS:
                out = subprocess.check_output(['arp', '-a', ip], text=True, timeout=1, stderr=subprocess.DEVNULL)
            else:
                out = subprocess.check_output(['arp', '-n', ip], text=True, timeout=1, stderr=subprocess.DEVNULL)
            
            mac = re.search(r'([0-9a-fA-F]{2}[:-]){5}([0-9a-fA-F]{2})', out, re.IGNORECASE)
            return mac.group(0).upper() if mac else "Unknown"
        except:
            return "Unknown"
    
    def _show_scan_menu(self, event):
        item = self.scan_tree.identify_row(event.y)
        if item:
            self.scan_tree.selection_set(item)
            self.scan_menu.post(event.x_root, event.y_root)
    
    def _scan_ping_selected(self):
        sel = self.scan_tree.selection()
        if sel:
            ip = self.scan_tree.item(sel[0], 'values')[0]
            open_cmd(f'ping {ip} -t' if IS_WINDOWS else f'ping {ip}')
            self.status.config(text=f"Pinging {ip}")
    
    def _scan_trace_selected(self):
        sel = self.scan_tree.selection()
        if sel:
            ip = self.scan_tree.item(sel[0], 'values')[0]
            cmd = f'tracert {ip}' if IS_WINDOWS else f'traceroute {ip}'
            open_cmd(cmd)
            self.status.config(text=f"Tracing {ip}")
    
    def _scan_vnc_selected(self):
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
    
    def _copy_name(self):
        sel = self.scan_tree.selection()
        if sel:
            name = self.scan_tree.item(sel[0], 'values')[1]
            if name:
                self.root.clipboard_clear()
                self.root.clipboard_append(name)
                self.status.config(text=f"Copied {name}")
    
    # ==================== PORT SCAN ====================
    def _show_port(self):
        self._clear()
        
        toolbar = tk.Frame(self.content, bg=COLORS['bg'])
        toolbar.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(toolbar, text="Target:", bg=COLORS['bg'], fg=COLORS['text_sec'], font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=(0, 5))
        self.port_target = tk.Entry(toolbar, bg=COLORS['card'], fg=COLORS['text'], 
                                    width=18, font=('Consolas', 10), relief=tk.FLAT, bd=1,
                                    insertbackground=COLORS['accent'])
        self.port_target.pack(side=tk.LEFT, padx=(0, 15))
        self.port_target.insert(0, "192.168.1.1")
        
        tk.Label(toolbar, text="Ports:", bg=COLORS['bg'], fg=COLORS['text_sec'], font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=(0, 5))
        self.port_list = tk.Entry(toolbar, bg=COLORS['card'], fg=COLORS['text'], 
                                  width=35, font=('Consolas', 10), relief=tk.FLAT, bd=1,
                                  insertbackground=COLORS['accent'])
        self.port_list.pack(side=tk.LEFT, padx=(0, 15))
        self.port_list.insert(0, "21,22,23,25,80,443,445,3389,5900,8080")
        
        tk.Button(toolbar, text="Scan", bg=COLORS['accent'], fg='white',
                 font=('Segoe UI', 10, 'bold'), padx=20, pady=6,
                 command=self._do_port_scan, relief=tk.FLAT, bd=0,
                 activebackground=COLORS['accent_hover']).pack(side=tk.LEFT)
        
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
        self.port_tree.column('Port', width=120)
        self.port_tree.column('Status', width=100)
        self.port_tree.column('Service', width=150)
        
        style = ttk.Style()
        style.configure('Treeview', background=COLORS['card'], foreground=COLORS['text'], 
                       fieldbackground=COLORS['card'], rowheight=26, font=('Segoe UI', 9))
        style.configure('Treeview.Heading', background=COLORS['sidebar'], foreground=COLORS['text'])
        
        self.port_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.services = {
            21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP', 53: 'DNS',
            80: 'HTTP', 110: 'POP3', 143: 'IMAP', 443: 'HTTPS', 445: 'SMB',
            3306: 'MySQL', 3389: 'RDP', 5432: 'PostgreSQL', 5900: 'VNC',
            8080: 'HTTP-Alt', 8443: 'HTTPS-Alt'
        }
    
    def _do_port_scan(self):
        target = self.port_target.get().strip()
        ports_str = self.port_list.get().strip()
        
        if not target:
            messagebox.showerror("Error", "Enter target IP!")
            return
        
        ports = []
        for p in ports_str.split(','):
            p = p.strip()
            if p.isdigit():
                ports.append(int(p))
        
        if not ports:
            messagebox.showerror("Error", "Enter valid ports!")
            return
        
        for item in self.port_tree.get_children():
            self.port_tree.delete(item)
        
        self.status.config(text=f"Scanning {len(ports)} ports on {target}...")
        
        def check_port(p):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.2)
                result = s.connect_ex((target, p))
                s.close()
                return p if result == 0 else None
            except:
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
        add_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(add_frame, text="IP:", bg=COLORS['bg'], fg=COLORS['text_sec'], font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=(0, 5))
        self.ping_ip = tk.Entry(add_frame, bg=COLORS['card'], fg=COLORS['text'], 
                                width=18, font=('Consolas', 10), relief=tk.FLAT, bd=1,
                                insertbackground=COLORS['accent'])
        self.ping_ip.pack(side=tk.LEFT, padx=(0, 15))
        
        tk.Label(add_frame, text="Name:", bg=COLORS['bg'], fg=COLORS['text_sec'], font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=(0, 5))
        self.ping_name = tk.Entry(add_frame, bg=COLORS['card'], fg=COLORS['text'], 
                                  width=15, font=('Segoe UI', 10), relief=tk.FLAT, bd=1,
                                  insertbackground=COLORS['accent'])
        self.ping_name.pack(side=tk.LEFT, padx=(0, 15))
        
        tk.Button(add_frame, text="Add", bg=COLORS['accent'], fg='white',
                 padx=20, pady=6, command=self._add_ping, relief=tk.FLAT, bd=0,
                 activebackground=COLORS['accent_hover']).pack(side=tk.LEFT, padx=(0, 8))
        tk.Button(add_frame, text="Remove All", bg=COLORS['error'], fg='white',
                 padx=20, pady=6, command=self._remove_all_ping, relief=tk.FLAT, bd=0,
                 activebackground='#e74c3c').pack(side=tk.LEFT)
        
        # Listbox
        list_frame = tk.LabelFrame(self.content, text="Saved Hosts", bg=COLORS['card'], 
                                   fg=COLORS['text'], font=('Segoe UI', 9, 'bold'),
                                   labelanchor='nw', bd=1, bg=COLORS['card'])
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.ping_list = tk.Listbox(list_frame, bg=COLORS['bg'], fg=COLORS['text'], 
                                    selectbackground=COLORS['accent'], font=('Consolas', 9),
                                    bd=0, highlightthickness=0)
        self.ping_list.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        btn_frame = tk.Frame(list_frame, bg=COLORS['card'])
        btn_frame.pack(fill=tk.X, padx=8, pady=(0, 8))
        tk.Button(btn_frame, text="▶ Ping Selected", bg=COLORS['success'], fg='white',
                 padx=15, pady=6, command=self._ping_selected, relief=tk.FLAT, bd=0,
                 activebackground='#2ea043').pack(side=tk.LEFT, padx=(0, 8))
        tk.Button(btn_frame, text="❌ Remove Selected", bg=COLORS['error'], fg='white',
                 padx=15, pady=6, command=self._remove_selected_ping, relief=tk.FLAT, bd=0,
                 activebackground='#e74c3c').pack(side=tk.LEFT)
        
        self._refresh_ping_list()
    
    def _add_ping(self):
        ip = self.ping_ip.get().strip()
        name = self.ping_name.get().strip()
        if not ip:
            messagebox.showwarning("Error", "Enter IP!")
            return
        if not name:
            name = ip
        self.ping_hosts.append({'ip': ip, 'name': name})
        self._refresh_ping_list()
        self.ping_ip.delete(0, tk.END)
        self.ping_name.delete(0, tk.END)
        self._save_config()
        self.status.config(text=f"Added {name}")
    
    def _ping_selected(self):
        sel = self.ping_list.curselection()
        if sel:
            host = self.ping_hosts[sel[0]]
            open_cmd(f'ping {host["ip"]} -t' if IS_WINDOWS else f'ping {host["ip"]}')
            self.status.config(text=f"Pinging {host['name']}")
    
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
        frame.pack(fill=tk.X, pady=40)
        
        tk.Label(frame, text="Target IP / Hostname:", bg=COLORS['bg'], 
                fg=COLORS['text'], font=('Segoe UI', 11)).pack(side=tk.LEFT, padx=5)
        self.trace_ip = tk.Entry(frame, bg=COLORS['card'], fg=COLORS['text'], 
                                 width=30, font=('Consolas', 11), relief=tk.FLAT, bd=1,
                                 insertbackground=COLORS['accent'])
        self.trace_ip.pack(side=tk.LEFT, padx=5)
        self.trace_ip.insert(0, "8.8.8.8")
        
        tk.Button(frame, text="Trace Route", bg=COLORS['accent'], fg='white',
                 font=('Segoe UI', 10, 'bold'), padx=20, pady=8,
                 command=self._do_trace, relief=tk.FLAT, bd=0,
                 activebackground=COLORS['accent_hover']).pack(side=tk.LEFT, padx=10)
    
    def _do_trace(self):
        ip = self.trace_ip.get().strip()
        if ip:
            cmd = f'tracert {ip}' if IS_WINDOWS else f'traceroute {ip}'
            open_cmd(cmd)
            self.status.config(text=f"Tracing {ip}")
    
    # ==================== VNC ====================
    def _show_vnc(self):
        self._clear()
        
        frame = tk.Frame(self.content, bg=COLORS['bg'])
        frame.pack(fill=tk.X, pady=40)
        
        tk.Label(frame, text="IP Address:", bg=COLORS['bg'], fg=COLORS['text'], 
                font=('Segoe UI', 11)).pack(side=tk.LEFT, padx=5)
        self.vnc_ip = tk.Entry(frame, bg=COLORS['card'], fg=COLORS['text'], 
                               width=20, font=('Consolas', 11), relief=tk.FLAT, bd=1,
                               insertbackground=COLORS['accent'])
        self.vnc_ip.pack(side=tk.LEFT, padx=5)
        self.vnc_ip.insert(0, "192.168.1.10")
        
        tk.Label(frame, text="Port:", bg=COLORS['bg'], fg=COLORS['text']).pack(side=tk.LEFT, padx=5)
        self.vnc_port = tk.Entry(frame, bg=COLORS['card'], fg=COLORS['text'], 
                                 width=8, font=('Consolas', 11), relief=tk.FLAT, bd=1,
                                 insertbackground=COLORS['accent'])
        self.vnc_port.pack(side=tk.LEFT, padx=5)
        self.vnc_port.insert(0, "5900")
        
        tk.Button(frame, text="Connect VNC", bg=COLORS['accent'], fg='white',
                 font=('Segoe UI', 10, 'bold'), padx=20, pady=8,
                 command=self._vnc_connect_from_input, relief=tk.FLAT, bd=0,
                 activebackground=COLORS['accent_hover']).pack(side=tk.LEFT, padx=10)
    
    def _vnc_connect_from_input(self):
        ip = self.vnc_ip.get().strip()
        port = self.vnc_port.get().strip()
        self._vnc_connect(ip, port)
    
    def _vnc_connect(self, ip, port="5900"):
        if not ip:
            messagebox.showerror("Error", "Enter IP address!")
            return
        
        self.status.config(text=f"Connecting VNC to {ip}:{port}...")
        
        def do():
            try:
                if IS_WINDOWS:
                    vnc_paths = [
                        r"C:\Program Files\RealVNC\VNC Viewer\vncviewer.exe",
                        r"C:\Program Files\TightVNC\tightvncviewer.exe",
                        r"C:\Program Files\UltraVNC\vncviewer.exe",
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
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Cannot launch VNC: {e}"))
        
        threading.Thread(target=do, daemon=True).start()
    
    # ==================== GROUPS ====================
    def _show_groups(self):
        self._clear()
        
        top = tk.Frame(self.content, bg=COLORS['bg'])
        top.pack(fill=tk.X, pady=(0, 15))
        
        self.new_group_name = tk.Entry(top, bg=COLORS['card'], fg=COLORS['text'], 
                                       width=20, font=('Segoe UI', 10), relief=tk.FLAT, bd=1,
                                       insertbackground=COLORS['accent'])
        self.new_group_name.pack(side=tk.LEFT, padx=0)
        tk.Button(top, text="Create Group", bg=COLORS['accent'], fg='white',
                 padx=20, pady=6, command=self._create_group, relief=tk.FLAT, bd=0,
                 activebackground=COLORS['accent_hover']).pack(side=tk.LEFT, padx=(8, 0))
        
        # Lists
        list_frame = tk.Frame(self.content, bg=COLORS['bg'])
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        left = tk.LabelFrame(list_frame, text="Groups", bg=COLORS['card'], fg=COLORS['text'],
                            font=('Segoe UI', 9, 'bold'), labelanchor='nw', bd=1)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        self.groups_list = tk.Listbox(left, bg=COLORS['bg'], fg=COLORS['text'], 
                                      selectbackground=COLORS['accent'], font=('Segoe UI', 9),
                                      bd=0, highlightthickness=0)
        self.groups_list.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self.groups_list.bind('<<ListboxSelect>>', self._on_group_select)
        
        right = tk.LabelFrame(list_frame, text="IPs in Group", bg=COLORS['card'], fg=COLORS['text'],
                             font=('Segoe UI', 9, 'bold'), labelanchor='nw', bd=1)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.ips_list = tk.Listbox(right, bg=COLORS['bg'], fg=COLORS['text'], 
                                   selectbackground=COLORS['accent'], font=('Segoe UI', 9),
                                   bd=0, highlightthickness=0)
        self.ips_list.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        btn_frame = tk.Frame(self.content, bg=COLORS['bg'])
        btn_frame.pack(fill=tk.X, pady=(8, 0))
        tk.Button(btn_frame, text="Add IP", bg=COLORS['accent'], fg='white',
                 padx=15, pady=6, command=self._add_ip_group, relief=tk.FLAT, bd=0,
                 activebackground=COLORS['accent_hover']).pack(side=tk.LEFT, padx=(0, 8))
        tk.Button(btn_frame, text="Remove IP", bg=COLORS['error'], fg='white',
                 padx=15, pady=6, command=self._remove_ip_group, relief=tk.FLAT, bd=0,
                 activebackground='#e74c3c').pack(side=tk.LEFT, padx=(0, 8))
        tk.Button(btn_frame, text="Load to Ping", bg=COLORS['success'], fg='white',
                 padx=15, pady=6, command=self._load_group_to_ping, relief=tk.FLAT, bd=0,
                 activebackground='#2ea043').pack(side=tk.LEFT)
        
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
        name = self.new_group_name.get().strip()
        if name and name not in self.groups:
            self.groups[name] = []
            self._refresh_groups()
            self._save_config()
            self.new_group_name.delete(0, tk.END)
            self.status.config(text=f"Created group '{name}'")
    
    def _add_ip_group(self):
        sel = self.groups_list.curselection()
        if not sel:
            messagebox.showwarning("Warning", "Select a group first!")
            return
        name = self.groups_list.get(sel[0]).split(' (')[0]
        ip = simpledialog.askstring("Add IP", "Enter IP address:")
        if ip and ip not in self.groups[name]:
            self.groups[name].append(ip)
            self._refresh_groups()
            self._save_config()
            self._on_group_select(None)
            self.status.config(text=f"Added {ip} to {name}")
    
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
    
    def _load_group_to_ping(self):
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
        self.status.config(text=f"Loaded {len(ips)} hosts to Ping")
    
    # ==================== BACKUP ====================
    def _show_backup(self):
        self._clear()
        
        frame = tk.Frame(self.content, bg=COLORS['bg'])
        frame.pack(expand=True)
        
        tk.Button(frame, text="📤 Export Configuration", bg=COLORS['accent'], fg='white',
                 font=('Segoe UI', 11), padx=40, pady=12, command=self._export,
                 relief=tk.FLAT, bd=0, activebackground=COLORS['accent_hover']).pack(pady=8)
        tk.Button(frame, text="📥 Import Configuration", bg=COLORS['accent'], fg='white',
                 font=('Segoe UI', 11), padx=40, pady=12, command=self._import,
                 relief=tk.FLAT, bd=0, activebackground=COLORS['accent_hover']).pack(pady=8)
        tk.Button(frame, text="🔄 Reset All Settings", bg=COLORS['error'], fg='white',
                 font=('Segoe UI', 11), padx=40, pady=12, command=self._reset,
                 relief=tk.FLAT, bd=0, activebackground='#e74c3c').pack(pady=8)
    
    def _export(self):
        f = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if f:
            data = {'ping_hosts': self.ping_hosts, 'groups': self.groups}
            with open(f, 'w') as fp:
                json.dump(data, fp, indent=2)
            messagebox.showinfo("Success", "Configuration exported!")
    
    def _import(self):
        f = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if f:
            try:
                with open(f, 'r') as fp:
                    data = json.load(fp)
                    self.ping_hosts = data.get('ping_hosts', [])
                    self.groups = data.get('groups', {"Default": []})
                    self._refresh_ping_list()
                    self._refresh_groups()
                    self._save_config()
                messagebox.showinfo("Success", "Configuration imported!")
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def _reset(self):
        if messagebox.askyesno("Confirm", "Reset all settings?"):
            self.ping_hosts.clear()
            self.groups = {"Default": []}
            self._refresh_ping_list()
            self._refresh_groups()
            self._save_config()
            messagebox.showinfo("Success", "All settings reset!")
    
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
