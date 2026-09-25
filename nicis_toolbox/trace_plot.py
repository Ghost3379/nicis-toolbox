import argparse
from pathlib import Path
import sys
from typing import Any, List, Optional, Union

try:
    import pandas as pd
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    HAS_PLOT_DEPS = True
except ImportError:
    HAS_PLOT_DEPS = False


def _check_deps():
    if not HAS_PLOT_DEPS:
        raise ImportError(
            "TracePlot requires 'pandas' and 'plotly'.\n"
            "Install them via: pip install pandas plotly openpyxl"
        )


def _detect_time_column(columns: List[str]) -> Optional[str]:
    """Auto-detect common timestamp or time column names."""
    candidates = [
        "Time_Relative", "time_relative", "relative_time",
        "Timestamp", "timestamp", "time", "Time",
        "t [s]", "t(s)", "t", "Time (s)", "Time [s]",
        "Time_s", "Zeit", "zeit", "Zeit (s)"
    ]
    col_map = {c.lower().strip(): c for c in columns}
    for cand in candidates:
        if cand.lower() in col_map:
            return col_map[cand.lower()]
    return None


class TracePlot:
    """
    Interactive multi-trace visualizer for oscilloscope, frequency, and sensor measurements.
    
    Supports:
    - CSV and Excel (.xlsx) inputs
    - Primary and secondary Y-axes
    - Relative time auto-zeroing (t - t0)
    - Rate-of-change / derivative trace generation
    - Active threshold zones with statistical summary annotation
    - Standalone interactive HTML export
    """

    def __init__(self, data_or_path: Union[str, Path, Any], sheet_name: Optional[str] = None):
        _check_deps()
        if isinstance(data_or_path, (str, Path)):
            path = Path(data_or_path)
            if not path.is_file():
                raise FileNotFoundError(f"Data file not found: {path}")

            self.file_name = path.stem
            if path.suffix.lower() in (".xlsx", ".xls"):
                self.df = pd.read_excel(path, sheet_name=sheet_name or 0)
            else:
                self.df = pd.read_csv(path)
        elif hasattr(data_or_path, "columns"):
            self.df = data_or_path.copy()
            self.file_name = "Measurement"
        else:
            raise ValueError("Expected a file path (str/Path) or a pandas DataFrame.")

    def plot(
        self,
        x_col: Optional[str] = None,
        y_cols: Optional[Union[str, List[str]]] = None,
        secondary_y_cols: Optional[Union[str, List[str]]] = None,
        relative_time: bool = True,
        add_derivative: bool = False,
        threshold: Optional[float] = None,
        threshold_col: Optional[str] = None,
        title: Optional[str] = None,
        x_label: Optional[str] = None,
        y_label: Optional[str] = None,
        secondary_y_label: Optional[str] = None,
        export_html: Optional[Union[str, Path]] = None,
        show: bool = True,
    ) -> Any:
        """
        Build and display the interactive Plotly multi-trace chart.
        """
        df = self.df.copy()

        # 1. Resolve X Column
        if x_col is None:
            x_col = _detect_time_column(list(df.columns)) or df.columns[0]
        if x_col not in df.columns:
            raise KeyError(f"X column '{x_col}' not found. Available: {list(df.columns)}")

        # Auto-compute relative time if x looks like an absolute epoch timestamp or if requested
        plot_x_col = x_col
        if relative_time and pd.api.types.is_numeric_dtype(df[x_col]):
            first_val = df[x_col].iloc[0]
            if first_val > 1000 or relative_time:
                df["_Time_Relative_s"] = df[x_col] - first_val
                plot_x_col = "_Time_Relative_s"
                if not x_label:
                    x_label = "Relative Time (s)"

        # 2. Resolve Primary Y Columns
        if y_cols is None:
            # Default to all numeric columns except the chosen X column
            candidates = [
                c for c in df.columns
                if c != x_col and c != plot_x_col and pd.api.types.is_numeric_dtype(df[c])
            ]
            primary_y = [candidates[0]] if candidates else []
        elif isinstance(y_cols, str):
            primary_y = [y_cols]
        else:
            primary_y = list(y_cols)

        # 3. Resolve Secondary Y Columns
        sec_y: List[str] = []
        if secondary_y_cols:
            sec_y = [secondary_y_cols] if isinstance(secondary_y_cols, str) else list(secondary_y_cols)

        has_secondary = bool(sec_y) or add_derivative
        fig = make_subplots(specs=[[{"secondary_y": has_secondary}]])

        # Color palette for clean multi-trace look
        palette = [
            "#1f77b4", "#2ca02c", "#d62728", "#9467bd",
            "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"
        ]

        # 4. Add Primary Y Traces
        for idx, col in enumerate(primary_y):
            if col not in df.columns:
                continue
            color = palette[idx % len(palette)]
            fig.add_trace(
                go.Scatter(
                    x=df[plot_x_col],
                    y=df[col],
                    mode="lines+markers" if len(df) < 150 else "lines",
                    marker=dict(size=4),
                    name=col,
                    line=dict(color=color, width=2),
                ),
                secondary_y=False,
            )

        # 5. Add Secondary Y Traces
        for idx, col in enumerate(sec_y):
            if col not in df.columns:
                continue
            color = palette[(idx + len(primary_y)) % len(palette)]
            fig.add_trace(
                go.Scatter(
                    x=df[plot_x_col],
                    y=df[col],
                    mode="lines+markers" if len(df) < 150 else "lines",
                    marker=dict(size=4),
                    name=f"{col} (Y2)",
                    line=dict(color=color, width=2, dash="dot"),
                ),
                secondary_y=True,
            )

        # 6. Add Derivative / Difference Trace if requested
        if add_derivative and primary_y:
            main_col = primary_y[0]
            diff_col = f"Δ_{main_col}"
            df[diff_col] = df[main_col].diff()
            fig.add_trace(
                go.Scatter(
                    x=df[plot_x_col],
                    y=df[diff_col],
                    mode="lines",
                    name=f"Δ {main_col} (diff)",
                    line=dict(color="#ff7f0e", width=1.5, dash="dash"),
                ),
                secondary_y=True,
            )
            if not secondary_y_label:
                secondary_y_label = f"Δ {main_col}"

        # 7. Add Threshold & Intel Box if specified
        target_col = threshold_col or (primary_y[0] if primary_y else None)
        if threshold is not None and target_col and target_col in df.columns:
            fig.add_hline(
                y=threshold,
                line_dash="dash",
                line_color="black",
                opacity=0.6,
                annotation_text=f"Threshold ({threshold})",
                annotation_position="bottom right",
            )
            active_mask = df[target_col] > threshold
            active_df = df[active_mask]
            if not active_df.empty:
                t_start = active_df[plot_x_col].min()
                t_end = active_df[plot_x_col].max()
                active_duration = t_end - t_start
                peak_val = active_df[target_col].max()

                # Highlight active zone in yellow
                fig.add_vrect(
                    x0=t_start,
                    x1=t_end,
                    fillcolor="yellow",
                    opacity=0.15,
                    layer="below",
                    line_width=0,
                )

                # Format duration unit
                if active_duration < 1e-3:
                    dur_str = f"{active_duration * 1e6:.2f} µs"
                elif active_duration < 1.0:
                    dur_str = f"{active_duration * 1e3:.2f} ms"
                else:
                    dur_str = f"{active_duration:.3f} s"

                intel_text = (
                    f"<b>Measurement Intel:</b><br>"
                    f"Peak ({target_col}): {peak_val:.2f}<br>"
                    f"Active Duration: {dur_str}<br>"
                    f"Samples above threshold: {len(active_df)}"
                )
                fig.add_annotation(
                    xref="paper",
                    yref="paper",
                    x=0.02,
                    y=0.98,
                    text=intel_text,
                    showarrow=False,
                    align="left",
                    bgcolor="rgba(255, 255, 255, 0.85)",
                    bordercolor="black",
                    borderwidth=1,
                )

        # 8. Layout Formatting
        plot_title = title or f"Measurement Trace: {self.file_name}"
        fig.update_layout(
            title=f"<b>{plot_title}</b>",
            xaxis_title=x_label or plot_x_col,
            hovermode="x unified",
            template="plotly_white",
            legend=dict(orientation="h", y=1.1, x=1, xanchor="right"),
            margin=dict(l=60, r=60, t=80, b=60),
        )

        fig.update_yaxes(
            title_text=f"<b>{y_label or (', '.join(primary_y) if primary_y else 'Value')}</b>",
            secondary_y=False,
        )
        if has_secondary:
            fig.update_yaxes(
                title_text=f"<b>{secondary_y_label or (', '.join(sec_y) if sec_y else 'Secondary')}</b>",
                secondary_y=True,
            )

        # 9. HTML Export
        if export_html:
            out_html = Path(export_html)
            out_html.parent.mkdir(parents=True, exist_ok=True)
            fig.write_html(str(out_html))
            print(f"[TracePlot] Exported interactive report to: {out_html.resolve()}")

        # 10. Display
        if show:
            fig.show()

        return fig


