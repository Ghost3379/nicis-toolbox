import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import List, Optional, Tuple


def _get_symbols() -> Tuple[str, str, str]:
    """Return platform-safe symbols based on terminal encoding support."""
    try:
        encoding = sys.stdout.encoding or "utf-8"
        "⚡📦✅❌".encode(encoding)
        return ("⚡", "📦", "✅", "❌")
    except (UnicodeEncodeError, AttributeError):
        return ("->", "[PART]", "[OK]", "[ERROR]")


ICON_ARROW, ICON_PART, ICON_OK, ICON_ERR = _get_symbols()


def print_installation_guide() -> None:
    """Print helpful installation steps when JLC2KiCadLib is missing."""
    print("=" * 60)
    print(f"{ICON_ERR} JLC2KiCadLib was not found on your system!")
    print("=" * 60)
    print("\nHow to install JLC2KiCadLib:\n")
    print("Option 1: Install via standard pip (if Python is in PATH):")
    print("  pip install JLC2KiCadLib\n")
    print("Option 2: Install into KiCad's bundled Python environment (Windows):")
    print("  # Run this in PowerShell:")
    print('  & "$env:LOCALAPPDATA\\Programs\\KiCad\\10.0\\bin\\python.exe" -m pip install JLC2KiCadLib')
    print("  # Or for KiCad 8/9 in Program Files:")
    print('  & "C:\\Program Files\\KiCad\\8.0\\bin\\python.exe" -m pip install JLC2KiCadLib\n')
    print("Option 3: Set custom executable path via environment variable:")
    print("  $env:JLC2KICAD_EXE = 'C:\\path\\to\\JLC2KiCadLib.exe'\n")
    print("Learn more at: https://github.com/TousstNicolas/JLC2KiCadLib")
    print("=" * 60 + "\n")


def find_jlc_executable() -> Optional[Path]:
    """Auto-detect JLC2KiCadLib.exe from PATH, env var, or common KiCad install directories."""
    # 0. Check explicit environment variable
    custom_env = os.environ.get("JLC2KICAD_EXE")
    if custom_env and Path(custom_env).is_file():
        return Path(custom_env)

    # 1. Check system PATH
    which_path = shutil.which("JLC2KiCadLib") or shutil.which("JLC2KiCadLib.exe")
    if which_path:
        return Path(which_path)

    # 2. Check user's Local AppData (e.g. KiCad 10+, 9, 8, etc.)
    local_appdata = os.environ.get("LOCALAPPDATA")
    if local_appdata:
        kicad_base = Path(local_appdata) / "Programs" / "KiCad"
        if kicad_base.exists():
            for version_dir in sorted(kicad_base.glob("*"), reverse=True):
                candidate = version_dir / "bin" / "Scripts" / "JLC2KiCadLib.exe"
                if candidate.is_file():
                    return candidate

    # 3. Check Program Files
    for pf_key in ("ProgramFiles", "ProgramFiles(x86)"):
        pf = os.environ.get(pf_key)
        if pf:
            kicad_base = Path(pf) / "KiCad"
            if kicad_base.exists():
                for version_dir in sorted(kicad_base.glob("*"), reverse=True):
                    candidate = version_dir / "bin" / "Scripts" / "JLC2KiCadLib.exe"
                    if candidate.is_file():
                        return candidate

    return None


def get_default_output_dir() -> Path:
    """Find a sensible default KiCad output folder across OneDrive and local Documents."""
    candidates = []

    # Check OneDrive folders (German 'Dokumente' and English 'Documents')
    for env_var in ("OneDrive", "OneDriveCommercial", "OneDriveConsumer"):
        one_drive = os.environ.get(env_var)
        if one_drive:
            od_path = Path(one_drive)
            candidates.append(od_path / "Dokumente" / "KiCad" / "JLC2KICAD-OUTPUT")
            candidates.append(od_path / "Documents" / "KiCad" / "JLC2KICAD-OUTPUT")

    # Local Documents folders
    home = Path.home()
    candidates.append(home / "Dokumente" / "KiCad" / "JLC2KICAD-OUTPUT")
    candidates.append(home / "Documents" / "KiCad" / "JLC2KICAD-OUTPUT")
    candidates.append(home / "KiCad" / "JLC2KICAD-OUTPUT")

    for path in candidates:
        if path.parent.exists():
            return path

    return home / "KiCad_JLC_Output"


def download_components(
    c_numbers: List[str],
    output_dir: Path,
    exe_path: Optional[Path] = None,
) -> bool:
    """Download and convert one or more LCSC parts into KiCad libraries."""
    resolved_exe = exe_path or find_jlc_executable()

    if not resolved_exe or not resolved_exe.is_file():
        print_installation_guide()
        return False

    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"{ICON_ARROW} Using tool: {resolved_exe}")
    print(f"{ICON_ARROW} Output dir: {output_dir}\n")

    success_count = 0
    for c_num in c_numbers:
        clean_c = c_num.strip().upper()
        if not clean_c:
            continue
        if not clean_c.startswith("C"):
            clean_c = f"C{clean_c}"

        print(f"{ICON_PART} Fetching component: {clean_c} ...")
        command = [str(resolved_exe), clean_c, "-dir", str(output_dir)]

        try:
            subprocess.run(command, check=True)
            print(f"{ICON_OK} Successfully processed {clean_c}\n")
            success_count += 1
        except subprocess.CalledProcessError as e:
            print(f"{ICON_ERR} Failed to fetch {clean_c} (Exit code {e.returncode})\n")
        except Exception as e:
            print(f"{ICON_ERR} Error executing command: {e}\n")

    print(f"Finished: {success_count}/{len(c_numbers)} component(s) processed.")
    return success_count > 0


def main():
    parser = argparse.ArgumentParser(
        description="JLC2KiCadLib Downloader: Fetch JLCPCB/LCSC components directly into KiCad."
    )
    parser.add_argument(
        "c_numbers",
        nargs="*",
        help="One or more LCSC C-numbers (e.g. C561480 C2040)",
    )
    parser.add_argument(
        "-d",
        "--dir",
        type=Path,
        default=None,
        help="Custom output directory (default: your KiCad documents folder)",
    )
    parser.add_argument(
        "--exe",
        type=Path,
        default=None,
        help="Explicit path to JLC2KiCadLib.exe if not auto-detected",
    )
    args = parser.parse_args()

    # Pre-check executable so we can guide the user immediately if missing
    resolved_exe = args.exe or find_jlc_executable()
    if not resolved_exe:
        print_installation_guide()
        return

    # If no parts provided via CLI arguments, prompt interactively
    if not args.c_numbers:
        print("=== JLC2KiCadLib Downloader ===")
        user_input = input(
            "Enter LCSC C-Number(s) (comma or space separated, e.g. C561480): "
        ).strip()
        if not user_input:
            print("No C-number entered. Aborting.")
            return

        parts = [p.strip() for p in user_input.replace(",", " ").split() if p.strip()]

        default_dir = get_default_output_dir()
        custom_dir = input(
            f"Output directory (Press Enter for [{default_dir}]): "
        ).strip()
        out_dir = Path(custom_dir) if custom_dir else default_dir
    else:
        parts = args.c_numbers
        out_dir = args.dir or get_default_output_dir()

    download_components(parts, output_dir=out_dir, exe_path=resolved_exe)


if __name__ == "__main__":
    main()
