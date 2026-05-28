"""
StrangeCat Monitor  v3.2
- Normal mode : sparkline graphs for CPU / CPU TEMP / RAM / GPU / GPU TEMP / VRAM / Net↓ / Net↑
- Compact mode: simple label+bar+value rows
- Footer (bottom) : temp source · time · HTTP port
- Grid responsive fixed in Graph mode (1-3 cols based on width, without extra scrollbar)
- Resize SE corner only → width drives scale → height auto-fit content
- Global rendering improved : palette, typography, spacing, graphs
"""
import tkinter as tk
from tkinter import ttk
import psutil, subprocess, threading, time, sys, os, json, socket
import winreg, ctypes, collections
from http.server import HTTPServer, BaseHTTPRequestHandler

try:
    ctypes.windll.kernel32.FreeConsole()
except Exception:
    pass

from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw

APP_NAME    = "StrangeCat Monitor"
APP_VER     = "3.2"
APPDATA     = os.path.join(os.getenv("APPDATA", os.path.expanduser("~")), "StrangeCat")
CFG_FILE    = os.path.join(APPDATA, "config.json")
EXE_PATH    = sys.executable if getattr(sys, "frozen", False) else os.path.abspath(__file__)
STARTUP_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
GRAPH_HIST  = 60

# ── PALETTE ───────────────────────────────────────────────────────────────────
C = {
    "bg":         "#080808", "surface":   "#101010", "surface2": "#161616",
    "border":     "#222222", "border2":   "#2e2e2e", "title_bg": "#0c0c0c",
    "acc":        "#d40000", "acc2":      "#ff2222", "acc_dim":  "#4a0000",
    "acc_soft":   "#1a0000",
    "ok":         "#00cc55", "warn":      "#f5a300", "hot":      "#ff3a3a",
    "dim":        "#333333", "mid":       "#555555", "muted":    "#888888",
    "fg":         "#c8c8c8", "fg_hi":     "#f0f0f0",
    "bar_bg":     "#191919", "tag_bg":    "#1c0000",
    "graph_bg":   "#0c0c0c", "graph_fill":"#3a0000",
    "cell_bg":    "#0e0e0e", "cell_border":"#1e1e1e",
    "foot_bg":    "#0a0a0a",
}

# ── DEFAULTS ──────────────────────────────────────────────────────────────────
DEFAULTS = {
    "start_on_boot": False, "start_minimized": False,
    "always_on_top": True,  "opacity": 0.96,
    "refresh_rate":  2,     "compact_mode": False,
    "temp_unit":     "C",
    "show_cpu": True, "show_cpu_temp": True, "show_ram": True,
    "show_gpu": True, "show_gpu_temp": True, "show_vram": True,
    "show_net": True,
    "http_enabled": True, "http_port": 5100,
    "pos_x": 120, "pos_y": 120,
    "window_width": 380,
    "close_action": "ask",  # "ask", "hide", "quit"
    "default_close_action": "minimize",  # "minimize", "quit"
    "language": "fr",  # "fr", "en"
    "show_disks": True,  # Show disk drives by default
    "perf_mode": "normal",  # "realtimes", "normal", "optimized", "low"
}

# ── TRANSLATIONS ───────────────────────────────────────────────────────────────
TRANSLATIONS = {
    "fr": {
        "app_name": "StrangeCat Monitor",
        "settings": "Paramètres",
        "save": "Enregistrer",
        "cancel": "Annuler",
        "close": "Fermer",
        "close_dialog_title": "Fermer",
        "close_dialog_question": "Que voulez-vous faire ?",
        "minimize": "Minimiser",
        "quit": "Quitter",
        "remember_choice": "Se souvenir de mon choix",
        "minimized_notification": "Minimisé dans le tray",
        "temp_source": "src:",
        "cpu": "CPU",
        "cpu_temp": "CPU TEMP",
        "ram": "RAM",
        "gpu": "GPU",
        "gpu_temp": "GPU TEMP",
        "vram": "VRAM",
        "net_down": "NET ↓",
        "net_up": "NET ↑",
        "section_general": "GÉNÉRAL",
        "section_display": "AFFICHAGE",
        "section_metrics": "MÉTRIQUES",
        "section_network": "RÉSEAU",
        "start_on_boot": "Démarrage au boot",
        "start_minimized": "Démarrer minimisé",
        "always_on_top": "Toujours au premier plan",
        "opacity": "Opacité",
        "refresh_rate": "Rafraîchissement (sec)",
        "compact_mode": "Mode compact",
        "temp_unit": "Unité température",
        "low_power_mode": "Mode économie d'énergie",
        "language": "Langue",
        "default_close_action": "Action fermeture",
        "show_cpu": "Afficher CPU",
        "show_cpu_temp": "Afficher CPU TEMP",
        "show_ram": "Afficher RAM",
        "show_gpu": "Afficher GPU",
        "show_gpu_temp": "Afficher GPU TEMP",
        "show_vram": "Afficher VRAM",
        "show_net": "Afficher NET",
        "show_disks": "Afficher disques",
        "http_enabled": "HTTP activé",
        "http_port": "Port HTTP",
    },
    "en": {
        "app_name": "StrangeCat Monitor",
        "settings": "Settings",
        "save": "Save",
        "cancel": "Cancel",
        "close": "Close",
        "close_dialog_title": "Close",
        "close_dialog_question": "What do you want to do?",
        "minimize": "Minimize",
        "quit": "Quit",
        "remember_choice": "Remember my choice",
        "minimized_notification": "Minimized to tray",
        "temp_source": "src:",
        "cpu": "CPU",
        "cpu_temp": "CPU TEMP",
        "ram": "RAM",
        "gpu": "GPU",
        "gpu_temp": "GPU TEMP",
        "vram": "VRAM",
        "net_down": "NET ↓",
        "net_up": "NET ↑",
        "section_general": "GENERAL",
        "section_display": "DISPLAY",
        "section_metrics": "METRICS",
        "section_network": "NETWORK",
        "start_on_boot": "Start on boot",
        "start_minimized": "Start minimized",
        "always_on_top": "Always on top",
        "opacity": "Opacity",
        "refresh_rate": "Refresh (sec)",
        "compact_mode": "Compact mode",
        "temp_unit": "Temperature unit",
        "low_power_mode": "Low power mode",
        "language": "Language",
        "default_close_action": "Close action",
        "show_cpu": "Show CPU",
        "show_cpu_temp": "Show CPU TEMP",
        "show_ram": "Show RAM",
        "show_gpu": "Show GPU",
        "show_gpu_temp": "Show GPU TEMP",
        "show_vram": "Show VRAM",
        "show_net": "Show NET",
        "show_disks": "Show disks",
        "http_enabled": "HTTP enabled",
        "http_port": "HTTP port",
    },
}

def t(key, lang="fr"):
    """Get translation for a key."""
    return TRANSLATIONS.get(lang, TRANSLATIONS["fr"]).get(key, key)

def load_cfg():
    try:
        os.makedirs(APPDATA, exist_ok=True)
        if os.path.exists(CFG_FILE):
            with open(CFG_FILE, "r", encoding="utf-8") as fh:
                d = json.load(fh)
            out = DEFAULTS.copy()
            out.update(d)
            return out
    except Exception:
        pass
    return DEFAULTS.copy()

def save_cfg(cfg):
    try:
        os.makedirs(APPDATA, exist_ok=True)
        with open(CFG_FILE, "w", encoding="utf-8") as fh:
            json.dump(cfg, fh, indent=2)
    except Exception:
        pass

# ── STARTUP ───────────────────────────────────────────────────────────────────
def set_startup(enable):
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_KEY, 0, winreg.KEY_SET_VALUE)
        if enable:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, f'"{EXE_PATH}"')
        else:
            try: winreg.DeleteValue(key, APP_NAME)
            except FileNotFoundError: pass
        winreg.CloseKey(key)
    except Exception: pass

def is_startup():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_KEY, 0, winreg.KEY_READ)
        winreg.QueryValueEx(key, APP_NAME)
        winreg.CloseKey(key)
        return True
    except Exception: return False

# ── GPU ───────────────────────────────────────────────────────────────────────
_gpu_cache = {"data": None, "time": 0}
_GPU_CACHE_TTL = 2.0  # cache GPU data for 2 seconds to reduce nvidia-smi calls

def get_gpu():
    now = time.time()
    if _gpu_cache["data"] and (now - _gpu_cache["time"]) < _GPU_CACHE_TTL:
        return _gpu_cache["data"]
    try:
        out = subprocess.check_output(
            ["nvidia-smi","--query-gpu=utilization.gpu,temperature.gpu,memory.used,memory.total",
             "--format=csv,noheader,nounits"],
            encoding="utf-8", creationflags=subprocess.CREATE_NO_WINDOW, timeout=3)
        u, t, mu, mt = [x.strip() for x in out.strip().split(",")]
        mu_gb, mt_gb = float(mu)/1024, float(mt)/1024
        result = {"usage":float(u),"temp":float(t),"vram_used":mu_gb,"vram_total":mt_gb,
                  "vram_pct":round(mu_gb/mt_gb*100,1) if mt_gb else 0,"ok":True}
        _gpu_cache["data"] = result
        _gpu_cache["time"] = now
        return result
    except Exception:
        return {"usage":0,"temp":0,"vram_used":0,"vram_total":0,"vram_pct":0,"ok":False}

