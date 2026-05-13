#!/usr/bin/env python3
"""
NETWORK SCANNER PRO - COMPLETE EDITION
9 Functions: Ping | Trace | Port Scan | Scan IP | Loop Detect | Groups | AI | VNC | Backup
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

# ============================================================================
# MÀU SẮC ĐƠN GIẢN
# ============================================================================
COLORS = {
    'bg': '#1E1E1E',
    'sidebar': '#2D2D2D',
    'card': '#252526',
    'accent': '#007ACC',
    'text': '#FFFFFF',
    'text_sec': '#CCCCCC',
    'success': '#6A9955',
    'error': '#F48771',
}

# ============================================================================
# HÀM MỞ CMD
# ============================================================================
def open_cmd(command):
    if IS_WINDOWS:
        subprocess.Popen(f'start cmd /k "{command}"', shell=True)
    else:
        subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', f'{command}; exec bash'])


# ============================================================================
# MAIN APP
# ============================================================================
class NetScanner:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Network Scanner Pro - Complete Edition")
        self.root.geometry("1300x750")
        self.root.configure(bg=COLORS['bg'])
        
        # Data
        self.ping_hosts = []  # Lưu IP ping
        self.groups = {"Default": []}
        self.config_file = Path.home() / ".net_scanner.json"
        
        self._create_ui()
        self._load_config()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _create_ui(self):
        # Header
        header = tk.Frame(self.root, bg=COLORS['accent'], height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="🌐 NETWORK SCANNER PRO", bg=COLORS['accent'], 
                fg='white', font=('Segoe UI', 14, 'bold')).pack(side=tk.LEFT, padx=20)
        self.status = tk.Label(header, text="✓ Ready", bg=COLORS['accent'], fg='white')
        self.status.pack(side=tk.RIGHT, padx=20)
        
        # Main
        main = tk.Frame(self.root, bg=COLORS['bg'])
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Sidebar
        sidebar = tk.Frame(main, bg=COLORS['sidebar'], width=120)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        sidebar.pack_propagate(False)
        
        buttons = [
            ("🔍 PING", self._show_ping),
            ("🗺️ TRACEROUTE", self._show_trace),
            ("🔌 PORT SCAN", self._show_port_scan),
            ("📡 SCAN IP", self._show_ip_scan),
            ("🔄 LOOP DETECT", self._show_loop_detect),
            ("📋 GROUPS", self._show_groups),
            ("🤖 AI", self._show_ai),
            ("🖥️ VNC", self._show_vnc),
            ("💾 BACKUP", self._show_backup),
        ]
        
        for text, cmd in buttons:
            btn = tk.Button(sidebar, text=text, bg=COLORS['sidebar'], fg=COLORS['text'],
                          font=('Segoe UI', 9), relief=tk.FLAT, command=cmd, padx=10, pady=10)
            btn.pack(fill=tk.X, pady=2, padx=5)
            btn.bind('<Enter>', lambda e, b=btn: b.config(bg=COLORS['accent']))
            btn.bind('<Leave>', lambda e, b=btn: b.config(bg=COLORS['sidebar']))
        
        # Content
        self.content = tk.Frame(main, bg=COLORS['bg'])
        self.content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self._show_welcome()
    
    def _show_welcome(self):
        self._clear_content()
        tk.Label(self.content, text="NETWORK SCANNER PRO", bg=COLORS['bg'], 
                fg=COLORS['accent'], font=('Segoe UI', 24, 'bold')).pack(expand=True, pady=50)
        tk.Label(self.content, text="Chọn chức năng từ thanh bên trái", bg=COLORS['bg'], 
                fg=COLORS['text_sec'], font=('Segoe UI', 12)).pack()
    
    def _clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()
    
    # ==================== 1. PING (CÓ LƯU IP) ====================
    def _show_ping(self):
        self._clear_content()
        
        tk.Label(self.content, text="🔍 PING MONITOR", bg=COLORS['bg'], 
                fg=COLORS['accent'], font=('Segoe UI', 16, 'bold')).pack(anchor=tk.W, padx=20, pady=20)
        
        # Add host
        frame = tk.Frame(self.content, bg=COLORS['bg'])
        frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(frame, text="IP:", bg=COLORS['bg'], fg=COLORS['text']).pack(side=tk.LEFT, padx=5)
        self.ping_ip = tk.Entry(frame, bg=COLORS['card'], fg=COLORS['text'], width=18)
        self.ping_ip.pack(side=tk.LEFT, padx=5)
        
        tk.Label(frame, text="Name:", bg=COLORS['bg'], fg=COLORS['text']).pack(side=tk.LEFT, padx=5)
        self.ping_name = tk.Entry(frame, bg=COLORS['card'], fg=COLORS['text'], width=15)
        self.ping_name.pack(side=tk.LEFT, padx=5)
        
        tk.Button(frame, text="➕ Add", bg=COLORS['accent'], fg='white', command=self._add_ping_host).pack(side=tk.LEFT, padx=10)
        tk.Button(frame, text="🗑️ Remove All", bg=COLORS['error'], fg='white', command=self._remove_all_ping).pack(side=tk.LEFT)
        
        # List saved hosts
        list_frame = tk.LabelFrame(self.content, text="Saved Hosts", bg=COLORS['card'], fg=COLORS['text'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.ping_listbox = tk.Listbox(list_frame, bg=COLORS['bg'], fg=COLORS['text'], 
                                       selectbackground=COLORS['accent'], height=8)
        self.ping_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Buttons for saved hosts
        btn_frame = tk.Frame(list_frame, bg=COLORS['card'])
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Button(btn_frame, text="▶ Ping Selected", bg=COLORS['success'], fg='white', 
                 command=self._ping_selected).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="❌ Remove Selected", bg=COLORS['error'], fg='white', 
                 command=self._remove_selected_ping).pack(side=tk.LEFT, padx=5)
        
        # Update list
        self._refresh_ping_list()
    
    def _add_ping_host(self):
        ip = self.ping_ip.get().strip()
        name = self.ping_name.get().strip()
        if not ip:
            messagebox.showwarning("Lỗi", "Nhập IP!")
            return
        if not name:
            name = ip
        self.ping_hosts.append({'ip': ip, 'name': name})
        self._refresh_ping_list()
        self.ping_ip.delete(0, tk.END)
        self.ping_name.delete(0, tk.END)
        self._save_config()
        self.status.config(text=f"✓ Đã thêm {name} ({ip})")
    
    def _ping_selected(self):
        sel = self.ping_listbox.curselection()
        if not sel:
            messagebox.showwarning("Lỗi", "Chọn host cần ping!")
            return
        host = self.ping_hosts[sel[0]]
        open_cmd(f'ping {host["ip"]} -t' if IS_WINDOWS else f'ping {host["ip"]}')
        self.status.config(text=f"✓ Đã mở CMD ping {host['name']}")
    
    def _remove_selected_ping(self):
        sel = self.ping_listbox.curselection()
        if sel:
            del self.ping_hosts[sel[0]]
            self._refresh_ping_list()
            self._save_config()
    
    def _remove_all_ping(self):
        self.ping_hosts.clear()
        self._refresh_ping_list()
        self._save_config()
    
    def _refresh_ping_list(self):
        self.ping_listbox.delete(0, tk.END)
        for h in self.ping_hosts:
            self.ping_listbox.insert(tk.END, f"{h['name']} ({h['ip']})")
    
    # ==================== 2. TRACEROUTE ====================
    def _show_trace(self):
        self._clear_content()
        
        tk.Label(self.content, text="🗺️ TRACEROUTE", bg=COLORS['bg'], 
                fg=COLORS['accent'], font=('Segoe UI', 16, 'bold')).pack(anchor=tk.W, padx=20, pady=20)
        
        frame = tk.Frame(self.content, bg=COLORS['bg'])
        frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(frame, text="Target:", bg=COLORS['bg'], fg=COLORS['text']).pack(side=tk.LEFT, padx=5)
        self.trace_ip = tk.Entry(frame, bg=COLORS['card'], fg=COLORS['text'], width=25)
        self.trace_ip.pack(side=tk.LEFT, padx=5)
        self.trace_ip.insert(0, "8.8.8.8")
        
        tk.Button(frame, text="Trace", bg=COLORS['accent'], fg='white', command=self._run_trace).pack(side=tk.LEFT, padx=10)
    
    def _run_trace(self):
        ip = self.trace_ip.get().strip()
        if ip:
            cmd = f'tracert {ip}' if IS_WINDOWS else f'traceroute {ip}'
            open_cmd(cmd)
            self.status.config(text=f"✓ Đã mở CMD trace {ip}")
    
    # ==================== 3. PORT SCAN ====================
    def _show_port_scan(self):
        self._clear_content()
        
        tk.Label(self.content, text="🔌 PORT SCANNER", bg=COLORS['bg'], 
                fg=COLORS['accent'], font=('Segoe UI', 16, 'bold')).pack(anchor=tk.W, padx=20, pady=20)
        
        frame = tk.Frame(self.content, bg=COLORS['bg'])
        frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(frame, text="Target IP:", bg=COLORS['bg'], fg=COLORS['text']).pack(side=tk.LEFT, padx=5)
        self.port_target = tk.Entry(frame, bg=COLORS['card'], fg=COLORS['text'], width=18)
        self.port_target.pack(side=tk.LEFT, padx=5)
        self.port_target.insert(0, "127.0.0.1")
        
        tk.Label(frame, text="Ports:", bg=COLORS['bg'], fg=COLORS['text']).pack(side=tk.LEFT, padx=5)
        self.port_input = tk.Entry(frame, bg=COLORS['card'], fg=COLORS['text'], width=30)
        self.port_input.pack(side=tk.LEFT, padx=5)
        self.port_input.insert(0, "22,80,443,3306,5432,8080")
        
        tk.Button(frame, text="Scan", bg=COLORS['accent'], fg='white', command=self._scan_ports).pack(side=tk.LEFT, padx=10)
        
        self.port_tree = ttk.Treeview(self.content, columns=('Port', 'Status', 'Service'), height=18)
        self.port_tree.heading('#0', text='')
        self.port_tree.heading('Port', text='Port')
        self.port_tree.heading('Status', text='Status')
        self.port_tree.heading('Service', text='Service')
        self.port_tree.column('#0', width=0)
        self.port_tree.column('Port', width=100)
        self.port_tree.column('Status', width=100)
        self.port_tree.column('Service', width=200)
        self.port_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', background=COLORS['card'], foreground=COLORS['text'], fieldbackground=COLORS['card'])
        style.configure('Treeview.Heading', background=COLORS['sidebar'], foreground=COLORS['text'])
    
    def _scan_ports(self):
        target = self.port_target.get().strip()
        ports_str = self.port_input.get().strip()
        if not target or not ports_str:
            return
        
        ports = []
        for p in ports_str.split(','):
            p = p.strip()
            if '-' in p:
                s, e = p.split('-')
                ports.extend(range(int(s), int(e)+1))
            else:
                try:
                    ports.append(int(p))
                except:
                    pass
        
        self.port_tree.delete(*self.port_tree.get_children())
        services = {22:'SSH', 80:'HTTP', 443:'HTTPS', 3306:'MySQL', 5432:'PostgreSQL', 
                   3389:'RDP', 5900:'VNC', 8080:'HTTP-Alt', 8443:'HTTPS-Alt', 25:'SMTP', 53:'DNS'}
        self.status.config(text=f"🔍 Scanning {len(ports)} ports on {target}...")
        
        def check(p):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.3)
                ok = s.connect_ex((target, p)) == 0
                s.close()
                if ok:
                    self.root.after(0, lambda x=p: self.port_tree.insert('', tk.END, values=(x, "OPEN", services.get(x, "Unknown"))))
            except:
                pass
        
        def do():
            with ThreadPoolExecutor(max_workers=50) as ex:
                ex.map(check, ports)
            self.root.after(0, lambda: self.status.config(text="✅ Scan completed"))
        
        threading.Thread(target=do, daemon=True).start()
    
    # ==================== 4. SCAN IP (CÓ HIỂN THỊ) ====================
    def _show_ip_scan(self):
        self._clear_content()
        
        tk.Label(self.content, text="📡 SCAN IP (CIDR)", bg=COLORS['bg'], 
                fg=COLORS['accent'], font=('Segoe UI', 16, 'bold')).pack(anchor=tk.W, padx=20, pady=20)
        
        frame = tk.Frame(self.content, bg=COLORS['bg'])
        frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(frame, text="CIDR:", bg=COLORS['bg'], fg=COLORS['text']).pack(side=tk.LEFT, padx=5)
        self.cidr_input = tk.Entry(frame, bg=COLORS['card'], fg=COLORS['text'], width=25)
        self.cidr_input.pack(side=tk.LEFT, padx=5)
        self.cidr_input.insert(0, "192.168.1.0/24")
        
        tk.Button(frame, text="Scan Network", bg=COLORS['accent'], fg='white', command=self._scan_network).pack(side=tk.LEFT, padx=10)
        
        self.scan_tree = ttk.Treeview(self.content, columns=('IP', 'Status', 'MAC'), height=18)
        self.scan_tree.heading('#0', text='')
        self.scan_tree.heading('IP', text='IP Address')
        self.scan_tree.heading('Status', text='Status')
        self.scan_tree.heading('MAC', text='MAC Address')
        self.scan_tree.column('#0', width=0)
        self.scan_tree.column('IP', width=150)
        self.scan_tree.column('Status', width=100)
        self.scan_tree.column('MAC', width=180)
        self.scan_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    def _scan_network(self):
        cidr = self.cidr_input.get().strip()
        if not cidr:
            return
        self.scan_tree.delete(*self.scan_tree.get_children())
        self.status.config(text=f"🔍 Scanning {cidr}...")
        
        def do():
            try:
                net = ipaddress.ip_network(cidr, strict=False)
                results = []
                
                def ping_ip(ip):
                    try:
                        param = '-n' if IS_WINDOWS else '-c'
                        subprocess.check_output(['ping', param, '1', '-W', '1', str(ip)], stderr=subprocess.DEVNULL, timeout=1)
                        mac = self._get_mac(str(ip))
                        results.append((str(ip), mac))
                    except:
                        pass
                
                with ThreadPoolExecutor(max_workers=50) as ex:
                    ex.map(ping_ip, net.hosts())
                
                def update():
                    for ip, mac in results:
                        self.scan_tree.insert('', tk.END, values=(ip, "🟢 ONLINE", mac))
                    self.status.config(text=f"✅ Scan completed - Found {len(results)} hosts")
                self.root.after(0, update)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        
        threading.Thread(target=do, daemon=True).start()
    
    def _get_mac(self, ip):
        try:
            cmd = ['arp', '-a', ip] if IS_WINDOWS else ['arp', '-n', ip]
            out = subprocess.check_output(cmd, universal_newlines=True, timeout=3)
            mac = re.search(r'([0-9a-fA-F]{2}[:-]){5}([0-9a-fA-F]{2})', out, re.IGNORECASE)
            return mac.group(0).upper() if mac else "Unknown"
        except:
            return "Unknown"
    
    # ==================== 5. LOOP DETECTION ====================
    def _show_loop_detect(self):
        self._clear_content()
        
        tk.Label(self.content, text="🔄 LOOP DETECTION", bg=COLORS['bg'], 
                fg=COLORS['accent'], font=('Segoe UI', 16, 'bold')).pack(anchor=tk.W, padx=20, pady=20)
        
        tk.Button(self.content, text="Detect Loops", bg=COLORS['accent'], fg='white', 
                 command=self._detect_loops, padx=20, pady=10).pack(anchor=tk.W, padx=20)
        
        self.loop_text = tk.Text(self.content, bg=COLORS['card'], fg=COLORS['text'], font=('Consolas', 9))
        self.loop_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    def _detect_loops(self):
        self.loop_text.delete("1.0", tk.END)
        self.loop_text.insert("1.0", "🔍 Analyzing ARP table...\n\n")
        self.status.config(text="🔍 Detecting loops...")
        
        def do():
            try:
                cmd = ['arp', '-a'] if IS_WINDOWS else ['arp', '-n']
                out = subprocess.check_output(cmd, universal_newlines=True, timeout=10)
                macs = defaultdict(list)
                for line in out.split('\n'):
                    ips = re.findall(r'(\d+\.\d+\.\d+\.\d+)', line)
                    m = re.search(r'([0-9a-fA-F]{2}[:-]){5}([0-9a-fA-F]{2})', line, re.IGNORECASE)
                    if ips and m:
                        mac = m.group(0).upper()
                        macs[mac].append(ips[0])
                
                dup = {mac: ips for mac, ips in macs.items() if len(ips) > 1}
                
                def update():
                    self.loop_text.insert(tk.END, f"📊 Total ARP entries: {len(macs)}\n")
                    self.loop_text.insert(tk.END, f"📊 Unique MACs: {len(set(macs.keys()))}\n\n")
                    if dup:
                        self.loop_text.insert(tk.END, "⚠️ WARNING: Duplicate MAC addresses found!\n\n")
                        for mac, ips in dup.items():
                            self.loop_text.insert(tk.END, f"🔴 MAC: {mac}\n   IPs: {', '.join(ips)}\n\n")
                        self.loop_text.insert(tk.END, "⚠️ SEVERITY: HIGH\n🔧 Action: Check switch STP configuration\n")
                    else:
                        self.loop_text.insert(tk.END, "✅ No duplicate MAC addresses found\n✅ SEVERITY: NONE\n")
                    self.status.config(text="✅ Detection completed")
                self.root.after(0, update)
            except Exception as e:
                self.root.after(0, lambda: self.loop_text.insert(tk.END, f"Error: {e}"))
        
        threading.Thread(target=do, daemon=True).start()
    
    # ==================== 6. GROUPS (CÓ LƯU IP) ====================
    def _show_groups(self):
        self._clear_content()
        
        tk.Label(self.content, text="📋 GROUP MANAGEMENT", bg=COLORS['bg'], 
                fg=COLORS['accent'], font=('Segoe UI', 16, 'bold')).pack(anchor=tk.W, padx=20, pady=20)
        
        # Create group
        frame = tk.Frame(self.content, bg=COLORS['bg'])
        frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.new_group = tk.Entry(frame, bg=COLORS['card'], fg=COLORS['text'], width=20)
        self.new_group.pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Create Group", bg=COLORS['accent'], fg='white', command=self._create_group).pack(side=tk.LEFT, padx=10)
        
        # Lists
        list_frame = tk.Frame(self.content, bg=COLORS['bg'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
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
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Button(btn_frame, text="➕ Add IP", bg=COLORS['accent'], fg='white', command=self._add_ip_group).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="❌ Remove IP", bg=COLORS['error'], fg='white', command=self._remove_ip_group).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="📋 Load to Ping", bg=COLORS['success'], fg='white', command=self._load_group_to_ping).pack(side=tk.LEFT, padx=5)
        
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
            self.status.config(text=f"✓ Created group '{name}'")
    
    def _add_ip_group(self):
        sel = self.groups_list.curselection()
        if not sel:
            messagebox.showwarning("Lỗi", "Chọn nhóm!")
            return
        name = self.groups_list.get(sel[0]).split(' (')[0]
        ip = simpledialog.askstring("Add IP", "Enter IP address:")
        if ip and ip not in self.groups[name]:
            self.groups[name].append(ip)
            self._refresh_groups()
            self._save_config()
            self._on_group_select(None)
            self.status.config(text=f"✓ Added {ip} to {name}")
    
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
            self._on_group_select(None)
            self._save_config()
    
    def _load_group_to_ping(self):
        sel = self.groups_list.curselection()
        if not sel:
            return
        name = self.groups_list.get(sel[0]).split(' (')[0]
        ips = self.groups.get(name, [])
        if not ips:
            messagebox.showwarning("Lỗi", "Nhóm rỗng!")
            return
        
        for ip in ips:
            if not any(h['ip'] == ip for h in self.ping_hosts):
                self.ping_hosts.append({'ip': ip, 'name': ip})
        self._refresh_ping_list()
        self._save_config()
        self.status.config(text=f"✓ Loaded {len(ips)} hosts to Ping tab")
    
    # ==================== 7. AI ====================
    def _show_ai(self):
        self._clear_content()
        
        tk.Label(self.content, text="🤖 AI ASSISTANT", bg=COLORS['bg'], 
                fg=COLORS['accent'], font=('Segoe UI', 16, 'bold')).pack(anchor=tk.W, padx=20, pady=20)
        
        self.chat = tk.Text(self.content, bg=COLORS['card'], fg=COLORS['text'], wrap=tk.WORD, height=15)
        self.chat.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        welcome = """🤖 AI NETWORK ASSISTANT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 Ask me:
  • "ping 8.8.8.8" - Check connectivity
  • "port scan" - Common ports
  • "slow network" - Troubleshooting
  • "packet loss" - Fix packet loss
  • "traceroute" - Network path
  • "my ip" - Your IP address

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
        self.chat.insert("1.0", welcome)
        
        input_frame = tk.Frame(self.content, bg=COLORS['bg'])
        input_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        self.ai_input = tk.Entry(input_frame, bg=COLORS['card'], fg=COLORS['text'])
        self.ai_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.ai_input.bind('<Return>', self._ask_ai)
        
        tk.Button(input_frame, text="Send", bg=COLORS['accent'], fg='white', command=self._ask_ai).pack(side=tk.RIGHT)
    
    def _ask_ai(self, event=None):
        q = self.ai_input.get().strip()
        if not q:
            return
        self.chat.insert(tk.END, f"\n👤 You: {q}\n")
        self.ai_input.delete(0, tk.END)
        
        low = q.lower()
        if 'ping' in low:
            ans = "📡 PING: ping -c 4 8.8.8.8\n✅ 0% loss = good connection"
        elif 'port' in low:
            ans = "🔌 COMMON PORTS:\n22=SSH, 80=HTTP, 443=HTTPS, 3306=MySQL, 5432=PostgreSQL, 3389=RDP, 5900=VNC"
        elif 'slow' in low or 'chậm' in low:
            ans = "🐌 SLOW NETWORK:\n1. Ping gateway\n2. Ping 8.8.8.8\n3. Traceroute"
        elif 'loss' in low or 'mất' in low:
            ans = "⚠️ PACKET LOSS:\n• Check cables\n• Check WiFi\n• Restart router"
        elif 'trace' in low:
            ans = "🗺️ TRACEROUTE: traceroute google.com\nShows network path"
        elif 'ip' in low:
            ans = f"📍 YOUR IP: {self._get_local_ip()}"
        else:
            ans = "💡 Try: ping, port scan, slow network, packet loss, traceroute, my ip"
        
        self.chat.insert(tk.END, f"🤖 AI: {ans}\n\n")
        self.chat.see(tk.END)
    
    def _get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    # ==================== 8. VNC (HOẠT ĐỘNG) ====================
    def _show_vnc(self):
        self._clear_content()
        
        tk.Label(self.content, text="🖥️ VNC CONNECTION", bg=COLORS['bg'], 
                fg=COLORS['accent'], font=('Segoe UI', 16, 'bold')).pack(anchor=tk.W, padx=20, pady=20)
        
        frame = tk.Frame(self.content, bg=COLORS['bg'])
        frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(frame, text="IP:", bg=COLORS['bg'], fg=COLORS['text']).pack(side=tk.LEFT, padx=5)
        self.vnc_ip = tk.Entry(frame, bg=COLORS['card'], fg=COLORS['text'], width=18)
        self.vnc_ip.pack(side=tk.LEFT, padx=5)
        self.vnc_ip.insert(0, "192.168.1.10")
        
        tk.Label(frame, text="Port:", bg=COLORS['bg'], fg=COLORS['text']).pack(side=tk.LEFT, padx=5)
        self.vnc_port = tk.Entry(frame, bg=COLORS['card'], fg=COLORS['text'], width=8)
        self.vnc_port.pack(side=tk.LEFT, padx=5)
        self.vnc_port.insert(0, "5900")
        
        tk.Label(frame, text="Password:", bg=COLORS['bg'], fg=COLORS['text']).pack(side=tk.LEFT, padx=5)
        self.vnc_pass = tk.Entry(frame, bg=COLORS['card'], fg=COLORS['text'], width=15, show="*")
        self.vnc_pass.pack(side=tk.LEFT, padx=5)
        
        tk.Button(frame, text="Connect VNC", bg=COLORS['accent'], fg='white', command=self._connect_vnc).pack(side=tk.LEFT, padx=10)
        
        self.vnc_status = tk.Text(self.content, bg=COLORS['card'], fg=COLORS['text'], height=4)
        self.vnc_status.pack(fill=tk.X, padx=20, pady=10)
    
    def _connect_vnc(self):
        ip = self.vnc_ip.get().strip()
        port = self.vnc_port.get().strip()
        password = self.vnc_pass.get().strip()
        
        if not ip:
            messagebox.showerror("Error", "Enter IP address!")
            return
        
        self.vnc_status.delete("1.0", tk.END)
        self.vnc_status.insert("1.0", f"🔄 Connecting to {ip}:{port}...\n")
        self.status.config(text=f"🔄 Connecting VNC to {ip}...")
        
        def do():
            try:
                # Test port
                s = socket.socket()
                s.settimeout(2)
                result = s.connect_ex((ip, int(port)))
                s.close()
                
                if result != 0:
                    self.root.after(0, lambda: self.vnc_status.insert(tk.END, f"❌ Port {port} closed or host offline\n"))
                    self.root.after(0, lambda: self.status.config(text="❌ VNC failed"))
                    return
                
                # Mở VNC Viewer
                if IS_WINDOWS:
                    # Thử nhiều đường dẫn
                    vnc_paths = [
                        r"C:\Program Files\RealVNC\VNC Viewer\vncviewer.exe",
                        r"C:\Program Files\TightVNC\tightvncviewer.exe",
                        r"C:\Program Files\UltraVNC\vncviewer.exe",
                        r"C:\Program Files (x86)\UltraVNC\vncviewer.exe",
                    ]
                    vnc_found = False
                    for path in vnc_paths:
                        if Path(path).exists():
                            cmd = f'"{path}" {ip}:{port}'
                            if password:
                                cmd += f' -password={password}'
                            subprocess.Popen(cmd, shell=True)
                            vnc_found = True
                            break
                    
                    if not vnc_found:
                        subprocess.Popen(f'start vncviewer {ip}:{port}', shell=True)
                else:
                    subprocess.Popen(['vncviewer', f'{ip}:{port}'])
                
                self.root.after(0, lambda: self.vnc_status.insert(tk.END, f"✅ VNC Viewer launched\n"))
                self.root.after(0, lambda: self.status.config(text=f"✅ VNC Viewer opened for {ip}"))
                
            except Exception as e:
                self.root.after(0, lambda: self.vnc_status.insert(tk.END, f"❌ Error: {e}\n"))
                self.root.after(0, lambda: self.status.config(text="❌ VNC failed"))
        
        threading.Thread(target=do, daemon=True).start()
    
    # ==================== 9. BACKUP ====================
    def _show_backup(self):
        self._clear_content()
        
        tk.Label(self.content, text="💾 BACKUP & RESTORE", bg=COLORS['bg'], 
                fg=COLORS['accent'], font=('Segoe UI', 16, 'bold')).pack(anchor=tk.W, padx=20, pady=20)
        
        frame = tk.Frame(self.content, bg=COLORS['bg'])
        frame.pack(expand=True)
        
        tk.Button(frame, text="📤 Export Configuration", bg=COLORS['accent'], fg='white', 
                 command=self._export, padx=30, pady=10).pack(pady=10)
        tk.Button(frame, text="📥 Import Configuration", bg=COLORS['accent'], fg='white', 
                 command=self._import, padx=30, pady=10).pack(pady=10)
        tk.Button(frame, text="🔄 Reset All", bg=COLORS['error'], fg='white', 
                 command=self._reset, padx=30, pady=10).pack(pady=10)
    
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


if __name__ == "__main__":
    app = NetScanner()
    app.run()
