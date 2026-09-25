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
from nicis_toolbox import Pyklus, download_components
```

---

## 🔌 Tool Spotlight: `jlc_fetch` (KiCad Component Downloader)

Quickly pull component schematic symbols, footprints, and 3D STEP models from LCSC/JLCPCB into KiCad using `JLC2KiCadLib`.

### Features:
- 🔍 **Auto-detects `JLC2KiCadLib.exe`** across `%LOCALAPPDATA%`, `Program Files`, and system `PATH`.
- 📁 **Smart KiCad library path resolution** (handles local Documents and OneDrive automatically).
- 📦 **Batch downloads**: Fetch one or multiple parts at once.
- 💡 **Helpful installation guide**: Automatically prints instructions if `JLC2KiCadLib` is not yet installed.

### Usage:

**1. Interactive Prompt (just hit enter for defaults):**
```bash
jlc-fetch
# or: python -m nicis_toolbox.jlc_fetch
```
```text
=== JLC2KiCadLib Downloader ===
Enter LCSC C-Number(s) (comma or space separated, e.g. C561480): C561480, C2040
Output directory (Press Enter for [.../KiCad/JLC2KICAD-OUTPUT]): 
```

**2. Fast Command-Line Mode (Single or Multiple Parts):**
```bash
jlc-fetch C561480 C2040 C3110
```

**3. Custom Output Directory:**
```bash
jlc-fetch C561480 -d ./my_project_lib
```

---

## ⏱️ Tool Spotlight: `Pyklus`

`Pyklus` (or `zyklus`) is designed to eliminate boilerplate when measuring execution time.

### 1. As a Context Manager (Recommended)
Time any block of code with a simple `with` statement:

```python
import time
from nicis_toolbox import Pyklus

with Pyklus("Data Processing"):
    time.sleep(0.5)
```
```text
[START] [Data Processing] Timer started.
[DONE]  [Data Processing] Completed in 500.12 ms
```

### 2. As a Function Decorator
Benchmark entire functions effortlessly:

```python
from nicis_toolbox import Pyklus

@Pyklus.timeit("Heavy Math")
def compute_data():
    return sum(x * x for x in range(1_000_000))

compute_data()
```

### 3. Manual Stopwatch with Lap / Split Times
Track multi-step pipelines:

```python
import time
from nicis_toolbox import Pyklus

timer = Pyklus("ETL Pipeline").start()

# Step 1
time.sleep(0.2)
timer.lap("Extract")

# Step 2
time.sleep(0.3)
timer.lap("Transform")

# Finish
total = timer.stop()
print(f"Total run time: {timer.formatted_elapsed}")
```

### 4. Silent Mode
If you just want the math without terminal prints, set `verbose=False`:

```python
timer = Pyklus("Silent Task", verbose=False).start()
# do work...
duration = timer.stop()  # raw seconds as float
print(f"Took: {timer.formatted_elapsed}")
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
│   └── jlc_fetch.py        # KiCad / JLC2KiCad component puller
└── examples/
    └── demo_pyklus.py      # Runnable showcase script
```

---

## 🛠️ Adding New Tools

To add a new tool to your toolbox:
1. Create a new file in `nicis_toolbox/your_tool.py`.
2. Export your class or function in `nicis_toolbox/__init__.py`.
3. Add a row to the table in this `README.md`!

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).