def plot_traces(
    file_or_df: Union[str, Path, Any],
    x_col: Optional[str] = None,
    y_cols: Optional[Union[str, List[str]]] = None,
    secondary_y_cols: Optional[Union[str, List[str]]] = None,
    **kwargs,
) -> Any:
    """Convenience functional wrapper for TracePlot."""
    tp = TracePlot(file_or_df)
    return tp.plot(x_col=x_col, y_cols=y_cols, secondary_y_cols=secondary_y_cols, **kwargs)


def main():
    parser = argparse.ArgumentParser(
        description="TracePlot: Fast interactive multi-trace Plotly viewer for CSV and Excel data."
    )
    parser.add_argument("file", type=Path, help="CSV or Excel file to plot")
    parser.add_argument("-x", "--x-col", default=None, help="Name of column for X-axis (auto-detected if omitted)")
    parser.add_argument("-y", "--y-cols", nargs="*", default=None, help="One or more columns for primary Y-axis")
    parser.add_argument("-s", "--secondary", nargs="*", default=None, help="Columns for secondary Y-axis")
    parser.add_argument("--sheet", default=None, help="Sheet name if reading an Excel workbook")
    parser.add_argument("--diff", action="store_true", help="Add derivative / difference trace on secondary Y-axis")
    parser.add_argument("--no-relative-time", action="store_true", help="Do not subtract starting time offset")
    parser.add_argument("--threshold", type=float, default=None, help="Threshold value to highlight active zone")
    parser.add_argument("--export", type=Path, default=None, help="Export standalone interactive HTML report")
    parser.add_argument("--no-show", action="store_true", help="Do not open browser window automatically")

    args = parser.parse_args()

    tp = TracePlot(args.file, sheet_name=args.sheet)
    tp.plot(
        x_col=args.x_col,
        y_cols=args.y_cols,
        secondary_y_cols=args.secondary,
        relative_time=not args.no_relative_time,
        add_derivative=args.diff,
        threshold=args.threshold,
        export_html=args.export,
        show=not args.no_show,
    )


if __name__ == "__main__":
    main()
