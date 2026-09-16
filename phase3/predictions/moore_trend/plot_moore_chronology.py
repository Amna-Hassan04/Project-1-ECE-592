import csv
import os

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


ECE_FILE = "phase3/data/ece_cache_history.csv"
OUTDIR = "phase3/plots/predictions"
PRED_DIR = "phase3/predictions/moore_trend"

os.makedirs(OUTDIR, exist_ok=True)
os.makedirs(PRED_DIR, exist_ok=True)

# Frozen ECE-only model. Do not refit using Hazel measurements.
SLOPE = 0.344827586207
INTERCEPT = -687.112068965517


def predict(year):
    log2_kib = SLOPE * year + INTERCEPT
    kib = 2 ** log2_kib
    return log2_kib, kib


# Read chronological ECE observations.
ece = []
with open(ECE_FILE, newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        ece.append({
            "year": int(row["year"]),
            "machine": row["machine"],
            "cpu": row["cpu"],
            "l2_kib": float(row["l2_capacity_kib"]),
        })

ece.sort(key=lambda x: x["year"])

years = [x["year"] for x in ece]
capacities = [x["l2_kib"] for x in ece]
oldest_year = min(years)
newest_year = max(years)


# Frozen Hazel prediction for the 2020 Cascade Lake target.
hazel_year = 2020
hazel_pred_log2, hazel_pred_kib = predict(hazel_year)
hazel_pred_mib = hazel_pred_kib / 1024


# Five-year-ahead projection from the newest ECE observation.
future_year = newest_year + 5
future_log2, future_kib = predict(future_year)
future_mib = future_kib / 1024


# Create figure.
fig, ax = plt.subplots(figsize=(11, 7))

# ECE measured history: solid points connected by a solid line.
ax.plot(
    years,
    capacities,
    marker="o",
    markersize=7,
    linewidth=2.2,
    linestyle="-",
    label="ECE measured systems",
    zorder=3,
)

# Frozen model over the historical period.
history_years = list(range(oldest_year, newest_year + 1))
history_predictions = [predict(year)[1] for year in history_years]

ax.plot(
    history_years,
    history_predictions,
    linestyle=":",
    linewidth=1.8,
    label="Frozen ECE-only model",
    zorder=2,
)

# Dashed continuation beyond the newest ECE observation.
future_years = list(range(newest_year, future_year + 1))
future_predictions = [predict(year)[1] for year in future_years]

ax.plot(
    future_years,
    future_predictions,
    linestyle="--",
    linewidth=2.2,
    label="Frozen future extrapolation",
    zorder=2,
)

# Frozen 2020 Hazel prediction. This is a prediction, not a measured point.
ax.scatter(
    hazel_year,
    hazel_pred_kib,
    marker="*",
    s=300,
    edgecolors="black",
    linewidths=0.8,
    zorder=6,
    label="Frozen 2020 Hazel prediction",
)

ax.annotate(
    f"Frozen 2020 Hazel prediction\n"
    f"{hazel_pred_kib:.2f} KiB ({hazel_pred_mib:.2f} MiB)",
    xy=(hazel_year, hazel_pred_kib),
    xytext=(2017.0, 430),
    fontsize=10,
    fontweight="bold",
    arrowprops=dict(arrowstyle="->", linewidth=1.4),
    zorder=7,
)

# Five-year projection.
ax.scatter(
    future_year,
    future_kib,
    marker="D",
    s=100,
    edgecolors="black",
    linewidths=0.8,
    zorder=6,
    label=f"{future_year} projection",
)

ax.annotate(
    f"{future_year} projection\n"
    f"{future_kib:.2f} KiB ({future_mib:.2f} MiB)",
    xy=(future_year, future_kib),
    xytext=(2025.0, 5600),
    fontsize=10,
    fontweight="bold",
    arrowprops=dict(arrowstyle="->", linewidth=1.4),
    zorder=7,
)

# Label the newest ECE observation.
latest_capacity = capacities[-1]
ax.annotate(
    f"{newest_year} ECE latest\n"
    f"{latest_capacity:.0f} KiB ({latest_capacity / 1024:.2f} MiB)",
    xy=(newest_year, latest_capacity),
    xytext=(2020.7, 3000),
    fontsize=10,
    arrowprops=dict(arrowstyle="->", linewidth=1.2),
    zorder=7,
)


# Logarithmic base-2 y-axis.
ax.set_yscale("log", base=2)


def format_kib(value, position):
    return f"{value:,.0f}"


ax.yaxis.set_major_formatter(FuncFormatter(format_kib))
ax.set_xlim(oldest_year - 0.5, future_year + 0.5)
ax.set_ylim(128, 8192)

ax.set_xlabel("Year", fontsize=13)
ax.set_ylabel("L2 capacity (KiB, log2 scale)", fontsize=13)
ax.set_title(
    "Chronological L2 Cache Scaling and Frozen Prediction",
    fontsize=17,
    fontweight="bold",
    pad=15,
)

ax.grid(True, which="both", linestyle="--", alpha=0.3)
ax.legend(loc="upper left", fontsize=10, frameon=True)

# Model information box.
model_text = (
    "Frozen ECE-only model parameters:\n"
    f"slope = {SLOPE:.12f} log2 KiB/year\n"
    f"intercept = {INTERCEPT:.12f}\n"
    "\n"
    "Key predictions:\n"
    f"2020 Hazel = {hazel_pred_kib:.2f} KiB ({hazel_pred_mib:.2f} MiB)\n"
    f"{future_year} projection = {future_kib:.2f} KiB ({future_mib:.2f} MiB)\n"
    "\n"
    "Observations:\n"
    f"ECE measured systems = {len(ece)}\n"
    f"ECE training period = {oldest_year}–{newest_year}\n"
    "Hazel data not used for fitting"
)

ax.text(
    0.98,
    0.04,
    model_text,
    transform=ax.transAxes,
    fontsize=9.5,
    verticalalignment="bottom",
    horizontalalignment="right",
    bbox=dict(
        boxstyle="round,pad=0.5",
        facecolor="white",
        edgecolor="gray",
        alpha=0.95,
    ),
)

plt.tight_layout()

png_path = os.path.join(OUTDIR, "moore_l2_chronology.png")
pdf_path = os.path.join(OUTDIR, "moore_l2_chronology.pdf")

plt.savefig(png_path, dpi=300, bbox_inches="tight")
plt.savefig(pdf_path, bbox_inches="tight")
plt.close()


# Save numerical prediction summary.
summary_path = os.path.join(PRED_DIR, "prediction_summary.txt")

with open(summary_path, "w") as f:
    f.write("ECE-only frozen Moore-style cache scaling model\n")
    f.write("================================================\n\n")
    f.write(f"observations={len(ece)}\n")
    f.write(f"training_year_min={oldest_year}\n")
    f.write(f"training_year_max={newest_year}\n")
    f.write(f"slope_log2_kib_per_year={SLOPE:.12f}\n")
    f.write(f"intercept={INTERCEPT:.12f}\n")
    f.write(f"hazel_target_year={hazel_year}\n")
    f.write(f"hazel_prediction_log2_kib={hazel_pred_log2:.6f}\n")
    f.write(f"hazel_prediction_kib={hazel_pred_kib:.2f}\n")
    f.write(f"hazel_prediction_mib={hazel_pred_mib:.4f}\n")
    f.write(f"future_year={future_year}\n")
    f.write(f"future_prediction_log2_kib={future_log2:.6f}\n")
    f.write(f"future_prediction_kib={future_kib:.2f}\n")
    f.write(f"future_prediction_mib={future_mib:.4f}\n")
    f.write("\n")
    f.write("The model was fit only to the ECE chronological dataset.\n")
    f.write("Hazel observations were not used for refitting.\n")
    f.write(
        "The 2020 Hazel point shown in the figure is the frozen "
        "prediction, not a retained measured observation.\n"
    )
    f.write(
        "The original Cascade Lake Hazel measurement is not currently "
        "retained in phase3/data/hazel.\n"
    )

print(f"Created: {png_path}")
print(f"Created: {pdf_path}")
print(f"Created: {summary_path}")
print()
print("Frozen model:")
print(f"  slope     = {SLOPE:.12f}")
print(f"  intercept = {INTERCEPT:.12f}")
print()
print(
    f"Frozen 2020 Hazel prediction: "
    f"{hazel_pred_kib:.2f} KiB ({hazel_pred_mib:.4f} MiB)"
)
print(
    f"{future_year} five-year projection: "
    f"{future_kib:.2f} KiB ({future_mib:.4f} MiB)"
)
