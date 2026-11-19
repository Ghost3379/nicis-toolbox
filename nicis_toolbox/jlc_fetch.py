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
    print("  pip install JLC2KiCadLib pip-system-certs\n")
    print("Option 2: Install into KiCad's bundled Python environment (Windows):")
    print("  # Run this in PowerShell:")
    print('  & "$env:LOCALAPPDATA\\Programs\\KiCad\\10.0\\bin\\python.exe" -m pip install JLC2KiCadLib pip-system-certs')
    print("  # Or for KiCad 8/9 in Program Files:")
    print('  & "C:\\Program Files\\KiCad\\8.0\\bin\\python.exe" -m pip install JLC2KiCadLib pip-system-certs\n')
    print("Option 3: Set custom executable path via environment variable:")
    print("  $env:JLC2KICAD_EXE = 'C:\\path\\to\\JLC2KiCadLib.exe'\n")
    print("Note: 'pip-system-certs' allows KiCad to trust corporate VPN/SSL inspection proxies.")
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


def find_associated_python(exe_path: Path) -> Optional[Path]:
    """Find the python.exe that powers this JLC2KiCadLib executable."""
    candidates = [
        exe_path.parent.parent / "python.exe",
        exe_path.parent / "python.exe",
        exe_path.parent.parent.parent / "python.exe",
    ]
    for cand in candidates:
        if cand.is_file():
            return cand

    py_which = shutil.which("python") or shutil.which("python3")
    if py_which:
        return Path(py_which)
    return None


def repair_ssl_certificates(python_exe: Path, is_auto_healing: bool = False) -> bool:
    """Install pip-system-certs into target Python environment to trust Windows/VPN Root CAs."""
    if is_auto_healing:
        print(f"\n{ICON_ARROW} Detected corporate SSL/VPN proxy block (CERTIFICATE_VERIFY_FAILED).")
        print(f"{ICON_ARROW} Auto-healing: Installing 'pip-system-certs' into KiCad Python environment...")
    else:
        print(f"\n{ICON_ARROW} Installing 'pip-system-certs' into KiCad Python environment...")
    print(f"{ICON_ARROW} Python binary: {python_exe}")
    try:
        res = subprocess.run(
            [str(python_exe), "-m", "pip", "install", "pip-system-certs"],
            capture_output=True,
            text=True,
        )
        if res.returncode == 0:
            print(f"{ICON_OK} 'pip-system-certs' installed successfully!\n")
            return True

        # Fallback with trusted hosts if pip itself was blocked by SSL proxy
        print(f"{ICON_ARROW} Standard pip install failed, retrying with trusted PyPI hosts...")
        res_retry = subprocess.run(
            [
                str(python_exe),
                "-m",
                "pip",
                "install",
                "pip-system-certs",
                "--trusted-host",
                "pypi.org",
                "--trusted-host",
                "files.pythonhosted.org",
            ],
            capture_output=True,
            text=True,
        )
        if res_retry.returncode == 0:
            print(f"{ICON_OK} 'pip-system-certs' installed successfully!\n")
            return True

        print(f"{ICON_ERR} Failed to auto-install pip-system-certs:\n{res_retry.stderr}")
        return False
    except Exception as err:
        print(f"{ICON_ERR} Error attempting auto-healing: {err}")
        return False


def _run_fetch_cmd(resolved_exe: Path, clean_c: str, output_dir: Path) -> Tuple[int, str]:
    """Execute JLC2KiCadLib while streaming live output and capturing text for analysis."""
    command = [str(resolved_exe), clean_c, "-dir", str(output_dir)]
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )
    except Exception as e:
        return -1, str(e)

    captured_output: List[str] = []
    if process.stdout:
        for line in process.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
            captured_output.append(line)
    process.wait()
    return process.returncode, "".join(captured_output)


def _consolidate_component_folder(comp_dir: Path) -> None:
    """Move all files from subfolders directly into the component folder and remove empty subfolders."""
    for p in list(comp_dir.rglob("*")):
        if p.is_file() and p.parent != comp_dir:
            dest = comp_dir / p.name
            if not dest.exists():
                shutil.move(str(p), str(dest))

    # Clean up empty subdirectories created by JLC2KiCadLib (footprint/, symbol/, packages3d/)
    for d in sorted(comp_dir.glob("*"), reverse=True):
        if d.is_dir():
            shutil.rmtree(d, ignore_errors=True)

    # Clean up 3D model path inside .kicad_mod to match consolidated folder
    for mod_file in comp_dir.glob("*.kicad_mod"):
        try:
            content = mod_file.read_text(encoding="utf-8", errors="ignore")
            # Replace 'packages3d/filename.step' with './filename.step'
            updated = re.sub(r'\(model\s+(?:"packages3d/|packages3d/)', '(model "./', content)
            mod_file.write_text(updated, encoding="utf-8")
        except Exception:
            pass


def download_components(
    c_numbers: List[str],
    output_dir: Path,
    exe_path: Optional[Path] = None,
) -> bool:
    """Download and convert one or more LCSC parts into dedicated component folders."""
    resolved_exe = exe_path or find_jlc_executable()

    if not resolved_exe or not resolved_exe.is_file():
        print_installation_guide()
        return False

    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"{ICON_ARROW} Using tool: {resolved_exe}")
    print(f"{ICON_ARROW} Output dir: {output_dir}\n")

    ssl_healed = False
    success_count = 0
    for c_num in c_numbers:
        clean_c = c_num.strip().upper()
        if not clean_c:
            continue
        if not clean_c.startswith("C"):
            clean_c = f"C{clean_c}"

        comp_dir = output_dir / clean_c
        comp_dir.mkdir(parents=True, exist_ok=True)

        print(f"{ICON_PART} Fetching component: {clean_c} -> {comp_dir.name}/ ...")
        returncode, output_text = _run_fetch_cmd(resolved_exe, clean_c, comp_dir)

        # Detect SSL / corporate VPN proxy block
        is_ssl_error = any(
            err_token in output_text
            for err_token in (
                "CERTIFICATE_VERIFY_FAILED",
                "SSLCertVerificationError",
                "self-signed certificate in certificate chain",
            )
        )

        if returncode != 0 and is_ssl_error and not ssl_healed:
            py_exe = find_associated_python(resolved_exe)
            if py_exe and repair_ssl_certificates(py_exe, is_auto_healing=True):
                ssl_healed = True
                print(f"{ICON_PART} Retrying fetch for {clean_c} ...")
                returncode, output_text = _run_fetch_cmd(resolved_exe, clean_c, comp_dir)

        if returncode == 0:
            _consolidate_component_folder(comp_dir)
            print(f"{ICON_OK} Successfully saved {clean_c} -> {comp_dir.name}/\n")
            success_count += 1
        else:
            print(f"{ICON_ERR} Failed to fetch {clean_c} (Exit code {returncode})\n")

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
    parser.add_argument(
        "--fix-ssl",
        action="store_true",
        help="Install pip-system-certs into KiCad's Python to trust corporate SSL/VPN proxies",
    )
    args = parser.parse_args()

    # Pre-check executable so we can guide the user immediately if missing
    resolved_exe = args.exe or find_jlc_executable()
    if not resolved_exe:
        print_installation_guide()
        return

    # Handle explicit --fix-ssl flag
    if args.fix_ssl:
        py_exe = find_associated_python(resolved_exe)
        if py_exe:
            repair_ssl_certificates(py_exe)
        else:
            print(f"{ICON_ERR} Could not determine Python binary for {resolved_exe}")
        if not args.c_numbers:
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
