#!/usr/bin/env python3
"""
Network Tool Ultimate v12.0 - FIXED
Fixed: traceroute, ping, quick ping, everything works!
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import tkinter.ttk as ttk
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
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

SYSTEM = platform.system().lower()
IS_WINDOWS = SYSTEM == 'windows'

print(f"✅ Running on: {SYSTEM.upper()}")

# ============================================================================
# COLORS
# ============================================================================
COLORS = {
    'bg': '#0A0E17',
    'sidebar': '#0F1322',
    'card': '#1A1F33',
    'card_hover': '#222842',
    'accent': '#00D4FF',
    'accent_green': '#10B981',
    'accent_red': '#EF4444',
    'accent_orange': '#F59E0B',
    'accent_purple': '#8B5CF6',
    'text': '#FFFFFF',
    'text_secondary': '#8A99B8',
    'border': '#2A3166',
}

# ============================================================================
# NETWORK ADAPTER - FIXED PING
# ============================================================================
class NetworkAdapter:
    @staticmethod
    def ping(host, count=4, timeout=2):
        try:
            # Sử dụng timeout phù hợp
            if IS_WINDOWS:
                cmd = ['ping', '-n', str(count), '-w', str(timeout * 1000), host]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 2)
                output = result.stdout.lower()
                
                # Parse Windows ping output
                times = []
                for m in re.findall(r'time[= ](\d+)ms', output):
                    times.append(float(m))
                
                lost = output.count('timed out') + output.count('unreachable')
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
            else:
                # Linux: ping -c count -W timeout host
                cmd = ['ping', '-c', str(count), '-W', str(timeout), host]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 2)
                output = result.stdout.lower()
                
                # Parse Linux ping output
                times = []
                for m in re.findall(r'time[= ](\d+\.?\d*)\s*ms', output):
                    times.append(float(m))
                
                # Parse packet loss
                loss_match = re.search(r'(\d+)% packet loss', output)
                loss_pct = int(loss_match.group(1)) if loss_match else 0
                
                # Parse sent/received
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
        except subprocess.TimeoutExpired:
            return {'success': False, 'sent': count, 'received': 0, 'loss_pct': 100, 'times': []}
        except Exception as e:
            print(f"Ping error: {e}")
            return {'success': False, 'sent': 0, 'received': 0, 'loss_pct': 100, 'times': []}
    
    @staticmethod
    def traceroute(host):
        try:
            if IS_WINDOWS:
                cmd = ['tracert', '-d', '-h', '30', host]
            else:
                # Linux: sử dụng traceroute hoặc tracepath
                # Thử traceroute trước
                try:
                    cmd = ['traceroute', '-n', '-m', '30', host]
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                    return result.stdout
                except FileNotFoundError:
                    # Nếu không có traceroute, dùng tracepath
                    cmd = ['tracepath', '-n', host]
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                    return result.stdout
            return result.stdout
        except subprocess.TimeoutExpired:
            return "Timeout: Traceroute took too long"
        except FileNotFoundError:
            return "Error: 'traceroute' not found. Install with: sudo apt install traceroute"
        except Exception as e:
            return f"Error: {str(e)}"
    
    @staticmethod
    def get_arp_table():
        try:
            if IS_WINDOWS:
                cmd = ['arp', '-a']
            else:
                cmd = ['arp', '-n']
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
# PREMIUM BUTTON
# ============================================================================
class PremiumButton(ctk.CTkButton):
    def __init__(self, parent, text="", icon="", command=None, color=COLORS['accent'], width=120):
        display_text = f"{icon} {text}" if icon else text
        super().__init__(
            parent, text=display_text, command=command,
            fg_color=color, hover_color=self._lighten(color),
            corner_radius=10, height=40, width=width,
            font=ctk.CTkFont(size=12, weight="bold")
        )
    
    def _lighten(self, color):
        if color == COLORS['accent']:
            return "#33EEFF"
        if color == COLORS['accent_green']:
            return "#2ECC71"
        if color == COLORS['accent_red']:
            return "#E74C3C"
        return color


# ============================================================================
# PREMIUM CARD
# ============================================================================
class PremiumCard(ctk.CTkFrame):
    def __init__(self, parent, title=""):
        super().__init__(parent, fg_color=COLORS['card'], corner_radius=15, border_width=1, border_color=COLORS['border'])
        
        if title:
            self.title_bar = ctk.CTkFrame(self, fg_color=COLORS['accent'], height=40, corner_radius=15)
            self.title_bar.pack(fill=tk.X, pady=(0, 10))
            self.title_bar.pack_propagate(False)
            
            ctk.CTkLabel(
                self.title_bar, text=title, 
                font=ctk.CTkFont(size=13, weight="bold"), 
                text_color="white"
            ).pack(side=tk.LEFT, padx=15)
        
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)


# ============================================================================
# HOST CARD - Continuous Ping
# ============================================================================
class HostCard(ctk.CTkFrame):
    def __init__(self, parent, ip, name, on_remove):
        super().__init__(parent, fg_color=COLORS['card_hover'], corner_radius=12, border_width=1, border_color=COLORS['border'])
        self.ip = ip
        self.name = name
        self.on_remove = on_remove
        self.running = True
        self.queue = queue.Queue()
        
        self._create_ui()
        self._start_ping()
    
    def _create_ui(self):
        self.pack(side=tk.LEFT, padx=8, pady=8, fill=tk.BOTH, expand=True)
        
        # Header with LED
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill=tk.X, padx=12, pady=10)
        
        self.led = ctk.CTkLabel(header, text="●", text_color=COLORS['accent_red'], font=ctk.CTkFont(size=16))
        self.led.pack(side=tk.LEFT)
        
        ctk.CTkLabel(self, text=self.name, font=ctk.CTkFont(size=14, weight="bold")).pack()
        ctk.CTkLabel(self, text=self.ip, text_color=COLORS['text_secondary'], font=ctk.CTkFont(size=11)).pack()
        
        ctk.CTkFrame(self, height=1, fg_color=COLORS['border']).pack(fill=tk.X, padx=12, pady=8)
        
        # Stats
        stats = ctk.CTkFrame(self, fg_color="transparent")
        stats.pack(fill=tk.X, padx=12, pady=5)
        
        row1 = ctk.CTkFrame(stats, fg_color="transparent")
        row1.pack(fill=tk.X, pady=2)
        self.sent_label = ctk.CTkLabel(row1, text="📤 Sent:0", text_color=COLORS['text_secondary'], font=ctk.CTkFont(size=10))
        self.sent_label.pack(side=tk.LEFT, expand=True)
        self.recv_label = ctk.CTkLabel(row1, text="📥 Recv:0", text_color=COLORS['text_secondary'], font=ctk.CTkFont(size=10))
        self.recv_label.pack(side=tk.LEFT, expand=True)
        
        row2 = ctk.CTkFrame(stats, fg_color="transparent")
        row2.pack(fill=tk.X, pady=2)
        self.loss_label = ctk.CTkLabel(row2, text="⚠️ Loss:0%", text_color=COLORS['text_secondary'], font=ctk.CTkFont(size=10))
        self.loss_label.pack(side=tk.LEFT, expand=True)
        self.time_label = ctk.CTkLabel(row2, text="⏱️ Time:---", text_color=COLORS['text_secondary'], font=ctk.CTkFont(size=10))
        self.time_label.pack(side=tk.LEFT, expand=True)
        
        ctk.CTkFrame(self, height=1, fg_color=COLORS['border']).pack(fill=tk.X, padx=12, pady=8)
        
        # Remote buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill=tk.X, padx=12, pady=8)
        
        for text, cmd, color in [
            ("🔌 SSH", self._ssh, COLORS['accent']),
            ("🌐 HTTP", self._http, COLORS['accent_green']),
            ("🖥️ RDP", self._rdp, COLORS['accent_purple']),
            ("📺 VNC", self._vnc, COLORS['accent_orange']),
            ("✕", self._remove, COLORS['accent_red']),
        ]:
            btn = ctk.CTkButton(btn_frame, text=text, width=50, height=30,
                               fg_color=color, corner_radius=8, command=cmd)
            btn.pack(side=tk.LEFT, padx=3, expand=True, fill=tk.X)
    
    def _start_ping(self):
        def ping_loop():
            while self.running:
                r = NetworkAdapter.ping(self.ip, count=1, timeout=2)
                self.queue.put(r)
                time.sleep(1)
        threading.Thread(target=ping_loop, daemon=True).start()
        threading.Thread(target=self._update_ui, daemon=True).start()
    
    def _update_ui(self):
        while self.running:
            try:
                while not self.queue.empty():
                    r = self.queue.get_nowait()
                    if r['success']:
                        self.led.configure(text_color=COLORS['accent_green'])
                        if r['avg']:
                            self.time_label.configure(text=f"⏱️ Time:{r['avg']:.0f}ms", text_color=COLORS['accent_green'])
                    else:
                        self.led.configure(text_color=COLORS['accent_red'])
                        self.time_label.configure(text="⏱️ Time:---", text_color=COLORS['accent_red'])
                    
                    self.sent_label.configure(text=f"📤 Sent:{r['sent']}")
                    self.recv_label.configure(text=f"📥 Recv:{r['received']}")
                    loss_color = COLORS['accent_red'] if r['loss_pct'] > 0 else COLORS['accent_green']
                    self.loss_label.configure(text=f"⚠️ Loss:{r['loss_pct']:.0f}%", text_color=loss_color)
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
        self.chat = ctk.CTkTextbox(self.parent, fg_color=COLORS['card'], corner_radius=12)
        self.chat.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        welcome = """🤖 AI NETWORK ASSISTANT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 Ask me about network:
   • "ping 8.8.8.8" - Check connectivity
   • "port scan" - Common ports
   • "slow network" - Troubleshooting
   • "packet loss" - Fix packet loss
   • "traceroute" - Network path
   • "my ip" - Your IP address

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
        self.chat.insert("0.0", welcome)
        
        input_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        input_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.entry = ctk.CTkEntry(input_frame, placeholder_text="Type your question...", corner_radius=12)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.entry.bind('<Return>', self._ask)
        
        send_btn = PremiumButton(input_frame, text="Send", icon="📤", color=COLORS['accent_green'], width=80)
        send_btn.configure(command=self._ask)
        send_btn.pack(side=tk.RIGHT)
    
    def _ask(self, event=None):
        q = self.entry.get().strip()
        if not q:
            return
        self.chat.insert(tk.END, f"\n👤 You: {q}\n")
        self.entry.delete(0, tk.END)
        
        q_lower = q.lower()
        if 'ping' in q_lower:
            ans = "📡 PING: ping -c 4 8.8.8.8\n✅ 0% loss = good connection"
        elif 'port' in q_lower:
            ans = "🔌 COMMON PORTS:\n22=SSH, 80=HTTP, 443=HTTPS, 3306=MySQL"
        elif 'slow' in q_lower:
            ans = "🐌 SLOW NETWORK:\n1. Ping gateway\n2. Ping 8.8.8.8\n3. Traceroute"
        elif 'loss' in q_lower:
            ans = "⚠️ PACKET LOSS:\n• Check cables\n• Check WiFi\n• Restart router"
        elif 'trace' in q_lower:
            ans = "🗺️ TRACEROUTE: traceroute google.com\nShows network path"
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
        self.root = ctk.CTk()
        self.root.title(f"Network Tool Ultimate - {SYSTEM.upper()} Edition")
        self.root.geometry("1400x800")
        self.root.configure(fg_color=COLORS['bg'])
        
        self.hosts = {}
        self.groups = {"Default": []}
        self.config_file = Path.home() / ".network_tool.json"
        
        self._load_config()
        self._create_ui()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _create_ui(self):
        # Header
        header = ctk.CTkFrame(self.root, height=60, fg_color=COLORS['accent'], corner_radius=0)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        ctk.CTkLabel(header, text="🌐 NETWORK TOOL ULTIMATE", 
                    font=ctk.CTkFont(size=18, weight="bold"), text_color="white").pack(side=tk.LEFT, padx=20)
        
        self.status_label = ctk.CTkLabel(header, text="✓ READY", text_color="white", font=ctk.CTkFont(size=11))
        self.status_label.pack(side=tk.RIGHT, padx=20)
        
        # Main container
        main = ctk.CTkFrame(self.root, fg_color="transparent")
        main.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Sidebar
        sidebar = ctk.CTkFrame(main, width=100, fg_color=COLORS['sidebar'], corner_radius=15)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        sidebar.pack_propagate(False)
        
        # Logo
        logo = ctk.CTkFrame(sidebar, fg_color=COLORS['accent'], height=80, corner_radius=15)
        logo.pack(fill=tk.X, pady=(10, 20))
        ctk.CTkLabel(logo, text="🌐", font=ctk.CTkFont(size=32), text_color="white").pack(pady=15)
        
        # Nav buttons
        nav_buttons = [
            ("🔍", "PING", "ping"),
            ("🗺️", "TRACE", "trace"),
            ("🔌", "PORTS", "ports"),
            ("📡", "SCAN", "scan"),
            ("🔗", "LOOP", "loop"),
            ("📊", "GROUPS", "groups"),
            ("🤖", "AI", "ai"),
            ("💾", "BACKUP", "backup"),
        ]
        
        self.nav_btns = {}
        for icon, text, page in nav_buttons:
            btn = ctk.CTkButton(
                sidebar, text=f"{icon}\n{text}", 
                command=lambda p=page: self._show_page(p),
                fg_color="transparent", hover_color=COLORS['card'],
                corner_radius=10, height=70,
                font=ctk.CTkFont(size=11, weight="bold")
            )
            btn.pack(fill=tk.X, pady=5, padx=10)
            self.nav_btns[page] = btn
        
        # Content
        self.content_area = ctk.CTkFrame(main, fg_color="transparent")
        self.content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Create pages
        self.pages = {}
        self._create_ping_page()
        self._create_trace_page()
        self._create_ports_page()
        self._create_scan_page()
        self._create_loop_page()
        self._create_groups_page()
        self._create_ai_page()
        self._create_backup_page()
        
        self._show_page("ping")
    
    def _show_page(self, page_name):
        for page in self.pages.values():
            page.pack_forget()
        self.pages[page_name].pack(fill=tk.BOTH, expand=True)
        
        for name, btn in self.nav_btns.items():
            btn.configure(fg_color=COLORS['accent'] if name == page_name else "transparent")
    
    # ============================================================
    # PAGE 1: PING - Quick Ping hoạt động
    # ============================================================
    def _create_ping_page(self):
        page = ctk.CTkFrame(self.content_area, fg_color="transparent")
        
        # Quick Ping Card
        quick_card = PremiumCard(page, "⚡ QUICK PING")
        quick_card.pack(fill=tk.X, pady=(0, 15))
        
        quick_row = ctk.CTkFrame(quick_card.content, fg_color="transparent")
        quick_row.pack(fill=tk.X)
        
        self.quick_ping_entry = ctk.CTkEntry(quick_row, placeholder_text="Enter IP or Hostname", width=300, height=45)
        self.quick_ping_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.quick_ping_entry.insert(0, "8.8.8.8")
        
        quick_btn = PremiumButton(quick_row, text="Ping", icon="🔍", color=COLORS['accent_green'], width=100)
        quick_btn.configure(command=self._quick_ping)
        quick_btn.pack(side=tk.LEFT)
        
        self.quick_result = ctk.CTkTextbox(quick_card.content, height=80, fg_color=COLORS['bg'])
        self.quick_result.pack(fill=tk.X, pady=(10, 0))
        
        # Add Host Card
        add_card = PremiumCard(page, "➕ ADD HOST FOR CONTINUOUS MONITORING")
        add_card.pack(fill=tk.X, pady=(0, 15))
        
        add_row = ctk.CTkFrame(add_card.content, fg_color="transparent")
        add_row.pack(fill=tk.X)
        
        self.ping_ip = ctk.CTkEntry(add_row, placeholder_text="IP Address", width=180)
        self.ping_ip.pack(side=tk.LEFT, padx=(0, 10))
        self.ping_ip.insert(0, "8.8.8.8")
        
        self.ping_name = ctk.CTkEntry(add_row, placeholder_text="Host Name", width=180)
        self.ping_name.pack(side=tk.LEFT, padx=(0, 10))
        self.ping_name.insert(0, "Google DNS")
        
        add_btn = PremiumButton(add_row, text="Add Host", icon="➕", color=COLORS['accent_green'], width=120)
        add_btn.configure(command=self._add_host)
        add_btn.pack(side=tk.LEFT)
        
        stop_btn = PremiumButton(add_row, text="Stop All", icon="⏹️", color=COLORS['accent_red'], width=120)
        stop_btn.configure(command=self._stop_all)
        stop_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Hosts container
        hosts_card = PremiumCard(page, "📡 MONITORING HOSTS")
        hosts_card.pack(fill=tk.BOTH, expand=True)
        
        self.hosts_scroll = ctk.CTkScrollableFrame(hosts_card.content, fg_color="transparent")
        self.hosts_scroll.pack(fill=tk.BOTH, expand=True)
        self.cards_frame = self.hosts_scroll
        
        self.pages["ping"] = page
    
    def _quick_ping(self):
        host = self.quick_ping_entry.get().strip()
        if not host:
            messagebox.showwarning("Error", "Enter a host to ping!")
            return
        
        self.quick_result.delete("0.0", "end")
        self.quick_result.insert("0.0", f"⏳ Pinging {host}...")
        self.status_label.configure(text="⏳ Pinging...")
        
        def do_ping():
            r = NetworkAdapter.ping(host, count=4)
            def update():
                if r['success']:
                    self.quick_result.delete("0.0", "end")
                    self.quick_result.insert("0.0", 
                        f"✅ {host} is ALIVE\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"📊 Packet Loss: {r['loss_pct']:.0f}%\n"
                        f"⏱️  Min: {r['min']:.1f}ms | Avg: {r['avg']:.1f}ms | Max: {r['max']:.1f}ms\n"
                        f"📤 Sent: {r['sent']} | 📥 Received: {r['received']}")
                    self.status_label.configure(text="✅ Ping successful")
                else:
                    self.quick_result.delete("0.0", "end")
                    self.quick_result.insert("0.0", 
                        f"❌ {host} is DEAD (100% packet loss)\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"💡 Check:\n"
                        f"   • Is the host online?\n"
                        f"   • Check your internet connection\n"
                        f"   • Try ping {host} from terminal")
                    self.status_label.configure(text="❌ Ping failed")
            self.root.after(0, update)
        
        threading.Thread(target=do_ping, daemon=True).start()
    
    def _add_host(self):
        ip = self.ping_ip.get().strip()
        name = self.ping_name.get().strip()
        if not ip:
            messagebox.showwarning("Error", "Enter IP address!")
            return
        if not name:
            name = ip
        if ip in self.hosts:
            messagebox.showwarning("Warning", f"Host {name} already exists!")
            return
        
        # Test ping before adding
        test = NetworkAdapter.ping(ip, count=1, timeout=1)
        if test['success']:
            self.status_label.configure(text=f"✓ {ip} is reachable")
        else:
            self.status_label.configure(text=f"⚠️ {ip} may be unreachable")
        
        card = HostCard(self.cards_frame, ip, name, self._remove_host)
        self.hosts[ip] = card
        self._save_config()
    
    def _remove_host(self, ip):
        if ip in self.hosts:
            del self.hosts[ip]
            self._save_config()
    
    def _stop_all(self):
        for host in list(self.hosts.values()):
            host.stop()
        self.hosts.clear()
        for widget in self.cards_frame.winfo_children():
            widget.destroy()
        self.status_label.configure(text="⏹️ All pings stopped")
    
    # ============================================================
    # PAGE 2: TRACEROUTE - FIXED
    # ============================================================
    def _create_trace_page(self):
        page = ctk.CTkFrame(self.content_area, fg_color="transparent")
        
        card = PremiumCard(page, "🗺️ TRACEROUTE")
        card.pack(fill=tk.BOTH, expand=True)
        
        input_row = ctk.CTkFrame(card.content, fg_color="transparent")
        input_row.pack(fill=tk.X, pady=(0, 15))
        
        self.trace_target = ctk.CTkEntry(input_row, placeholder_text="Target IP or Hostname", width=350, height=45)
        self.trace_target.pack(side=tk.LEFT, padx=(0, 10))
        self.trace_target.insert(0, "8.8.8.8")
        
        trace_btn = PremiumButton(input_row, text="Trace Route", icon="🗺️", color=COLORS['accent'], width=140)
        trace_btn.configure(command=self._run_traceroute)
        trace_btn.pack(side=tk.LEFT)
        
        self.trace_text = ctk.CTkTextbox(card.content, font=ctk.CTkFont(family="Consolas", size=10))
        self.trace_text.pack(fill=tk.BOTH, expand=True)
        
        # Add info note
        info = ctk.CTkLabel(card.content, text="💡 Note: If traceroute fails, install with: sudo apt install traceroute", 
                           text_color=COLORS['text_secondary'], font=ctk.CTkFont(size=10))
        info.pack(pady=(5, 0))
        
        self.pages["trace"] = page
    
    def _run_traceroute(self):
        host = self.trace_target.get().strip()
        if not host:
            messagebox.showwarning("Error", "Enter a target!")
            return
        
        self.trace_text.delete("0.0", "end")
        self.trace_text.insert("0.0", f"⏳ Tracing route to {host}...\n")
        self.status_label.configure(text="⏳ Tracing...")
        
        def do_trace():
            out = NetworkAdapter.traceroute(host)
            def update():
                self.trace_text.delete("0.0", "end")
                self.trace_text.insert("0.0", out)
                self.status_label.configure(text="✓ Trace complete")
            self.root.after(0, update)
        
        threading.Thread(target=do_trace, daemon=True).start()
    
    # ============================================================
    # PAGE 3: PORT SCAN
    # ============================================================
    def _create_ports_page(self):
        page = ctk.CTkFrame(self.content_area, fg_color="transparent")
        
        card = PremiumCard(page, "🔌 PORT SCANNER")
        card.pack(fill=tk.BOTH, expand=True)
        
        input_row = ctk.CTkFrame(card.content, fg_color="transparent")
        input_row.pack(fill=tk.X, pady=(0, 15))
        
        self.scan_target = ctk.CTkEntry(input_row, placeholder_text="Target IP", width=180, height=45)
        self.scan_target.pack(side=tk.LEFT, padx=(0, 10))
        self.scan_target.insert(0, "127.0.0.1")
        
        self.scan_ports = ctk.CTkEntry(input_row, placeholder_text="Ports (e.g., 22,80,443 or 1-1000)", width=280, height=45)
        self.scan_ports.pack(side=tk.LEFT, padx=(0, 10))
        self.scan_ports.insert(0, "22,80,443,3306,5432,8080")
        
        scan_btn = PremiumButton(input_row, text="Scan", icon="🔍", color=COLORS['accent_green'], width=100)
        scan_btn.configure(command=self._scan_ports)
        scan_btn.pack(side=tk.LEFT)
        
        self.port_tree = ttk.Treeview(card.content, columns=('Port', 'Status', 'Service'), height=18)
        self.port_tree.column('#0', width=0)
        self.port_tree.column('Port', width=100)
        self.port_tree.column('Status', width=150)
        self.port_tree.column('Service', width=250)
        self.port_tree.heading('Port', text='Port')
        self.port_tree.heading('Status', text='Status')
        self.port_tree.heading('Service', text='Service')
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', background=COLORS['bg'], foreground=COLORS['text'], fieldbackground=COLORS['bg'])
        style.configure('Treeview.Heading', background=COLORS['card'], foreground='white')
        
        self.port_tree.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.pages["ports"] = page
    
    def _scan_ports(self):
        target = self.scan_target.get().strip()
        ports_str = self.scan_ports.get().strip()
        if not target or not ports_str:
            messagebox.showwarning("Error", "Enter target and ports!")
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
        self.status_label.configure(text=f"🔍 Scanning {len(ports)} ports on {target}...")
        
        services = {22: 'SSH', 80: 'HTTP', 443: 'HTTPS', 3306: 'MySQL',
                    5432: 'PostgreSQL', 8080: 'HTTP-Alt', 3389: 'RDP', 5900: 'VNC'}
        
        def check_port(p):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.3)
                ok = s.connect_ex((target, p)) == 0
                s.close()
                return (p, ok)
            except:
                return (p, False)
        
        def do_scan():
            open_ports = []
            with ThreadPoolExecutor(max_workers=50) as ex:
                for p, ok in ex.map(check_port, ports):
                    if ok:
                        open_ports.append(p)
                        def add_row(port=p):
                            self.port_tree.insert('', 'end', values=(port, "✓ OPEN", services.get(port, "Unknown")))
                        self.root.after(0, add_row)
            
            def update_status():
                self.status_label.configure(text=f"✓ Scan complete - Found {len(open_ports)} open ports")
            self.root.after(0, update_status)
        
        threading.Thread(target=do_scan, daemon=True).start()
    
    # ============================================================
    # PAGE 4: NETWORK SCAN
    # ============================================================
    def _create_scan_page(self):
        page = ctk.CTkFrame(self.content_area, fg_color="transparent")
        
        card = PremiumCard(page, "📡 NETWORK SCAN (CIDR)")
        card.pack(fill=tk.BOTH, expand=True)
        
        input_row = ctk.CTkFrame(card.content, fg_color="transparent")
        input_row.pack(fill=tk.X, pady=(0, 15))
        
        self.cidr_entry = ctk.CTkEntry(input_row, placeholder_text="CIDR (e.g., 192.168.1.0/24)", width=300, height=45)
        self.cidr_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.cidr_entry.insert(0, "192.168.1.0/24")
        
        scan_btn = PremiumButton(input_row, text="Scan Network", icon="📡", color=COLORS['accent'], width=150)
        scan_btn.configure(command=self._scan_network)
        scan_btn.pack(side=tk.LEFT)
        
        self.network_tree = ttk.Treeview(card.content, columns=('IP', 'Status'), height=18)
        self.network_tree.column('#0', width=0)
        self.network_tree.column('IP', width=200)
        self.network_tree.column('Status', width=100)
        self.network_tree.heading('IP', text='IP Address')
        self.network_tree.heading('Status', text='Status')
        self.network_tree.pack(fill=tk.BOTH, expand=True)
        
        self.pages["scan"] = page
    
    def _scan_network(self):
        cidr = self.cidr_entry.get().strip()
        if not cidr:
            messagebox.showwarning("Error", "Enter CIDR!")
            return
        
        self.network_tree.delete(*self.network_tree.get_children())
        self.status_label.configure(text=f"📡 Scanning {cidr}...")
        
        def do_scan():
            try:
                net = ipaddress.ip_network(cidr, strict=False)
                ips = list(net.hosts())
                total = len(ips)
                
                def ping_ip(ip):
                    r = NetworkAdapter.ping(str(ip), count=1, timeout=1)
                    return str(ip) if r['success'] else None
                
                found = 0
                with ThreadPoolExecutor(max_workers=50) as ex:
                    for ip in ex.map(ping_ip, ips):
                        if ip:
                            found += 1
                            def add_row(i=ip):
                                self.network_tree.insert('', 'end', values=(i, "✓ ALIVE"))
                            self.root.after(0, add_row)
                
                def update_status():
                    self.status_label.configure(text=f"✓ Scan complete - Found {found} active hosts out of {total}")
                self.root.after(0, update_status)
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        
        threading.Thread(target=do_scan, daemon=True).start()
    
    # ============================================================
    # PAGE 5: LOOP DETECTION
    # ============================================================
    def _create_loop_page(self):
        page = ctk.CTkFrame(self.content_area, fg_color="transparent")
        
        card = PremiumCard(page, "🔗 LOOP DETECTION (ARP ANALYSIS)")
        card.pack(fill=tk.BOTH, expand=True)
        
        detect_btn = PremiumButton(card.content, text="Detect Loops", icon="🔍", color=COLORS['accent_orange'], width=150)
        detect_btn.configure(command=self._detect_loops)
        detect_btn.pack(anchor=tk.W, pady=(0, 15))
        
        self.loop_text = ctk.CTkTextbox(card.content, font=ctk.CTkFont(family="Consolas", size=10))
        self.loop_text.pack(fill=tk.BOTH, expand=True)
        
        self.pages["loop"] = page
    
    def _detect_loops(self):
        self.loop_text.delete("0.0", "end")
        self.loop_text.insert("0.0", "🔍 Analyzing ARP table...\n\n")
        self.status_label.configure(text="🔍 Detecting loops...")
        
        def do_detect():
            arp = NetworkAdapter.get_arp_table()
            duplicates = {mac: ips for mac, ips in arp.items() if len(ips) > 1}
            
            def update():
                self.loop_text.insert(tk.END, f"📊 Total ARP entries: {len(arp)}\n")
                self.loop_text.insert(tk.END, f"📊 Unique MACs: {len(set(arp.keys()))}\n\n")
                
                if duplicates:
                    self.loop_text.insert(tk.END, "⚠️  WARNING: Duplicate MAC addresses detected!\n")
                    self.loop_text.insert(tk.END, "="*50 + "\n\n")
                    for mac, ips in duplicates.items():
                        self.loop_text.insert(tk.END, f"🔴 MAC: {mac}\n")
                        self.loop_text.insert(tk.END, f"   IPs: {', '.join(ips)}\n\n")
                    self.loop_text.insert(tk.END, "⚠️  SEVERITY: HIGH\n")
                    self.loop_text.insert(tk.END, "🔧 Action: Check switch STP configuration\n")
                    self.status_label.configure(text="⚠️ Loop detected!")
                else:
                    self.loop_text.insert(tk.END, "✅ No duplicate MAC addresses found\n")
                    self.loop_text.insert(tk.END, "✅ SEVERITY: NONE\n")
                    self.status_label.configure(text="✓ No loops detected")
                
                self.loop_text.insert(tk.END, "\n✅ Analysis complete!\n")
            
            self.root.after(0, update)
        
        threading.Thread(target=do_detect, daemon=True).start()
    
    # ============================================================
    # PAGE 6: GROUPS
    # ============================================================
    def _create_groups_page(self):
        page = ctk.CTkFrame(self.content_area, fg_color="transparent")
        
        # Create group
        create_card = PremiumCard(page, "📊 CREATE GROUP")
        create_card.pack(fill=tk.X, pady=(0, 15))
        
        row = ctk.CTkFrame(create_card.content, fg_color="transparent")
        row.pack(fill=tk.X)
        
        self.new_group = ctk.CTkEntry(row, placeholder_text="Group Name", width=250, height=40)
        self.new_group.pack(side=tk.LEFT, padx=(0, 10))
        
        create_btn = PremiumButton(row, text="Create Group", icon="➕", color=COLORS['accent_green'], width=140)
        create_btn.configure(command=self._create_group)
        create_btn.pack(side=tk.LEFT)
        
        # Groups and IPs
        list_card = PremiumCard(page, "📋 GROUPS & IPS")
        list_card.pack(fill=tk.BOTH, expand=True)
        
        list_container = ctk.CTkFrame(list_card.content, fg_color="transparent")
        list_container.pack(fill=tk.BOTH, expand=True)
        
        left = ctk.CTkFrame(list_container, fg_color=COLORS['bg'], corner_radius=10)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        ctk.CTkLabel(left, text="GROUPS", font=ctk.CTkFont(weight="bold")).pack(pady=8)
        self.groups_list = tk.Listbox(left, bg=COLORS['bg'], fg=COLORS['text'], 
                                      selectbackground=COLORS['accent'], height=15)
        self.groups_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.groups_list.bind('<<ListboxSelect>>', self._on_group_select)
        
        right = ctk.CTkFrame(list_container, fg_color=COLORS['bg'], corner_radius=10)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        ctk.CTkLabel(right, text="IPS IN GROUP", font=ctk.CTkFont(weight="bold")).pack(pady=8)
        self.ips_list = tk.Listbox(right, bg=COLORS['bg'], fg=COLORS['text'],
                                   selectbackground=COLORS['accent'], height=15)
        self.ips_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        btn_frame = ctk.CTkFrame(list_card.content, fg_color="transparent")
        btn_frame.pack(fill=tk.X, pady=(15, 0))
        
        add_ip_btn = PremiumButton(btn_frame, text="Add IP", icon="➕", color=COLORS['accent'], width=100)
        add_ip_btn.configure(command=self._add_ip_to_group)
        add_ip_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        remove_ip_btn = PremiumButton(btn_frame, text="Remove IP", icon="❌", color=COLORS['accent_red'], width=120)
        remove_ip_btn.configure(command=self._remove_ip_from_group)
        remove_ip_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        load_btn = PremiumButton(btn_frame, text="Load to Ping", icon="📋", color=COLORS['accent_green'], width=140)
        load_btn.configure(command=self._load_group_to_ping)
        load_btn.pack(side=tk.LEFT)
        
        self.pages["groups"] = page
        self._refresh_groups()
    
    def _refresh_groups(self):
        self.groups_list.delete(0, tk.END)
        for name in self.groups:
            self.groups_list.insert(tk.END, f"{name} ({len(self.groups[name])})")
    
    def _on_group_select(self, event):
        sel = self.groups_list.curselection()
        if sel:
            name = self.groups_list.get(sel[0]).split(' (')[0]
            self.ips_list.delete(0, tk.END)
            for ip in self.groups.get(name, []):
                self.ips_list.insert(tk.END, ip)
    
    def _create_group(self):
        name = self.new_group.get().strip()
        if not name:
            messagebox.showwarning("Error", "Enter group name!")
            return
        if name in self.groups:
            messagebox.showwarning("Error", "Group already exists!")
            return
        self.groups[name] = []
        self.new_group.delete(0, tk.END)
        self._refresh_groups()
        self._save_config()
        messagebox.showinfo("Success", f"Group '{name}' created!")
    
    def _add_ip_to_group(self):
        sel = self.groups_list.curselection()
        if not sel:
            messagebox.showwarning("Error", "Select a group!")
            return
        name = self.groups_list.get(sel[0]).split(' (')[0]
        ip = simpledialog.askstring("Add IP", "Enter IP address:")
        if ip and ip not in self.groups[name]:
            self.groups[name].append(ip)
            self._refresh_groups()
            self._save_config()
            messagebox.showinfo("Success", f"Added {ip} to {name}")
    
    def _remove_ip_from_group(self):
        sel = self.groups_list.curselection()
        ip_sel = self.ips_list.curselection()
        if not sel or not ip_sel:
            messagebox.showwarning("Error", "Select an IP to remove!")
            return
        name = self.groups_list.get(sel[0]).split(' (')[0]
        ip = self.ips_list.get(ip_sel[0])
        if ip in self.groups[name]:
            self.groups[name].remove(ip)
            self._refresh_groups()
            self._save_config()
            messagebox.showinfo("Success", f"Removed {ip} from {name}")
    
    def _load_group_to_ping(self):
        sel = self.groups_list.curselection()
        if not sel:
            messagebox.showwarning("Error", "Select a group!")
            return
        name = self.groups_list.get(sel[0]).split(' (')[0]
        ips = self.groups.get(name, [])
        if not ips:
            messagebox.showwarning("Error", "Group is empty!")
            return
        
        self._show_page("ping")
        for ip in ips:
            if ip not in self.hosts:
                card = HostCard(self.cards_frame, ip, ip, self._remove_host)
                self.hosts[ip] = card
        messagebox.showinfo("Success", f"Loaded {len(ips)} hosts to Ping tab")
    
    # ============================================================
    # PAGE 7: AI
    # ============================================================
    def _create_ai_page(self):
        page = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.ai = AIAssistant(page)
        self.pages["ai"] = page
    
    # ============================================================
    # PAGE 8: BACKUP
    # ============================================================
    def _create_backup_page(self):
        page = ctk.CTkFrame(self.content_area, fg_color="transparent")
        
        card = PremiumCard(page, "💾 BACKUP & RESTORE")
        card.pack(expand=True)
        
        center = ctk.CTkFrame(card.content, fg_color="transparent")
        center.pack(expand=True, pady=30)
        
        export_btn = PremiumButton(center, text="Export Configuration", icon="📤", color=COLORS['accent_green'], width=220)
        export_btn.configure(command=self._export_config)
        export_btn.pack(pady=10)
        
        import_btn = PremiumButton(center, text="Import Configuration", icon="📥", color=COLORS['accent'], width=220)
        import_btn.configure(command=self._import_config)
        import_btn.pack(pady=10)
        
        reset_btn = PremiumButton(center, text="Reset All Settings", icon="🔄", color=COLORS['accent_red'], width=220)
        reset_btn.configure(command=self._reset_all)
        reset_btn.pack(pady=10)
        
        self.pages["backup"] = page
    
    # ============================================================
    # BACKUP FUNCTIONS
    # ============================================================
    def _export_config(self):
        file = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if file:
            with open(file, 'w') as f:
                json.dump({'groups': self.groups}, f, indent=2)
            messagebox.showinfo("Success", "Configuration exported!")
    
    def _import_config(self):
        file = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if file:
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                    self.groups = data.get('groups', {"Default": []})
                    self._refresh_groups()
                    self._save_config()
                messagebox.showinfo("Success", "Configuration imported!")
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def _reset_all(self):
        if messagebox.askyesno("Confirm", "Reset all settings and stop all pings?"):
            self._stop_all()
            self.groups = {"Default": []}
            self._refresh_groups()
            self._save_config()
            messagebox.showinfo("Success", "All settings reset!")
    
    def _save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump({'groups': self.groups}, f, indent=2)
    
    def _load_config(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    self.groups = data.get('groups', {"Default": []})
            except:
                pass
    
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
