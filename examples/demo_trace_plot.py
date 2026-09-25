"""
Demo: Interactive Signal & Measurement Plotting with TracePlot.

Plots frequency ramp test data, calculates rate-of-change on a secondary axis,
and highlights threshold crossing with an automatic stats annotation box.
"""

from pathlib import Path
import sys

# Ensure nicis_toolbox is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from nicis_toolbox import TracePlot, plot_traces


def main():
    print("=== TracePlot Demo ===")
    demo_dir = Path(__file__).parent
    sample_csv = demo_dir / "sample_frequency_log.csv"
    output_html = demo_dir / "output_trace_plot.html"

    print(f"Loading measurement dataset: {sample_csv.name}")

    # 1. Initialize TracePlot with our test data
    tp = TracePlot(sample_csv)

    print("\nPlot configuration:")
    print("  - X-Axis: Relative Time (auto-zeroed)")
    print("  - Primary Y: Frequency_Hz")
    print("  - Secondary Y: Derivative / Rate of change (diff)")
    print("  - Threshold Highlight: > 1000 Hz")
    print(f"  - Export HTML: {output_html.name}")

    # 2. Generate interactive chart with derivative & threshold intel
    fig = tp.plot(
        x_col="Timestamp",
        y_cols=["Frequency_Hz"],
        relative_time=True,
        add_derivative=True,
        threshold=1000.0,
        title="Frequency Response Ramp Analysis",
        x_label="Time since trigger (s)",
        y_label="Frequency (Hz)",
        secondary_y_label="Rate of Change (Δ Hz)",
        export_html=output_html,
        show=False,  # Set to True in interactive use to pop open browser
    )

    print(f"\n[DONE] Interactive Plotly report generated!")
    print(f"Open in any browser: {output_html.resolve()}")


if __name__ == "__main__":
    main()
