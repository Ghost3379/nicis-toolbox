"""
KiCad-Stash: Auto-sort external component archives (SnapEDA, UltraLibrarian, SamacSys, etc.)
directly into your KiCad project or global library folders, with automatic 3D model relinking.
"""

import argparse
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
from typing import Dict, List, Optional, Tuple
import zipfile


def _get_symbols() -> Tuple[str, str, str, str]:
    """Return platform-safe symbols based on terminal encoding support."""
    try:
        encoding = sys.stdout.encoding or "utf-8"
        "📦✅❌⚡".encode(encoding)
        return ("📦", "✅", "❌", "⚡")
    except (UnicodeEncodeError, AttributeError):
        return ("[STASH]", "[OK]", "[ERR]", "->")


ICON_STASH, ICON_OK, ICON_ERR, ICON_ARROW = _get_symbols()


def find_library_structure(lib_dir: Path) -> Dict[str, Path]:
    """
    Auto-detect 3D model, footprint (.pretty), and symbol directories inside target library.
    If subfolders do not exist yet, creates them matching existing project prefix conventions.
    """
    lib_dir = lib_dir.resolve()
    if not lib_dir.exists():
        lib_dir.mkdir(parents=True, exist_ok=True)

    structure: Dict[str, Optional[Path]] = {
        "models_3d": None,
        "footprints": None,
        "symbols": None,
    }

    subdirs = [d for d in lib_dir.iterdir() if d.is_dir()]
    for d in subdirs:
        name_lower = d.name.lower()
        if structure["models_3d"] is None and ("3d" in name_lower or "model" in name_lower):
            structure["models_3d"] = d
        elif structure["footprints"] is None and (d.name.endswith(".pretty") or "footprint" in name_lower):
            structure["footprints"] = d
        elif structure["symbols"] is None and ("sym" in name_lower or "symbol" in name_lower):
            structure["symbols"] = d

    # Detect existing naming prefix if any folder has e.g. 'NX-Edge_'
    prefix = ""
    for found_dir in filter(None, structure.values()):
        if "_" in found_dir.name:
            prefix = found_dir.name.split("_")[0] + "_"
            break

    # Auto-create missing directories matching detected convention
    if not structure["models_3d"]:
        structure["models_3d"] = lib_dir / f"{prefix}3dModels"
        structure["models_3d"].mkdir(parents=True, exist_ok=True)
    if not structure["footprints"]:
        structure["footprints"] = lib_dir / f"{prefix}footprints.pretty"
        structure["footprints"].mkdir(parents=True, exist_ok=True)
    if not structure["symbols"]:
        structure["symbols"] = lib_dir / f"{prefix}symbols"
        structure["symbols"].mkdir(parents=True, exist_ok=True)

    return {k: v for k, v in structure.items() if v is not None}


def auto_detect_library_dir(start_dir: Optional[Path] = None) -> Optional[Path]:
    """Search working directory and parents for a KiCad library folder."""
    current = (start_dir or Path.cwd()).resolve()

    # Search current and subdirectories (up to 3 levels down)
    for root, dirs, _ in os.walk(str(current)):
        depth = len(Path(root).relative_to(current).parts)
        if depth > 3:
            dirs.clear()
            continue
        p = Path(root)
        name_lower = p.name.lower()
        if "kicad" in name_lower and ("lib" in name_lower or "library" in name_lower):
            return p
        if any(d.endswith(".pretty") for d in dirs):
            return p

    # Search up to parent directories (up to 3 levels up)
    cand = current
    for _ in range(3):
        cand = cand.parent
        for sub in cand.glob("*"):
            if sub.is_dir():
                name_lower = sub.name.lower()
                if "kicad" in name_lower and ("lib" in name_lower or "library" in name_lower):
                    return sub

    return None


