# 🐱 StrangeCat Monitor v3.6

A lightweight Windows desktop monitor designed for **Wallpaper Engine** integration.

StrangeCat Monitor displays your live system stats in a floating desktop widget and exposes them locally through a small HTTP API so compatible wallpapers can animate your hardware data in real time.

* ✅ No internet required
* ✅ Lightweight & portable
* ✅ Works locally on `127.0.0.1:5100/performance`
* ✅ Compatible with Wallpaper Engine
* ✅ Graph mode & compact mode
* ✅ System tray support
* ✅ Disk monitoring (auto-detected drives)
* ✅ Multilingual (English / French)
* ✅ Configurable performance modes

---

# Quick Start

## 1. Download & Launch

Download the latest release and launch:

```txt
StrangeCat Monitor.exe
```

No Python or additional setup required.

---

## 2. Verify the Monitor is Running

When the app is running, the footer should show:

```txt
● :5100
```

This means the local HTTP server is active.

---

## 3. Configure Wallpaper Engine

Open Wallpaper Engine and ensure your wallpaper uses:

```txt
Port: 5100
```

StrangeCat Monitor serves live data at:

```txt
http://127.0.0.1:5100/performance
```

---

## 4. Done 🎉

Compatible wallpapers will now display your live CPU, RAM, GPU, temperatures, and network activity automatically.

---

# Installation

## Standalone EXE

1. Download the latest release
2. Move it anywhere you want
3. Double-click:

```txt
StrangeCat Monitor.exe
```

No installation required.

---

## Auto-start with Windows

Open:

```txt
⚙ Settings → System
```

Enable:

* Start on boot
* Start minimized (optional)

StrangeCat Monitor will now launch automatically with Windows.

> Recommended for Wallpaper Engine users.

---

# Wallpaper Engine Setup

## How it Works

StrangeCat Monitor runs a tiny local server:

```txt
http://127.0.0.1:5100/performance
```

Wallpaper Engine wallpapers can read this endpoint and animate your system stats live.

```txt
StrangeCat Monitor
        │
        ├──► Floating desktop widget
        │
        └──► Local HTTP API (:5100)
                     │
                     └──► Wallpaper Engine wallpaper
```

---

## Test the Connection

Open this address in your browser:

```txt
http://127.0.0.1:5100/performance
```

If you see JSON data, everything is working correctly.

---

## Port Mismatch (Important)

Some wallpapers are designed for other monitoring apps using port `5000`.

StrangeCat Monitor uses:

```txt
5100
```

If your wallpaper cannot connect:

* either change the wallpaper port to `5100`
* or change StrangeCat Monitor's port in:

```txt
Settings → HTTP API
```

---

# The Interface

```txt
┌──────────────────────────────────────────────────────┐
│ 🐱 STRANGECAT    🇬🇧  [⊟] [⚙] [—] [✕]              │
│    MONITOR  v3.6                                     │
├──────────────────────────────────────────────────────┤
│                                                      │
│        Live system metrics displayed here            │
│                                                      │
├──────────────────────────────────────────────────────┤
│ src: LibreHardwareMonitor   14:32:07   ● :5100  ◢  │
└──────────────────────────────────────────────────────┘
```

---

## Title Bar Buttons

| Button    | Description                      |
| --------- | -------------------------------- |
| 🇬🇧 / 🇫🇷  | Language toggle (EN/FR)          |
| `⊟` / `⊞` | Toggle Graph Mode / Compact Mode |
| `⚙`       | Open Settings                    |
| `—`       | Hide to system tray              |
| `✕`       | Quit application                 |

---

## Footer Information

| Position | Description            |
| -------- | ---------------------- |
| Left     | CPU temperature source |
| Center   | Current time           |
| Right    | HTTP server status     |

---

## Window Controls

* Drag the title bar to move the window
* Drag the bottom-right corner `◢` to resize
* Window content scales automatically
* Minimum window height: 100px (header always visible)

---

# Display Modes

## Graph Mode

Default mode with live graphs and metric history.

Each metric has its own card with a real-time sparkline graph showing the last 60 seconds.

```txt
┌─────────────┐
│ CPU     40% │
│ ∿∿∿∿∿∿∿●   │
└─────────────┘
```

### Features

* Responsive grid layout (1–3 columns depending on width)
* Individual metric cards, collapsible (▾/▸)
* Live graph history
* Automatic color warnings

### Collapse Behavior

Collapsed metrics stay in the grid but take minimal height — the header row remains visible while other metrics expand to use the freed space.

### Color Indicators

* 🟢 Green → normal
* 🟡 Yellow → high usage
* 🔴 Red → critical usage

---

## Compact Mode

Minimal bar-based layout with no graphs.

