"""PDF quality report generator — uses matplotlib only (no extra deps)."""
import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


def generate_pdf_report(report: dict, work_dir: Path) -> Path:
    """Render a quality report PDF and return its path."""
    pdf_path = work_dir / "report.pdf"
    plots_dir = work_dir / "plots"

    all_col_plots = {
        **report.get("histogram_plots", {}),
        **report.get("column_plots", {}),   # SDV preferred
    }

    with PdfPages(str(pdf_path)) as pdf:
        _page_overview(pdf, report)
        _page_distributions(pdf, report, plots_dir, all_col_plots)
        _page_correlations(pdf, report, plots_dir)

    return pdf_path


# ── helpers ────────────────────────────────────────────────────────────────────

def _score_color(v: float) -> str:
    return "#3ecf8e" if v >= 0.7 else "#fbbf24" if v >= 0.4 else "#e05252"


def _hdr_band(fig):
    """Dark top banner shared by all pages."""
    ax = fig.add_axes([0, 0.93, 1, 0.07])
    ax.set_facecolor("#0d1b2e")
    ax.axis("off")
    ax.text(0.5, 0.62, "DataSynthesis131", ha="center", va="center",
            fontsize=18, fontweight="bold", color="white")
    ax.text(0.5, 0.18, "Quality Evaluation Report", ha="center", va="center",
            fontsize=10, color="#7ba8d8")


def _table_ax(fig, rect, title):
    """Add a light-background axes with a border and a bold title."""
    ax = fig.add_axes(rect)
    ax.set_facecolor("#f8fafd")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_edgecolor("#dde6f0")
        sp.set_linewidth(0.8)
    ax.text(0.02, 0.96, title, fontsize=11, fontweight="bold",
            color="#111", va="top")
    return ax


# ── page 1: overview ───────────────────────────────────────────────────────────

def _page_overview(pdf: PdfPages, report: dict):
    fig = plt.figure(figsize=(8.27, 11.69))
    fig.patch.set_facecolor("white")
    _hdr_band(fig)

    overall = report.get("overall_score", 0)
    pct = round(overall * 100)
    sc = _score_color(overall)
    method = report.get("method_used", "—")
    date_str = datetime.date.today().strftime("%B %d, %Y")

    # ── score block ────────────────────────────────────────────────────────────
    ax_s = _table_ax(fig, [0.20, 0.79, 0.60, 0.125], "")
    ax_s.text(0.5, 0.72, f"{pct}%", ha="center", va="center",
              fontsize=44, fontweight="bold", color=sc)
    ax_s.text(0.5, 0.18, "Overall Quality Score", ha="center", va="center",
              fontsize=10, color="#555")

    # meta row (date / method)
    ax_meta = fig.add_axes([0.05, 0.755, 0.9, 0.025])
    ax_meta.axis("off")
    ax_meta.text(0.0, 0.5, f"Date: {date_str}", fontsize=8.5, color="#777", va="center")
    ax_meta.text(1.0, 0.5, f"Method: {method}", fontsize=8.5, color="#777",
                 va="center", ha="right")

    # ── metrics table ──────────────────────────────────────────────────────────
    ax_m = _table_ax(fig, [0.05, 0.43, 0.9, 0.305], "Quality Metrics")

    # dark header row
    ax_m.axhspan(0.845, 0.915, facecolor="#0d1b2e", zorder=0)
    for x, lbl in [(0.02, "Metric"), (0.55, "Value"), (0.78, "Direction")]:
        ax_m.text(x, 0.880, lbl, fontsize=9, fontweight="bold",
                  color="white", va="center")

    rows = [
        ("Propensity Score",    f"{report.get('propensity_score', 0):.4f}",          "↓ lower is better"),
        ("Log-Cluster Metric",  f"{report.get('log_cluster_metric', 0):.4f}",         "↓ lower is better"),
        ("Prediction Accuracy", f"{report.get('prediction_accuracy', 0)*100:.1f}%",   "↑ higher is better"),
        ("SDV Score",           f"{report.get('sdv_score', 0)*100:.1f}%",             "↑ higher is better"),
        ("Data Validity",       f"{report.get('data_validity', 0)*100:.1f}%",         "↑ higher is better"),
    ]
    row_h = 0.13
    for i, (lbl, val, note) in enumerate(rows):
        y = 0.80 - i * row_h - row_h / 2
        ax_m.axhspan(y - row_h / 2 + 0.005, y + row_h / 2 - 0.005,
                     facecolor="#f0f5fc" if i % 2 == 0 else "#f8fafd", zorder=0)
        ax_m.text(0.02, y, lbl,  fontsize=9.5, color="#333", va="center")
        ax_m.text(0.55, y, val,  fontsize=10,  fontweight="bold", color="#111", va="center")
        ax_m.text(0.78, y, note, fontsize=8,   color="#888", va="center", style="italic")

    # ── column shapes ──────────────────────────────────────────────────────────
    col_shapes = report.get("column_shapes_details", [])
    if col_shapes:
        ax_c = _table_ax(fig, [0.05, 0.02, 0.9, 0.385],
                         "Column Distribution Scores (SDV — Column Shapes)")
        shown = col_shapes[:12]
        n = len(shown)
        row_h = 0.78 / max(n, 1)
        for i, item in enumerate(shown):
            col_name = str(item["Column"])
            score = float(item["Score"])
            y = 0.90 - i * row_h - row_h / 2
            ax_c.axhspan(y - row_h / 2 + 0.003, y + row_h / 2 - 0.003,
                         facecolor="#f0f5fc" if i % 2 == 0 else "#f8fafd", zorder=0)
            ax_c.text(0.02, y, col_name, fontsize=8.5, color="#333", va="center")
            bc = _score_color(score)
            ax_c.barh(y, score * 0.35, height=row_h * 0.55,
                      left=0.55, color=bc, alpha=0.65, zorder=2)
            ax_c.text(0.53, y, f"{score*100:.1f}%",
                      fontsize=8.5, color="#333", va="center", ha="right")
        if len(col_shapes) > 12:
            ax_c.text(0.5, 0.03, f"… and {len(col_shapes) - 12} more columns",
                      fontsize=8, color="#888", ha="center")

    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