def relink_3d_model(kicad_mod_path: Path, rel_3d_path: str) -> bool:
    """
    Ensure the .kicad_mod file correctly references the 3D model via portable relative path.
    """
    try:
        content = kicad_mod_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return False

    normalized_rel = rel_3d_path.replace("\\", "/")

    # Check if a (model ...) section already exists
    if re.search(r"\(model\s+", content):
        # Replace existing model path string or unquoted token
        updated = re.sub(
            r'\(model\s+(?:"[^"]*"|[^\s\(\)]+)',
            f'(model "{normalized_rel}"',
            content,
            count=1,
        )
    else:
        # Inject model block before the final closing parenthesis
        model_block = (
            f'\n  (model "{normalized_rel}"\n'
            f"    (at (xyz 0 0 0))\n"
            f"    (scale (xyz 1 1 1))\n"
            f"    (rotate (xyz 0 0 0))\n"
            f"  )\n"
        )
        last_paren = content.rfind(")")
        if last_paren != -1:
            updated = content[:last_paren] + model_block + content[last_paren:]
        else:
            updated = content + model_block

    try:
        kicad_mod_path.write_text(updated, encoding="utf-8")
        return True
    except Exception:
        return False


def relink_symbol_footprint(
    kicad_sym_path: Path,
    lib_nickname: str,
    footprint_name: Optional[str] = None,
) -> bool:
    """
    Ensure the symbol points to '<lib_nickname>:<footprint_name>' instead of generic 'footprint:...'.
    """
    try:
        content = kicad_sym_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return False

    # If footprint_name is not provided, extract existing footprint name from the property
    if not footprint_name:
        match = re.search(r'\(property\s+"Footprint"\s+"(?:[^:"]*:)?([^"]+)"', content)
        if match:
            footprint_name = match.group(1)

    if not footprint_name:
        return False

    target_ref = f"{lib_nickname}:{footprint_name}"

    if re.search(r'\(property\s+"Footprint"', content):
        updated = re.sub(
            r'(\(property\s+"Footprint"\s+)"[^"]*"',
            rf'\1"{target_ref}"',
            content,
        )
    else:
        # Inject Footprint property after Value or Reference
        prop_block = f'\n    (property "Footprint" "{target_ref}" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))'
        val_match = re.search(r'(\(property\s+"Value"[\s\S]*?\)\s*\))', content)
        if val_match:
            idx = val_match.end()
            updated = content[:idx] + prop_block + content[idx:]
        else:
            last_paren = content.rfind(")")
            updated = content[:last_paren] + prop_block + content[last_paren:] if last_paren != -1 else content + prop_block

    try:
        kicad_sym_path.write_text(updated, encoding="utf-8")
        return True
    except Exception:
        return False


def stash_archive(
    source_path: Path,
    target_lib: Path,
    overwrite: bool = True,
) -> Dict[str, List[Path]]:
    """
    Unpack archive or scan folder, distribute files to KiCad library, and relink 3D models.
    """
    source_path = source_path.resolve()
    target_lib = target_lib.resolve()

    lib_struct = find_library_structure(target_lib)
    models_3d_dir = lib_struct["models_3d"]
    footprints_dir = lib_struct["footprints"]
    symbols_dir = lib_struct["symbols"]

    stashed: Dict[str, List[Path]] = {
        "models_3d": [],
        "footprints": [],
        "symbols": [],
    }

    with tempfile.TemporaryDirectory() as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)

        if source_path.is_file() and source_path.suffix.lower() == ".zip":
            with zipfile.ZipFile(source_path, "r") as zf:
                zf.extractall(tmp_dir)
            scan_dir = tmp_dir
        elif source_path.is_dir():
            scan_dir = source_path
        else:
            # Single component file passed directly
            scan_dir = tmp_dir
            shutil.copy2(source_path, tmp_dir / source_path.name)

        # Collect all relevant files
        found_3d: List[Path] = []
        found_fps: List[Path] = []
        found_syms: List[Path] = []

        for p in scan_dir.rglob("*"):
            if not p.is_file():
                continue
            ext = p.suffix.lower()
            if ext in (".step", ".stp", ".wrl"):
                found_3d.append(p)
            elif ext == ".kicad_mod":
                found_fps.append(p)
            elif ext in (".kicad_sym", ".lib"):
                found_syms.append(p)

        # 1. Stash 3D Models
        for f3d in found_3d:
            dest = models_3d_dir / f3d.name
            if dest.exists() and not overwrite:
                stashed["models_3d"].append(dest)
                continue
            shutil.copy2(f3d, dest)
            stashed["models_3d"].append(dest)

        # 2. Stash Symbols & Relink Footprint reference
        lib_nickname = footprints_dir.stem
        for fsym in found_syms:
            dest = symbols_dir / fsym.name
            shutil.copy2(fsym, dest)
            stashed["symbols"].append(dest)

            # Match with best footprint or update existing footprint tag
            best_fp_stem = None
            if found_fps:
                best_fp_stem = found_fps[0].stem
                for cand in found_fps:
                    if cand.stem.lower() in fsym.stem.lower() or fsym.stem.lower() in cand.stem.lower():
                        best_fp_stem = cand.stem
                        break
            relink_symbol_footprint(dest, lib_nickname=lib_nickname, footprint_name=best_fp_stem)

        # 3. Stash Footprints & Relink 3D Models
        for ffp in found_fps:
            dest = footprints_dir / ffp.name
            shutil.copy2(ffp, dest)
            stashed["footprints"].append(dest)

            # Auto-relink if a 3D model was stashed alongside this footprint
            if stashed["models_3d"]:
                # Match by similar name or take the primary 3D model
                best_3d = stashed["models_3d"][0]
                for cand in stashed["models_3d"]:
                    if cand.stem.lower() in ffp.stem.lower() or ffp.stem.lower() in cand.stem.lower():
                        best_3d = cand
                        break

                rel_path = f"../{models_3d_dir.name}/{best_3d.name}"
                relink_3d_model(dest, rel_path)

    return stashed