```txt
CPU       ▬▬▬▬▬▬▬▬▬░░░░░   40 %
RAM       ▬▬▬▬▬▬▬▬▬▬▬░░░   51 %
GPU       ▬▬▬▬░░░░░░░░░░   22 %
C:        ▬▬▬▬▬▬▬░░░░░░░   48 %
D:        ▬▬░░░░░░░░░░░░   14 %
```

Perfect for small desktop corners and lower CPU usage.

### Compact Mode Features

* Smaller footprint
* Auto-adjusting height (horizontal resize only)
* Lower rendering cost
* Cleaner minimalist layout

---

# Settings

Open settings with:

```txt
⚙
```

---

## System

| Option          | Description           |
| --------------- | --------------------- |
| Start on boot   | Launch with Windows   |
| Start minimized | Launch hidden in tray |

---

## Display

| Option               | Description                        |
| -------------------- | ---------------------------------- |
| Always on top        | Keep above other windows           |
| Compact mode         | Enable compact layout              |
| Opacity              | Window transparency                |
| Refresh rate         | 1s / 2s / 5s updates               |
| Temp unit            | Celsius or Fahrenheit              |
| Low power mode       | Reduce refresh when hidden         |
| Performance mode     | Ultra / Normal / Optimized / Low   |
| Language             | English / French                   |

---

## HTTP API

| Option             | Description                  |
| ------------------ | ---------------------------- |
| Enable HTTP server | Enable wallpaper integration |
| Port               | Default: `5100`              |

---

## Visible Metrics

You can individually enable or disable metrics.

Disabled metrics:

* disappear from the widget
* stop being sent to wallpapers

Disk metrics can be toggled globally or per drive.

---

# Available Metrics

| Metric           | Description              |
| ---------------- | ------------------------ |
| CPU Usage        | Processor usage (%)      |
| CPU Temperature  | CPU temperature          |
| RAM Usage        | Memory usage (%)         |
| GPU Usage        | GPU load (%)             |
| GPU Temperature  | GPU temperature          |
| VRAM Usage       | GPU memory usage         |
| Network Download | Download speed           |
| Network Upload   | Upload speed             |
| Disk C:          | Drive usage (auto-detected) |
| Disk D: …        | Additional drives (if present) |

---

# Disk Monitoring

StrangeCat Monitor automatically detects all connected drives (C:, D:, E:, F:, G:, etc.).

## Data Collected Per Drive

* Usage percentage
* Used space (GB)
* Total space (GB)
* Free space (GB)
* Sparkline history (Graph mode)

## Options

Enable or disable disk monitoring globally under **Settings → Visible Metrics**, or toggle individual drives separately. Configuration is saved to `config.json`.

---

# Performance Modes

Choose a performance mode under **Settings → Display → Performance Mode**.

| Mode      | Disk     | RAM  | CPU  | GPU  | VRAM |
| --------- | -------- | ---- | ---- | ---- | ---- |
| Ultra     | 10s      | 1s   | 1s   | 1s   | 1s   |
| Normal    | 30s      | 2s   | 2s   | 2s   | 2s   |
| Optimized | 1 min    | 4s   | 4s   | 4s   | 4s   |
| Low       | 5 min    | 10s  | 10s  | 10s  | 10s  |

Each metric is collected on its own interval, reducing unnecessary system calls. The internal check loop runs every 0.5s.

---

# CPU Temperature

Windows usually requires an external helper application for accurate CPU temperatures.

StrangeCat Monitor automatically tries multiple methods and uses the first available source.

## Recommended: LibreHardwareMonitor

For the best compatibility:

1. Download LibreHardwareMonitor
2. Run it as Administrator
3. Leave it running in the background
4. Restart StrangeCat Monitor

Footer example:

```txt
src: LibreHardwareMonitor
```

---

## Temperature Source Priority

| Priority | Source               |
| -------- | -------------------- |
| 1        | psutil built-in      |
| 2        | WMI ACPI             |
| 3        | WMI PerfData         |
| 4        | LibreHardwareMonitor |
| 5        | CoreTemp             |

---

# Multilingual Support

StrangeCat Monitor supports **English** and **French**.

* Switch language instantly via the 🇬🇧 / 🇫🇷 flag button in the title bar
* Or go to **Settings → Display → Language**
* The entire interface updates in real time — no restart required

---

# Single Instance

Only one instance of StrangeCat Monitor can run at a time. If you try to launch a second instance, a message will appear:

```txt
StrangeCat Monitor is already running
```

This prevents duplicate entries in Task Manager.

---

# Close Behavior

When you click ✕, a confirmation dialog appears:

* **Minimize** — hides to system tray
* **Quit** — exits completely

You can check **Remember my choice** to skip this dialog in future sessions. Use the **Ask Again** button in Settings to reset this preference.

> When starting minimized, a tray notification appears for 3 seconds to confirm the app is running.

---