# ── page 2: distributions ──────────────────────────────────────────────────────

def _page_distributions(pdf: PdfPages, report: dict, plots_dir: Path, all_col_plots: dict):
    picks = report.get("distribution_picks", {})
    pick_keys = [k for k in ("best", "median", "worst") if k in picks]
    if not pick_keys:
        return

    LABELS = {
        "best":   "Best Distribution",
        "median": "Representative Distribution",
        "worst":  "Worst Distribution",
    }

    n = len(pick_keys)
    fig = plt.figure(figsize=(8.27, 11.69))
    fig.patch.set_facecolor("white")
    _hdr_band(fig)

    # Distribute n plot panels evenly in the remaining space (0..0.92)
    usable_h = 0.88
    panel_h = usable_h / n
    gap = 0.015

    for idx, key in enumerate(pick_keys):
        info = picks[key]
        col, score = info["col"], info["score"]
        img_file = all_col_plots.get(col)

        bottom = usable_h - (idx + 1) * panel_h + gap / 2
        height = panel_h - gap

        ax = fig.add_axes([0.05, bottom, 0.9, height])
        title = f"{LABELS[key]}: {col}  ({score * 100:.2f}%)"

        if img_file and (plots_dir / img_file).exists():
            img = mpimg.imread(str(plots_dir / img_file))
            ax.imshow(img, aspect="auto")
            ax.axis("off")
            ax.set_title(title, fontsize=10, pad=4, color="#111")
        else:
            ax.axis("off")
            ax.text(0.5, 0.5, f"{title}\n(plot not available)",
                    ha="center", va="center", fontsize=10, color="#999")

    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


# ── page 3: correlations ───────────────────────────────────────────────────────

def _page_correlations(pdf: PdfPages, report: dict, plots_dir: Path):
    corr_names = report.get("correlation_plots", [])
    corr_files = [plots_dir / f for f in corr_names if (plots_dir / f).exists()]
    if not corr_files:
        return

    n = len(corr_files)
    fig = plt.figure(figsize=(8.27, 11.69))
    fig.patch.set_facecolor("white")
    _hdr_band(fig)

    usable_h = 0.88
    panel_h = usable_h / n
    gap = 0.015
    LABELS = {"real": "Real Data", "synthetic": "Synthetic Data"}

    for idx, fpath in enumerate(corr_files):
        bottom = usable_h - (idx + 1) * panel_h + gap / 2
        ax = fig.add_axes([0.05, bottom, 0.9, panel_h - gap])
        img = mpimg.imread(str(fpath))
        ax.imshow(img, aspect="auto")
        ax.axis("off")
        label_key = next((k for k in LABELS if k in fpath.name), fpath.stem)
        ax.set_title(f"Correlation Matrix — {LABELS.get(label_key, fpath.stem)}",
                     fontsize=10, pad=4, color="#111")

    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)
