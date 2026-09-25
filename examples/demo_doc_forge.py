"""
Demo: Batch Document Generation with DocForge.

Creates a sample test report template, then batches 5 documents while
excluding board #3, demonstrating placeholder replacement and number sequencing.
"""

from pathlib import Path
import sys

# Ensure nicis_toolbox is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from docx import Document
from nicis_toolbox import DocForge


def create_sample_template(path: Path):
    """Generate a clean sample test report template for this demo."""
    doc = Document()
    doc.add_heading("Elektronik Prüfprotokoll / Test Report", level=1)

    p = doc.add_paragraph()
    p.add_run("Baugruppe: ").bold = True
    p.add_run("Transceiver Modul V2\n")
    p.add_run("Seriennummer: ").bold = True
    # The placeholder is styled in bold inside a run:
    run_sn = p.add_run("{SERIAL_NUMBER}")
    run_sn.bold = True
    p.add_run("\nPrüfdatum: {DATE}\nPrüfer: {TESTER}")

    # Add a test measurement table
    table = doc.add_table(rows=1, cols=3)
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    hdr[0].text = "Messung"
    hdr[1].text = "Sollwert"
    hdr[2].text = "Status"

    row_data = [
        ("Versorgungsspannung (VCC)", "3.30 V ± 0.05V", "BESTANDEN (PASS)"),
        ("Ruhestrom (Standby)", "< 1.5 mA", "BESTANDEN (PASS)"),
        ("Sendeleistung (TX Power)", "+14 dBm", "BESTANDEN (PASS)"),
    ]

    for item, req, status in row_data:
        row_cells = table.add_row().cells
        row_cells[0].text = item
        row_cells[1].text = req
        row_cells[2].text = status

    doc.save(str(path))
    print(f"Sample template created: {path.name}")


def main():
    print("=== DocForge Demo ===")
    demo_dir = Path(__file__).parent
    template_path = demo_dir / "sample_template.docx"
    output_dir = demo_dir / "output_doc_forge"

    # 1. Create a dummy template if needed
    create_sample_template(template_path)

    # 2. Initialize DocForge
    forge = DocForge(template_path=template_path, output_dir=output_dir)

    # 3. Generate batch of 5 boards, skipping board #3
    print("\nGenerating batch of test reports (Boards 1 to 5, excluding Board 3)...")
    generated = forge.generate_range(
        start=1,
        end=5,
        exclude={3},
        date_code="240924",  # Custom YYMMDD date code
        prefix="Messprotokoll_",
        placeholder="{SERIAL_NUMBER}",
        extra_mapping={
            "{DATE}": "24.09.2024",
            "{TESTER}": "Nici",
        },
    )

    print(f"\nGenerated {len(generated)} files in: {output_dir.resolve()}")
    for f in generated:
        print(f"  -> {f.name}")


if __name__ == "__main__":
    main()
