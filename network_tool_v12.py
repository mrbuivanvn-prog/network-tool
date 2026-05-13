#!/usr/bin/env python3
"""
NETWORK SCANNER - Like Advanced IP Scanner
Features: Scan IP | Port Scan | Ping | Traceroute | VNC | Groups | Backup
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

SYSTEM = platform.system().lower()
IS_WINDOWS = SYSTEM == 'windows'

# Màu sắc đơn giản, chuyên nghiệp
COLORS = {
    'bg': '#1E1E1E',
    'sidebar': '#2D2D2D',
    'card': '#252526',
    'accent': '#007ACC',
    'text': '#FFFFFF',
    'text_sec': '#CCCCCC',
    'success': '#6A9955',
    'error': '#F48771',
    'online': '#6A9955',
    'offline': '#F48771',
}


class NetworkScanner:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Network Scanner Pro")
        self.root.geometry("1300x750")
        self.root.configure(bg=COLORS['bg'])
        
        # Dữ liệu
        self.ping_hosts = []
        self.groups = {"Default": []}
        self.config_file = Path.home() / ".net_scanner.json"
        
        self._create_ui()
        self._load_config()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _create_ui(self):
        # Header
        header = tk.Frame(self.root, bg=COLORS['accent'], height=45)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="Network Scanner Pro", bg=COLORS['accent'], 
                fg='white', font=('Segoe UI', 13, 'bold')).pack(side=tk.LEFT, padx=15)
        self.status = tk.Label(header, text="Ready", bg=COLORS['accent'], fg='white', font=('Segoe UI', 9))
        self.status.pack(side=tk.RIGHT, padx=15)
        
        # Main
        main = tk.Frame(self.root, bg=COLORS['bg'])
        main.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # Left panel
        left = tk.Frame(main, bg=COLORS['sidebar'], width=150)
        left.pack(side=tk.LEFT, fill=tk.Y)
        left.pack_propagate(False)
        
        # Nút chức năng
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
            btn = tk.Button(left, text=text, bg=COLORS['sidebar'], fg=COLORS['text'],
                          font=('Segoe UI', 10), relief=tk.FLAT, command=cmd,
                          anchor=tk.W, padx=15, pady=8)
            btn.pack(fill=tk.X)
            btn.bind('<Enter>', lambda e, b=btn: b.config(bg=COLORS['accent']))
            btn.bind('<Leave>', lambda e, b=btn: b.config(bg=COLORS['sidebar']))
        
        # Right content
        self.content = tk.Frame(main, bg=COLORS['bg'])
        self.content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Mặc định hiện Scan IP
        self._show_scan()
    
    def _clear(self):
        for w in self.content.winfo_children():
            w.destroy()
    
    # ==================== SCAN IP (NHƯ ADVANCED IP SCANNER) ====================
    def _show_scan(self):
        self._clear()
        
        # Toolbar
        toolbar = tk.Frame(self.content, bg=COLORS['bg'])
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(toolbar, text="IP Range:", bg=COLORS['bg'], fg=COLORS['text']).pack(side=tk.LEFT, padx=5)
        self.scan_range = tk.Entry(toolbar, bg=COLORS['card'], fg=COLORS['text'], width=20)
        self.scan_range.pack(side=tk.LEFT, padx=5)
        self.scan_range.insert(0, "192.168.1.1-192.168.1.254")
        
        tk.Label(toolbar, text="or CIDR:", bg=COLORS['bg'], fg=COLORS['text']).pack(side=tk.LEFT, padx=5)
        self.scan_cidr = tk.Entry(toolbar, bg=COLORS['card'], fg=COLORS['text'], width=18)
        self.scan_cidr.pack(side=tk.LEFT, padx=5)
        self.scan_cidr.insert(0, "192.168.1.0/24")
        
        tk.Button(toolbar, text="▶ Scan", bg=COLORS['accent'], fg='white', command=self._do_scan).pack(side=tk.LEFT, padx=10)
        
        # Treeview hiển thị kết quả
        columns = ('IP', 'Name', 'Status', 'MAC', 'Response')
        self.scan_tree = ttk.Treeview(self.content, columns=columns, height=22)
        self.scan_tree.heading('#0', text='')
        self.scan_tree.heading('IP', text='IP Address')
        self.scan_tree.heading('Name', text='Host Name')
        self.scan_tree.heading('Status', text='Status')
        self.scan_tree.heading('MAC', text='MAC Address')
        self.scan_tree.heading('Response', text='Response (ms)')
        
        self.scan_tree.column('#0', width=0)
        self.scan_tree.column('IP', width=140)
        self.scan_tree.column('Name', width=160)
        self.scan_tree.column('Status', width=80)
        self.scan_tree.column('MAC', width=160)
        self.scan_tree.column('Response', width=80)
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', background=COLORS['card'], foreground=COLORS['text'], fieldbackground=COLORS['card'])
        style.configure('Treeview.Heading', background=COLORS['sidebar'], foreground=COLORS['text'])
        
        self.scan_tree.pack(fill=tk.BOTH, expand=True)
        
        # Right-click menu
        self.scan_menu = tk.Menu(self.scan_tree, tearoff=0)
        self.scan_menu.add_command(label="Ping", command=self._scan_ping_selected)
        self.scan_menu.add_command(label="Traceroute", command=self._scan_trace_selected)
        self.scan_menu.add_command(label="VNC Connect", command=self._scan_vnc_selected)
        self.scan_menu.add_separator()
        self.scan_menu.add_command(label="Copy IP", command=self._copy_ip)
        self.scan_tree.bind("<Button-3>", self._show_scan_menu)
    
    def _do_scan(self):
        # Xóa kết quả cũ
        for item in self.scan_tree.get_children():
            self.scan_tree.delete(item)
        
        # Lấy range IP
        range_str = self.scan_range.get().strip()
        cidr_str = self.scan_cidr.get().strip()
        
        ips = []
        if range_str and '-' in range_str:
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
        elif cidr_str:
            try:
                net = ipaddress.ip_network(cidr_str, strict=False)
                ips = [str(ip) for ip in net.hosts()]
            except:
                pass
        
        if not ips:
            messagebox.showerror("Error", "Invalid IP range!")
            return
        
        self.status.config(text=f"Scanning {len(ips)} IPs...")
        
        def scan_ip(ip):
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
                    return (ip, hostname, "Online", mac, f"{response}ms")
                return None
            except:
                return None
        
        def do():
            results = []
            with ThreadPoolExecutor(max_workers=30) as ex:
                for r in ex.map(scan_ip, ips):
                    if r:
                        results.append(r)
            
            def update():
                for ip, name, status, mac, resp in results:
                    self.scan_tree.insert('', tk.END, values=(ip, name, status, mac, resp))
                self.status.config(text=f"Scan completed - Found {len(results)} devices")
            self.root.after(0, update)
        
        threading.Thread(target=do, daemon=True).start()
    
    def _get_mac(self, ip):
        try:
            cmd = ['arp', '-a', ip] if IS_WINDOWS else ['arp', '-n', ip]
            out = subprocess.check_output(cmd, universal_newlines=True, timeout=3)
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
    
    def _scan_trace_selected(self):
        sel = self.scan_tree.selection()
        if sel:
            ip = self.scan_tree.item(sel[0], 'values')[0]
            cmd = f'tracert {ip}' if IS_WINDOWS else f'traceroute {ip}'
            open_cmd(cmd)
    
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
        self.port_list = tk.Entry(toolbar, bg=COLORS['card'], fg=COLORS['text'], width=30)
        self.port_list.pack(side=tk.LEFT, padx=5)
        self.port_list.insert(0, "21,22,23,25,80,443,445,3389,5900,8080")
        
        tk.Button(toolbar, text="Scan", bg=COLORS['accent'], fg='white', command=self._do_port_scan).pack(side=tk.LEFT, padx=10)
        
        # Treeview kết quả
        self.port_tree = ttk.Treeview(self.content, columns=('Port', 'Status', 'Service'), height=22)
        self.port_tree.heading('#0', text='')
        self.port_tree.heading('Port', text='Port')
        self.port_tree.heading('Status', text='Status')
        self.port_tree.heading('Service', text='Service')
        self.port_tree.column('#0', width=0)
        self.port_tree.column('Port', width=100)
        self.port_tree.column('Status', width=80)
        self.port_tree.column('Service', width=150)
        self.port_tree.pack(fill=tk.BOTH, expand=True)
        
        # Service mapping
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
        
        # Xóa kết quả cũ
        for item in self.port_tree.get_children():
            self.port_tree.delete(item)
        
        self.status.config(text=f"Scanning {len(ports)} ports on {target}...")
        
        def check_port(p):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.2)
                result = s.connect_ex((target, p))
                s.close()
                if result == 0:
                    return p
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
                            values=(x, "OPEN", self.services.get(x, "Unknown"))))
            self.root.after(0, lambda: self.status.config(text=f"Scan completed - Found {len(open_ports)} open ports"))
        
        threading.Thread(target=do, daemon=True).start()
    
    # ==================== PING (CÓ LƯU IP) ====================
    def _show_ping(self):
        self._clear()
        
        # Add host
        add_frame = tk.Frame(self.content, bg=COLORS['bg'])
        add_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(add_frame, text="IP:", bg=COLORS['bg'], fg=COLORS['text']).pack(side=tk.LEFT, padx=5)
        self.ping_ip = tk.Entry(add_frame, bg=COLORS['card'], fg=COLORS['text'], width=18)
        self.ping_ip.pack(side=tk.LEFT, padx=5)
        
        tk.Label(add_frame, text="Name:", bg=COLORS['bg'], fg=COLORS['text']).pack(side=tk.LEFT, padx=5)
        self.ping_name = tk.Entry(add_frame, bg=COLORS['card'], fg=COLORS['text'], width=15)
        self.ping_name.pack(side=tk.LEFT, padx=5)
        
        tk.Button(add_frame, text="Add", bg=COLORS['accent'], fg='white', command=self._add_ping).pack(side=tk.LEFT, padx=10)
        tk.Button(add_frame, text="Remove All", bg=COLORS['error'], fg='white', command=self._remove_all_ping).pack(side=tk.LEFT)
        
        # List saved hosts
        list_frame = tk.LabelFrame(self.content, text="Saved Hosts", bg=COLORS['card'], fg=COLORS['text'])
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.ping_list = tk.Listbox(list_frame, bg=COLORS['bg'], fg=COLORS['text'], 
                                    selectbackground=COLORS['accent'], height=12)
        self.ping_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Buttons
        btn_frame = tk.Frame(list_frame, bg=COLORS['card'])
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Button(btn_frame, text="▶ Ping Selected", bg=COLORS['success'], fg='white', 
                 command=self._ping_selected).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="❌ Remove Selected", bg=COLORS['error'], fg='white', 
                 command=self._remove_selected_ping).pack(side=tk.LEFT, padx=5)
        
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
        frame.pack(fill=tk.X, pady=20)
        
        tk.Label(frame, text="Target:", bg=COLORS['bg'], fg=COLORS['text']).pack(side=tk.LEFT, padx=5)
        self.trace_ip = tk.Entry(frame, bg=COLORS['card'], fg=COLORS['text'], width=25)
        self.trace_ip.pack(side=tk.LEFT, padx=5)
        self.trace_ip.insert(0, "8.8.8.8")
        
        tk.Button(frame, text="Trace", bg=COLORS['accent'], fg='white', command=self._do_trace).pack(side=tk.LEFT, padx=10)
    
    def _do_trace(self):
        ip = self.trace_ip.get().strip()
        if ip:
            cmd = f'tracert {ip}' if IS_WINDOWS else f'traceroute {ip}'
            open_cmd(cmd)
    
    # ==================== VNC ====================
    def _show_vnc(self):
        self._clear()
        
        frame = tk.Frame(self.content, bg=COLORS['bg'])
        frame.pack(fill=tk.X, pady=20)
        
        tk.Label(frame, text="IP Address:", bg=COLORS['bg'], fg=COLORS['text']).pack(side=tk.LEFT, padx=5)
        self.vnc_ip = tk.Entry(frame, bg=COLORS['card'], fg=COLORS['text'], width=20)
        self.vnc_ip.pack(side=tk.LEFT, padx=5)
        self.vnc_ip.insert(0, "192.168.1.10")
        
        tk.Label(frame, text="Port:", bg=COLORS['bg'], fg=COLORS['text']).pack(side=tk.LEFT, padx=5)
        self.vnc_port = tk.Entry(frame, bg=COLORS['card'], fg=COLORS['text'], width=8)
        self.vnc_port.pack(side=tk.LEFT, padx=5)
        self.vnc_port.insert(0, "5900")
        
        tk.Button(frame, text="Connect VNC", bg=COLORS['accent'], fg='white', 
                 command=self._vnc_connect_from_input).pack(side=tk.LEFT, padx=10)
    
    def _vnc_connect_from_input(self):
        ip = self.vnc_ip.get().strip()
        port = self.vnc_port.get().strip()
        self._vnc_connect(ip, port)
    
    def _vnc_connect(self, ip, port="5900"):
        if not ip:
            messagebox.showerror("Error", "Enter IP address!")
            return
        
        self.status.config(text=f"Connecting VNC to {ip}...")
        
        def do():
            try:
                if IS_WINDOWS:
                    # Tìm VNC Viewer
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
                self.root.after(0, lambda: self.status.config(text=f"VNC Viewer launched for {ip}"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Cannot launch VNC: {e}"))
        
        threading.Thread(target=do, daemon=True).start()
    
    # ==================== GROUPS ====================
    def _show_groups(self):
        self._clear()
        
        # Create group
        top = tk.Frame(self.content, bg=COLORS['bg'])
        top.pack(fill=tk.X, pady=(0, 10))
        
        self.new_group_name = tk.Entry(top, bg=COLORS['card'], fg=COLORS['text'], width=20)
        self.new_group_name.pack(side=tk.LEFT, padx=5)
        tk.Button(top, text="Create Group", bg=COLORS['accent'], fg='white', 
                 command=self._create_group).pack(side=tk.LEFT, padx=10)
        
        # Lists
        list_frame = tk.Frame(self.content, bg=COLORS['bg'])
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Groups list
        left = tk.LabelFrame(list_frame, text="Groups", bg=COLORS['card'], fg=COLORS['text'])
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.groups_list = tk.Listbox(left, bg=COLORS['bg'], fg=COLORS['text'], selectbackground=COLORS['accent'])
        self.groups_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.groups_list.bind('<<ListboxSelect>>', self._on_group_select)
        
        # IPs list
        right = tk.LabelFrame(list_frame, text="IPs in Group", bg=COLORS['card'], fg=COLORS['text'])
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        self.ips_list = tk.Listbox(right, bg=COLORS['bg'], fg=COLORS['text'], selectbackground=COLORS['accent'])
        self.ips_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Buttons
        btn_frame = tk.Frame(self.content, bg=COLORS['bg'])
        btn_frame.pack(fill=tk.X, pady=10)
        tk.Button(btn_frame, text="Add IP", bg=COLORS['accent'], fg='white', command=self._add_ip_group).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Remove IP", bg=COLORS['error'], fg='white', command=self._remove_ip_group).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Load to Ping", bg=COLORS['success'], fg='white', command=self._load_group_to_ping).pack(side=tk.LEFT, padx=5)
        
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
        messagebox.showinfo("Success", f"Loaded {len(ips)} hosts to Ping tab")
    
    # ==================== BACKUP ====================
    def _show_backup(self):
        self._clear()
        
        frame = tk.Frame(self.content, bg=COLORS['bg'])
        frame.pack(expand=True, pady=50)
        
        tk.Button(frame, text="📤 Export Configuration", bg=COLORS['accent'], fg='white', 
                 command=self._export, padx=30, pady=10).pack(pady=10)
        tk.Button(frame, text="📥 Import Configuration", bg=COLORS['accent'], fg='white', 
                 command=self._import, padx=30, pady=10).pack(pady=10)
        tk.Button(frame, text="🔄 Reset All", bg=COLORS['error'], fg='white', 
                 command=self._reset, padx=30, pady=10).pack(pady=10)
    
    def _export(self):
        f = filedialog.asksaveasfilename(defaultextension=".json")
        if f:
            data = {'ping_hosts': self.ping_hosts, 'groups': self.groups}
            with open(f, 'w') as fp:
                json.dump(data, fp, indent=2)
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
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def _reset(self):
        if messagebox.askyesno("Confirm", "Reset all?"):
            self.ping_hosts.clear()
            self.groups = {"Default": []}
            self._refresh_ping_list()
            self._refresh_groups()
            self._save_config()
            messagebox.showinfo("Success", "Reset done!")
    
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
