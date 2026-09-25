# 🧰 Nici's Toolbox (`nicis-toolbox`)

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/Ghost3379/nicis-toolbox)

A curated collection of handy Python utilities, helpers, and day-to-day productivity tools written by [@Ghost3379](https://github.com/Ghost3379).

---

## 📦 What's Inside

| Tool | Module / CLI | Description |
| :--- | :--- | :--- |
| **Pyklus** | `nicis_toolbox.Pyklus` | Precision stopwatch, context manager, and function decorator with split laps and smart unit formatting (`ns`, `us`, `ms`, `s`, `min:sec`). |
| **JLC Fetch** | `nicis_toolbox.jlc_fetch` / `jlc-fetch` | Auto-detects KiCad & `JLC2KiCadLib` to download LCSC/JLCPCB parts, symbols, footprints, and 3D models directly into KiCad libraries with batch support. |
| **Ghostwriter** | `nicis_toolbox.ghostwriter` / `ghostwriter` | Simulates realistic human typing with natural rhythm, thinking pauses, and realistic typos/backspaces. Perfect for Word and Google Docs. |
| **cpy-snooze** | `nicis_toolbox.cpy_snooze` | CircuitPython deep sleep helper. Uses a pin-swap trick to avoid `ValueError: Pin in use` and safely deinitializes hardware to save battery. |

---

## 🚀 Quickstart & Installation

Clone this repository to your local machine:

```bash
git clone https://github.com/Ghost3379/nicis-toolbox.git
cd nicis-toolbox
```

Install it in **editable mode** so changes you make to the code are immediately available everywhere on your machine:

```bash
pip install -e .
```

Now you can import your tools into any Python project or run CLI commands directly:

```python
from nicis_toolbox import Pyklus, download_components, type_text, CpySnooze
```

---

## 💤 Tool Spotlight: `cpy-snooze` (CircuitPython Deep Sleep Helper)

In CircuitPython, when you assign a GPIO to a button (`button = DigitalInOut(pin)`), the runtime locks that pin exclusively. Trying to arm an `alarm.pin.PinAlarm(pin)` while the button still owns it throws a fatal error:

> `ValueError: Pin in use`

Most projects compromise by wiring *two separate buttons* (one for normal control, one to wake up). **`cpy-snooze`** solves this cleanly using the **Pin-Swap Trick**:
1. Releases the real button pin with `.deinit()`.
2. Temporarily points the button reference to an unused dummy GPIO pin.
3. Automatically shuts down power-hungry peripherals (NeoPixels, I2S audio, I2C IMUs, PWM LEDs) to reach true microamp quiescent current.
4. Arms the `PinAlarm` on the freed hardware pin and enters deep sleep!

### Usage in CircuitPython (`code.py`):

```python
import time
import board
import neopixel
from nicis_toolbox.cpy_snooze import CpySnooze

# 1. Initialize Snooze with physical button pin and a dummy pin
snooze = CpySnooze(button_pin=board.D2, dummy_pin=board.D6)
button = snooze.button

# 2. Check if the board just woke from sleep
if CpySnooze.woke_from_sleep():
    print("Woke up from button press!")

# 3. Setup hardware
pixels = neopixel.NeoPixel(board.D5, 144)

# 4. Register hardware for automated power-down
snooze.register(pixels)

# 5. When idle, enter deep sleep safely
snooze.deep_sleep()
```

*(You can also copy [cpy_snooze.py](file:///c:/Users/i40011169/LOCAL%20Docs/GIT/nicis-toolbox/nicis_toolbox/cpy_snooze.py) directly into the `/lib` folder of your `CIRCUITPY` drive!)*

---

## 👻 Tool Spotlight: `ghostwriter` (Human Typing Mimic)

Simulates realistic human keystrokes directly into Word, Google Docs, or text editors to bypass paste-detection and version-history inspections.

### Features:
- 📋 **Clipboard Direct**: Copy text anywhere, run `ghostwriter -c`, and it types what is on your clipboard.
- 🇩🇪 **Native Unicode & Umlaut Support**: Full native support for German characters (`ä`, `ö`, `ü`, `ß`) without dropped keys.
- 🎯 **Simulated Typos & Corrections**: Occasionally hits adjacent keys, pauses to "notice" the mistake, hits Backspace, and corrects it.
- 🧠 **Natural Thinking Pauses**: Pauses longer at the end of sentences (`.`, `!`, `?`) and paragraphs (`\n`).
- ⚡ **Zero External Dependencies**: Built entirely on standard Python and native OS APIs.

### Usage:

```bash
# Copy text with Ctrl+C, then run:
ghostwriter -c
```

---

## 🔌 Tool Spotlight: `jlc_fetch` (KiCad Component Downloader)

Quickly pull component schematic symbols, footprints, and 3D STEP models from LCSC/JLCPCB into KiCad using `JLC2KiCadLib`.

### Features:
- 🔍 **Auto-detects `JLC2KiCadLib.exe`** across `%LOCALAPPDATA%`, `Program Files`, and system `PATH`.
- 📁 **Smart KiCad library path resolution** (handles local Documents and OneDrive automatically).
- 📦 **Batch downloads**: Fetch one or multiple parts at once.

### Usage:

```bash
# Interactive prompt:
jlc-fetch

# Fast command-line mode:
jlc-fetch C561480 C2040 C3110
```

---

## ⏱️ Tool Spotlight: `Pyklus`

`Pyklus` (or `zyklus`) is designed to eliminate boilerplate when measuring execution time.

### Usage:

```python
import time
from nicis_toolbox import Pyklus

# 1. Context Manager
with Pyklus("Fast Calculation"):
    time.sleep(0.5)

# 2. Function Decorator
@Pyklus.timeit("Heavy Function")
def do_work():
    ...
```

---

## 📂 Repository Structure

```text
nicis-toolbox/
├── README.md               # You are here!
├── pyproject.toml          # Packaging configuration & CLI entrypoints
├── .gitignore              # Ignored files & caches
├── LICENSE                 # MIT License
├── nicis_toolbox/          # Main package source
│   ├── __init__.py         # Package exports
│   ├── pyklus.py           # Precision stopwatch & timer utility
│   ├── jlc_fetch.py        # KiCad / JLC2KiCad component puller
│   ├── ghostwriter.py      # Human typing & keystroke simulator
│   └── cpy_snooze.py       # CircuitPython single-button deep sleep manager
└── examples/
    ├── demo_pyklus.py      # Pyklus demo
    └── demo_cpy_snooze.py  # cpy-snooze demo & guide
```

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).
