#!/usr/bin/env python3
"""
Network Tool Ultimate v13.0 - Pure Tkinter (Easy Build)
Chạy mượt trên Windows & Linux, build EXE không lỗi
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

# ============================================================================
# CONFIGURATION
# ============================================================================
SYSTEM = platform.system().lower()
IS_WINDOWS = SYSTEM == 'windows'

print(f"✅ Running on: {SYSTEM.upper()}")

# ============================================================================
# COLORS - Modern Dark Theme
# ============================================================================
COLORS = {
    'bg': '#0A0E17',
    'sidebar': '#0F1322',
    'card': '#1A1F33',
    'card_hover': '#222842',
    'accent': '#00D4FF',
    'green': '#10B981',
    'red': '#EF4444',
    'orange': '#F59E0B',
    'purple': '#8B5CF6',
    'text': '#FFFFFF',
    'text_sec': '#8A99B8',
    'border': '#2A3166',
}

# ============================================================================
# NETWORK ADAPTER
# ============================================================================
class NetworkAdapter:
    @staticmethod
    def ping(host, count=4, timeout=2):
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
                'min': min(times) if times else None,
                'avg': sum(times) / len(times) if times else None,
                'max': max(times) if times else None,
            }
        except:
            return {'success': False, 'sent': 0, 'received': 0, 'loss_pct': 100, 'times': []}
    
    @staticmethod
    def traceroute(host):
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
            return f"Error: {str(e)}"
    
    @staticmethod
    def get_arp_table():
        try:
            cmd = ['arp', '-a'] if IS_WINDOWS else ['arp', '-n']
            result = subprocess.check_output(cmd, universal_newlines=True, timeout=10)
            arp = defaultdict(list)
            for line in result.split('\n'):
                if IS_WINDOWS:
                    m = re.search(r'(\d+\.\d+\.\d+\.\d+)\s+([0-9a-fA-F-]{17})', line)
                else:
                    m = re.search(r'(\d+\.\d+\.\d+\.\d+).*?([0-9a-fA-F:]{17})', line)
                if m:
                    arp[m.group(2).upper()].append(m.group(1))
            return dict(arp)
        except:
            return {}
    
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
# STYLED BUTTON
# ============================================================================
class StyledButton(tk.Button):
    def __init__(self, parent, text, command=None, bg=COLORS['accent'], width=12):
        super().__init__(parent, text=text, command=command, bg=bg, fg='white',
                        font=('Segoe UI', 10, 'bold'), relief=tk.FLAT, cursor='hand2',
                        width=width, padx=5, pady=5)
        self.default_bg = bg
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
    
    def _on_enter(self, e):
        self.config(bg=self._lighten(self.default_bg))
    
    def _on_leave(self, e):
        self.config(bg=self.default_bg)
    
    def _lighten(self, color):
        if color == COLORS['accent']:
            return '#33EEFF'
        if color == COLORS['green']:
            return '#2ECC71'
        if color == COLORS['red']:
            return '#E74C3C'
        return color


# ============================================================================
# HOST CARD
# ============================================================================
class HostCard(tk.Frame):
    def __init__(self, parent, ip, name, on_remove):
        super().__init__(parent, bg=COLORS['card'], relief=tk.RAISED, bd=1)
        self.ip = ip
        self.name = name
        self.on_remove = on_remove
        self.running = True
        self.queue = queue.Queue()
        
        self._create_ui()
        self._start_ping()
    
    def _create_ui(self):
        self.pack(side=tk.LEFT, padx=8, pady=8, fill=tk.BOTH, expand=True)
        
        # Header
        header = tk.Frame(self, bg=COLORS['card'])
        header.pack(fill=tk.X, padx=10, pady=8)
        
        self.led = tk.Label(header, text="●", bg=COLORS['card'], fg=COLORS['red'], font=('Arial', 14))
        self.led.pack(side=tk.LEFT)
        
        remove_btn = StyledButton(header, "✕", self._remove, COLORS['red'], 3)
        remove_btn.pack(side=tk.RIGHT)
        
        tk.Label(self, text=self.name, bg=COLORS['card'], fg=COLORS['text'],
                font=('Segoe UI', 12, 'bold')).pack()
        tk.Label(self, text=self.ip, bg=COLORS['card'], fg=COLORS['text_sec'],
                font=('Segoe UI', 9)).pack()
        
        tk.Frame(self, bg=COLORS['border'], height=1).pack(fill=tk.X, padx=10, pady=6)
        
        # Stats
        self.sent_lbl = tk.Label(self, text="📤 Sent: 0", bg=COLORS['card'], fg=COLORS['text_sec'])
        self.sent_lbl.pack(anchor=tk.W, padx=10)
        self.recv_lbl = tk.Label(self, text="📥 Recv: 0", bg=COLORS['card'], fg=COLORS['text_sec'])
        self.recv_lbl.pack(anchor=tk.W, padx=10)
        self.loss_lbl = tk.Label(self, text="⚠️ Loss: 0%", bg=COLORS['card'], fg=COLORS['text_sec'])
        self.loss_lbl.pack(anchor=tk.W, padx=10)
        self.time_lbl = tk.Label(self, text="⏱️ Time: ---", bg=COLORS['card'], fg=COLORS['text_sec'])
        self.time_lbl.pack(anchor=tk.W, padx=10)
        
        tk.Frame(self, bg=COLORS['border'], height=1).pack(fill=tk.X, padx=10, pady=6)
        
        # Remote buttons
        btn_frame = tk.Frame(self, bg=COLORS['card'])
        btn_frame.pack(fill=tk.X, padx=10, pady=6)
        
        for text, cmd, color in [("SSH", self._ssh, COLORS['accent']),
                                  ("HTTP", self._http, COLORS['green']),
                                  ("RDP", self._rdp, COLORS['purple']),
                                  ("VNC", self._vnc, COLORS['orange'])]:
            btn = tk.Button(btn_frame, text=text, bg=COLORS['sidebar'], fg='white',
                          font=('Segoe UI', 8), relief=tk.FLAT, command=cmd)
            btn.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
            btn.bind('<Enter>', lambda e, b=btn, c=color: b.config(bg=c))
            btn.bind('<Leave>', lambda e, b=btn: b.config(bg=COLORS['sidebar']))
    
    def _start_ping(self):
        def loop():
            while self.running:
                r = NetworkAdapter.ping(self.ip, count=1, timeout=2)
                self.queue.put(r)
                time.sleep(1)
        threading.Thread(target=loop, daemon=True).start()
        threading.Thread(target=self._update, daemon=True).start()
    
    def _update(self):
        while self.running:
            try:
                while not self.queue.empty():
                    r = self.queue.get_nowait()
                    if r['success']:
                        self.led.config(fg=COLORS['green'])
                        if r['avg']:
                            self.time_lbl.config(text=f"⏱️ Time: {r['avg']:.0f}ms", fg=COLORS['green'])
                    else:
                        self.led.config(fg=COLORS['red'])
                        self.time_lbl.config(text="⏱️ Time: ---", fg=COLORS['red'])
                    
                    self.sent_lbl.config(text=f"📤 Sent: {r['sent']}")
                    self.recv_lbl.config(text=f"📥 Recv: {r['received']}")
                    loss_color = COLORS['red'] if r['loss_pct'] > 0 else COLORS['green']
                    self.loss_lbl.config(text=f"⚠️ Loss: {r['loss_pct']:.0f}%", fg=loss_color)
            except:
                pass
            time.sleep(0.1)
    
    def _ssh(self):
        if IS_WINDOWS:
            subprocess.Popen(f'start ssh {self.ip}', shell=True)
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
            subprocess.Popen(f'vncviewer {self.ip}', shell=True)
    
    def _remove(self):
        self.running = False
        self.destroy()
        if self.on_remove:
            self.on_remove(self.ip)
    
    def stop(self):
        self.running = False


# ============================================================================
# AI ASSISTANT
# ============================================================================
class AIAssistant:
    def __init__(self, parent):
        self.parent = parent
        self._create_ui()
    
    def _create_ui(self):
        tk.Label(self.parent, text="🤖 AI NETWORK ASSISTANT", bg=COLORS['bg'], 
                fg=COLORS['accent'], font=('Segoe UI', 14, 'bold')).pack(pady=10)
        
        self.chat = tk.Text(self.parent, bg=COLORS['card'], fg=COLORS['text'],
                           font=('Segoe UI', 10), wrap=tk.WORD, height=18)
        self.chat.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        welcome = """💡 Ask me about network:

  • "ping 8.8.8.8" - Check connectivity
  • "port scan" - Common ports
  • "slow network" - Troubleshooting
  • "packet loss" - Fix packet loss
  • "traceroute" - Network path
  • "my ip" - Your IP address

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
        self.chat.insert("1.0", welcome)
        
        input_frame = tk.Frame(self.parent, bg=COLORS['bg'])
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.entry = tk.Entry(input_frame, bg=COLORS['card'], fg=COLORS['text'],
                             font=('Segoe UI', 10), relief=tk.FLAT)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.entry.bind('<Return>', self._ask)
        
        StyledButton(input_frame, "Send", self._ask, COLORS['green'], 8).pack(side=tk.RIGHT)
    
    def _ask(self, event=None):
        q = self.entry.get().strip()
        if not q:
            return
        self.chat.insert(tk.END, f"\n👤 You: {q}\n")
        self.entry.delete(0, tk.END)
        
        q_lower = q.lower()
        if 'ping' in q_lower:
            ans = "📡 PING: ping -c 4 8.8.8.8\n✅ 0% loss = good"
        elif 'port' in q_lower:
            ans = "🔌 COMMON PORTS:\n22=SSH, 80=HTTP, 443=HTTPS, 3306=MySQL"
        elif 'slow' in q_lower:
            ans = "🐌 SLOW NETWORK:\n1. Ping gateway\n2. Ping 8.8.8.8\n3. Traceroute"
        elif 'loss' in q_lower:
            ans = "⚠️ PACKET LOSS:\n• Check cables\n• Check WiFi\n• Restart router"
        elif 'trace' in q_lower:
            ans = "🗺️ TRACEROUTE: traceroute google.com"
        elif 'ip' in q_lower:
            ans = f"📍 YOUR IP: {NetworkAdapter.get_local_ip()}"
        else:
            ans = "💡 Try: ping, port scan, slow network, packet loss, traceroute, my ip"
        
        self.chat.insert(tk.END, f"🤖 AI: {ans}\n\n")
        self.chat.see(tk.END)


