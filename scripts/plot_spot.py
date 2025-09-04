#!/usr/bin/env python3

# /// script
# requires-python = ">=3.11"
# dependencies = [
#  "matplotlib",
#  "pandas",
#  "atlasify"
# ]
# ///

import argparse
from pathlib import Path
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import pandas as pd
import atlasify


parser = argparse.ArgumentParser()
parser.add_argument(
    "input_folder", type=Path, help="Path to input folder containing CSV files"
)
parser.add_argument(
    "--output",
    type=Path,
    help="Path to output file",
)
parser.add_argument("--show", action="store_true", help="Show plot")

args = parser.parse_args()

df_main_fast = pd.read_csv(
    args.input_folder / "cern_results_spot-mon-phase2_recoonly_actsfasttracking.csv"
)
df_main_mixed = pd.read_csv(
    args.input_folder / "cern_results_spot-mon-phase2_recoonly_actstracking.csv"
)

df_main_fast["build_date"] = pd.to_datetime(df_main_fast["build_date"])
df_main_fast = df_main_fast.sort_values(by="build_date")
df_main_fast.index = df_main_fast["build_date"]

df_main_mixed["build_date"] = pd.to_datetime(df_main_mixed["build_date"])
df_main_mixed = df_main_mixed.sort_values(by="build_date")
df_main_mixed.index = df_main_mixed["build_date"]

atlasify.monkeypatch_axis_labels()

# fig, ax = plt.subplots(figsize=(10, 5), dpi=200)
# df_main_mixed.plot(y="ActsTrackFindingAlg", kind="line", ax=ax)
# ax.set_ylim(0, 3)
# fig, ax = plt.subplots(figsize=(10, 5), dpi=200)
# df_main_fast.plot(y="ActsTrackFindingAlg", kind="line", ax=ax)
# ax.set_ylim(0, 3)

stitch = df_main_fast.build_date.max()
print("stitch", stitch)
df_main = pd.concat([df_main_fast, df_main_mixed[df_main_mixed.build_date > stitch]])

# fig, ax = plt.subplots(figsize=(10, 5), dpi=200)
# df_main.plot(y="ActsTrackFindingAlg", kind="line", ax=ax)
# ax.set_ylim(0, 3)

df_main

fig, ax = plt.subplots(1, 1, figsize=(10, 4), dpi=200)
# fig.subplots_adjust(wspace=0.01)

components = [
    "ActsTrackFindingAlg",
    "ActsPixelSeedingAlg",
    "ActsPixelClusterizationAlg",
    "ActsStripClusterizationAlg",
    "ActsAmbiguityResolutionAlg",
]

labels = [
    "Track finding",
    "Pixel seeding",
    "Pixel clusterization",
    "Strip clusterization",
    "Ambiguity resolution",
]

HS23 = 27

pad = timedelta(days=0)
xmin = datetime(2024, 7, 12)  # - pad
xmax = df_main["build_date"].max()
print("xmax", xmax)

plot_df = df_main.copy()
zoom_xmin = datetime(2025, 5, 1)

time_sum = sum(plot_df[component] * HS23 for component in components)

plot_df = plot_df[time_sum > 0]
time_sum = time_sum[time_sum > 0]

zoom_df = plot_df[plot_df["build_date"] >= zoom_xmin]
time_sum_zoom = sum(zoom_df[component] * HS23 for component in components)

lines = []

lines += [
    # ("Initial optimization kick-off", plot_df["build_date"].min()),
    ("ATL-PHYS-PUB-2024-017", 70, 90, "right", datetime(2024, 9, 1)),
    # ("Optim. kick-off", datetime(2025, 5, 1)),
    ("(2)", 80, 0, "right", datetime(2025, 6, 24)),
    ("(3)", 80, 0, "left", datetime(2025, 7, 1)),
    ("(4)", 80, 0, "right", datetime(2025, 7, 22)),
    ("(5)", 80, 0, "left", datetime(2025, 7, 25)),
    # ("Pipeline report", datetime(2025, 8, 1)),
]