# Troubleshooting

## Wallpaper Shows "--" or No Data

Checklist:

* Is StrangeCat Monitor running?
* Does footer show `● :5100`?
* Is Wallpaper Engine using port `5100`?
* Does this URL work?

```txt
http://127.0.0.1:5100/performance
```

---

## CPU Temperature Shows "N/A"

Install and run:

```txt
LibreHardwareMonitor
```

as Administrator.

---

## GPU Shows 0% or Missing Data

GPU monitoring currently supports:

* ✅ NVIDIA GPUs
* ❌ AMD GPUs
* ❌ Intel GPUs

StrangeCat Monitor uses:

```txt
nvidia-smi
```

for GPU metrics.

---

## Window Is Off-Screen

Reset window position:

```txt
%APPDATA%\StrangeCat\config.json
```

Set:

```json
{
  "pos_x": 100,
  "pos_y": 100
}
```

Then restart the app.

---

## Port 5100 Already in Use

Change the port in:

```txt
Settings → HTTP API
```

Example:

```txt
5101
5200
```

---

## High CPU Usage

Recommended settings:

* Set Performance Mode to **Low** or **Optimized**
* Enable Low Power Mode
* Use 5s refresh rate
* Use Compact Mode
* Minimize to tray

---

## Reset All Settings

Delete:

```txt
%APPDATA%\StrangeCat\config.json
```

The app will recreate default settings automatically.

---

# For Developers

## Run from Source

Requires:

* Python 3.10+

Install dependencies:

```bash
pip install psutil pillow pystray pywin32 wmi
```

Generate icon:

```bash
python make_icon.py
```

Launch:

```bash
python strangecat_monitor.py
```

---

# HTTP API

## Endpoint

```http
GET http://127.0.0.1:5100/performance
```

---

## Example Response

```json
{
  "timestamp": 1767331384.18,
  "psutil": {
    "cpu": 40.0,
    "memory": 51.2,
    "gpu_usage": 22.0,
    "gpu_temp": 41.0,
    "cpu_temp": 58.5,
    "cpu_temp_method": "LibreHardwareMonitor",
    "upload_speed": 12.4,
    "download_speed": 340.1,
    "disk_C": 48.0,
    "disk_D": 14.0
  }
}
```

---

## Wallpaper Integration Example

```javascript
const PORT = 5100;

async function fetchStats() {
  try {
    const res = await fetch(
      `http://127.0.0.1:${PORT}/performance`
    );

    const data = await res.json();
    const ps = data.psutil ?? {};

    console.log(ps.cpu);
    console.log(ps.memory);
    console.log(ps.gpu_usage);
    console.log(ps.cpu_temp);
    console.log(ps.disk_C);

  } catch {
    // Monitor offline
  }
}

setInterval(fetchStats, 2000);
fetchStats();
```

---

# Build From Source

```bash
pip install pyinstaller psutil pillow pystray pywin32 wmi

python make_icon.py

build.bat
```

Output:

```txt
dist/StrangeCat Monitor.exe
```

---

# Config File

```txt
%APPDATA%\StrangeCat\config.json
```

All application settings are stored here.

Deleting the file resets everything to defaults.

---

# Changelog

## v3.6

* Configurable performance modes: Ultra, Normal, Optimized, Low
* Each metric collected at its own interval (smarter resource usage)
* New **Performance Mode** dropdown in Settings
* Removed redundant close-action dropdown (replaced by **Ask Again** button)

## v3.5

* Automatic disk detection (C:, D:, E:, …)
* Disk usage shown in Compact and Graph modes
* Per-drive toggle in Settings → Visible Metrics
* Disk data included in HTTP API response

## v3.4

* Minimum window height fixed at 100px (header always visible)
* Improved collapse behavior: collapsed graphs keep column width, only height is reduced
* Docstrings and comments added throughout the codebase

## v3.3

* Collapsed graphs stay visible at reduced size (spacer instead of hidden)
* Language flag button (🇫🇷 / 🇬🇧) added to the title bar for instant switching
* Single-instance enforcement via socket lock (port 51999)
* `os._exit(0)` used on quit — no background processes left running
* Fixed language change causing header/footer duplication
* Fixed Combobox text color in readonly mode

## v3.2

* Footer redesign
* Responsive native Tkinter grid
* Improved graph rendering (actual canvas height, padding fixes)
* Better compact mode resizing
* Refined dark theme
* Multilingual support (English / French), changeable in real time
* Improved close dialog: Minimize / Quit + Remember my choice
* Startup notification when launched minimized (auto-closes after 3s)

## v3.1

* First responsive graph grid
* Larger UI controls
* Low Power Mode
* GPU cache system

## v2.2

* CoreTemp crash fix
* Settings save fix
* Improved resize system (8 directions)

## v1.0

Initial release.