# ── CPU TEMP ──────────────────────────────────────────────────────────────────
_temp_state = {"value": None, "method": "searching…"}

def _clamp(v): return v if (v and 0 < v < 125) else None

def _try_psutil():
    try:
        d = psutil.sensors_temperatures()
        if not d: return None, None
        for key in ("coretemp","k10temp","zenpower","cpu_thermal","acpitz","nct6798","nct6776"):
            if key in d:
                vals = [e.current for e in d[key] if 0 < e.current < 125]
                if vals: return round(sum(vals)/len(vals),1), f"psutil/{key}"
        for entries in d.values():
            vals = [e.current for e in entries if 0 < e.current < 125]
            if vals: return round(sum(vals)/len(vals),1), "psutil"
    except Exception: pass
    return None, None

def _try_wmi_thermal():
    try:
        import wmi
        w = wmi.WMI(namespace="root/wmi")
        s = w.MSAcpi_ThermalZoneTemperature()
        if s: return _clamp(round((s[0].CurrentTemperature/10.0)-273.15,1)), "WMI/AcpiThermal"
    except Exception: pass
    return None, None

def _try_wmi_perfdata():
    try:
        import wmi
        z = wmi.WMI().Win32_PerfFormattedData_Counters_ThermalZoneInformation()
        if z: return _clamp(round(float(z[0].Temperature)-273.15,1)), "WMI/PerfData"
    except Exception: pass
    return None, None

def _try_librehw():
    try:
        import wmi
        for ns in ("root/LibreHardwareMonitor","root/OpenHardwareMonitor"):
            try:
                vals = [s.Value for s in wmi.WMI(namespace=ns).Sensor()
                        if s.SensorType=="Temperature"
                        and any(k in s.Name.lower() for k in ("cpu","core","package"))
                        and s.Value and 0 < s.Value < 125]
                if vals: return round(sum(vals)/len(vals),1), ns.split("/")[1]
            except Exception: pass
    except Exception: pass
    return None, None

def _try_coretemp():
    hnd = ptr = None
    try:
        MAX = 128
        class CTData(ctypes.Structure):
            _fields_ = [("uiLoad",ctypes.c_uint*MAX),("uiTjMax",ctypes.c_uint*MAX),
                        ("uiCoreCnt",ctypes.c_uint),("uiCPUCnt",ctypes.c_uint),
                        ("fTemp",ctypes.c_float*MAX),("fVID",ctypes.c_float),
                        ("fCPUSpeed",ctypes.c_float),("fFSBSpeed",ctypes.c_float),
                        ("fMultiplier",ctypes.c_float),("sCPUName",ctypes.c_char*100),
                        ("ucFahrenheit",ctypes.c_ubyte),("ucDeltaToTjMax",ctypes.c_ubyte)]
        hnd = ctypes.windll.kernel32.OpenFileMappingW(0x0004, False, "CoreTempMappingObject")
        if not hnd: return None, None
        ptr = ctypes.windll.kernel32.MapViewOfFile(hnd, 0x0004, 0, 0, 0)
        if not ptr: return None, None
        raw = ctypes.string_at(ptr, ctypes.sizeof(CTData))
        ctypes.windll.kernel32.UnmapViewOfFile(ptr); ptr = None
        ctypes.windll.kernel32.CloseHandle(hnd);    hnd = None
        d = CTData.from_buffer(ctypes.create_string_buffer(raw, ctypes.sizeof(CTData)))
        n = max(0, min(int(d.uiCoreCnt), MAX))
        temps = [d.fTemp[i] for i in range(n) if 0 < d.fTemp[i] < 125]
        if temps: return round(sum(temps)/len(temps),1), "CoreTemp"
    except Exception: pass
    finally:
        try:
            if ptr: ctypes.windll.kernel32.UnmapViewOfFile(ptr)
        except Exception: pass
        try:
            if hnd: ctypes.windll.kernel32.CloseHandle(hnd)
        except Exception: pass
    return None, None

_TEMP_METHODS = [_try_psutil, _try_wmi_thermal, _try_wmi_perfdata, _try_librehw, _try_coretemp]

def get_cpu_temp():
    for fn in _TEMP_METHODS:
        try:
            val, name = fn()
            if val is not None:
                _temp_state["value"] = val; _temp_state["method"] = name
                return val, name
        except Exception: pass
    _temp_state["value"] = None; _temp_state["method"] = "unavailable"
    return None, "unavailable"

# ── NETWORK ───────────────────────────────────────────────────────────────────
_net_prev = {"sent":0, "recv":0, "t":time.time()}

def get_net_speed():
    try:
        now = psutil.net_io_counters(); t = time.time()
        dt  = max(t - _net_prev["t"], 0.01)
        up   = max(round((now.bytes_sent - _net_prev["sent"])/dt/1024,1), 0)
        down = max(round((now.bytes_recv - _net_prev["recv"])/dt/1024,1), 0)
        _net_prev.update({"sent":now.bytes_sent,"recv":now.bytes_recv,"t":t})
        return up, down
    except Exception: return 0.0, 0.0

# ── DISK DRIVES ────────────────────────────────────────────────────────────────
_disk_drives = []  # List of detected disk drives (e.g., ['C:', 'D:', 'E:'])

def detect_disk_drives():
    """Detect all available disk drives on the system."""
    global _disk_drives
    try:
        drives = []
        for partition in psutil.disk_partitions():
            if partition.device and len(partition.device) > 0:
                # Extract drive letter (e.g., 'C:' from 'C:\\')
                drive = partition.device[:2].upper()
                if drive not in drives and drive.endswith(':'):
                    drives.append(drive)
        _disk_drives = sorted(drives)
        return _disk_drives
    except Exception:
        return []

def get_disk_usage():
    """Get disk usage for all detected drives."""
    usage = {}
    for drive in _disk_drives:
        try:
            disk = psutil.disk_usage(drive)
            usage[drive] = {
                "percent": round(disk.percent, 1),
                "used_gb": round(disk.used / (1024**3), 1),
                "total_gb": round(disk.total / (1024**3), 1),
                "free_gb": round(disk.free / (1024**3), 1)
            }
        except Exception:
            usage[drive] = {"percent": 0, "used_gb": 0, "total_gb": 0, "free_gb": 0}
    return usage

# ── PERF COLLECT ──────────────────────────────────────────────────────────────
_perf_lock = threading.Lock()
_perf_data = {}

# Performance mode refresh rates (in seconds)
PERF_MODE_RATES = {
    "realtimes": {"disk": 10, "ram": 1, "cpu": 1, "gpu": 1, "vram": 1, "net": 1},
    "normal": {"disk": 30, "ram": 2, "cpu": 2, "gpu": 2, "vram": 2, "net": 2},
    "optimized": {"disk": 60, "ram": 4, "cpu": 4, "gpu": 4, "vram": 4, "net": 4},
    "low": {"disk": 300, "ram": 10, "cpu": 10, "gpu": 10, "vram": 10, "net": 10},
}

def collect_perf(metrics_to_collect=None):
    """Collect performance metrics. If metrics_to_collect is provided, only collect those metrics."""
    metrics_to_collect = metrics_to_collect or ["cpu", "ram", "gpu", "vram", "disk", "net", "cpu_temp"]
    
    # Start with existing data to preserve values for metrics not being collected
    with _perf_lock:
        block = _perf_data.get("psutil", {}).copy()
    
    if "cpu" in metrics_to_collect:
        cpu = psutil.cpu_percent(interval=None)
        block["cpu"] = round(cpu,1)
    
    if "ram" in metrics_to_collect:
        mem = psutil.virtual_memory()
        block["memory"] = round(mem.percent,1)
        block["memory_gb"] = f"{round(mem.used/1024**3,1)}GB/{round(mem.total/1024**3,1)}GB"
    
    if "gpu" in metrics_to_collect or "vram" in metrics_to_collect:
        gpu = get_gpu()
        if "gpu" in metrics_to_collect:
            block["gpu_usage"] = round(gpu["usage"],1)
            block["gpu_temp"] = round(gpu["temp"],1)
        if "vram" in metrics_to_collect:
            block["vram_usage"] = round(gpu["vram_pct"],1)
            block["vram_gb"] = f"{round(gpu['vram_used'],1)}GB/{round(gpu['vram_total'],1)}GB"
    
    if "cpu_temp" in metrics_to_collect:
        ct, _ = get_cpu_temp()
        block["cpu_temp"] = round(ct,1) if ct else None
        block["cpu_temp_method"] = _temp_state["method"]
    
    if "net" in metrics_to_collect:
        up, dn = get_net_speed()
        block["upload_speed"] = up
        block["download_speed"] = dn
    
    if "disk" in metrics_to_collect:
        disk = get_disk_usage()
        # Add disk data directly to block (only if drives detected)
        for drive, data in disk.items():
            drive_lower = drive.lower().replace(":", "")
            key = f"{drive_lower}_disk"
            block[key] = f"{data['used_gb']} GB/{data['total_gb']} GB"
    
    block["timestamp"] = time.time()
    payload = {"timestamp": time.time(), "psutil": block}
    with _perf_lock: _perf_data.clear(); _perf_data.update(payload)
    return payload

# ── HTTP ──────────────────────────────────────────────────────────────────────
class PerfHandler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        if self.path == "/performance":
            with _perf_lock: body = json.dumps(_perf_data, indent=2).encode()
            self.send_response(200)
            self.send_header("Content-Type","application/json")
            self.send_header("Content-Length",str(len(body)))
            self.send_header("Access-Control-Allow-Origin","*")
            self.end_headers(); self.wfile.write(body)
        else:
            self.send_response(404); self.end_headers()

