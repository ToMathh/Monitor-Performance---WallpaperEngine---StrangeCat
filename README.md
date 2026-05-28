```
╔══════════════════════════════════════════════════════════════════╗
║           🐱  STRANGECAT MONITOR  v3.2  —  README               ║
╚══════════════════════════════════════════════════════════════════╝
```

# StrangeCat Monitor

A lightweight Windows system monitor that sits on your desktop and feeds real-time performance data to your **Wallpaper Engine** wallpapers — all locally, no internet required.

---

## Table of Contents

- [What does it do?](#what-does-it-do)
- [Installation](#installation)
- [The Interface](#the-interface)
- [Graph Mode vs Compact Mode](#graph-mode-vs-compact-mode)
- [Settings](#settings)
- [Using it with Wallpaper Engine](#using-it-with-wallpaper-engine)
- [CPU Temperature](#cpu-temperature)
- [Troubleshooting](#troubleshooting)
- [For Developers](#for-developers)

---

## What does it do?

StrangeCat Monitor does two things at the same time:

**① It shows a floating widget on your desktop**
A small borderless window displays your system stats in real time — CPU usage, RAM, GPU, temperatures, and network speeds. It stays on top of everything, is draggable anywhere on screen, and resizable.

**② It feeds data to your Wallpaper Engine wallpapers**
Behind the scenes, it runs a tiny local server. Wallpaper Engine wallpapers that support StrangeCat Monitor can read your live system stats and display them — animated bars, live graphs, glowing indicators, whatever the wallpaper is designed to show.

```
  StrangeCat Monitor (running in background)
        │
        │  reads your hardware every 2 seconds
        │
        ├──► updates the floating widget on your desktop
        │
        └──► serves data at http://127.0.0.1:5100/performance
                    │
                    └──► Wallpaper Engine wallpaper reads it
                         and animates your stats live
```

> The monitor needs to be running for compatible wallpapers to show live data.
> You can minimize it to the system tray — it will keep working in the background.

---

## Installation

### Option A — Run from source (requires Python)

1. Make sure [Python 3.10+](https://www.python.org/) is installed
2. Open a terminal in the StrangeCat Monitor folder and run:

```
pip install psutil pillow pystray pywin32 wmi
```

3. Run once to generate the icon:
```
python make_icon.py
```

4. Launch the app:
```
python strangecat_monitor.py
```

### Option B — Standalone EXE (no Python needed)

Double-click `build.bat` to generate `dist\StrangeCat Monitor.exe`.
Move it anywhere you like and run it directly — no dependencies needed.

### Auto-start with Windows

Open Settings (`⚙`) → System → enable **"Start on boot"** and save.
StrangeCat Monitor will launch automatically every time Windows starts.

> **Tip:** If you use Wallpaper Engine, enabling auto-start ensures your wallpaper always has live data without having to manually launch the monitor.

---

## The Interface

```
┌──────────────────────────────────────────────────────┐  ← red accent line
│ 🐱 STRANGECAT          [⊟] [⚙] [—] [✕]             │  ← drag here to move
│    MONITOR  v3.2                                     │
├──────────────────────────────────────────────────────┤
│                                                      │
│   your metrics displayed here (graph or compact)     │
│                                                      │
├──────────────────────────────────────────────────────┤
│  src: LibreHardwareMonitor   14:32:07   ● :5100  ◢  │  ← footer
└──────────────────────────────────────────────────────┘  ← red accent line
```

**Title bar buttons:**

| Button | What it does |
|--------|--------------|
| `⊟` / `⊞` | Switch between Graph mode and Compact mode |
| `⚙` | Open Settings |
| `—` | Hide to system tray (keeps running) |
| `✕` | Quit completely |

**Footer (bottom of window):**

| Position | What it shows |
|----------|---------------|
| Left | Which method is reading your CPU temperature |
| Center | Current time |
| Right | `● :5100` = HTTP server active · `○ off` = disabled |

**Moving & resizing:**
- Drag the title bar to move the window
- Drag the `◢` corner (bottom-right) to resize
- The content scales automatically with the window size

---

## Graph Mode vs Compact Mode

Toggle between modes with the `⊟` / `⊞` button in the title bar.

### Graph Mode (default)

Each metric gets its own cell with a live sparkline graph showing the last 60 seconds of history. Cells are arranged in a responsive grid — 1, 2, or 3 columns depending on how wide you make the window.

```
  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
  │ ▾ CPU   40% │  │ ▾ RAM   51% │  │ ▾ GPU    22%│
  │ ∿∿∿∿∿∿∿∿●  │  │ ▬▬▬▬▬▬▬▬● │  │ ∿∿∿∿∿∿∿∿●  │
  └─────────────┘  └─────────────┘  └─────────────┘
  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
  │ ▾ GPU TEMP  │  │ ▾ VRAM  12% │  │ ▾ NET ↓     │
  │  41.0°      │  │ ▬▬●         │  │   ∿∿∿∿∿●   │
  └─────────────┘  └─────────────┘  └─────────────┘
```

Each cell can be **collapsed** individually by clicking the `▾` arrow — useful if you don't care about a specific metric but still want it active for the wallpaper.

Color coding:
- 🟢 Green = normal
- 🟡 Yellow = getting high (CPU/GPU/RAM above ~75%)
- 🔴 Red = critical (above ~90%)

### Compact Mode

A minimal bar-based view with no graphs — just labels, a progress bar, and the current value. Much smaller footprint, great for a corner of your screen.

```
  CPU       ▬▬▬▬▬▬▬▬▬▬▬▬░░░░░   40 %
  CPU TEMP  ▬▬▬▬▬▬▬▬░░░░░░░░░   58 °
  RAM       ▬▬▬▬▬▬▬▬▬▬▬▬▬░░░░   51 %
  GPU       ▬▬▬▬░░░░░░░░░░░░░   22 %
  ...
```

> In Compact mode, window height adjusts automatically to fit the content. Only width is resizable.

---

## Settings

Click `⚙` to open the settings window.

### System
| Option | Description |
|--------|-------------|
| Start on boot | Launch automatically when Windows starts |
| Start minimized | Start hidden in the system tray |

### Display
| Option | Description |
|--------|-------------|
| Always on top | Keep the window above all other apps |
| Compact mode | Switch to compact bar view |
| Opacity | Window transparency (from 30% to 100%) |
| Refresh rate | How often stats update (1, 2, or 5 seconds) |
| Temp unit | Celsius or Fahrenheit |
| Low power mode | Slow down refresh when window is hidden (saves CPU) |

### HTTP API
| Option | Description |
|--------|-------------|
| Enable HTTP server | Turn the data feed on or off |
| Port | Port number (default: **5100**) |

### Visible Metrics
Toggle each metric on or off individually — it hides it from the widget and stops sending it to wallpapers.

---

## Using it with Wallpaper Engine

### Compatible wallpapers

Wallpapers that support StrangeCat Monitor will automatically show your live stats when the monitor is running. Just make sure:

1. StrangeCat Monitor is running (or starts with Windows)
2. The HTTP server is enabled (footer shows `● :5100`)
3. The wallpaper is set in Wallpaper Engine

> **Port note:** StrangeCat Monitor uses port **5100**. Some other monitors (like sheetau's PerformanceMonitor) use port **5000**. If a wallpaper was built for port 5000, it won't connect to StrangeCat Monitor without changing either the port in Settings or the port in the wallpaper.

### What data is available to wallpapers?

| Metric | What it represents |
|--------|--------------------|
| CPU usage | How hard your processor is working, in % |
| CPU temperature | Processor temperature in °C or °F |
| RAM usage | How much of your memory is in use, in % |
| GPU usage | How hard your graphics card is working, in % |
| GPU temperature | Graphics card temperature |
| VRAM usage | How much GPU memory is in use, in % |
| Network download | Current download speed in KB/s |
| Network upload | Current upload speed in KB/s |

---

## CPU Temperature

Reading CPU temperature on Windows requires a helper app on most systems. StrangeCat Monitor tries several methods automatically and uses the first one that works:

1. Built-in Windows sensors (works on some laptops and OEM systems, no extra app needed)
2. **LibreHardwareMonitor** — the most reliable option for desktops
3. **CoreTemp** — alternative if LibreHardwareMonitor doesn't work on your system

The active source is shown in the bottom-left footer of the window.

**To get CPU temperature readings on most desktops:**

1. Download [LibreHardwareMonitor](https://github.com/LibreHardwareMonitor/LibreHardwareMonitor/releases)
2. Run it **as Administrator** (right-click → Run as administrator)
3. Leave it running in the background
4. Restart StrangeCat Monitor — the footer should now show `src: LibreHardwareMonitor`

> LibreHardwareMonitor can be minimized to the tray. It doesn't need to be visible to work.

---

## Troubleshooting

### My wallpaper shows "--" or no data

The wallpaper can't reach StrangeCat Monitor. Work through this checklist:

- **Is StrangeCat Monitor running?** Check your system tray for the 🐱 icon. If it's not there, launch the app.
- **Is the HTTP server on?** The footer should show `● :5100`. If it says `○ off`, go to Settings → HTTP API and enable it.
- **Is the port correct?** Open a browser and go to `http://127.0.0.1:5100/performance`. If you see a page full of numbers, the server is working fine — the issue is in the wallpaper. If the page doesn't load, the server isn't running.
- **Port mismatch?** Some wallpapers are built for port 5000 (a different monitor app). Check if your wallpaper has a port setting, or change the port in StrangeCat Monitor Settings to match.

---

### CPU temperature shows "N/A"

Windows doesn't give direct access to CPU temperature sensors on most systems.

**Fix:** Install [LibreHardwareMonitor](https://github.com/LibreHardwareMonitor/LibreHardwareMonitor/releases), run it as Administrator, and leave it in the background. See the [CPU Temperature](#cpu-temperature) section above.

---

### GPU shows 0% or no data

StrangeCat Monitor reads GPU data using NVIDIA's built-in tool (`nvidia-smi`). This only works with NVIDIA graphics cards.

- **AMD or Intel GPU:** GPU metrics are not supported. CPU, RAM, and network will still work fine.
- **NVIDIA GPU but still showing 0%:** Open a Command Prompt and type `nvidia-smi`. If you get an error, reinstall your NVIDIA drivers from [nvidia.com](https://www.nvidia.com/Download/index.aspx).

---

### The window disappeared / is off-screen

This can happen after changing monitor resolution or unplugging a display.

**Fix:**
1. Right-click the 🐱 tray icon → **Show**
2. If the window still doesn't appear on screen, open `%APPDATA%\StrangeCat\config.json` in Notepad, set `pos_x` and `pos_y` to `100`, save, and relaunch.

---

### Port 5100 is already in use

The footer shows `○ off` even with the server enabled, or the app shows an error on startup.

**Fix:** Go to Settings → HTTP API → change the port to something else (e.g. `5101`, `5200`). Click SAVE — the server restarts automatically. Update your wallpaper's port setting to match if needed.

> To find out what's using port 5100: open Command Prompt and run `netstat -ano | findstr :5100`

---

### The app uses too much CPU

- Enable **Low Power Mode** in Settings → Display (on by default)
- Set **Refresh Rate** to 5 seconds in Settings → Display
- Switch to **Compact Mode** — fewer graphics to draw
- Minimize to tray when you don't need the widget visible — refresh slows down automatically

---

### Auto-start doesn't work

**Fix:** Run StrangeCat Monitor once as Administrator (right-click the .exe or .py → Run as administrator), enable Start on boot in Settings, and save. Future launches won't need admin rights.

---

### Reset everything to defaults

Delete this file and the app will start fresh with default settings:

```
%APPDATA%\StrangeCat\config.json
```

---

## For Developers

### HTTP API

```
GET http://127.0.0.1:5100/performance
```

Response:

```json
{
  "timestamp": 1767331384.18,
  "psutil": {
    "cpu":              40.0,
    "memory":           51.2,
    "memory_gb":        "8.2GB/16.0GB",
    "gpu_usage":        22.0,
    "gpu_temp":         41.0,
    "vram_usage":       12.0,
    "vram_gb":          "1.5GB/12.0GB",
    "cpu_temp":         58.5,
    "cpu_temp_method":  "LibreHardwareMonitor",
    "upload_speed":     12.4,
    "download_speed":   340.1,
    "timestamp":        1767331384.18
  }
}
```

CORS header `Access-Control-Allow-Origin: *` is included on every response — no extra config needed in Wallpaper Engine.

### Wallpaper integration example

```javascript
const PORT = 5100;

async function fetchStats() {
  try {
    const res  = await fetch(`http://127.0.0.1:${PORT}/performance`);
    const data = await res.json();
    const ps   = data.psutil ?? {};

    // Use the values — all numbers, null if unavailable
    console.log(ps.cpu);           // CPU %
    console.log(ps.memory);        // RAM %
    console.log(ps.gpu_usage);     // GPU %
    console.log(ps.cpu_temp);      // °C or null
    console.log(ps.download_speed); // KB/s

  } catch {
    // Monitor not running — show fallback state
  }
}

setInterval(fetchStats, 2000); // match the default refresh rate
fetchStats();
```

### Building from source

```bat
pip install pyinstaller psutil pillow pystray pywin32 wmi
python make_icon.py
build.bat
```

Output: `dist\StrangeCat Monitor.exe`

### Config file

```
%APPDATA%\StrangeCat\config.json
```

All settings are stored here. The app creates it on first launch with defaults. Safe to delete to reset.

### Temperature source priority

| Priority | Source | Requires |
|----------|--------|----------|
| 1 | psutil built-in | Nothing (Linux / some OEM laptops) |
| 2 | WMI AcpiThermal | Nothing (ACPI BIOS) |
| 3 | WMI PerfData | Nothing (Windows performance counters) |
| 4 | LibreHardwareMonitor | Running as Administrator |
| 5 | CoreTemp | Running with shared memory enabled |

Active source exposed as `cpu_temp_method` in the API response.

### Changelog

**v3.2**
- Footer moved to bottom: temp source · time · HTTP status
- Graph grid fully rewritten — native Tkinter grid with `uniform` weights, no Canvas/Scrollbar
- Refined dark palette, green value labels, dot glow ring on sparklines
- Graph mode: correct initial height (420px) when toggling from compact

**v3.1**
- First responsive grid implementation in graph mode
- Larger footer and header buttons
- Low Power Mode, GPU cache (2s TTL)
- Default refresh rate increased from 1s to 2s

**v2.2**
- CoreTemp shared memory crash fixed
- Settings save fixed, config now in `%APPDATA%`
- 8-direction window resize

**v1.0**
- Initial release: floating widget, compact mode, HTTP API
