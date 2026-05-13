#!/usr/bin/env python3
"""
NETWORK TOOL ULTIMATE v3.1 - FIXED COLOR
Full 8 Functions: PING | TRACEROUTE | SCAN IP | PORT SCAN | ANALYSIS | GROUPS | BACKUP | INFO
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
import base64
from io import BytesIO

# ============================================================================
# KIỂM TRA PIL CHO ẢNH
# ============================================================================
try:
    from PIL import Image, ImageTk
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

# ============================================================================
# ẢNH SỨA BASE64
# ============================================================================
JELLYFISH_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAAMgAAADICAYAAACtWK6eAAAACXBIWXMAAAsTAAALEwEAmpwYAAAF8GlUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4gPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iQWRvYmUgWE1QIENvcmUgNS42LWMxNDUgNzkuMTYzNDk5LCAyMDE4LzA4LzEzLTE2OjQwOjIyICAgICAgICAiPiA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPiA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIiB4bWxuczp4bXA9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8iIHhtbG5zOnhtcE1NPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvbW0vIiB4bWxuczpzdFJlZj0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL3NUeXBlL1Jlc291cmNlUmVmIyIgeG1wOkNyZWF0b3JUb29sPSJBZG9iZSBQaG90b3Nob3AgQ0MgMjAxOSAoV2luZG93cykiIHhtcE1NOkluc3RhbmNlSUQ9InhtcC5paWQ6M0I5MjI5RjQxQkFCMTFFQTgzMDhFODM5RkY5MjAzQzgiIHhtcE1NOkRvY3VtZW50SUQ9InhtcC5kaWQ6M0I5MjI5RjUxQkFCMTFFQTgzMDhFODM5RkY5MjAzQzgiPiA8eG1wTU06RGVyaXZlZEZyb20gc3RSZWY6aW5zdGFuY2VJRD0ieG1wLmlpZDozQjkyMjlGMjFCQUIxMUVBODMwOEU4MzlGRjkyMDNDOCIgc3RSZWY6ZG9jdW1lbnRJRD0ieG1wLmRpZDozQjkyMjlGMzFCQUIxMUVBODMwOEU4MzlGRjkyMDNDOCIvPiA8L3JkZjpEZXNjcmlwdGlvbj4gPC9yZGY6UkRGPiA8L3g6eG1wbWV0YT4gPD94cGFja2V0IGVuZD0iciI/Pk3I/YYAAAY5SURBVHic7dpPaBxVHMfx7yRtsu0f0pCmaRMyNfQgooKxgqAieBBBxIt48SIoKnhRSk+lFy+CgngQRDx48CCIh+KhUEFBwYsoNQhGLdImaZNmN81ump3d7Gx3szPzm9/vax+Y2W0y833v/T2P8GYCgUAgEAgEAoFAIBAIBAKBQCAQCAQCgUAgEAgEAoFAIBAIBAKBQCAQCAQCgb1Wx+MG6qiqqnK5XDAMAwCgKAqyLIuqqoiiCACqqiKKIoqiwLIsVFXlVFVFlmXoug4AUBQFwzAghBAiYRiGiKIIVVUBAKqqwjAMCCGEQAhBGIYhyLIMXdfhcrkghBAIISCEQEVFBSzLgmVZMExVVaFpGgAAuq5DURRYloUQQoRlWYiiCEVRAACyLMPlckGSJBiGASEEIBgGpmkCQojQdR2yLAsAkCQJkiSBEAIhBKqqAgBM0wQhhIi6rsMwDMiyDCEEYRiGEEIQwzBQFAUAgKIokCQJQggEQUC5XA6GYSC6rsM0TQghEIZhIISAEAIhBKqqAgBM0wQhhIjrug5d1yFJEgBAlmW4XC7U1dWBEAJhGIZQFAVCCJHL5SCEAAAgSRJcLhc0TQMAaJoGVVUBABBCIISAEAKapiEIAsIwDMSyLITL5YIkSZBleVzTNMiyjEwmgxBCIISAEAKGYcA0TQghEIZhCMMwAAAIIZBlaVzTNEiSBFVVIYQAhBAIIZBlGZqmjWuaBkEQEAQBwzAEQUCSJBiGgXw+D0EQAADjsiwjhAC2KkIICCGwLAuSJEFRFITDYXAcB0mSBACwLAuWZYEQAkKIYRjGZVkGx3GQZRmapkFRFCiKAo7jIEmSAAAQQsBxHIQQiKKIYRgG0zQBACzLorq6GqZpAgBM08S4JEmQJGncMAwQQiBJ0rikKApUVYXH40EwGITL5YIkSQAAWJYF0zQhSRJkWcYwDAMhBAAgSRI8Hg9UVQUAwDRN1NbWwjRNCCEwTRMAgGEYCCEAAKZpAhBCIEmSODtlCAAgSRI8Hg+8Xi8EQQAAME0TqqoiEAgAAFRVhSzLkCQJmqYhGAyC4zgAAJqmwev1YmZmBrquYxwAoKoqKIoCABiGgWVZUBSFqakp1NXVYffu3eA4DgAA0zRBCAGGYaCqKmRZRjgcRjgcBkIITNMEIcS4JEnjlyhSFEUIIRBFEeFwGJIkAQBQVVXFNE2Ew2Fs3rwZq1evhizL4DgO0WgUmqZh/vz5qKiogKqqiEajCIfD0DQNkiSBYRgAyJ/xVCqFVCqFYRiiLAuWZQEgiUQCU1NT6O3tRSgUQnV1NViWxTgAqKoKXddBCIFpmrBtG4qigGEYJJNJSJKE8Xg8DgAghGB6ehrJZBJerxcejweapuHFF18EIQTj4XAYS5YsQSaTwRNPPIHbbrsNANDa2orHH38cPp8PBw4cQHl5Ocbj8TgAgO/7AQDc932cz+fhcrkw54cffsCjjz6KAwcOoK+vD9PT05AkCSNGUWQYYRhGUJZlcBwHl8sFmqaRy+Vw8eJFjI2NIZfL4fTp0/jjjz9ACIFhGLAuETyGYYzn83lks1lEo1FUVlaio6MDExMTOHHiBJa0tSGbzSIajcLv9yN34gRqamrQ2NCAgwcPQtd1jAOAruuIx+MAALfbDYvjEIlEUF1djcHBQVy8eBHRaBQ8cVFRUYHu7m6sWLECy5cvx+zZswFkh9loNIpkMolFixahoqICzL/C4/GAYRjE43HMmjULvu5u9Pf3Y+vWrXjnnXdACIFpmiCEQNM0mKaJ8fHx8fH/qdfrhSzLQO5jPL/zEwBQ1+04u3M3mG3bkDt6FABQV1eHWCyGQCCA6upqVFdXI5FIYHh4GOFwGLquIxAIwDRNRKNRSJKEaDSK9vZ2jI2Nged5uN1u2LYNlmVRXV2NVCqFQCAAd3MzYrEY2traIEmS+AwAMQwDgiAAILIsi2EYYjwYDIJhGNEwDEiSJHo8HhFAPsaRZVmEEBPDwSBYloVlWSIhBIfDYUQiEezfvx+GYaClpQXbtm1DZ2cnUqkUdu7ciZ6eHkSjUfFeAKJhGIAQAl3Xkc/nkU6n4Xa7sXjxYqTTaczOzsakp1mMx+MQRRGyLONYKIRAIABCCERRhCRJIAABT0cHzp8/j46ODoyMjKB85UqU//ILwvww7LkKs7OzoWkaWJbF/8q+/74HAGCaJgRBACEEiUQCqqoiHo/DNE0QQiCKInRdRzAYhCiKyOfzoCgKHMcBAKqrq3HvvfciHA6D4zg0NjZidnY2pk8VASDLMizLQnV1NcLhMDZt2oT5Pp/pcrnQ1NSEdDoNhmHQ1NQEIQRcLhckSYJgWRYcx0FRFFRXV6OhoQFjY2NobGzE1NQUysrK4PH7YVkWwuEwLMuCqqoIhULgOA4Mw0CSJMjy/7kqCIKAYVlomoY777wTkUgE+Xwes7OzsXnzZnR3d+Pll19GfX09/H4/NE0Dx3EAgEwmA0mSwPM8hGEYcBwHQRAgiiIsy0I0GoVlWbAsC+EyGeRyOVRXV2PZsmVYuHAhmpub0dXVhQ0bNsBw3gOisbERyD2+fr8fgUAAw+EwqqurwXEcKisrQQiBqqpYvXo1hBDMzs4GAKhqVQXX4cNgli2D4QwFpVIJwWAQbre7lE6n/1VRAoFAIBAIBAKBQCAQCAQCgUAgEAgEAoFAIBAIBAKBQCAQCAQCgcD+1H8Sqs9FqMq8yQAAAABJRU5ErkJggg=="

def get_jellyfish_image():
    if not PILLOW_AVAILABLE:
        return None
    try:
        img_data = base64.b64decode(JELLYFISH_BASE64)
        img = Image.open(BytesIO(img_data))
        img = img.resize((180, 180), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)
    except:
        return None

# ============================================================================
# HỆ ĐIỀU HÀNH
# ============================================================================
SYSTEM = platform.system().lower()
IS_WINDOWS = SYSTEM == 'windows'

# ============================================================================
# MÀU SẮC - FIXED (KHÔNG ALPHA CHANNEL)
# ============================================================================
COLORS = {
    'bg_deep': '#020617',
    'bg_mid': '#0F172A',
    'card_glass': '#1E293B',      # Đã bỏ alpha CC
    'border_neon': '#06B6D4',
    'neon_cyan': '#00F0FF',
    'neon_pink': '#FF007F',
    'neon_purple': '#A855F7',
    'neon_green': '#10B981',
    'neon_orange': '#F97316',
    'text_glow': '#FFFFFF',
    'text_dim': '#94A3B8',
    'success': '#34D399',
    'error': '#F87171',
    'warning': '#FBBF24',
}

# ============================================================================
# LỚP NỀN SỨA BƠI
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
            self.create_oval(80, 250, 160, 330, fill="#38BDF8", outline="#22D3EE", width=2, tags="jellyfish")
            for i in range(6):
                self.create_line(100 + i*10, 330, 90 + i*15, 400, fill="#22D3EE", width=2, tags="jellyfish")
    
    def animate_jellyfish(self):
        if self.jellyfish_photo and self.winfo_width() > 0:
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
# GLASS CARD (KHÔNG ALPHA)
# ============================================================================
class GlassCard(tk.Frame):
    def __init__(self, parent, title=""):
        super().__init__(parent, bg=COLORS['card_glass'], highlightbackground=COLORS['border_neon'], highlightthickness=1, bd=1, relief=tk.RAISED)
        if title:
            tk.Label(self, text=title, bg=COLORS['card_glass'], fg=COLORS['neon_cyan'], font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=12, pady=(8, 0))
        self.content = tk.Frame(self, bg=COLORS['card_glass'])
        self.content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# ============================================================================
# HOST CARD
# ============================================================================
class HostCard(tk.Frame):
    def __init__(self, parent, ip, name, on_remove):
        super().__init__(parent, bg=COLORS['bg_mid'], bd=1, relief=tk.FLAT, 
                        highlightbackground=COLORS['border_neon'], highlightthickness=1)
        self.ip = ip
        self.name = name
        self.on_remove = on_remove
        self.running = True
        self.queue = queue.Queue()
        self.last_update = 0
        self.update_interval = 3
        self.mac = self._get_mac()
        self.vlan = "Default"
        self.vnc_user = ""
        self.vnc_pass = ""
        self.notes = ""
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
        
        for text, cmd, color in [("SSH", self._ssh, COLORS['neon_cyan']), 
                                  ("HTTP", self._http, COLORS['neon_green']), 
                                  ("VNC", self._vnc, COLORS['neon_pink']), 
                                  ("RDP", self._rdp, COLORS['neon_purple'])]:
            btn = tk.Button(btn_row, text=text, bg=COLORS['bg_deep'], fg=color, 
                          font=('Segoe UI', 8, 'bold'), relief=tk.FLAT, command=cmd)
            btn.pack(side=tk.LEFT, padx=4, expand=True, fill=tk.X)
    
    def _get_mac(self):
        try:
            cmd = ['arp', '-a', self.ip] if IS_WINDOWS else ['arp', '-n', self.ip]
            out = subprocess.check_output(cmd, universal_newlines=True, timeout=3)
            mac = re.search(r'([0-9a-fA-F]{2}[:-]){5}([0-9a-fA-F]{2})', out)
            return mac.group(0) if mac else "Unknown"
        except:
            return "Unknown"
    
    def _ping_once(self):
        try:
            param = '-n' if IS_WINDOWS else '-c'
            cmd = ['ping', param, '1', '-W', '1', self.ip]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
            success = result.returncode == 0
            times = re.findall(r'time[= ](\d+\.?\d*)\s*ms', result.stdout.lower())
            avg = float(times[0]) if times else None
            return {'success': success, 'avg': avg}
        except:
            return {'success': False, 'avg': None}
    
    def _start_ping(self):
        def loop():
            while self.running:
                current = time.time()
                if current - self.last_update >= self.update_interval:
                    r = self._ping_once()
                    self.queue.put(r)
                    self.mac = self._get_mac()
                    self.last_update = current
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
                        txt = f"✓ ONLINE | Ping: {r['avg']:.0f}ms" if r['avg'] else "✓ ONLINE"
                        self.stats_text.config(text=txt, fg=COLORS['success'])
                    else:
                        self.led.config(fg=COLORS['error'])
                        self.stats_text.config(text="✗ OFFLINE", fg=COLORS['error'])
            except:
                pass
            time.sleep(0.5)
    
    def _settings(self):
        win = tk.Toplevel(self)
        win.title(f"Cài đặt {self.name}")
        win.geometry("400x350")
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
        
        tk.Label(win, text="Ghi chú:", bg=COLORS['bg_mid'], fg='white').pack(anchor=tk.W, padx=15, pady=(10,0))
        notes_t = tk.Text(win, bg=COLORS['bg_deep'], fg='white', height=4)
        notes_t.insert("1.0", self.notes)
        notes_t.pack(fill=tk.X, padx=15, pady=5)
        
        def save():
            self.vlan = vlan_e.get()
            self.vnc_user = user_e.get()
            self.vnc_pass = pass_e.get()
            self.notes = notes_t.get("1.0", tk.END).strip()
            win.destroy()
            messagebox.showinfo("Thành công", "Đã lưu cài đặt!")
        
        tk.Button(win, text="Lưu", command=save, bg=COLORS['neon_cyan'], fg='black', font=('Segoe UI', 10, 'bold')).pack(pady=15)
    
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
        try:
            subprocess.Popen(['vncviewer', self.ip])
        except:
            messagebox.showerror("Lỗi", "VNC Viewer chưa được cài đặt!")
    
    def _remove(self):
        self.running = False
        self.destroy()
        if self.on_remove:
            self.on_remove(self.ip)
    
    def stop(self):
        self.running = False

# ============================================================================
# MAIN APP
# ============================================================================
class NetToolApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🐙 NETWORK TOOL ULTIMATE v3.1")
        self.root.geometry("1500x900")
        
        self.bg_canvas = JellyfishBackground(self.root)
        self.bg_canvas.pack(fill=tk.BOTH, expand=True)
        
        self.main_container = tk.Frame(self.bg_canvas, bg='')
        self.main_container.place(relwidth=1, relheight=1)
        
        self.hosts = {}
        self.groups = {"Default": []}
        self.config_file = Path.home() / ".network_tool.json"
        
        self._create_ui()
        self._load_config()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _create_ui(self):
        # Header
        header = tk.Frame(self.main_container, bg=COLORS['card_glass'], 
                         highlightbackground=COLORS['border_neon'], highlightthickness=1)
        header.pack(fill=tk.X, pady=10, padx=15)
        
        tk.Label(header, text="🌊 NETWORK TOOL ULTIMATE", bg=COLORS['card_glass'], 
                fg=COLORS['neon_cyan'], font=('Segoe UI', 18, 'bold')).pack(side=tk.LEFT, padx=20)
        tk.Label(header, text="🐙 Jellyfish 3D", bg=COLORS['card_glass'], 
                fg=COLORS['neon_pink'], font=('Segoe UI', 10)).pack(side=tk.LEFT)
        
        self.status_bar = tk.Label(header, text="✓ Sẵn sàng", bg=COLORS['card_glass'], 
                                   fg=COLORS['neon_green'], font=('Segoe UI', 9))
        self.status_bar.pack(side=tk.RIGHT, padx=20)
        
        # Sidebar
        sidebar = tk.Frame(self.main_container, bg=COLORS['card_glass'], width=140,
                          highlightbackground=COLORS['border_neon'], highlightthickness=1)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=15, pady=10)
        sidebar.pack_propagate(False)
        
        logo = tk.Frame(sidebar, bg=COLORS['neon_cyan'], height=70)
        logo.pack(fill=tk.X, pady=(10, 20))
        tk.Label(logo, text="🐙", bg=COLORS['neon_cyan'], fg='black', font=('Arial', 28)).pack(pady=10)
        
        nav_items = [
            ("📡 PING", self.show_ping, COLORS['neon_cyan']),
            ("🗺️ TRACEROUTE", self.show_trace, COLORS['neon_purple']),
            ("🔍 SCAN IP", self.show_scan, COLORS['neon_green']),
            ("🔌 PORT SCAN", self.show_ports, COLORS['neon_orange']),
            ("📊 ANALYSIS", self.show_analysis, COLORS['neon_pink']),
            ("📋 GROUPS", self.show_groups, COLORS['neon_cyan']),
            ("💾 BACKUP", self.show_backup, COLORS['neon_green']),
            ("ℹ️ INFO", self.show_info, COLORS['neon_purple']),
        ]
        
        for text, cmd, color in nav_items:
            btn = NeonButton(sidebar, text=text, command=cmd, color=color, width=12)
            btn.pack(pady=6, padx=10)
        
        # Content
        self.content = tk.Frame(self.main_container, bg=COLORS['card_glass'])
        self.content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.pages = {}
        self._build_ping_tab()
        self._build_traceroute_tab()
        self._build_scan_tab()
        self._build_portscan_tab()
        self._build_analysis_tab()
        self._build_groups_tab()
        self._build_backup_tab()
        self._build_info_tab()
        
        self.show_ping()
    
    # ==================== TAB 1: PING ====================
    def _build_ping_tab(self):
        page = tk.Frame(self.content, bg=COLORS['card_glass'])
        
        add_card = GlassCard(page, "🐙 THÊM HOST GIÁM SÁT")
        add_card.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        row = tk.Frame(add_card.content, bg=COLORS['card_glass'])
        row.pack(fill=tk.X)
        
        tk.Label(row, text="IP:", bg=COLORS['card_glass'], fg=COLORS['text_glow']).pack(side=tk.LEFT, padx=5)
        self.ping_ip = tk.Entry(row, bg=COLORS['bg_mid'], fg='white', width=18, insertbackground=COLORS['neon_cyan'])
        self.ping_ip.pack(side=tk.LEFT, padx=5)
        self.ping_ip.insert(0, "8.8.8.8")
        
        tk.Label(row, text="Tên:", bg=COLORS['card_glass'], fg=COLORS['text_glow']).pack(side=tk.LEFT, padx=5)
        self.ping_name = tk.Entry(row, bg=COLORS['bg_mid'], fg='white', width=18, insertbackground=COLORS['neon_cyan'])
        self.ping_name.pack(side=tk.LEFT, padx=5)
        self.ping_name.insert(0, "Google DNS")
        
        NeonButton(row, "➕ Thêm Host", self._add_host, COLORS['neon_green'], 12).pack(side=tk.LEFT, padx=10)
        NeonButton(row, "⏹️ Dừng tất cả", self._stop_all, COLORS['error'], 12).pack(side=tk.LEFT)
        
        # Quick Ping
        quick_card = GlassCard(page, "⚡ QUICK PING")
        quick_card.pack(fill=tk.X, padx=20, pady=10)
        
        qrow = tk.Frame(quick_card.content, bg=COLORS['card_glass'])
        qrow.pack(fill=tk.X)
        
        self.quick_ip = tk.Entry(qrow, bg=COLORS['bg_mid'], fg='white', width=25, insertbackground=COLORS['neon_cyan'])
        self.quick_ip.pack(side=tk.LEFT, padx=5)
        self.quick_ip.insert(0, "8.8.8.8")
        
        NeonButton(qrow, "Ping", self._quick_ping, COLORS['neon_cyan'], 10).pack(side=tk.LEFT, padx=10)
        
        self.quick_result = tk.Text(quick_card.content, bg=COLORS['bg_mid'], fg=COLORS['text_glow'], height=3, font=('Consolas', 9))
        self.quick_result.pack(fill=tk.X, pady=10)
        
        # Hosts container
        hosts_card = GlassCard(page, "📡 DANH SÁCH GIÁM SÁT")
        hosts_card.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.hosts_container = tk.Frame(hosts_card.content, bg=COLORS['card_glass'])
        self.hosts_container.pack(fill=tk.BOTH, expand=True)
        
        self.pages["ping"] = page
    
    def _quick_ping(self):
        host = self.quick_ip.get().strip()
        if not host:
            return
        self.quick_result.delete("1.0", tk.END)
        self.quick_result.insert("1.0", f"⏳ Đang ping {host}...")
        
        def do():
            r = self._ping_host(host, 4)
            def up():
                self.quick_result.delete("1.0", tk.END)
                if r['success']:
                    self.quick_result.insert("1.0", f"✅ {host} ONLINE\n📊 Loss: {r['loss']:.0f}%\n⏱️ Min: {r['min']:.1f}ms | Avg: {r['avg']:.1f}ms | Max: {r['max']:.1f}ms")
                else:
                    self.quick_result.insert("1.0", f"❌ {host} OFFLINE - Không có phản hồi")
            self.root.after(0, up)
        threading.Thread(target=do, daemon=True).start()
    
    def _ping_host(self, host, count=4):
        try:
            param = '-n' if IS_WINDOWS else '-c'
            cmd = ['ping', param, str(count), '-W', '2', host]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            output = result.stdout.lower()
            times = re.findall(r'time[= ](\d+\.?\d*)\s*ms', output)
            times = [float(t) for t in times]
            if IS_WINDOWS:
                lost = output.count('timed out') + output.count('unreachable')
                loss = (lost / count * 100)
            else:
                loss_m = re.search(r'(\d+)% packet loss', output)
                loss = int(loss_m.group(1)) if loss_m else 0
            return {
                'success': len(times) > 0,
                'loss': loss,
                'min': min(times) if times else 0,
                'max': max(times) if times else 0,
                'avg': sum(times)/len(times) if times else 0
            }
        except:
            return {'success': False, 'loss': 100, 'min': 0, 'max': 0, 'avg': 0}
    
    def _add_host(self):
        ip = self.ping_ip.get().strip()
        name = self.ping_name.get().strip()
        if not ip:
            return
        if not name:
            name = ip
        if ip in self.hosts:
            messagebox.showwarning("Cảnh báo", "Host đã tồn tại!")
            return
        card = HostCard(self.hosts_container, ip, name, self._remove_host)
        self.hosts[ip] = card
        self._save_config()
        self.status_bar.config(text=f"✓ Đã thêm {name}")
    
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
        self.status_bar.config(text="✓ Đã dừng tất cả")
    
    # ==================== TAB 2: TRACEROUTE ====================
    def _build_traceroute_tab(self):
        page = tk.Frame(self.content, bg=COLORS['card_glass'])
        
        card = GlassCard(page, "🗺️ TRACEROUTE")
        card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        row = tk.Frame(card.content, bg=COLORS['card_glass'])
        row.pack(fill=tk.X, pady=10)
        
        self.trace_target = tk.Entry(row, bg=COLORS['bg_mid'], fg='white', width=30, insertbackground=COLORS['neon_cyan'])
        self.trace_target.pack(side=tk.LEFT, padx=5)
        self.trace_target.insert(0, "8.8.8.8")
        
        NeonButton(row, "Trace", self._run_trace, COLORS['neon_purple'], 10).pack(side=tk.LEFT, padx=10)
        
        self.trace_text = tk.Text(card.content, bg=COLORS['bg_mid'], fg=COLORS['text_glow'], font=('Consolas', 9))
        self.trace_text.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.pages["trace"] = page
    
    def _run_trace(self):
        host = self.trace_target.get().strip()
        if not host:
            return
        self.trace_text.delete("1.0", tk.END)
        self.trace_text.insert("1.0", f"⏳ Đang trace đến {host}...\n")
        
        def do():
            try:
                cmd = ['tracert', '-d', host] if IS_WINDOWS else ['traceroute', '-n', host]
                out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, universal_newlines=True, timeout=60)
                self.trace_text.delete("1.0", tk.END)
                self.trace_text.insert("1.0", out)
            except Exception as e:
                self.trace_text.delete("1.0", tk.END)
                self.trace_text.insert("1.0", f"Lỗi: {e}")
        threading.Thread(target=do, daemon=True).start()
    
    # ==================== TAB 3: SCAN IP ====================
    def _build_scan_tab(self):
        page = tk.Frame(self.content, bg=COLORS['card_glass'])
        
        card = GlassCard(page, "🔍 SCAN MẠNG (CIDR)")
        card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        row = tk.Frame(card.content, bg=COLORS['card_glass'])
        row.pack(fill=tk.X, pady=10)
        
        self.cidr_entry = tk.Entry(row, bg=COLORS['bg_mid'], fg='white', width=25, insertbackground=COLORS['neon_cyan'])
        self.cidr_entry.pack(side=tk.LEFT, padx=5)
        self.cidr_entry.insert(0, "192.168.1.0/24")
        
        NeonButton(row, "Scan", self._run_scan, COLORS['neon_green'], 10).pack(side=tk.LEFT, padx=10)
        
        # Treeview
        self.scan_tree = ttk.Treeview(card.content, columns=('IP', 'Status', 'MAC'), height=18)
        self.scan_tree.heading('#0', text='')
        self.scan_tree.heading('IP', text='IP Address')
        self.scan_tree.heading('Status', text='Status')
        self.scan_tree.heading('MAC', text='MAC Address')
        self.scan_tree.column('#0', width=0)
        self.scan_tree.column('IP', width=150)
        self.scan_tree.column('Status', width=100)
        self.scan_tree.column('MAC', width=180)
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', background=COLORS['bg_mid'], foreground=COLORS['text_glow'], fieldbackground=COLORS['bg_mid'])
        style.configure('Treeview.Heading', background=COLORS['card_glass'], foreground=COLORS['neon_cyan'])
        
        self.scan_tree.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.pages["scan"] = page
    
    def _run_scan(self):
        cidr = self.cidr_entry.get().strip()
        if not cidr:
            return
        self.scan_tree.delete(*self.scan_tree.get_children())
        self.status_bar.config(text="🔍 Đang quét mạng...")
        
        def do():
            try:
                net = ipaddress.ip_network(cidr, strict=False)
                def ping_ip(ip):
                    r = self._ping_host(str(ip), 1)
                    if r['success']:
                        mac = self._get_mac_from_arp(str(ip))
                        self.root.after(0, lambda i=str(ip), m=mac: self.scan_tree.insert('', tk.END, values=(i, "✅ ONLINE", m)))
                with ThreadPoolExecutor(max_workers=30) as ex:
                    ex.map(ping_ip, net.hosts())
                self.root.after(0, lambda: self.status_bar.config(text="✅ Đã quét xong"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Lỗi", str(e)))
        threading.Thread(target=do, daemon=True).start()
    
    def _get_mac_from_arp(self, ip):
        try:
            cmd = ['arp', '-a', ip] if IS_WINDOWS else ['arp', '-n', ip]
            out = subprocess.check_output(cmd, universal_newlines=True, timeout=3)
            mac = re.search(r'([0-9a-fA-F]{2}[:-]){5}([0-9a-fA-F]{2})', out)
            return mac.group(0) if mac else "Unknown"
        except:
            return "Unknown"
    
    # ==================== TAB 4: PORT SCAN ====================
    def _build_portscan_tab(self):
        page = tk.Frame(self.content, bg=COLORS['card_glass'])
        
        card = GlassCard(page, "🔌 PORT SCANNER")
        card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        row = tk.Frame(card.content, bg=COLORS['card_glass'])
        row.pack(fill=tk.X, pady=10)
        
        tk.Label(row, text="IP:", bg=COLORS['card_glass'], fg=COLORS['text_glow']).pack(side=tk.LEFT, padx=5)
        self.port_target = tk.Entry(row, bg=COLORS['bg_mid'], fg='white', width=15, insertbackground=COLORS['neon_cyan'])
        self.port_target.pack(side=tk.LEFT, padx=5)
        self.port_target.insert(0, "127.0.0.1")
        
        tk.Label(row, text="Ports:", bg=COLORS['card_glass'], fg=COLORS['text_glow']).pack(side=tk.LEFT, padx=5)
        self.port_list = tk.Entry(row, bg=COLORS['bg_mid'], fg='white', width=30, insertbackground=COLORS['neon_cyan'])
        self.port_list.pack(side=tk.LEFT, padx=5)
        self.port_list.insert(0, "22,80,443,3306,5432,8080")
        
        NeonButton(row, "Scan", self._scan_ports, COLORS['neon_orange'], 10).pack(side=tk.LEFT, padx=10)
        
        self.port_tree = ttk.Treeview(card.content, columns=('Port', 'Status', 'Service'), height=18)
        self.port_tree.heading('#0', text='')
        self.port_tree.heading('Port', text='Port')
        self.port_tree.heading('Status', text='Status')
        self.port_tree.heading('Service', text='Service')
        self.port_tree.column('#0', width=0)
        self.port_tree.column('Port', width=100)
        self.port_tree.column('Status', width=100)
        self.port_tree.column('Service', width=150)
        self.port_tree.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.pages["ports"] = page
    
    def _scan_ports(self):
        target = self.port_target.get().strip()
        ports_str = self.port_list.get().strip()
        if not target or not ports_str:
            return
        
        ports = []
        for p in ports_str.split(','):
            p = p.strip()
            try:
                ports.append(int(p))
            except:
                pass
        
        self.port_tree.delete(*self.port_tree.get_children())
        services = {22: 'SSH', 80: 'HTTP', 443: 'HTTPS', 3306: 'MySQL', 5432: 'PostgreSQL', 8080: 'HTTP-Alt', 3389: 'RDP', 5900: 'VNC'}
        self.status_bar.config(text=f"🔍 Đang quét {len(ports)} cổng trên {target}...")
        
        def check(p):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.3)
                result = s.connect_ex((target, p)) == 0
                s.close()
                if result:
                    self.root.after(0, lambda port=p: self.port_tree.insert('', tk.END, values=(port, "✅ OPEN", services.get(port, "Unknown"))))
            except:
                pass
        
        def do():
            with ThreadPoolExecutor(max_workers=50) as ex:
                ex.map(check, ports)
            self.root.after(0, lambda: self.status_bar.config(text="✅ Đã quét xong"))
        
        threading.Thread(target=do, daemon=True).start()
    
    # ==================== TAB 5: ANALYSIS ====================
    def _build_analysis_tab(self):
        page = tk.Frame(self.content, bg=COLORS['card_glass'])
        
        card = GlassCard(page, "📊 PHÂN TÍCH MẠNG")
        card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        NeonButton(card.content, "Phân tích", self._analyze, COLORS['neon_pink'], 15).pack(pady=10)
        
        self.analysis_text = tk.Text(card.content, bg=COLORS['bg_mid'], fg=COLORS['text_glow'], font=('Consolas', 10))
        self.analysis_text.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.pages["analysis"] = page
    
    def _analyze(self):
        self.analysis_text.delete("1.0", tk.END)
        local_ip = self._get_local_ip()
        self.analysis_text.insert("1.0", f"📡 THÔNG TIN MẠNG\n{'-'*40}\n")
        self.analysis_text.insert(tk.END, f"🖥️ IP cục bộ: {local_ip}\n")
        self.analysis_text.insert(tk.END, f"🐙 Host đang giám sát: {len(self.hosts)}\n")
        self.analysis_text.insert(tk.END, f"📋 Số nhóm: {len(self.groups)}\n")
        self.analysis_text.insert(tk.END, f"\n💡 Gợi ý:\n")
        self.analysis_text.insert(tk.END, f"   • Thêm host vào danh sách giám sát\n")
        self.analysis_text.insert(tk.END, f"   • Tạo nhóm để quản lý nhiều IP\n")
        self.analysis_text.insert(tk.END, f"   • Xuất cấu hình để backup\n")
    
    def _get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    # ==================== TAB 6: GROUPS ====================
    def _build_groups_tab(self):
        page = tk.Frame(self.content, bg=COLORS['card_glass'])
        
        card = GlassCard(page, "📋 QUẢN LÝ NHÓM")
        card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create group
        row = tk.Frame(card.content, bg=COLORS['card_glass'])
        row.pack(fill=tk.X, pady=10)
        
        self.new_group_name = tk.Entry(row, bg=COLORS['bg_mid'], fg='white', width=20, insertbackground=COLORS['neon_cyan'])
        self.new_group_name.pack(side=tk.LEFT, padx=5)
        
        NeonButton(row, "Tạo nhóm", self._create_group, COLORS['neon_green'], 12).pack(side=tk.LEFT, padx=10)
        
        # Lists
        list_frame = tk.Frame(card.content, bg=COLORS['card_glass'])
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        left = tk.Frame(list_frame, bg=COLORS['bg_mid'], bd=1, relief=tk.SUNKEN)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        tk.Label(left, text="NHÓM", bg=COLORS['bg_mid'], fg=COLORS['neon_cyan']).pack()
        self.groups_list = tk.Listbox(left, bg=COLORS['bg_deep'], fg='white', selectbackground=COLORS['neon_cyan'])
        self.groups_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.groups_list.bind('<<ListboxSelect>>', self._on_group_select)
        
        right = tk.Frame(list_frame, bg=COLORS['bg_mid'], bd=1, relief=tk.SUNKEN)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        tk.Label(right, text="IP TRONG NHÓM", bg=COLORS['bg_mid'], fg=COLORS['neon_cyan']).pack()
        self.ips_list = tk.Listbox(right, bg=COLORS['bg_deep'], fg='white', selectbackground=COLORS['neon_cyan'])
        self.ips_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Buttons
        btn_frame = tk.Frame(card.content, bg=COLORS['card_glass'])
        btn_frame.pack(fill=tk.X, pady=10)
        
        NeonButton(btn_frame, "➕ Thêm IP", self._add_ip_to_group, COLORS['neon_cyan'], 12).pack(side=tk.LEFT, padx=5)
        NeonButton(btn_frame, "❌ Xóa IP", self._remove_ip_from_group, COLORS['error'], 12).pack(side=tk.LEFT, padx=5)
        NeonButton(btn_frame, "📋 Load sang Ping", self._load_group_to_ping, COLORS['neon_green'], 15).pack(side=tk.LEFT, padx=5)
        
        self.pages["groups"] = page
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
        if not name:
            messagebox.showwarning("Lỗi", "Nhập tên nhóm!")
            return
        if name in self.groups:
            messagebox.showwarning("Lỗi", "Nhóm đã tồn tại!")
            return
        self.groups[name] = []
        self.new_group_name.delete(0, tk.END)
        self._refresh_groups()
        self._save_config()
        messagebox.showinfo("Thành công", f"Đã tạo nhóm '{name}'")
    
    def _add_ip_to_group(self):
        sel = self.groups_list.curselection()
        if not sel:
            messagebox.showwarning("Lỗi", "Chọn một nhóm!")
            return
        name = self.groups_list.get(sel[0]).split(' (')[0]
        ip = simpledialog.askstring("Thêm IP", "Nhập địa chỉ IP:")
        if ip and ip not in self.groups[name]:
            self.groups[name].append(ip)
            self._refresh_groups()
            self._save_config()
            messagebox.showinfo("Thành công", f"Đã thêm {ip} vào nhóm {name}")
    
    def _remove_ip_from_group(self):
        sel = self.groups_list.curselection()
        isel = self.ips_list.curselection()
        if not sel or not isel:
            messagebox.showwarning("Lỗi", "Chọn IP cần xóa!")
            return
        name = self.groups_list.get(sel[0]).split(' (')[0]
        ip = self.ips_list.get(isel[0])
        if ip in self.groups[name]:
            self.groups[name].remove(ip)
            self._refresh_groups()
            self._save_config()
            messagebox.showinfo("Thành công", f"Đã xóa {ip} khỏi nhóm {name}")
    
    def _load_group_to_ping(self):
        sel = self.groups_list.curselection()
        if not sel:
            return
        name = self.groups_list.get(sel[0]).split(' (')[0]
        ips = self.groups.get(name, [])
        if not ips:
            messagebox.showwarning("Lỗi", "Nhóm trống!")
            return
        self.show_ping()
        for ip in ips:
            if ip not in self.hosts:
                card = HostCard(self.hosts_container, ip, ip, self._remove_host)
                self.hosts[ip] = card
        messagebox.showinfo("Thành công", f"Đã load {len(ips)} host vào Ping tab")
    
    # ==================== TAB 7: BACKUP ====================
    def _build_backup_tab(self):
        page = tk.Frame(self.content, bg=COLORS['card_glass'])
        
        card = GlassCard(page, "💾 BACKUP & RESTORE")
        card.pack(expand=True, padx=20, pady=20)
        
        center = tk.Frame(card.content, bg=COLORS['card_glass'])
        center.pack(expand=True, pady=30)
        
        NeonButton(center, "📤 Export Config", self._export, COLORS['neon_cyan'], 20).pack(pady=10)
        NeonButton(center, "📥 Import Config", self._import, COLORS['neon_green'], 20).pack(pady=10)
        NeonButton(center, "🔄 Reset All", self._reset_all, COLORS['error'], 20).pack(pady=10)
        
        self.pages["backup"] = page
    
    def _export(self):
        f = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if f:
            data = {'hosts': list(self.hosts.keys()), 'groups': self.groups}
            with open(f, 'w') as fp:
                json.dump(data, fp, indent=2)
            messagebox.showinfo("Thành công", "Đã xuất cấu hình!")
    
    def _import(self):
        f = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if f:
            try:
                with open(f, 'r') as fp:
                    data = json.load(fp)
                for ip in data.get('hosts', []):
                    if ip not in self.hosts:
                        HostCard(self.hosts_container, ip, ip, self._remove_host)
                        self.hosts[ip] = True
                self.groups = data.get('groups', {"Default": []})
                self._refresh_groups()
                self._save_config()
                messagebox.showinfo("Thành công", "Đã nhập cấu hình!")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể import: {e}")
    
    def _reset_all(self):
        if messagebox.askyesno("Xác nhận", "Reset tất cả cài đặt?"):
            self._stop_all()
            self.groups = {"Default": []}
            self._refresh_groups()
            self._save_config()
            messagebox.showinfo("Thành công", "Đã reset tất cả!")
    
    # ==================== TAB 8: INFO ====================
    def _build_info_tab(self):
        page = tk.Frame(self.content, bg=COLORS['card_glass'])
        
        card = GlassCard(page, "ℹ️ THÔNG TIN HỆ THỐNG")
        card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        info_text = f"""
