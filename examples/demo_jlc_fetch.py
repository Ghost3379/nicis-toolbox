"""
Demo: Fetching JLCPCB/LCSC components for KiCad using jlc_fetch.

This demo pulls the XKB Connection TM-2025A multi-directional lever switch
(JLCPCB Part: C318949), complete with its schematic symbol, footprint, and 3D model.
"""

import sys
from pathlib import Path

# Add project root to sys.path so it works without pip install
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from nicis_toolbox import download_components, find_jlc_executable
from nicis_toolbox.jlc_fetch import get_default_output_dir


def main():
    print("=== JLC Fetch Demo ===")
    print("Component: XKB Connection TM-2025A (Multi-Directional Lever Switch)")
    print("Part Number: C318949\n")

    # 1. Verify executable is found
    exe = find_jlc_executable()
    if not exe:
        print("[!] JLC2KiCadLib.exe was not detected automatically.")
        print("    Run 'jlc-fetch' in your terminal to see installation options.")
        return

    print(f"Found JLC2KiCadLib at: {exe}")

    # 2. Choose output directory (here: ./output_demo next to this script)
    output_dir = Path(__file__).parent / "jlc_demo_output"
    print(f"Target Output Directory: {output_dir}\n")

    # 3. Download and convert component
    success = download_components(["C318949"], output_dir=output_dir)

    if success:
        print("\n🎉 Component C318949 successfully converted!")
        print(f"Check the generated KiCad files in: {output_dir.resolve()}")
    else:
        print("\n[!] Failed to download component. Please check your internet connection.")


if __name__ == "__main__":
    main()