_http_server = None
def start_http(port):
    global _http_server
    stop_http()
    try:
        _http_server = HTTPServer(("127.0.0.1", port), PerfHandler)
        threading.Thread(target=_http_server.serve_forever, daemon=True).start()
    except Exception: pass

def stop_http():
    global _http_server
    if _http_server:
        try: _http_server.shutdown()
        except Exception: pass
        _http_server = None

# ── TRAY ──────────────────────────────────────────────────────────────────────
def make_tray_img():
    sz=64; img=Image.new("RGBA",(sz,sz),(0,0,0,0)); d=ImageDraw.Draw(img)
    d.rounded_rectangle([2,2,sz-3,sz-3],radius=9,fill=(13,13,13,255),outline=(212,0,0,255),width=2)
    for ex in (14,sz-14): d.polygon([(ex-9,32),(ex,10),(ex+9,32)],fill=(200,0,0,255))
    d.ellipse([8,26,sz-8,sz-6],fill=(28,28,28,255),outline=(140,0,0,200),width=1)
    for ex in (20,sz-20): d.ellipse([ex-5,34,ex+5,44],fill=(220,0,0,255))
    d.polygon([(sz//2,47),(sz//2-4,52),(sz//2+4,52)],fill=(190,55,55,255))
    return img

# ── METRICS DEFINITION ────────────────────────────────────────────────────────
# (key, label, unit, fixed_max, warn, hot, scale_mode)
# scale_mode "fixed"=0-fixed_max, "dynamic"=scales to peak
BASE_METRICS = [
    ("cpu",      "CPU",      "%",    100, 70, 90,  "fixed"),
    ("cpu_temp", "CPU TEMP", "°",    100, 70, 85,  "fixed"),
    ("ram",      "RAM",      "%",    100, 75, 90,  "fixed"),
    ("gpu",      "GPU",      "%",    100, 70, 90,  "fixed"),
    ("gpu_temp", "GPU TEMP", "°",    100, 70, 85,  "fixed"),
    ("vram",     "VRAM",     "%",    100, 75, 90,  "fixed"),
    ("net_down", "NET ↓",   "KB/s", None,None,None,"dynamic"),
    ("net_up",   "NET ↑",   "KB/s", None,None,None,"dynamic"),
]

def get_metrics():
    """Get full metrics list including detected disk drives."""
    metrics = list(BASE_METRICS)
    for drive in _disk_drives:
        metrics.append((f"disk_{drive}", f"DISK {drive}", "%", 100, 80, 95, "fixed"))
    return metrics

METRICS = get_metrics()

SHOW_KEY = {
    "cpu":"show_cpu","cpu_temp":"show_cpu_temp","ram":"show_ram",
    "gpu":"show_gpu","gpu_temp":"show_gpu_temp","vram":"show_vram",
    "net_down":"show_net","net_up":"show_net",
}
# Add disk drive show keys dynamically
for drive in _disk_drives:
    SHOW_KEY[f"disk_{drive}"] = f"show_disk_{drive.lower()}"

# ── SETTINGS WINDOW ───────────────────────────────────────────────────────────
class SettingsWin:
    def __init__(self, root, cfg, on_apply):
        self.cfg = {k:v for k,v in cfg.items()}
        self.cb  = on_apply
        self.lang = cfg.get("language", "fr")
        w = tk.Toplevel(root)
        self.w = w
        w.title(f"{APP_NAME}  ·  {t('settings', self.lang)}")
        w.geometry("460x680"); w.minsize(420,520)
        w.resizable(True,True); w.configure(bg=C["bg"])
        w.attributes("-topmost",True); w.grab_set()
        self._build()

    def _build(self):
        w = self.w
        # accent bar + header
        tk.Frame(w,bg=C["acc"],height=3).pack(fill="x")
        hdr = tk.Frame(w,bg=C["title_bg"]); hdr.pack(fill="x")
        tk.Label(hdr,text="⚙",font=("Segoe UI Emoji",13),
                 bg=C["title_bg"],fg=C["acc"]).pack(side="left",padx=(14,4),pady=10)
        hf = tk.Frame(hdr,bg=C["title_bg"]); hf.pack(side="left",pady=8)
        tk.Label(hf,text="CONFIGURATION",font=("Consolas",11,"bold"),
                 bg=C["title_bg"],fg=C["acc"]).pack(anchor="w")
        tk.Label(hf,text=f"StrangeCat Monitor  v{APP_VER}",font=("Consolas",7),
                 bg=C["title_bg"],fg=C["mid"]).pack(anchor="w")
        tk.Frame(w,bg=C["border"],height=1).pack(fill="x")

        # ── SAVE bar pinned at BOTTOM (packed before canvas so it stays fixed) ──
        tk.Frame(w,bg=C["border"],height=1).pack(fill="x",side="bottom")
        btn_bar = tk.Frame(w,bg=C["title_bg"],height=62)
        btn_bar.pack(fill="x",side="bottom"); btn_bar.pack_propagate(False)

        self._save_var = tk.StringVar(value="💾  SAVE")

        def _mk_btn(parent, text_src, cmd, bg, fg, hbg, hfg="#fff", use_var=False):
            kw = {"textvariable":text_src} if use_var else {"text":text_src}
            b = tk.Label(parent, **kw, font=("Consolas",10,"bold"),
                         bg=bg, fg=fg, cursor="hand2", padx=20, pady=14)
            b.pack(side="right", padx=8, pady=6)
            b.bind("<Button-1>", lambda e: cmd())
            b.bind("<Enter>",    lambda e, lb=b: lb.config(bg=hbg, fg=hfg))
            b.bind("<Leave>",    lambda e, lb=b: lb.config(bg=bg,  fg=fg))
            return b

        def do_save():
            self._collect()
            self._save_var.set("✓  SAVED!")
            self.w.after(1400, lambda: self._save_var.set("💾  SAVE"))

        def do_save_close():
            self._collect(); self.w.destroy()

        _mk_btn(btn_bar,"✕  " + t("cancel", self.lang), self.w.destroy, C["surface2"],C["muted"],C["dim"],C["fg"])
        _mk_btn(btn_bar,t("save", self.lang) + " & " + t("close", self.lang).lower(), do_save_close, C["acc_dim"],C["fg"],"#3a0000",C["fg_hi"])
        _mk_btn(btn_bar, self._save_var, do_save, C["acc"],"#fff",C["acc2"], use_var=True)

        # ── scrollable body ──
        canvas = tk.Canvas(w,bg=C["bg"],highlightthickness=0)
        sb = ttk.Scrollbar(w,orient="vertical",command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right",fill="y"); canvas.pack(side="left",fill="both",expand=True)
        f = tk.Frame(canvas,bg=C["bg"])
        wid = canvas.create_window((0,0),window=f,anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(wid,width=e.width))
        f.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(-1*(e.delta//120),"units"))

        st = ttk.Style(); st.theme_use("default")
        st.configure("TCombobox",fieldbackground=C["surface"],background=C["surface"],
                     foreground=C["fg"],selectbackground=C["acc"],selectforeground="#fff",
                     bordercolor=C["border"])
        st.map("TCombobox", fieldbackground=[("readonly", C["surface"])],
                          foreground=[("readonly", C["fg"])])
        st.configure("TScrollbar",background=C["dim"],troughcolor=C["bg"],
                     bordercolor=C["bg"],arrowcolor=C["muted"])

        P = {"padx":22}
        def section(txt):
            tk.Frame(f,bg=C["border"],height=1).pack(fill="x",pady=(14,4),**P)
            lf=tk.Frame(f,bg=C["bg"]); lf.pack(anchor="w",**P)
            tk.Label(lf,text="▸ ",font=("Consolas",8,"bold"),bg=C["bg"],fg=C["fg_hi"]).pack(side="left")
            tk.Label(lf,text=txt,font=("Consolas",8,"bold"),bg=C["bg"],fg=C["fg_hi"]).pack(side="left")

        def row(label, var, kind="check", values=None, from_=None, to=None, res=None, wc=6):
            r=tk.Frame(f,bg=C["surface2"],highlightbackground=C["border"],highlightthickness=1)
            r.pack(fill="x",pady=2,**P)
            tk.Label(r,text=label,font=("Consolas",9),bg=C["surface2"],fg=C["fg"],
                     width=24,anchor="w").pack(side="left",padx=10,pady=5)
            if kind=="check":
                tk.Checkbutton(r,variable=var,bg=C["surface2"],fg=C["acc"],
                               selectcolor=C["bg"],activebackground=C["surface2"],
                               activeforeground=C["acc"],bd=0).pack(side="left",padx=4)
            elif kind=="combo":
                ttk.Combobox(r,textvariable=var,values=values,
                             width=wc,state="readonly").pack(side="left",padx=4)
            elif kind=="scale":
                tk.Scale(r,from_=from_,to=to,resolution=res,orient="horizontal",
                         variable=var,bg=C["surface2"],fg=C["fg"],troughcolor=C["dim"],
                         highlightthickness=0,activebackground=C["acc"],
                         length=130,sliderlength=14).pack(side="left",padx=4)
            elif kind=="entry":
                tk.Entry(r,textvariable=var,width=wc,bg=C["bg"],fg=C["fg"],
                         insertbackground=C["fg"],relief="flat",bd=6,
                         highlightbackground=C["border"],highlightthickness=1
                         ).pack(side="left",padx=4,pady=4)

        section(t("section_general", self.lang))
        self.v_boot = tk.BooleanVar(value=is_startup())
        self.v_mini = tk.BooleanVar(value=bool(self.cfg.get("start_minimized",False)))
        row(t("start_on_boot", self.lang),   self.v_boot)
        row(t("start_minimized", self.lang), self.v_mini)

        section(t("section_display", self.lang))
        self.v_top     = tk.BooleanVar(value=bool(self.cfg.get("always_on_top",True)))
        self.v_compact = tk.BooleanVar(value=bool(self.cfg.get("compact_mode",False)))
        self.v_opacity = tk.DoubleVar(value=float(self.cfg.get("opacity",0.96)))
        self.v_refresh = tk.IntVar(value=int(self.cfg.get("refresh_rate",2)))
        self.v_unit    = tk.StringVar(value=str(self.cfg.get("temp_unit","C")))
        self.v_lang    = tk.StringVar(value=str(self.cfg.get("language","fr")))
        self.v_close_action = tk.StringVar(value=str(self.cfg.get("default_close_action","minimize")))
        row(t("always_on_top", self.lang),  self.v_top)
        row(t("compact_mode", self.lang),   self.v_compact)
        row(t("opacity", self.lang),        self.v_opacity,"scale",from_=0.3,to=1.0,res=0.05)
        row(t("refresh_rate", self.lang),  self.v_refresh,"combo",values=[1,2,5],wc=4)
        row(t("temp_unit", self.lang),      self.v_unit,  "combo",values=["C","F"],wc=4)
        row(t("language", self.lang),       self.v_lang,  "combo",values=["fr","en"],wc=4)
        # Custom row for close action reset with "Ask Again" button only
        r=tk.Frame(f,bg=C["surface2"],highlightbackground=C["border"],highlightthickness=1)
        r.pack(fill="x",pady=2,**P)
        tk.Label(r,text="Close Action",font=("Consolas",9),bg=C["surface2"],fg=C["fg"],
                 width=24,anchor="w").pack(side="left",padx=10,pady=5)
        def reset_close_action():
            self.cfg["close_action"] = "ask"
            save_cfg(self.cfg)
        tk.Button(r,text="Ask Again",font=("Consolas",8),bg=C["acc"],fg="#fff",
                  cursor="hand2",bd=0,command=reset_close_action).pack(side="left",padx=4)
        # Performance mode dropdown
        self.v_perf_mode = tk.StringVar(value=str(self.cfg.get("perf_mode","normal")))
        row("Performance Mode", self.v_perf_mode, "combo", values=["realtimes","normal","optimized","low"], wc=10)

        section(t("section_network", self.lang) + "  (127.0.0.1:<port>/performance)")
        self.v_http_on   = tk.BooleanVar(value=bool(self.cfg.get("http_enabled",True)))
        self.v_http_port = tk.IntVar(value=int(self.cfg.get("http_port",5100)))
        row(t("http_enabled", self.lang), self.v_http_on)
        row(t("http_port", self.lang),     self.v_http_port,"entry",wc=6)

        section(t("section_metrics", self.lang))
        self.v_show = {}
        for key, lbl_key in [("show_cpu","show_cpu"),("show_cpu_temp","show_cpu_temp"),
                         ("show_ram","show_ram"),("show_gpu","show_gpu"),
                         ("show_gpu_temp","show_gpu_temp"),("show_vram","show_vram"),
                         ("show_net","show_net")]:
            self.v_show[key] = tk.BooleanVar(value=bool(self.cfg.get(key,True)))
            row(t(lbl_key, self.lang), self.v_show[key])

        # Add disk drives section if drives are detected
        if _disk_drives:
            section("DISK DRIVES")
            self.v_show_disks = tk.BooleanVar(value=bool(self.cfg.get("show_disks", True)))
            row(t("show_disks", self.lang), self.v_show_disks)
            # Individual disk drive toggles
            for drive in _disk_drives:
                key = f"show_disk_{drive.lower()}"
                self.v_show[key] = tk.BooleanVar(value=bool(self.cfg.get(key, True)))
                row(f"Disk {drive}", self.v_show[key])

        section("CPU TEMP SOURCE")
        val = _temp_state.get("value"); mth = _temp_state.get("method","—")
        tip = tk.Frame(f,bg=C["tag_bg"],highlightbackground=C["acc_dim"],highlightthickness=1)
        tip.pack(fill="x",pady=4,**P)
        tk.Label(tip,text=f"✓  {val:.1f}°  via {mth}" if val else f"✗  {mth}",
                 font=("Consolas",8,"bold"),bg=C["tag_bg"],
                 fg=C["ok"] if val else C["hot"],justify="left",anchor="w"
                 ).pack(anchor="w",padx=10,pady=4)
        tk.Label(tip,text="Priority: psutil → WMI/AcpiThermal → WMI/PerfData\n"
                 "         → LibreHardwareMonitor → CoreTemp",
                 font=("Consolas",7),bg=C["tag_bg"],fg=C["muted"],
                 justify="left",anchor="w").pack(anchor="w",padx=10,pady=(0,6))
        if not val:
            tk.Label(tip,text="→ Run LibreHardwareMonitor as Administrator for reliable readings.",
                     font=("Consolas",7),bg=C["tag_bg"],fg=C["warn"],
                     justify="left",anchor="w").pack(anchor="w",padx=10,pady=(0,6))
        tk.Frame(f,bg=C["bg"],height=10).pack()

    def _collect(self):
        try:
            port = int(self.v_http_port.get())
            if not (1 <= port <= 65535): raise ValueError
        except (ValueError, tk.TclError):
            port = self.cfg.get("http_port",5100)
            self.v_http_port.set(port)

        self.cfg.update({
            "start_on_boot":   bool(self.v_boot.get()),
            "start_minimized": bool(self.v_mini.get()),
            "always_on_top":   bool(self.v_top.get()),
            "compact_mode":    bool(self.v_compact.get()),
            "opacity":         round(float(self.v_opacity.get()),2),
            "refresh_rate":    int(self.v_refresh.get()),
            "temp_unit":       str(self.v_unit.get()),
            "language":        str(self.v_lang.get()),
            "default_close_action": str(self.v_close_action.get()),
            "http_enabled":    bool(self.v_http_on.get()),
            "http_port":       port,
            "perf_mode":       str(self.v_perf_mode.get()),
        })
        for k,v in self.v_show.items():
            self.cfg[k] = bool(v.get())
        # Save show_disks if it exists
        if hasattr(self, 'v_show_disks'):
            self.cfg["show_disks"] = bool(self.v_show_disks.get())
        set_startup(self.cfg["start_on_boot"])
        save_cfg(self.cfg)
        self.cb(self.cfg)

# ── MAIN APP ──────────────────────────────────────────────────────────────────
_GRIP = 16   # SE corner grip size (px)
_MIN_W = 200

class App:
    def __init__(self, root, cfg):
        self.root    = root
        self.cfg     = cfg
        self.lang    = cfg.get("language", "fr")
        self.running = True
        self._rows   = {}
        self._hist   = {m[0]: collections.deque([0.0]*GRAPH_HIST, maxlen=GRAPH_HIST)
                        for m in METRICS}
        self._drag_active   = False
        self._resize_active = False
        self._user_resizing = False  # track if user is manually resizing
        self._collapsed = {}  # track which metrics are collapsed in graph mode
        # Track last update times for each metric (for performance mode)
        self._last_updates = {"cpu": 0, "ram": 0, "gpu": 0, "vram": 0, "disk": 0, "net": 0, "cpu_temp": 0}
        self._build()
        threading.Thread(target=self._loop, daemon=True).start()
        root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── scale helpers ─────────────────────────────────────────────────────────
    def _scale(self):
        """Calculate scale factor based on current window width (reference: 380px).
        Returns a value between 0.6 and 3.0 to scale UI elements proportionally.
        """
        w = self.root.winfo_width()
        if w < 10: w = self.cfg.get("window_width", 380)
        return max(0.6, min(3.0, w / 380))

    def _sz(self):
        """Return sizing dictionary based on current mode and scale factor.
        Includes font sizes, bar heights, graph heights, and padding values.
        """
        s = self._scale()
        if self.cfg.get("compact_mode"):
            # Compact mode: smaller fonts, no graphs
            return {"font_lbl": max(7, int(8*s)), "font_val": max(8, int(9*s)),
                    "bar_h":    max(4, int(5*s)),  "graph_h": 0,
                    "pad_y":    max(3, int(4*s)),  "pad_x": max(10, int(12*s))}
        else:
            # Graph mode: larger fonts, visible graphs
            return {"font_lbl": max(8, int(9*s)), "font_val": max(10, int(13*s)),
                    "bar_h":    max(4, int(6*s)),  "graph_h": max(35, int(50*s)),
                    "pad_y":    max(4, int(6*s)),  "pad_x":   max(12, int(16*s))}

    # ── window build ──────────────────────────────────────────────────────────
    def _build(self):
        """Build the main window structure: title bar, body, and footer."""
        r = self.root
        r.overrideredirect(True)  # Remove window decorations
        r.configure(bg=C["bg"])
        r.attributes("-topmost", self.cfg["always_on_top"])
        r.attributes("-alpha",   self.cfg["opacity"])
        w = self.cfg.get("window_width", 380)
        # Set initial height based on mode (compact: small, graph: larger for grid)
        compact = self.cfg.get("compact_mode", False)
        init_h = 80 if compact else 520
        r.geometry(f"{w}x{init_h}+{self.cfg['pos_x']}+{self.cfg['pos_y']}")
        self._build_title()
        self._build_footer()   # Footer packed BEFORE body so it stays at bottom
        self._build_body()
        # Bind mouse events for dragging and resizing
        self.root.bind("<Motion>",          self._on_motion)
        self.root.bind("<ButtonPress-1>",   self._on_press)
        self.root.bind("<B1-Motion>",       self._on_drag)
        self.root.bind("<ButtonRelease-1>", self._on_release)
        # Ensure minimum window dimensions to always show header
        r.minsize(_MIN_W, 100)

    def _in_grip(self, rx, ry):
        """Check if mouse position is within the SE corner grip area."""
        ww = self.root.winfo_width()
        wh = self.root.winfo_height()
        return rx >= ww - _GRIP and ry >= wh - _GRIP

    def _on_motion(self, e):
        """Handle mouse motion - update cursor when over resize grip."""
        rx = e.x_root - self.root.winfo_rootx()
        ry = e.y_root - self.root.winfo_rooty()
        try:
            self.root.config(cursor="size_nw_se" if self._in_grip(rx, ry) else "")
        except Exception: pass

    def _on_press(self, e):
        """Handle mouse button press - start drag or resize operation."""
        rx = e.x_root - self.root.winfo_rootx()
        ry = e.y_root - self.root.winfo_rooty()
        if self._in_grip(rx, ry):
            # Start resize operation
            self._resize_active = True
            self._drag_active   = False
            self._user_resizing = True
            self._rx = e.x_root; self._ry = e.y_root
            self._rw = self.root.winfo_width()
            self._rh = self.root.winfo_height()
            self._wx = self.root.winfo_x()
            self._wy = self.root.winfo_y()
        else:
            # Start drag operation
            self._resize_active = False
            self._drag_active   = True
            self._dx = e.x_root - self.root.winfo_x()
            self._dy = e.y_root - self.root.winfo_y()

    def _on_drag(self, e):
        """Handle mouse drag - resize window or move window."""
        if self._resize_active:
            # Diagonal resize from SE corner - expand right and down
            nw = max(_MIN_W, self._rw + (e.x_root - self._rx))
            compact = self.cfg.get("compact_mode", False)
            if compact:
                # In compact mode, only resize width, not height
                nh = self._rh
            else:
                # In graph mode, allow both width and height resize
                nh = self._rh + (e.y_root - self._ry)
            self.cfg["window_width"] = nw
            # Keep position fixed, expand width and height
            self.root.geometry(f"{nw}x{nh}+{self._wx}+{self._wy}")
            # Rescale content live
            self._rescale_rows()
        elif self._drag_active:
            # Move window
            nx = e.x_root - self._dx
            ny = e.y_root - self._dy
            self.root.geometry(f"+{nx}+{ny}")
            self.cfg["pos_x"] = nx; self.cfg["pos_y"] = ny

    def _on_release(self, e):
        """Handle mouse button release - end drag or resize operation."""
        if self._resize_active:
            self._resize_active = False
            self._user_resizing = False
            try: self.root.config(cursor="")
            except Exception: pass
            # Update saved position to current actual position after resize
            self._wx = self.root.winfo_x()
            self._wy = self.root.winfo_y()
            self._rebuild_rows()   # Full rebuild with new sizes
        self._drag_active = False

    # ── title bar ─────────────────────────────────────────────────────────────
    def _build_title(self):
        """Build the title bar with app name, controls, and drag functionality."""
        # Destroy existing title components if they exist
        if hasattr(self, '_acc_top') and self._acc_top:
            try: self._acc_top.destroy()
            except Exception: pass
        if hasattr(self, '_title_bar') and self._title_bar:
            try: self._title_bar.destroy()
            except Exception: pass

        # Top accent line
        self._acc_top = tk.Frame(self.root, bg=C["acc"], height=2)
        self._acc_top.pack(fill="x")

        # Title bar frame with fixed height
        self._title_bar = tk.Frame(self.root, bg=C["title_bg"], height=40)
        self._title_bar.pack(fill="x")
        self._title_bar.pack_propagate(False)

        # Bind drag events to title bar (for window moving)
        self._title_bar.bind("<ButtonPress-1>",   self._on_press)
        self._title_bar.bind("<B1-Motion>",       self._on_drag)
        self._title_bar.bind("<ButtonRelease-1>", self._on_release)
        self._title_bar.bind("<Motion>",          self._on_motion)

        # Cat icon + app name (left side)
        left = tk.Frame(self._title_bar, bg=C["title_bg"])
        left.pack(side="left", padx=(10, 4), pady=4)
        tk.Label(left, text="🐱", font=("Segoe UI Emoji", 13),
                 bg=C["title_bg"], fg=C["acc"]).pack(side="left", padx=(0, 6))
        lf = tk.Frame(left, bg=C["title_bg"])
        lf.pack(side="left")
        tk.Label(lf, text="STRANGECAT", font=("Consolas", 10, "bold"),
                 bg=C["title_bg"], fg=C["fg_hi"]).pack(anchor="w")
        tk.Label(lf, text=f"MONITOR  v{APP_VER}",  font=("Consolas", 7),
                 bg=C["title_bg"], fg=C["mid"]).pack(anchor="w")

        # Control buttons (right side)
        btns = tk.Frame(self._title_bar, bg=C["title_bg"])
        btns.pack(side="right", padx=4)

        def tbtn(txt, cmd, hbg=C["surface2"], hfg=C["fg_hi"]):
            """Helper to create a title bar button with hover effects."""
            b = tk.Label(btns, text=txt, font=("Segoe UI Emoji", 11),
                         bg=C["title_bg"], fg=C["muted"], cursor="hand2",
                         padx=7, pady=5)
            b.pack(side="left")
            b.bind("<Button-1>", lambda e: cmd())
            b.bind("<Enter>", lambda e, lb=b, h=hbg, f=hfg: lb.config(fg=f, bg=h))
            b.bind("<Leave>", lambda e, lb=b:               lb.config(fg=C["muted"], bg=C["title_bg"]))
            return b

        self._compact_btn = tbtn("⊟", self._toggle_compact)
        self._update_compact_btn()
        self._lang_btn = tbtn("🇫🇷" if self.lang == "fr" else "🇬🇧", self._toggle_language)
        tbtn("⚙", self._open_settings)
        tbtn("—", self._hide)
        tbtn("✕", self._quit, hbg=C["acc_dim"], hfg="#fff")

        # Separator line below title bar
        tk.Frame(self.root, bg=C["border"], height=1).pack(fill="x")

    def _update_compact_btn(self):
        """Update the compact mode button appearance based on current mode."""
        c = self.cfg.get("compact_mode",False)
        self._compact_btn.config(text="⊟" if not c else "⊞",
                                 fg=C["acc"] if c else C["mid"])

    def _toggle_compact(self):
        """Toggle between compact and graph display modes."""
        self.cfg["compact_mode"] = not self.cfg.get("compact_mode",False)
        save_cfg(self.cfg)
        self._update_compact_btn()
        # When switching to graph mode, give it a proper initial height
        if not self.cfg["compact_mode"]:
            w = self.cfg.get("window_width", 380)
            x = self.root.winfo_x(); y = self.root.winfo_y()
            self.root.geometry(f"{w}x520+{x}+{y}")
        self._build_body()

    def _toggle_language(self):
        """Show language selection dropdown menu."""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="🇫🇷 French", command=lambda: self._set_language("fr"))
        menu.add_command(label="🇬🇧 English", command=lambda: self._set_language("en"))

        # Position menu below the language button
        x = self._lang_btn.winfo_rootx()
        y = self._lang_btn.winfo_rooty() + self._lang_btn.winfo_height()
        menu.tk_popup(x, y)

    def _set_language(self, lang):
        """Set the application language and rebuild UI."""
        self.cfg["language"] = lang
        self.lang = lang
        save_cfg(self.cfg)
        self._lang_btn.config(text="🇫🇷" if lang == "fr" else "🇬🇧")
        self._build_title()
        self._build_body()
        self._build_footer()

    def _toggle_collapse(self, key):
        """Toggle collapse state for a specific metric in graph mode.
        When collapsed, the graph canvas is hidden but the header remains visible.
        """
        self._collapsed[key] = not self._collapsed.get(key, False)
        # Rebuild to update grid layout and row weights
        self._rebuild_rows()

    # ── body container ─────────────────────────────────────────────────────────
    def _build_body(self):
        """Build the main body container that holds all metric rows."""
        # Destroy existing body/canvas/scrollbar if they exist
        if hasattr(self, '_body') and self._body:
            try: self._body.destroy()
            except Exception: pass
        if hasattr(self, '_canvas') and self._canvas:
            try: self._canvas.destroy()
            except Exception: pass
        if hasattr(self, '_scrollbar') and self._scrollbar:
            try: self._scrollbar.destroy()
            except Exception: pass
        self._canvas    = None
        self._scrollbar = None

        compact = self.cfg.get("compact_mode", False)
        # Create body frame that fills available space
        self._body = tk.Frame(self.root, bg=C["bg"])
        if compact:
            # Compact mode: only expand horizontally
            self._body.pack(fill="x")
        else:
            # Graph mode: expand both horizontally and vertically
            self._body.pack(fill="both", expand=True)
        self._rebuild_rows()

    def _rebuild_rows(self):
        """Rebuild all metric rows based on current mode and collapse state."""
        for w in self._body.winfo_children():
            w.destroy()
        self._rows = {}
        sz      = self._sz()
        compact = self.cfg.get("compact_mode", False)

        if compact:
            # Compact mode: vertical layout with simple bar rows
            for key, label, unit, fmax, warn, hot, gmode in METRICS:
                sk = SHOW_KEY.get(key)
                if sk and not self.cfg.get(sk, True):
                    continue
                self._rows[key] = self._make_bar_row(label, unit, sz)
        else:
            # Graph mode: responsive grid layout
            w = self.root.winfo_width()
            if w < 10: w = self.cfg.get("window_width", 380)

            # Responsive columns based on window width
            if w < 480:
                cols = 1
            elif w < 780:
                cols = 2
            else:
                cols = 3

            # Get all visible metrics (both expanded and collapsed)
            visible = [(key, label, unit, fmax, warn, hot, gmode)
                       for key, label, unit, fmax, warn, hot, gmode in METRICS
                       if self.cfg.get(SHOW_KEY.get(key, ""), True)
                       and not (key.startswith("disk_") and not self.cfg.get("show_disks", True))]

            # Grid container fills the body
            grid_container = tk.Frame(self._body, bg=C["bg"])
            grid_container.pack(fill="both", expand=True, padx=6, pady=6)

            num_rows = (len(visible) + cols - 1) // cols

            # Configure grid columns and rows
            for i in range(cols):
                grid_container.columnconfigure(i, weight=1, uniform="col")
            for i in range(num_rows):
                # Collapsed rows get less weight (smaller height)
                is_collapsed_row = any(self._collapsed.get(m[0], False) 
                                      for m in visible[i*cols:(i+1)*cols])
                grid_container.rowconfigure(i, weight=0 if is_collapsed_row else 1, uniform="row")

            # Place all metrics in grid (collapsed ones stay in grid but with hidden graph)
            for idx, (key, label, unit, fmax, warn, hot, gmode) in enumerate(visible):
                col_idx = idx % cols
                row_idx = idx // cols
                is_collapsed = self._collapsed.get(key, False)
                row_widget = self._make_graph_row_in_grid(
                    label, unit, sz, fmax, warn, hot, gmode, is_collapsed, key, grid_container)
                self._rows[key] = row_widget
                row_widget["outer"].grid(
                    row=row_idx, column=col_idx,
                    sticky="nsew", padx=3, pady=3)

        self._auto_resize()

    def _rescale_rows(self):
        """Quick rescale without full rebuild - update fonts & graph heights."""
        sz = self._sz()
        for key, row in self._rows.items():
            try:
                if row["mode"] == "graph":
                    row["lbl"].config(font=("Consolas", sz["font_lbl"], "bold"))
                    row["val"].config(font=("Consolas", sz["font_val"], "bold"))
                    row["unit"].config(font=("Consolas", sz["font_lbl"]))
                    if not row.get("collapsed", False):
                        row["canvas"].config(height=sz["graph_h"])
                        row["height"] = sz["graph_h"]
                else:
                    row["lbl"].config(font=("Consolas", sz["font_lbl"], "bold"))
                    row["val"].config(font=("Consolas", sz["font_val"], "bold"))
                    row["unit"].config(font=("Consolas", sz["font_lbl"]))
            except Exception:
                pass
        # Rebuild to re-flow grid on resize
        self._rebuild_rows()

    def _auto_resize(self):
        """Auto-fit window height in compact mode. In graph mode, leave user in control."""
        self.root.update_idletasks()
        w = self.cfg.get("window_width", 380)
        x = self.root.winfo_x(); y = self.root.winfo_y()
        compact = self.cfg.get("compact_mode", False)
        if compact and not self._user_resizing:
            h = self.root.winfo_reqheight()
            self.root.geometry(f"{w}x{h}+{x}+{y}")

    # ── compact row: label | bar | value unit ─────────────────────────────────
    def _make_bar_row(self, label, unit, sz):
        """Create a compact mode row with label, progress bar, and value."""
        f = tk.Frame(self._body, bg=C["bg"])
        f.pack(fill="x", padx=sz["pad_x"], pady=sz["pad_y"])

        # Metric label
        lbl = tk.Label(f, text=label, font=("Consolas", sz["font_lbl"], "bold"),
                       bg=C["bg"], fg=C["muted"], width=10, anchor="w")
        lbl.pack(side="left")

        # Progress bar container
        bf = tk.Frame(f, bg=C["bar_bg"], height=sz["bar_h"],
                      highlightbackground=C["dim"], highlightthickness=1)
        bf.pack(side="left", fill="x", expand=True, padx=(4,6))
        bf.pack_propagate(False)
        # Actual progress bar (resized dynamically)
        bar = tk.Frame(bf, bg=C["acc"])
        bar.place(x=0, y=0, relheight=1.0, width=0)

        # Value display
        val = tk.Label(f, text="—", font=("Consolas", sz["font_val"], "bold"),
                       bg=C["bg"], fg=C["ok"], width=6, anchor="e")
        val.pack(side="left")
        # Unit label
        unit_lbl = tk.Label(f, text=unit, font=("Consolas", sz["font_lbl"]),
                            bg=C["bg"], fg=C["dim"], width=4, anchor="w")
        unit_lbl.pack(side="left")
        return {"mode":"compact","bar":bar,"bf":bf,"val":val,
                "lbl":lbl,"unit":unit_lbl}

    # ── graph row: label + value | sparkline canvas ───────────────────────────
    def _make_graph_row(self, label, unit, sz, fmax, warn, hot, gmode, is_collapsed, key):
        """Create a graph mode row with header and sparkline canvas (legacy, not used in grid mode)."""
        outer = tk.Frame(self._body, bg=C["surface"],
                         highlightbackground=C["border"], highlightthickness=1)
        outer.pack(fill="x", padx=sz["pad_x"], pady=sz["pad_y"])

        hdr = tk.Frame(outer, bg=C["surface"]); hdr.pack(fill="x", padx=10, pady=(6,0))

        # Collapse/expand button
        collapse_btn = tk.Label(hdr, text="▼" if not is_collapsed else "▶",
                                font=("Segoe UI Emoji", 11), bg=C["surface"], fg=C["acc"],
                                cursor="hand2", padx=7)
        collapse_btn.pack(side="left")
        collapse_btn.bind("<Button-1>", lambda e: self._toggle_collapse(key))

        lbl = tk.Label(hdr, text=label, font=("Consolas", sz["font_lbl"], "bold"),
                       bg=C["surface"], fg=C["muted"], anchor="w")
        lbl.pack(side="left")
        unit_lbl = tk.Label(hdr, text=unit, font=("Consolas", sz["font_lbl"]),
                            bg=C["surface"], fg=C["dim"])
        unit_lbl.pack(side="right")
        val = tk.Label(hdr, text="—", font=("Consolas", sz["font_val"], "bold"),
                       bg=C["surface"], fg=C["fg"])
        val.pack(side="right", padx=(0,6))

        # Graph canvas (hidden if collapsed)
        graph_frame = tk.Frame(outer, bg=C["surface"])
        if not is_collapsed:
            graph_frame.pack(fill="x", padx=8, pady=(3,8))

        gh = sz["graph_h"]
        gc = tk.Canvas(graph_frame, bg=C["graph_bg"], height=gh, highlightthickness=0)
        if not is_collapsed:
            gc.pack(fill="x")

        return {"mode":"graph","canvas":gc,"val":val,"lbl":lbl,"unit":unit_lbl,
                "fmax":fmax,"warn":warn,"hot":hot,"gmode":gmode,"height":gh,
                "collapsed":is_collapsed,"graph_frame":graph_frame,"collapse_btn":collapse_btn}

    # ── graph row for grid layout ───────────────────────────────────────────────
    def _make_graph_row_in_grid(self, label, unit, sz, fmax, warn, hot, gmode, is_collapsed, key, parent):
        """Create a graph row widget for grid layout.
        When collapsed, the outer box disappears and only name + % are shown.
        """
        # When collapsed, use plain background without border
        bg = C["bg"] if is_collapsed else C["cell_bg"]
        border = C["bg"] if is_collapsed else C["cell_border"]
        thickness = 0 if is_collapsed else 1
        
        outer = tk.Frame(parent, bg=bg,
                         highlightbackground=border, highlightthickness=thickness)

        # Header row inside cell (always visible, even when collapsed)
        hdr = tk.Frame(outer, bg=bg)
        hdr.pack(fill="x", padx=8, pady=(6, 0))

        # Collapse toggle button
        collapse_btn = tk.Label(hdr, text="▾" if not is_collapsed else "▸",
                                font=("Consolas", 9, "bold"), bg=bg, fg=C["acc"],
                                cursor="hand2", padx=4)
        collapse_btn.pack(side="left")
        collapse_btn.bind("<Button-1>", lambda e: self._toggle_collapse(key))

        # Metric label
        lbl = tk.Label(hdr, text=label, font=("Consolas", sz["font_lbl"], "bold"),
                       bg=bg, fg=C["muted"], anchor="w")
        lbl.pack(side="left", padx=(2, 0))

        # Unit label
        unit_lbl = tk.Label(hdr, text=unit, font=("Consolas", sz["font_lbl"]),
                            bg=bg, fg=C["dim"])
        unit_lbl.pack(side="right", padx=(0, 2))

        # Value label
        val = tk.Label(hdr, text="—", font=("Consolas", sz["font_val"], "bold"),
                       bg=bg, fg=C["ok"])
        val.pack(side="right", padx=(0, 4))

        # Thin accent separator (only when expanded)
        if not is_collapsed:
            sep = tk.Frame(outer, bg=C["border"], height=1)
            sep.pack(fill="x", padx=8, pady=(4, 0))

        # Graph canvas container (only packed when expanded)
        graph_frame = tk.Frame(outer, bg=C["graph_bg"])
        if not is_collapsed:
            graph_frame.pack(fill="both", expand=True, padx=6, pady=(3, 6))

        # Graph canvas (only created and packed when expanded)
        gh = sz["graph_h"]
        gc = tk.Canvas(graph_frame, bg=C["graph_bg"], height=gh, highlightthickness=0)
        if not is_collapsed:
            gc.pack(fill="both", expand=True)

        return {"mode":"graph","canvas":gc,"val":val,"lbl":lbl,"unit":unit_lbl,
                "fmax":fmax,"warn":warn,"hot":hot,"gmode":gmode,"height":gh,
                "collapsed":is_collapsed,"graph_frame":graph_frame,
                "collapse_btn":collapse_btn,"outer":outer}

    # ── footer bar ─────────────────────────────────────────────────────────────
    def _build_footer(self):
        """Build the footer with status info, time, and HTTP status."""
        # Destroy existing footer components if they exist
        for attr in ['_grip_lbl', '_foot', '_footer_sep', '_footer_acc']:
            if hasattr(self, attr) and getattr(self, attr):
                try: getattr(self, attr).destroy()
                except Exception: pass
                setattr(self, attr, None)

        # Top separator
        self._footer_sep = tk.Frame(self.root, bg=C["border"], height=1)
        self._footer_sep.pack(fill="x")

        # Footer frame with fixed height
        self._foot = tk.Frame(self.root, bg=C["foot_bg"], height=28)
        self._foot.pack(fill="x", side="bottom")
        self._foot.pack_propagate(False)

        # Left: temperature source status
        self.status_lbl = tk.Label(
            self._foot, text="", font=("Consolas", 8),
            bg=C["foot_bg"], fg=C["mid"], anchor="w")
        self.status_lbl.pack(side="left", padx=10, pady=6)

        # Center: current time
        self.time_lbl = tk.Label(
            self._foot, text="", font=("Consolas", 8, "bold"),
            bg=C["foot_bg"], fg=C["muted"], anchor="center")
        self.time_lbl.pack(side="left", expand=True)

        # Right: HTTP server status
        self.http_lbl = tk.Label(
            self._foot, text="", font=("Consolas", 8),
            bg=C["foot_bg"], fg=C["mid"], anchor="e", width=12)
        self.http_lbl.pack(side="right", padx=12, pady=6)

        # Bottom accent line
        self._footer_acc = tk.Frame(self.root, bg=C["acc"], height=2)
        self._footer_acc.pack(fill="x", side="bottom")

        # SE corner grip indicator (above the accent bar)
        self._grip_lbl = tk.Label(self.root, text="◢", font=("Consolas", 9),
                                  bg=C["foot_bg"], fg=C["dim"], cursor="size_nw_se")
        self._grip_lbl.place(relx=1.0, rely=1.0, anchor="se", y=-2)
        self._grip_lbl.bind("<ButtonPress-1>",   self._on_press)
        self._grip_lbl.bind("<B1-Motion>",       self._on_drag)
        self._grip_lbl.bind("<ButtonRelease-1>", self._on_release)

    # ── data collection loop ─────────────────────────────────────────────────────
    def _loop(self):
        """Main data collection loop - runs in background thread."""
        while self.running:
            try:
                # Get performance mode and refresh rates
                perf_mode = self.cfg.get("perf_mode", "normal")
                rates = PERF_MODE_RATES.get(perf_mode, PERF_MODE_RATES["normal"])
                
                # Determine which metrics need updating
                now = time.time()
                metrics_to_collect = []
                
                for metric, interval in rates.items():
                    if now - self._last_updates.get(metric, 0) >= interval:
                        metrics_to_collect.append(metric)
                        self._last_updates[metric] = now
                
                # Always collect cpu_temp (not in performance mode)
                metrics_to_collect.append("cpu_temp")
                
                if metrics_to_collect:
                    d = collect_perf(metrics_to_collect)
                    self.root.after(0, lambda data=d: self._refresh(data))
            except Exception: pass
            time.sleep(0.5)  # Check every 0.5s for performance mode updates

    def _col(self, val, warn, hot):
        """Return color based on value thresholds (ok/warn/hot)."""
        if warn is None: return C["ok"]
        if val >= hot:   return C["hot"]
        if val >= warn:  return C["warn"]
        return C["ok"]

    def _draw_graph(self, row, key):
        """Draw sparkline graph on canvas with filled area and current value dot."""
        gc = row["canvas"]
        cw = gc.winfo_width()
        ch = gc.winfo_height()  # Use actual canvas height instead of row["height"]
        if cw < 4: cw = max(100, self.cfg.get("window_width", 380) - 50)
        if ch < 10: ch = 50  # Minimum height for graph
        gc.delete("all")
        history = list(self._hist[key])
        if not history: return

        # Determine Y-axis scale
        if row["gmode"] == "dynamic":
            peak = max(max(history), 1)
            for cap in (10,50,100,500,1000,5000,10000,50000):
                if peak <= cap: top = cap; break
            else: top = peak * 1.2
        else:
            top = row["fmax"] or 100

        # Calculate point positions
        n    = len(history)
        step = cw / max(n-1, 1)
        pts  = []
        # Add padding at bottom and top to prevent cutoff
        padding = 4
        draw_h = ch - padding * 2
        for i, v in enumerate(history):
            x = i * step
            y = padding + draw_h - (min(v, top) / top) * draw_h
            pts.append((max(0,x), max(padding, min(ch-padding, y))))

        # Draw filled area under the line
        poly = [(0, ch)] + pts + [(pts[-1][0], ch)]
        flat_poly = [c for p in poly for c in p]
        if len(flat_poly) >= 6:
            gc.create_polygon(flat_poly, fill=C["graph_fill"], outline="")

        # Draw the line itself
        if len(pts) >= 2:
            gc.create_line([c for p in pts for c in p],
                           fill=C["acc"], width=max(1, int(self._scale()*1.5)),
                           smooth=True, joinstyle="round", capstyle="round")

        # Draw dot at current value with color threshold
        if pts:
            lx, ly = pts[-1]
            r = max(3, int(self._scale()*3))
            val = history[-1]
            col = self._col(val, row["warn"], row["hot"])
            # Glow ring
            gc.create_oval(lx-r-1, ly-r-1, lx+r+1, ly+r+1,
                           fill="", outline=col, width=1)
            gc.create_oval(lx-r, ly-r, lx+r, ly+r, fill=col, outline="")

        # Show scale cap for dynamic mode
        if row["gmode"] == "dynamic":
            gc.create_text(cw-3, padding+2, text=f"{int(top)}", anchor="ne",
                           fill=C["dim"], font=("Consolas", max(7, int(7*self._scale()))))

    def _refresh(self, d):
        """Update UI with latest performance data - called from background thread."""
        # Skip drawing if window is hidden (low power optimization)
        try:
            if not self.root.winfo_ismapped():
                return
        except Exception:
            pass

        ps   = d["psutil"]
        unit = self.cfg.get("temp_unit","C")
        tw, th = (158,185) if unit=="F" else (70,85)

        def to_f(v): return round(v*9/5+32,1) if (unit=="F" and v) else v

        # Extract values from performance data
        vals = {
            "cpu":      ps["cpu"],
            "cpu_temp": to_f(ps.get("cpu_temp")),
            "ram":      ps["memory"],
            "gpu":      ps["gpu_usage"],
            "gpu_temp": to_f(ps["gpu_temp"]),
            "vram":     ps["vram_usage"],
            "net_down": ps["download_speed"],
            "net_up":   ps["upload_speed"],
        }
        # Add disk drive values if available (disk data is now directly in psutil block)
        if self.cfg.get("show_disks", True):
            for drive in _disk_drives:
                drive_lower = drive.lower().replace(":", "")
                key = f"{drive_lower}_disk"
                if key in ps:
                    # data is a string like "737.4 GB/930.6 GB"
                    try:
                        data = ps[key]
                        parts = data.split(" GB/")
                        used_gb = float(parts[0])
                        total_gb = float(parts[1].split(" GB")[0])
                        percent = round(used_gb / total_gb * 100, 1) if total_gb > 0 else 0
                        vals[f"disk_{drive}"] = percent
                    except (ValueError, IndexError, ZeroDivisionError):
                        vals[f"disk_{drive}"] = 0

        # Update history for graphs
        for key, v in vals.items():
            if v is not None:
                if key not in self._hist:
                    self._hist[key] = collections.deque([0.0]*GRAPH_HIST, maxlen=GRAPH_HIST)
                self._hist[key].append(float(v))

        compact = self.cfg.get("compact_mode",False)

        # Update each metric row
        for key, row in self._rows.items():
            v = vals.get(key)
            # Determine color based on thresholds
            if key in ("cpu_temp","gpu_temp"):
                col = self._col(v or 0, tw, th)
            elif key in ("net_down","net_up"):
                col = C["ok"]
            else:
                _, _, _, _, warn, hot, _ = next(m for m in METRICS if m[0]==key)
                col = self._col(v or 0, warn, hot)

            # Format value text
            if key.startswith("disk_"):
                # Disk drives: show percentage
                txt = "N/A" if v is None else f"{int(v)}%"
            else:
                txt = ("N/A" if v is None else
                       f"{v:.1f}" if key in ("cpu_temp","gpu_temp") else
                       f"{int(v)}")

            if compact:
                # Compact mode: update bar and value
                row["val"].configure(text=txt, fg=col if v is not None else C["dim"])
                if v is not None:
                    row["bar"].configure(bg=col)
                    bw = row["bf"].winfo_width()
                    if bw < 2: bw = 60
                    _, _, _, fmax, warn, hot, _ = next(m for m in METRICS if m[0]==key)
                    pct = min(v/(fmax or max(v,1)), 1.0)
                    row["bar"].place(x=0, y=0, relheight=1.0, width=max(1,int(pct*bw)))
            else:
                # Graph mode: update value and redraw graph if not collapsed
                row["val"].configure(text=txt, fg=col if v is not None else C["dim"])
                if not row.get("collapsed", False):
                    self._draw_graph(row, key)

        # Update footer status
        self.status_lbl.configure(
            text=f"{t('temp_source', self.lang)} {_temp_state['method']}")
        self.time_lbl.configure(
            text=time.strftime('%H:%M:%S'))
        port = self.cfg.get("http_port",5100)
        if self.cfg.get("http_enabled",True):
            self.http_lbl.configure(text=f"● :{port}", fg=C["ok"])
        else:
            self.http_lbl.configure(text="○ off", fg=C["dim"])

    # ── actions ───────────────────────────────────────────────────────────────
    def _on_close(self):
        """Handle window close button (X) based on default_close_action setting."""
        action = self.cfg.get("default_close_action", "minimize")
        if action == "quit":
            self._quit()
        else:
            self._hide()

    def _hide(self):  self.root.withdraw()
    def show(self):   self.root.deiconify(); self.root.lift()

    def _open_settings(self):
        SettingsWin(self.root, self.cfg, self._apply_cfg)

    def _apply_cfg(self, new):
        old_port   = self.cfg.get("http_port",5100)
        old_http   = self.cfg.get("http_enabled",True)
        old_compact = self.cfg.get("compact_mode", False)
        old_default_close = self.cfg.get("default_close_action", "minimize")
        old_lang    = self.cfg.get("language", "fr")
        self.cfg = new
        self.lang = new.get("language", "fr")
        self.root.attributes("-topmost", new["always_on_top"])
        self.root.attributes("-alpha",   new["opacity"])
        self._update_compact_btn()
        # Reset close_action if default_close_action changed (to avoid conflicts)
        if new.get("default_close_action") != old_default_close:
            new["close_action"] = "ask"
        # Rebuild body whenever settings change (visibility, compact mode, etc.)
        self._build_body()
        # Only restart HTTP server if settings actually changed
        if new["http_enabled"] != old_http or (new["http_enabled"] and new["http_port"] != old_port):
            if new["http_enabled"]:
                start_http(new["http_port"])
            else:
                stop_http()
        save_cfg(new)

    def _quit(self):
        close_action = self.cfg.get("close_action", "ask")

        if close_action == "hide":
            self._hide()
            return
        elif close_action == "quit":
            self._do_quit()
            return

        # Ask user
        dlg = tk.Toplevel(self.root)
        dlg.title(t("close_dialog_title", self.lang))
        dlg.geometry("320x140")
        dlg.configure(bg=C["surface"])
        dlg.attributes("-topmost", True)
        dlg.resizable(False, False)

        # Center dialog
        dlg.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - 320) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 140) // 2
        dlg.geometry(f"+{x}+{y}")

        tk.Label(dlg, text=t("close_dialog_question", self.lang), font=("Consolas", 10, "bold"),
                bg=C["surface"], fg=C["fg_hi"]).pack(pady=(15, 10))

        btn_frame = tk.Frame(dlg, bg=C["surface"])
        btn_frame.pack(pady=5)

        def on_hide():
            if remember_var.get():
                self.cfg["close_action"] = "hide"
            else:
                self.cfg["close_action"] = self.cfg.get("default_close_action", "minimize")
            save_cfg(self.cfg)
            dlg.destroy()
            self._hide()

        def on_quit():
            if remember_var.get():
                self.cfg["close_action"] = "quit"
            else:
                self.cfg["close_action"] = self.cfg.get("default_close_action", "minimize")
            save_cfg(self.cfg)
            dlg.destroy()
            self._do_quit()

        remember_var = tk.BooleanVar(value=False)

        tk.Button(btn_frame, text=t("minimize", self.lang), command=on_hide,
                bg=C["surface2"], fg=C["fg"], font=("Consolas", 9),
                relief="flat", padx=15, pady=5).pack(side="left", padx=5)
        tk.Button(btn_frame, text=t("quit", self.lang), command=on_quit,
                bg=C["acc_dim"], fg="#fff", font=("Consolas", 9),
                relief="flat", padx=15, pady=5).pack(side="left", padx=5)

        tk.Checkbutton(dlg, text=t("remember_choice", self.lang), variable=remember_var,
                      bg=C["surface"], fg=C["muted"], selectcolor=C["surface2"],
                      font=("Consolas", 8), activebackground=C["surface"],
                      activeforeground=C["fg"]).pack(pady=(10, 5))

    def _do_quit(self):
        self.running = False
        stop_http()
        save_cfg(self.cfg)
        try:
            self.root.destroy()
        except Exception:
            pass
        try:
            import os
            os._exit(0)
        except Exception:
            sys.exit(0)

# ── SINGLE INSTANCE CHECK ─────────────────────────────────────────────────────
def is_already_running():
    try:
        # Try to bind to a specific port to check if another instance is running
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("127.0.0.1", 51999))  # Use a specific port for single instance check
        s.close()
        return False
    except socket.error:
        # Another instance is running, try to send quit command
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(("127.0.0.1", 51999))
            s.sendall(b"QUIT")
            s.close()
            # Wait for old instance to quit
            time.sleep(0.5)
        except Exception:
            pass
        return True

# ── ENTRY ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Detect disk drives at startup (only once)
    detect_disk_drives()
    # Update METRICS and SHOW_KEY with detected drives (only once)
    METRICS = get_metrics()
    for drive in _disk_drives:
        SHOW_KEY[f"disk_{drive}"] = f"show_disk_{drive.lower()}"

    if is_already_running():
        print("Another instance is already running. Exiting.")
        sys.exit(0)

    cfg  = load_cfg()
    root = tk.Tk()
    app  = App(root, cfg)

    # Start socket server to listen for quit commands from new instances
    def listen_for_quit():
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind(("127.0.0.1", 51999))
            server.listen(1)
            server.settimeout(1.0)  # Non-blocking with timeout
            while app.running:
                try:
                    conn, addr = server.accept()
                    data = conn.recv(1024)
                    if data == b"QUIT":
                        conn.close()
                        server.close()
                        app._do_quit()
                        return
                    conn.close()
                except socket.timeout:
                    continue
                except Exception:
                    break
        except Exception:
            pass

    threading.Thread(target=listen_for_quit, daemon=True).start()

    if cfg.get("http_enabled",True):
        start_http(cfg.get("http_port",5100))

    def _show(i,it): root.after(0,app.show)
    def _hide(i,it): root.after(0,app._hide)
    def _sett(i,it): root.after(0,app._open_settings)
    def _quit(i,it): 
        i.stop()
        app._do_quit()

    def _show_minimized_notification():
        lang = cfg.get("language", "fr")
        notif = tk.Toplevel(root)
        notif.title(t("app_name", lang))
        notif.geometry("280x80")
        notif.configure(bg=C["surface"])
        notif.attributes("-topmost", True)
        notif.resizable(False, False)
        notif.overrideredirect(True)

        # Center notification on screen
        screen_w = notif.winfo_screenwidth()
        screen_h = notif.winfo_screenheight()
        x = (screen_w - 280) // 2
        y = (screen_h - 80) // 2
        notif.geometry(f"+{x}+{y}")

        tk.Label(notif, text="🐱 " + t("app_name", lang), font=("Consolas", 11, "bold"),
                bg=C["surface"], fg=C["acc"]).pack(pady=(12, 5))
        tk.Label(notif, text=t("minimized_notification", lang), font=("Consolas", 9),
                bg=C["surface"], fg=C["muted"]).pack(pady=(0, 8))

        # Auto-close after 3 seconds
        notif.after(3000, notif.destroy)

    tray = Icon(APP_NAME, make_tray_img(), APP_NAME, Menu(
        MenuItem("Show",_show), MenuItem("Hide",_hide),
        MenuItem("Settings",_sett), Menu.SEPARATOR, MenuItem("Quit",_quit),
    ))
    threading.Thread(target=tray.run, daemon=True).start()

    # Show notification if started minimized
    if cfg.get("start_minimized"):
        root.after(500, _show_minimized_notification)
        root.after(3000, app._hide)  # Hide after notification closes

    root.mainloop()