🐙 NETWORK TOOL ULTIMATE v3.1
{'='*40}

✨ TÍNH NĂNG:
  • Ping Monitoring (liên tục, không giật)
  • Traceroute - Xem đường đi mạng
  • Scan IP - Quét mạng CIDR
  • Port Scanner - Quét cổng nhanh
  • Group Management - Quản lý nhóm IP
  • Backup/Restore - Lưu cấu hình
  • VNC/SSH/RDP/HTTP tích hợp

🖥️ THÔNG TIN MÁY:
  • Hệ điều hành: {platform.system()} {platform.release()}
  • Python: {platform.python_version()}
  • IP cục bộ: {self._get_local_ip()}

🐙 Jellyfish 3D Background
{'='*40}
        """
        
        tk.Label(card.content, text=info_text, bg=COLORS['card_glass'], fg=COLORS['text_glow'], 
                font=('Consolas', 10), justify=tk.LEFT).pack(pady=20)
        
        self.pages["info"] = page
    
    # ==================== ĐIỀU HƯỚNG ====================
    def show_ping(self): self._show_page("ping")
    def show_trace(self): self._show_page("trace")
    def show_scan(self): self._show_page("scan")
    def show_ports(self): self._show_page("ports")
    def show_analysis(self): self._show_page("analysis")
    def show_groups(self): self._show_page("groups")
    def show_backup(self): self._show_page("backup")
    def show_info(self): self._show_page("info")
    
    def _show_page(self, name):
        for p in self.pages.values():
            p.pack_forget()
        self.pages[name].pack(fill=tk.BOTH, expand=True)
    
    def _save_config(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump({'hosts': list(self.hosts.keys()), 'groups': self.groups}, f)
        except:
            pass
    
    def _load_config(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                for ip in data.get('hosts', []):
                    if ip not in self.hosts:
                        HostCard(self.hosts_container, ip, ip, self._remove_host)
                        self.hosts[ip] = True
                self.groups = data.get('groups', {"Default": []})
                self._refresh_groups()
            except:
                pass
    
    def _on_close(self):
        self._stop_all()
        self.root.destroy()
    
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = NetToolApp()
    app.run()