# ============================================================================
# MAIN APPLICATION
# ============================================================================
class NetToolApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"Network Tool Ultimate - {SYSTEM.upper()}")
        self.root.geometry("1400x800")
        self.root.configure(bg=COLORS['bg'])
        
        self.hosts = {}
        self.groups = {"Default": []}
        self.config_file = Path.home() / ".network_tool.json"
        
        self._load_config()
        self._create_ui()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _create_ui(self):
        # Header
        header = tk.Frame(self.root, bg=COLORS['accent'], height=55)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="🌐 NETWORK TOOL ULTIMATE", bg=COLORS['accent'],
                fg='white', font=('Segoe UI', 16, 'bold')).pack(side=tk.LEFT, padx=20)
        self.status = tk.Label(header, text="✓ READY", bg=COLORS['accent'], fg='white')
        self.status.pack(side=tk.RIGHT, padx=20)
        
        # Main
        main = tk.Frame(self.root, bg=COLORS['bg'])
        main.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Sidebar
        sidebar = tk.Frame(main, bg=COLORS['sidebar'], width=100)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        sidebar.pack_propagate(False)
        
        # Logo
        logo = tk.Frame(sidebar, bg=COLORS['accent'], height=80)
        logo.pack(fill=tk.X, pady=(10, 20))
        tk.Label(logo, text="🌐", bg=COLORS['accent'], fg='white',
                font=('Arial', 32)).pack(pady=15)
        
        # Nav buttons
        self.nav_btns = {}
        nav_items = [
            ("🔍 PING", self._show_ping),
            ("🗺️ TRACE", self._show_trace),
            ("🔌 PORTS", self._show_ports),
            ("📡 SCAN", self._show_scan),
            ("🔗 LOOP", self._show_loop),
            ("📊 GROUPS", self._show_groups),
            ("🤖 AI", self._show_ai),
            ("💾 BACKUP", self._show_backup),
        ]
        
        for text, cmd in nav_items:
            btn = tk.Button(sidebar, text=text, bg=COLORS['sidebar'], fg=COLORS['text_sec'],
                          font=('Segoe UI', 10), relief=tk.FLAT, cursor='hand2',
                          padx=10, pady=8, command=cmd)
            btn.pack(fill=tk.X, pady=4, padx=10)
            btn.bind('<Enter>', lambda e, b=btn: b.config(bg=COLORS['card']))
            btn.bind('<Leave>', lambda e, b=btn: b.config(bg=COLORS['sidebar']))
            self.nav_btns[text] = btn
        
        # Content
        self.content = tk.Frame(main, bg=COLORS['bg'])
        self.content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Pages
        self.pages = {}
        self._create_ping_page()
        self._create_trace_page()
        self._create_ports_page()
        self._create_scan_page()
        self._create_loop_page()
        self._create_groups_page()
        self._create_ai_page()
        self._create_backup_page()
        
        self._show_ping()
    
    # ============================================================
    # PING PAGE
    # ============================================================
    def _create_ping_page(self):
        page = tk.Frame(self.content, bg=COLORS['bg'])
        
        # Quick ping
        quick_frame = tk.Frame(page, bg=COLORS['card'], relief=tk.RAISED, bd=1)
        quick_frame.pack(fill=tk.X, padx=10, pady=10)
        tk.Label(quick_frame, text="⚡ QUICK PING", bg=COLORS['card'], fg=COLORS['accent'],
                font=('Segoe UI', 12, 'bold')).pack(anchor=tk.W, padx=15, pady=8)
        
        q_row = tk.Frame(quick_frame, bg=COLORS['card'])
        q_row.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        self.quick_entry = tk.Entry(q_row, bg=COLORS['bg'], fg=COLORS['text'],
                                   font=('Segoe UI', 11), width=25)
        self.quick_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.quick_entry.insert(0, "8.8.8.8")
        
        StyledButton(q_row, "Ping", self._quick_ping, COLORS['green'], 8).pack(side=tk.LEFT)
        
        self.quick_result = tk.Text(quick_frame, bg=COLORS['bg'], fg=COLORS['text'],
                                   height=4, font=('Consolas', 9))
        self.quick_result.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        # Add host
        add_frame = tk.Frame(page, bg=COLORS['card'], relief=tk.RAISED, bd=1)
        add_frame.pack(fill=tk.X, padx=10, pady=10)
        tk.Label(add_frame, text="➕ ADD HOST", bg=COLORS['card'], fg=COLORS['accent'],
                font=('Segoe UI', 12, 'bold')).pack(anchor=tk.W, padx=15, pady=8)
        
        a_row = tk.Frame(add_frame, bg=COLORS['card'])
        a_row.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        self.ping_ip = tk.Entry(a_row, bg=COLORS['bg'], fg=COLORS['text'], width=18)
        self.ping_ip.pack(side=tk.LEFT, padx=(0, 10))
        self.ping_ip.insert(0, "8.8.8.8")
        
        self.ping_name = tk.Entry(a_row, bg=COLORS['bg'], fg=COLORS['text'], width=18)
        self.ping_name.pack(side=tk.LEFT, padx=(0, 10))
        self.ping_name.insert(0, "Google DNS")
        
        StyledButton(a_row, "Add", self._add_host, COLORS['green'], 6).pack(side=tk.LEFT)
        StyledButton(a_row, "Stop All", self._stop_all, COLORS['red'], 8).pack(side=tk.LEFT, padx=(10, 0))
        
        # Hosts
        hosts_frame = tk.Frame(page, bg=COLORS['card'], relief=tk.RAISED, bd=1)
        hosts_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        tk.Label(hosts_frame, text="📡 MONITORING HOSTS", bg=COLORS['card'], fg=COLORS['accent'],
                font=('Segoe UI', 12, 'bold')).pack(anchor=tk.W, padx=15, pady=8)
        
        self.hosts_container = tk.Frame(hosts_frame, bg=COLORS['card'])
        self.hosts_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.pages["ping"] = page
    
    def _quick_ping(self):
        host = self.quick_entry.get().strip()
        if not host:
            return
        self.quick_result.delete("1.0", tk.END)
        self.quick_result.insert("1.0", f"⏳ Pinging {host}...")
        
        def do():
            r = NetworkAdapter.ping(host, 4)
            def up():
                self.quick_result.delete("1.0", tk.END)
                if r['success']:
                    self.quick_result.insert("1.0",
                        f"✅ {host} is ALIVE\n"
                        f"📊 Loss: {r['loss_pct']:.0f}%\n"
                        f"⏱️ Min: {r['min']:.1f}ms | Avg: {r['avg']:.1f}ms | Max: {r['max']:.1f}ms")
                else:
                    self.quick_result.insert("1.0", f"❌ {host} is DEAD")
            self.root.after(0, up)
        threading.Thread(target=do, daemon=True).start()
    
    def _add_host(self):
        ip = self.ping_ip.get().strip()
        name = self.ping_name.get().strip()
        if not ip:
            return
        if not name:
            name = ip
        if ip in self.hosts:
            return
        HostCard(self.hosts_container, ip, name, self._remove_host)
        self.hosts[ip] = None
        self._save_config()
    
    def _remove_host(self, ip):
        if ip in self.hosts:
            del self.hosts[ip]
            self._save_config()
    
    def _stop_all(self):
        for w in self.hosts_container.winfo_children():
            if hasattr(w, 'stop'):
                w.stop()
            w.destroy()
        self.hosts.clear()
    
    # ============================================================
    # TRACE PAGE
    # ============================================================
    def _create_trace_page(self):
        page = tk.Frame(self.content, bg=COLORS['bg'])
        
        frame = tk.Frame(page, bg=COLORS['card'], relief=tk.RAISED, bd=1)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(frame, text="🗺️ TRACEROUTE", bg=COLORS['card'], fg=COLORS['accent'],
                font=('Segoe UI', 14, 'bold')).pack(anchor=tk.W, padx=15, pady=10)
        
        row = tk.Frame(frame, bg=COLORS['card'])
        row.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        self.trace_target = tk.Entry(row, bg=COLORS['bg'], fg=COLORS['text'], width=30, font=('Segoe UI', 11))
        self.trace_target.pack(side=tk.LEFT, padx=(0, 10))
        self.trace_target.insert(0, "8.8.8.8")
        
        StyledButton(row, "Trace", self._run_trace, COLORS['accent'], 8).pack(side=tk.LEFT)
        
        self.trace_text = tk.Text(frame, bg=COLORS['bg'], fg=COLORS['text'], font=('Consolas', 9))
        self.trace_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        self.pages["trace"] = page
    
    def _run_trace(self):
        host = self.trace_target.get().strip()
        if not host:
            return
        self.trace_text.delete("1.0", tk.END)
        self.trace_text.insert("1.0", f"Tracing {host}...\n")
        
        def do():
            out = NetworkAdapter.traceroute(host)
            self.root.after(0, lambda: self.trace_text.delete("1.0", tk.END))
            self.root.after(0, lambda: self.trace_text.insert("1.0", out))
        threading.Thread(target=do, daemon=True).start()
    
    # ============================================================
    # PORTS PAGE
    # ============================================================
    def _create_ports_page(self):
        page = tk.Frame(self.content, bg=COLORS['bg'])
        
        frame = tk.Frame(page, bg=COLORS['card'], relief=tk.RAISED, bd=1)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(frame, text="🔌 PORT SCANNER", bg=COLORS['card'], fg=COLORS['accent'],
                font=('Segoe UI', 14, 'bold')).pack(anchor=tk.W, padx=15, pady=10)
        
        row = tk.Frame(frame, bg=COLORS['card'])
        row.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        self.scan_target = tk.Entry(row, bg=COLORS['bg'], fg=COLORS['text'], width=15)
        self.scan_target.pack(side=tk.LEFT, padx=(0, 10))
        self.scan_target.insert(0, "127.0.0.1")
        
        self.scan_ports = tk.Entry(row, bg=COLORS['bg'], fg=COLORS['text'], width=30)
        self.scan_ports.pack(side=tk.LEFT, padx=(0, 10))
        self.scan_ports.insert(0, "22,80,443,3306,5432,8080")
        
        StyledButton(row, "Scan", self._scan_ports, COLORS['green'], 8).pack(side=tk.LEFT)
        
        # Treeview
        self.port_tree = ttk.Treeview(frame, columns=('Port', 'Status', 'Service'), height=18)
        self.port_tree.column('#0', width=0)
        self.port_tree.column('Port', width=100)
        self.port_tree.column('Status', width=150)
        self.port_tree.column('Service', width=200)
        self.port_tree.heading('Port', text='Port')
        self.port_tree.heading('Status', text='Status')
        self.port_tree.heading('Service', text='Service')
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', background=COLORS['bg'], foreground=COLORS['text'], fieldbackground=COLORS['bg'])
        style.configure('Treeview.Heading', background=COLORS['card'], foreground=COLORS['text'])
        
        self.port_tree.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        self.pages["ports"] = page
    
    def _scan_ports(self):
        target = self.scan_target.get().strip()
        ports_str = self.scan_ports.get().strip()
        if not target or not ports_str:
            return
        
        ports = []
        for p in ports_str.split(','):
            p = p.strip()
            if '-' in p:
                s, e = p.split('-')
                ports.extend(range(int(s), int(e)+1))
            else:
                ports.append(int(p))
        
        self.port_tree.delete(*self.port_tree.get_children())
        services = {22: 'SSH', 80: 'HTTP', 443: 'HTTPS', 3306: 'MySQL', 5432: 'PostgreSQL', 3389: 'RDP', 5900: 'VNC'}
        
        def check(p):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.3)
                ok = s.connect_ex((target, p)) == 0
                s.close()
                return (p, ok)
            except:
                return (p, False)
        
        def do():
            with ThreadPoolExecutor(max_workers=50) as ex:
                for p, ok in ex.map(check, ports):
                    if ok:
                        self.root.after(0, lambda x=p: self.port_tree.insert('', 'end', values=(x, "✓ OPEN", services.get(x, "Unknown"))))
        threading.Thread(target=do, daemon=True).start()
    
    # ============================================================
    # SCAN PAGE
    # ============================================================
    def _create_scan_page(self):
        page = tk.Frame(self.content, bg=COLORS['bg'])
        
        frame = tk.Frame(page, bg=COLORS['card'], relief=tk.RAISED, bd=1)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(frame, text="📡 NETWORK SCAN (CIDR)", bg=COLORS['card'], fg=COLORS['accent'],
                font=('Segoe UI', 14, 'bold')).pack(anchor=tk.W, padx=15, pady=10)
        
        row = tk.Frame(frame, bg=COLORS['card'])
        row.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        self.cidr_entry = tk.Entry(row, bg=COLORS['bg'], fg=COLORS['text'], width=25)
        self.cidr_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.cidr_entry.insert(0, "192.168.1.0/24")
        
        StyledButton(row, "Scan", self._scan_network, COLORS['accent'], 10).pack(side=tk.LEFT)
        
        self.network_tree = ttk.Treeview(frame, columns=('IP', 'Status'), height=18)
        self.network_tree.column('#0', width=0)
        self.network_tree.column('IP', width=200)
        self.network_tree.column('Status', width=100)
        self.network_tree.heading('IP', text='IP Address')
        self.network_tree.heading('Status', text='Status')
        self.network_tree.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        self.pages["scan"] = page
    
    def _scan_network(self):
        cidr = self.cidr_entry.get().strip()
        if not cidr:
            return
        self.network_tree.delete(*self.network_tree.get_children())
        
        def do():
            try:
                net = ipaddress.ip_network(cidr, strict=False)
                def ping_ip(ip):
                    r = NetworkAdapter.ping(str(ip), 1, 1)
                    return str(ip) if r['success'] else None
                with ThreadPoolExecutor(max_workers=50) as ex:
                    for ip in ex.map(ping_ip, net.hosts()):
                        if ip:
                            self.root.after(0, lambda x=ip: self.network_tree.insert('', 'end', values=(x, "✓ ALIVE")))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        threading.Thread(target=do, daemon=True).start()
    
    # ============================================================
    # LOOP PAGE
    # ============================================================
    def _create_loop_page(self):
        page = tk.Frame(self.content, bg=COLORS['bg'])
        
        frame = tk.Frame(page, bg=COLORS['card'], relief=tk.RAISED, bd=1)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(frame, text="🔗 LOOP DETECTION", bg=COLORS['card'], fg=COLORS['accent'],
                font=('Segoe UI', 14, 'bold')).pack(anchor=tk.W, padx=15, pady=10)
        
        StyledButton(frame, "Detect Loops", self._detect_loops, COLORS['orange'], 12).pack(anchor=tk.W, padx=15, pady=(0, 10))
        
        self.loop_text = tk.Text(frame, bg=COLORS['bg'], fg=COLORS['text'], font=('Consolas', 9))
        self.loop_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        self.pages["loop"] = page
    
    def _detect_loops(self):
        self.loop_text.delete("1.0", tk.END)
        self.loop_text.insert("1.0", "Analyzing ARP table...\n")
        
        def do():
            arp = NetworkAdapter.get_arp_table()
            dup = {mac: ips for mac, ips in arp.items() if len(ips) > 1}
            def up():
                self.loop_text.delete("1.0", tk.END)
                if dup:
                    self.loop_text.insert("1.0", f"⚠️ Found {len(dup)} duplicate MACs:\n\n")
                    for mac, ips in dup.items():
                        self.loop_text.insert(tk.END, f"MAC: {mac}\nIPs: {', '.join(ips)}\n\n")
                else:
                    self.loop_text.insert("1.0", "✅ No duplicate MACs found")
            self.root.after(0, up)
        threading.Thread(target=do, daemon=True).start()
    
    # ============================================================
    # GROUPS PAGE
    # ============================================================
    def _create_groups_page(self):
        page = tk.Frame(self.content, bg=COLORS['bg'])
        
        # Create group
        create_frame = tk.Frame(page, bg=COLORS['card'], relief=tk.RAISED, bd=1)
        create_frame.pack(fill=tk.X, padx=10, pady=10)
        tk.Label(create_frame, text="📊 CREATE GROUP", bg=COLORS['card'], fg=COLORS['accent'],
                font=('Segoe UI', 12, 'bold')).pack(anchor=tk.W, padx=15, pady=8)
        
        c_row = tk.Frame(create_frame, bg=COLORS['card'])
        c_row.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        self.new_group = tk.Entry(c_row, bg=COLORS['bg'], fg=COLORS['text'], width=20)
        self.new_group.pack(side=tk.LEFT, padx=(0, 10))
        StyledButton(c_row, "Create", self._create_group, COLORS['green'], 8).pack(side=tk.LEFT)
        
        # Lists
        list_frame = tk.Frame(page, bg=COLORS['card'], relief=tk.RAISED, bd=1)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        tk.Label(list_frame, text="📋 GROUPS & IPS", bg=COLORS['card'], fg=COLORS['accent'],
                font=('Segoe UI', 12, 'bold')).pack(anchor=tk.W, padx=15, pady=8)
        
        list_container = tk.Frame(list_frame, bg=COLORS['card'])
        list_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))
        
        left = tk.Frame(list_container, bg=COLORS['bg'], relief=tk.SUNKEN, bd=1)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        tk.Label(left, text="GROUPS", bg=COLORS['bg'], fg=COLORS['accent']).pack()
        self.groups_list = tk.Listbox(left, bg=COLORS['bg'], fg=COLORS['text'], selectbackground=COLORS['accent'])
        self.groups_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.groups_list.bind('<<ListboxSelect>>', self._on_group_select)
        
        right = tk.Frame(list_container, bg=COLORS['bg'], relief=tk.SUNKEN, bd=1)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        tk.Label(right, text="IPS", bg=COLORS['bg'], fg=COLORS['accent']).pack()
        self.ips_list = tk.Listbox(right, bg=COLORS['bg'], fg=COLORS['text'], selectbackground=COLORS['accent'])
        self.ips_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Buttons
        btn_frame = tk.Frame(list_frame, bg=COLORS['card'])
        btn_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        StyledButton(btn_frame, "Add IP", self._add_ip_to_group, COLORS['accent'], 8).pack(side=tk.LEFT, padx=5)
        StyledButton(btn_frame, "Remove IP", self._remove_ip_from_group, COLORS['red'], 10).pack(side=tk.LEFT, padx=5)
        StyledButton(btn_frame, "Load to Ping", self._load_group_to_ping, COLORS['green'], 12).pack(side=tk.LEFT, padx=5)
        
        self.pages["groups"] = page
        self._refresh_groups()
    
    def _refresh_groups(self):
        self.groups_list.delete(0, tk.END)
        for n in self.groups:
            self.groups_list.insert(tk.END, f"{n} ({len(self.groups[n])})")
    
    def _on_group_select(self, e):
        sel = self.groups_list.curselection()
        if sel:
            n = self.groups_list.get(sel[0]).split(' (')[0]
            self.ips_list.delete(0, tk.END)
            for ip in self.groups.get(n, []):
                self.ips_list.insert(tk.END, ip)
    
    def _create_group(self):
        n = self.new_group.get().strip()
        if not n:
            return
        if n in self.groups:
            messagebox.showwarning("Error", "Group exists")
            return
        self.groups[n] = []
        self.new_group.delete(0, tk.END)
        self._refresh_groups()
        self._save_config()
    
    def _add_ip_to_group(self):
        sel = self.groups_list.curselection()
        if not sel:
            return
        n = self.groups_list.get(sel[0]).split(' (')[0]
        ip = simpledialog.askstring("Add IP", "Enter IP:")
        if ip and ip not in self.groups[n]:
            self.groups[n].append(ip)
            self._refresh_groups()
            self._save_config()
    
    def _remove_ip_from_group(self):
        sel = self.groups_list.curselection()
        isel = self.ips_list.curselection()
        if not sel or not isel:
            return
        n = self.groups_list.get(sel[0]).split(' (')[0]
        ip = self.ips_list.get(isel[0])
        if ip in self.groups[n]:
            self.groups[n].remove(ip)
            self._refresh_groups()
            self._save_config()
    
    def _load_group_to_ping(self):
        sel = self.groups_list.curselection()
        if not sel:
            return
        n = self.groups_list.get(sel[0]).split(' (')[0]
        ips = self.groups.get(n, [])
        if not ips:
            return
        self._show_ping()
        for ip in ips:
            if ip not in self.hosts:
                HostCard(self.hosts_container, ip, ip, self._remove_host)
                self.hosts[ip] = None
    
    # ============================================================
    # AI PAGE
    # ============================================================
    def _create_ai_page(self):
        page = tk.Frame(self.content, bg=COLORS['bg'])
        self.ai = AIAssistant(page)
        self.pages["ai"] = page
    
    # ============================================================
    # BACKUP PAGE
    # ============================================================
    def _create_backup_page(self):
        page = tk.Frame(self.content, bg=COLORS['bg'])
        
        frame = tk.Frame(page, bg=COLORS['card'], relief=tk.RAISED, bd=1)
        frame.pack(expand=True, padx=10, pady=10)
        
        center = tk.Frame(frame, bg=COLORS['card'])
        center.pack(expand=True, pady=30)
        
        StyledButton(center, "📤 Export Config", self._export_config, COLORS['green'], 20).pack(pady=8)
        StyledButton(center, "📥 Import Config", self._import_config, COLORS['accent'], 20).pack(pady=8)
        StyledButton(center, "🔄 Reset All", self._reset_all, COLORS['red'], 20).pack(pady=8)
        
        self.pages["backup"] = page
    
    def _export_config(self):
        f = filedialog.asksaveasfilename(defaultextension=".json")
        if f:
            with open(f, 'w') as fp:
                json.dump({'groups': self.groups}, fp, indent=2)
            messagebox.showinfo("Success", "Exported")
    
    def _import_config(self):
        f = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if f:
            with open(f, 'r') as fp:
                self.groups = json.load(fp).get('groups', {"Default": []})
                self._refresh_groups()
                self._save_config()
            messagebox.showinfo("Success", "Imported")
    
    def _reset_all(self):
        if messagebox.askyesno("Confirm", "Reset all?"):
            self._stop_all()
            self.groups = {"Default": []}
            self._refresh_groups()
            self._save_config()
    
    def _save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump({'groups': self.groups}, f)
    
    def _load_config(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.groups = json.load(f).get('groups', {"Default": []})
            except:
                pass
    
    # ============================================================
    # NAVIGATION
    # ============================================================
    def _show_ping(self):
        for p in self.pages.values():
            p.pack_forget()
        self.pages["ping"].pack(fill=tk.BOTH, expand=True)
    
    def _show_trace(self):
        for p in self.pages.values():
            p.pack_forget()
        self.pages["trace"].pack(fill=tk.BOTH, expand=True)
    
    def _show_ports(self):
        for p in self.pages.values():
            p.pack_forget()
        self.pages["ports"].pack(fill=tk.BOTH, expand=True)
    
    def _show_scan(self):
        for p in self.pages.values():
            p.pack_forget()
        self.pages["scan"].pack(fill=tk.BOTH, expand=True)
    
    def _show_loop(self):
        for p in self.pages.values():
            p.pack_forget()
        self.pages["loop"].pack(fill=tk.BOTH, expand=True)
    
    def _show_groups(self):
        for p in self.pages.values():
            p.pack_forget()
        self._refresh_groups()
        self.pages["groups"].pack(fill=tk.BOTH, expand=True)
    
    def _show_ai(self):
        for p in self.pages.values():
            p.pack_forget()
        self.pages["ai"].pack(fill=tk.BOTH, expand=True)
    
    def _show_backup(self):
        for p in self.pages.values():
            p.pack_forget()
        self.pages["backup"].pack(fill=tk.BOTH, expand=True)
    
    def _on_close(self):
        self._stop_all()
        self.root.destroy()
    
    def run(self):
        self.root.mainloop()


# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    app = NetToolApp()
    app.run()