def print_stash_summary(
    source_name: str,
    target_lib: Path,
    stashed: Dict[str, List[Path]],
) -> None:
    """Print clean, concise 4-line summary without terminal spam."""
    lib_name = target_lib.name
    total_files = sum(len(items) for items in stashed.values())

    print(f"\n{ICON_STASH} Stashing: {source_name} -> {lib_name}")

    # 3D Model line
    if stashed["models_3d"]:
        m_names = ", ".join(f"{p.parent.name}/{p.name}" for p in stashed["models_3d"])
        print(f"   ├─ 3D Model  : {m_names}")
    else:
        print("   ├─ 3D Model  : (none found)")

    # Footprint line
    if stashed["footprints"]:
        fp_names = ", ".join(f"{p.parent.name}/{p.name}" for p in stashed["footprints"])
        print(f"   ├─ Footprint : {fp_names} (3D linked)")
    else:
        print("   ├─ Footprint : (none found)")

    # Symbol line
    if stashed["symbols"]:
        sym_names = ", ".join(f"{p.parent.name}/{p.name}" for p in stashed["symbols"])
        print(f"   └─ Symbol    : {sym_names} (Footprint linked)")
    else:
        print("   └─ Symbol    : (none found)")

    if total_files > 0:
        print(f"{ICON_OK} Done! {total_files} file(s) stashed.\n")
    else:
        print(f"{ICON_ERR} No KiCad files found in archive.\n")


def main():
    parser = argparse.ArgumentParser(
        description="KiCad-Stash: Auto-sort external component archives directly into KiCad libraries."
    )
    parser.add_argument(
        "source",
        nargs="?",
        type=Path,
        help="Path to downloaded .zip or folder containing component files",
    )
    parser.add_argument(
        "-l",
        "--lib",
        type=Path,
        default=None,
        help="Target KiCad Library directory (auto-detected if omitted)",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Overwrite existing files if already present",
    )
    args = parser.parse_args()

    # Resolve target library
    target_lib = args.lib or auto_detect_library_dir()
    if not target_lib:
        print(f"{ICON_ARROW} No KiCad library folder specified.")
        user_input = input("Enter target KiCad library folder: ").strip()
        if not user_input:
            print("Aborted.")
            return
        target_lib = Path(user_input)

    # Resolve source archive / folder
    source = args.source
    if not source:
        # Check Downloads folder for most recent zip as a convenience
        downloads = Path.home() / "Downloads"
        recent_zips = sorted(downloads.glob("*.zip"), key=os.path.getmtime, reverse=True) if downloads.exists() else []

        prompt = "Enter path to .zip or folder: "
        if recent_zips:
            prompt = f"Enter path to .zip or folder [Enter for recent: {recent_zips[0].name}]: "

        user_input = input(prompt).strip()
        if user_input:
            source = Path(user_input)
        elif recent_zips:
            source = recent_zips[0]
        else:
            print("No source provided. Aborted.")
            return

    if not source.exists():
        print(f"{ICON_ERR} Source path not found: {source}")
        return

    stashed = stash_archive(source, target_lib=target_lib, overwrite=args.force)
    print_stash_summary(source.name, target_lib=target_lib, stashed=stashed)


if __name__ == "__main__":
    main()
