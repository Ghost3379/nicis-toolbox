# 🧰 Nici's Toolbox (`nicis-toolbox`)

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/Ghost3379/nicis-toolbox)
[![Documentation](https://img.shields.io/badge/Docs-examples%2FREADME-blueviolet.svg)](examples/README.md)

A curated collection of handy Python utilities, electronics helpers, embedded scripts, and day-to-day productivity tools written by [@Ghost3379](https://github.com/Ghost3379).

---

## 🚀 Quickstart & Installation

Clone this repository and install it in **editable mode** so changes are immediately available system-wide:

```bash
git clone https://github.com/Ghost3379/nicis-toolbox.git
cd nicis-toolbox
pip install -e .
```

Now you can import any tool in Python or run CLI commands directly from your terminal!

```python
from nicis_toolbox import Pyklus, download_components, type_text, CpySnooze, DocForge, TracePlot, stash_archive
```

---

## 📦 What's Inside

| Tool | CLI Command | Module | Description | Guide & Demo |
| :--- | :--- | :--- | :--- | :--- |
| **Pyklus** | — | `nicis_toolbox.Pyklus` | Sub-microsecond stopwatch, context manager, and decorator timer with split laps and smart unit scaling. | [Docs](examples/README.md#1-⏱️-pyklus-stopwatch--benchmark-timer) • [Demo](examples/demo_pyklus.py) |
| **JLC Fetch** | `jlc-fetch` | `nicis_toolbox.jlc_fetch` | Auto-detects KiCad & `JLC2KiCadLib` to download LCSC/JLCPCB parts, symbols, footprints, and 3D models with SSL self-healing and isolated part folders. | [Docs](examples/README.md#2-🔌-jlc-fetch-kicad-component-puller) • [Demo](examples/demo_jlc_fetch.py) |
| **KiCad-Stash** | `kicad-stash` / `ki-stash` | `nicis_toolbox.kicad_stash` | External component archive sorter & linker. Unpacks SnapEDA / UltraLibrarian / JLC folders, auto-detects KiCad libraries (`_3dModels`, `_footprints.pretty`, `_symbols`), relinks 3D model paths in footprints and footprint nicknames in symbols. | [Docs](examples/README.md#7-🗄️-kicad-stash-external-component-archive-sorter--linker) • [Demo](examples/demo_kicad_stash.py) |
| **Ghostwriter** | `ghostwriter` | `nicis_toolbox.ghostwriter` | Simulates realistic human typing with Gaussian jitter, thinking pauses, and typo corrections. Zero external dependencies. | [Docs](examples/README.md#3-👻-ghostwriter-human-typing-mimic) • [Demo](examples/demo_ghostwriter.py) |
| **cpy-snooze** | — | `nicis_toolbox.cpy_snooze` | CircuitPython deep sleep helper. Uses the pin-swap trick to avoid `ValueError: Pin in use` and safely deinitializes hardware. | [Docs](examples/README.md#4-💤-cpy-snooze-circuitpython-deep-sleep-helper) • [Demo](examples/demo_cpy_snooze.py) |
| **DocForge** | `doc-forge` | `nicis_toolbox.doc_forge` | Batch Word (.docx) report and protocol generator with styling preservation, number ranges, exclusions, and CSV mode. | [Docs](examples/README.md#5-📄-docforge-batch-word-report-generator) • [Demo](examples/demo_doc_forge.py) |
| **TracePlot** | `trace-plot` | `nicis_toolbox.trace_plot` | Interactive Plotly visualizer for oscilloscope & measurement CSV/Excel data. Dual Y-axes, derivative traces, threshold stats & HTML export. | [Docs](examples/README.md#6-📈-traceplot-interactive-measurement--oscilloscope-visualizer) • [Demo](examples/demo_trace_plot.py) |

> 📖 **Looking for in-depth documentation and code examples?**  
> Check out the complete [**Tool Documentation & Examples Manual (examples/README.md)**](examples/README.md)!

---

## ⚡ Quick CLI Cheatsheet

Once installed with `pip install -e .`, you can run these commands directly from any terminal:

```bash
# 1. Fetch a KiCad component into an isolated folder with SSL self-healing (e.g. C318949)
jlc-fetch C318949

# 2. Stash a downloaded component zip (SnapEDA / UltraLibrarian) directly into your KiCad project:
kicad-stash TPS62840DLCR.zip

# 3. Simulate human typing from clipboard into Word / Google Docs (5s countdown)
ghostwriter -c

# 4. Generate batch of 100 Word reports, excluding broken units:
doc-forge template.docx -o ./reports --range 1 100 --exclude 89 90 --prefix "Messprotokoll_"

# 5. Interactively plot oscilloscope / frequency data with rate-of-change (diff):
trace-plot measurements.csv --diff --export report.html
```

---

## 📂 Repository Structure

```text
nicis-toolbox/
├── README.md               # Main repository storefront (You are here!)
├── pyproject.toml          # Packaging configuration & CLI entrypoints
├── .gitignore              # Ignored files & caches
├── LICENSE                 # MIT License
├── nicis_toolbox/          # Main package source
│   ├── __init__.py         # Package exports
│   ├── pyklus.py           # Precision stopwatch & timer utility
│   ├── jlc_fetch.py        # KiCad / JLC2KiCad component puller
│   ├── kicad_stash.py      # KiCad external component archive sorter & linker
│   ├── ghostwriter.py      # Human typing & keystroke simulator
│   ├── cpy_snooze.py       # CircuitPython single-button deep sleep manager
│   ├── doc_forge.py        # Batch Word report & protocol generator
│   └── trace_plot.py       # Interactive oscilloscope & measurement visualizer
└── examples/               # Runnable showcases & detailed documentation
    ├── README.md           # Full technical manual & API reference
    ├── demo_pyklus.py      # Pyklus stopwatch & decorator showcase
    ├── demo_jlc_fetch.py   # JLC fetch demo (TM-2025A lever switch C318949)
    ├── demo_kicad_stash.py # KiCad-Stash archive sorting & relinking demo
    ├── demo_ghostwriter.py # Ghostwriter human typing demo
    ├── demo_cpy_snooze.py  # CircuitPython single-button deep sleep guide
    ├── demo_doc_forge.py   # DocForge batch report generator demo
    ├── demo_trace_plot.py  # TracePlot interactive measurement visualizer demo
    └── sample_frequency_log.csv  # Anonymized sample frequency measurement dataset
```

---

## 📄 License
This project is open-source software licensed under the [MIT License](LICENSE).
