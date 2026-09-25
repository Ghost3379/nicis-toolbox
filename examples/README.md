# 📖 Tool Documentation & Examples Manual

This directory contains runnable demonstrations and in-depth technical documentation for every utility in **`nicis-toolbox`**.

---

## 📑 Table of Contents
1. [⏱️ Pyklus (Stopwatch & Benchmark Timer)](#1-⏱️-pyklus-stopwatch--benchmark-timer)
2. [🔌 JLC Fetch (KiCad Component Puller)](#2-🔌-jlc-fetch-kicad-component-puller)
3. [👻 Ghostwriter (Human Typing Mimic)](#3-👻-ghostwriter-human-typing-mimic)
4. [💤 cpy-snooze (CircuitPython Deep Sleep Helper)](#4-💤-cpy-snooze-circuitpython-deep-sleep-helper)

---

## 1. ⏱️ Pyklus (Stopwatch & Benchmark Timer)

**Demo Script:** [`demo_pyklus.py`](./demo_pyklus.py)  
**Module:** `nicis_toolbox.Pyklus` (or `nicis_toolbox.zyklus`)

`Pyklus` is an all-in-one execution timer with sub-microsecond precision (`time.perf_counter()`), supporting split laps, context managers, and function decorators.

### Key Capabilities:
- **Smart Unit Scaling:** Automatically formats raw seconds into human units:
  - `< 1 µs` $\rightarrow$ `ns` (nanoseconds)
  - `< 1 ms` $\rightarrow$ `us` (microseconds)
  - `< 1 s` $\rightarrow$ `ms` (milliseconds)
  - `< 60 s` $\rightarrow$ `s` (seconds)
  - `≥ 60 s` $\rightarrow$ `Xm YY.YYs` (minutes and seconds)
- **Safe Terminal Output:** Adapts prefixes (`⏱️`/`[START]`, `↳`/`->`, `🏁`/`[DONE]`) to match terminal encoding (UTF-8 vs Windows CP1252).

### Usage Patterns:

#### A. Context Manager (Cleanest for blocks)
```python
import time
from nicis_toolbox import Pyklus

with Pyklus("Data Processing"):
    time.sleep(0.25)
```
```text
[START] [Data Processing] Timer started.
[DONE]  [Data Processing] Completed in 250.31 ms
```

#### B. Function Decorator
```python
from nicis_toolbox import Pyklus

@Pyklus.timeit("Sorting Algorithm")
def sort_items(data):
    return sorted(data)
```

#### C. Manual Stopwatch with Lap / Split Times
```python
import time
from nicis_toolbox import Pyklus

timer = Pyklus("Pipeline").start()
time.sleep(0.1)
timer.lap("Step 1: Download")
time.sleep(0.2)
timer.lap("Step 2: Parse")
total_seconds = timer.stop()
```

---

## 2. 🔌 JLC Fetch (KiCad Component Puller)

**Demo Script:** [`demo_jlc_fetch.py`](./demo_jlc_fetch.py)  
**Module:** `nicis_toolbox.jlc_fetch`  
**CLI Command:** `jlc-fetch`

Downloads components from JLCPCB/LCSC via `JLC2KiCadLib` and generates ready-to-use KiCad schematic symbols, footprints, and 3D STEP models.

### Key Capabilities:
- **Auto-Discovery:** Automatically scans `%LOCALAPPDATA%`, `C:\Program Files\KiCad`, and system `PATH` to locate `JLC2KiCadLib.exe`.
- **Smart Library Paths:** Resolves default KiCad library folders across local Documents and OneDrive (`.../KiCad/JLC2KICAD-OUTPUT`) with zero hardcoded paths.
- **Batch Mode:** Fetch multiple parts in a single run.
- **Troubleshooting Guide:** Automatically prints an installation guide if `JLC2KiCadLib` is not detected.

### CLI Usage:
```bash
# Interactive mode (prompts for C-number and output folder):
jlc-fetch

# Fast single-part download (e.g. TM-2025A lever switch):
jlc-fetch C318949

# Batch downloading multiple parts:
jlc-fetch C318949 C2040 C561480

# Custom output destination:
jlc-fetch C318949 -d ./my_footprints
```

### Python API Usage:
```python
from pathlib import Path
from nicis_toolbox import download_components

download_components(["C318949"], output_dir=Path("./kicad_libs"))
```

### 💡 Corporate Proxy & SSL Verification Fix:
If running on a corporate network with SSL inspection proxies, `requests` may raise `SSLCertVerificationError`. Fix this once across all KiCad Python tools by installing `pip-system-certs`:
```powershell
& "$env:LOCALAPPDATA\Programs\KiCad\10.0\bin\python.exe" -m pip install pip-system-certs
```

---

## 3. 👻 Ghostwriter (Human Typing Mimic)

**Demo Script:** [`demo_ghostwriter.py`](./demo_ghostwriter.py)  
**Module:** `nicis_toolbox.ghostwriter`  
**CLI Command:** `ghostwriter`

Simulates realistic human keystrokes directly into Word, Google Docs, or text editors to bypass paste-detection and version-history inspections.

### Key Capabilities:
- **Zero External Dependencies:** Built with Python standard library `ctypes` accessing native Windows `SendInput` APIs.
- **Full German Character Support:** Correctly types German umlauts (`ä`, `ö`, `ü`, `ß`) and punctuation without dropped or corrupted characters.
- **Anti-Bot Rhythm Engine:**
  - **Keystroke Jitter:** Gaussian distribution around your target WPM.
  - **Sentence & Paragraph Thinking:** Longer natural pauses at `.`, `!`, `?` (0.5s–1.6s) and newlines (0.8s–2.2s).
  - **Simulated Typos & Corrections:** ~2% chance of hitting an adjacent key, pausing to "realize" the mistake, hitting `Backspace`, and typing the correct character.
- **Direct Clipboard Mode (`-c`):** Read text straight from the OS clipboard without saving to a temporary file.

### CLI Usage:
```bash
# 1. Direct from Clipboard (Fastest):
# Copy your text with Ctrl+C, then execute:
ghostwriter -c

# 2. From a text file:
ghostwriter essay.txt

# 3. Custom speed and startup countdown:
ghostwriter -c --wpm 70 --delay 3

# 4. Disable typos for perfectly accurate typing:
ghostwriter -c --no-typos
```

### Python API Usage:
```python
from nicis_toolbox import type_text

type_text("Hier ist mein Text zum Tippen.", speed_wpm=60, simulate_typos=True, delay_start=5)
```

---

## 4. 💤 cpy-snooze (CircuitPython Deep Sleep Helper)

**Demo Script:** [`demo_cpy_snooze.py`](./demo_cpy_snooze.py)  
**Module:** `nicis_toolbox.cpy_snooze` (or `nicis_toolbox.CpySnooze`)

Solves the classic CircuitPython single-button deep sleep dilemma by implementing the **Pin-Swap Trick**.

### The CircuitPython "Pin in Use" Problem:
1. When you define `button = DigitalInOut(pin)`, CircuitPython locks that GPIO exclusively.
2. If you try to create an `alarm.pin.PinAlarm(pin)` while the button object is alive, it crashes with:  
   `ValueError: Pin in use`
3. If you simply `.deinit()` the button, any remaining references or loops crash with `ValueError: Object deinitialized`.

### The Pin-Swap Solution:
1. **Swap & Free:** `snooze.deep_sleep()` deinitializes the button on the hardware pin and temporarily points the object to an unused dummy GPIO pin.
2. **Power Down Hardware:** Automatically deinitializes registered peripherals (NeoPixels, I2S audio, I2C IMUs, PWM LEDs) to reach true microamp quiescent current.
3. **Arm Alarm:** Binds `alarm.pin.PinAlarm` to the freed physical button pin and enters deep sleep.
4. When awakened, the exact same single button continues normal operation!

### Usage in CircuitPython (`code.py`):
```python
import time
import board
import neopixel
from nicis_toolbox.cpy_snooze import CpySnooze

# 1. Initialize Snooze Manager (D2 = physical button, D6 = unused dummy pin)
snooze = CpySnooze(button_pin=board.D2, dummy_pin=board.D6)
button = snooze.button

# 2. Check if board woke from sleep
if CpySnooze.woke_from_sleep():
    print("Woke up from deep sleep button press!")

# 3. Setup and register power-hungry peripherals
pixels = neopixel.NeoPixel(board.D5, 144)
snooze.register(pixels)

# 4. Main application loop
while True:
    if not button.value:
        print("Button pressed during runtime!")
    
    # On idle timeout:
    snooze.deep_sleep()
```

*(You can copy [`cpy_snooze.py`](../nicis_toolbox/cpy_snooze.py) directly into the `/lib` folder of your `CIRCUITPY` USB drive!)*