start, end = datetime(year=2025, month=1, day=6), datetime(year=2025, month=3, day=1)
ax.fill_between([start, end], 0, 80, color="lightgray", alpha=0.25, ec="none")
ax.text(
    start + (end - start) / 2, 80, "(1)", rotation=0, va="top", ha="center", fontsize=10
)

for rel, y, rot, ha, date in lines:
    # ax.axvline(date, color="gray", linestyle="--")
    ax.vlines(date, ymin=0, ymax=80, color="gray", linestyle="--")
    off = timedelta(days=1) * (-1 if ha == "right" else 1)
    ax.text(date + off, y, rel, rotation=rot, va="top", ha=ha, fontsize=10)

if HS23 != 1:
    pass
    # ax.fill_between([xmin, xmax+pad], 0, 45, color="tab:green", alpha=0.05, ec="none")
    # ax.fill_between([xmin, xmax+pad], 45, 50, color="tab:orange", alpha=0.05, ec="none")


for component, label in zip(components, labels):
    ax.plot(plot_df["build_date"], plot_df[component] * HS23, label=label)
    # ax2.plot(zoom_df["build_date"], zoom_df[component]*HS23, label=label)

ax.plot(plot_df["build_date"], time_sum, label="Total", color="black", linewidth=1.5)
# ax2.plot(zoom_df["build_date"], time_sum_zoom, label="Total", color="black", linewidth=1.5)


_, ymax = ax.get_ylim()
# ax.set_ylim(0, ymax*1.21)
# ax2.set_ylim(0)
for _ax in (ax,):
    _ax.set_xlabel("Date")

    lab = "Reconstruction time"

    if HS23 != 1:
        lab += r" [HS23$\times{}$s]"
    else:
        lab += " [s]"

    _ax.set_ylabel(lab)

ax.legend(bbox_to_anchor=(0.5, 0.9999), loc="upper left", ncol=2, frameon=False)
# ax.axhline(45, color="grey", ls="--")
# ax2.legend(ncol=1)
ax.set_xlim(xmin, xmax + pad)
# ax2.set_xlim(zoom_xmin, xmax)

# ax.set_xticks(ax.get_xticks())
# ax.set_xticklabels(ax.get_xticklabels(), rotation=0)

# ax2.yaxis.tick_right()
# ax2.yaxis.set_label_position("right")
# ax2.set_xticklabels(ax2.get_xticklabels(), rotation=-45, ha="left")


s = r"""
Intel(R) Xeon(R) Gold 6326 
HS23: 27
"""

ds = r"""
ITk Layout: 03-00-00, $t\bar{t}$, $\langle\mu\rangle = 200$, $\sqrt{s} = 14$ TeV
ACTS-based, Fast
"""

ax.text(0.16, 0.52, s=s.strip(), transform=ax.transAxes)

# hep.atlas.text("", fontsize=16)

# ax.text(
#         0.01,
#         0.897,
#         s="ATLAS",
#         fontname="TeX Gyre Heros",
#         transform=ax.transAxes,
#         fontsize=16*1.2,
#         va="bottom",
#         fontstyle="italic",
#         fontweight="bold",
#     )

# ax.text(
#         0.1,
#         0.897+0.0005,
#         s="Simulation Preliminary",
#         fontname="TeX Gyre Heros",
#         transform=ax.transAxes,
#         fontsize=16,
#         va="bottom",
#     )

# ax.text(0.01, 0.85, s=ds.strip(), transform=ax.transAxes)


atlasify.atlasify(
    axes=ax,
    brand="ATLAS",
    atlas="Simulation Preliminary",
    subtext=ds.strip(),
    enlarge=1.3,
)
# plt.ticklabel_format(style="sci", axis="x", scilimits=(-5, 5), useMathText=True)

ylim = ax.get_ylim()
ax.set_ylim(0, ylim[1])

fig.tight_layout()

if args.output is not None:
    fig.savefig(args.output)

if args.output is None or args.show:
    plt.show()
