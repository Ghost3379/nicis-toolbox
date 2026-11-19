"""
Demo: Stashing external component archives into KiCad libraries using KiCad-Stash.

Demonstrates unpacking a mock external component archive (SnapEDA / UltraLibrarian style)
and sorting its 3D model, footprint, and symbol into their respective KiCad folders,
while relinking the footprint's 3D model path to the new relative location.
"""

from pathlib import Path
import sys
import tempfile
import zipfile

# Add project root to sys.path so it works without pip install
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from nicis_toolbox import stash_archive
from nicis_toolbox.kicad_stash import print_stash_summary


def main():
    print("=== KiCad-Stash Demo ===")
    demo_dir = Path(__file__).parent / "stash_demo_output"
    demo_dir.mkdir(parents=True, exist_ok=True)

    # 1. Create a mock KiCad library folder structure
    lib_dir = demo_dir / "Demo_KiCad_Library"
    (lib_dir / "NX-Demo_3dModels").mkdir(parents=True, exist_ok=True)
    (lib_dir / "NX-Demo_footprints.pretty").mkdir(parents=True, exist_ok=True)
    (lib_dir / "NX-Demo_symbols").mkdir(parents=True, exist_ok=True)

    # 2. Create a mock downloaded SnapEDA zip file
    zip_path = demo_dir / "TPS62840DLCR.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("TPS62840DLCR.step", "ISO-10303-21; /* Mock STEP file */ END-ISO-10303-21;")
        zf.writestr(
            "TPS62840DLCR.kicad_mod",
            '(footprint "TPS62840DLCR" (layer "F.Cu")\n'
            '  (descr "High efficiency step-down converter")\n'
            '  (model "broken_c_drive_path/TPS62840DLCR.step"\n'
            '    (at (xyz 0 0 0))\n'
            '    (scale (xyz 1 1 1))\n'
            '    (rotate (xyz 0 0 0))\n'
            '  )\n'
            ')',
        )
        zf.writestr(
            "TPS62840DLCR.kicad_sym",
            '(kicad_symbol_lib (symbol "TPS62840DLCR" (in_bom yes) (on_board yes)))',
        )

    # 3. Stash the archive into the KiCad library
    stashed = stash_archive(zip_path, target_lib=lib_dir)
    print_stash_summary(zip_path.name, target_lib=lib_dir, stashed=stashed)


if __name__ == "__main__":
    main()
