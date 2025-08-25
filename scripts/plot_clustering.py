#!/usr/bin/env python3

import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import uproot
import awkward as ak
import scipy.stats
import numpy as np
import atlasify

from common import markers, colors, robust_mean, robust_std, ratio_std


base_dir = Path(__file__).parent.parent.parent

parser = argparse.ArgumentParser()
parser.add_argument("input", type=Path)
parser.add_argument("mode", choices=["pixelalg", "pixeltool", "stripalg", "striptool"])
parser.add_argument(
    "--output",
    type=Path,
    help="Path to output file",
)
parser.add_argument("--show", action="store_true", help="Show plot")
args = parser.parse_args()

path_acts = {
    "pixelalg": "ActsPixelClusterizationAlg/TimeVsClusters",
    "pixeltool": "ActsPixelClusterizationAlg/ActsPixelClusteringTool/TimeVsClusters",
    "stripalg": "ActsStripClusterizationAlg/TimeVsClusters",
    "striptool": "ActsStripClusterizationAlg/ActsStripClusteringTool/TimeVsClusters",
}[args.mode]
path_athena = {
    "pixelalg": "ITkPixelClusterization/TimeVsClusters",
    "pixeltool": "ITkPixelClusterization/ITkMergedPixelsTool/TimeVsClusters",
    "stripalg": "ITkStripClusterization/TimeVsClusters",
    "striptool": "ITkStripClusterization/ITkStripClusteringTool/TimeVsClusters",
}[args.mode]

if args.mode.startswith("pixel"):
    xlabel = "Number of Pixel Clusters"
    bin_edges = np.array([140] + np.linspace(170, 310, 16).tolist() + [330]) * 1e3
else:
    xlabel = "Number of Strip Clusters"
    bin_edges = np.array([140] + np.linspace(170, 310, 16).tolist() + [330]) * 1e3
bin_mid = 0.5 * (bin_edges[:-1] + bin_edges[1:])
bin_size = 0.5 * (bin_edges[1:] - bin_edges[:-1])

data = uproot.open(args.input)

data_athena = ak.to_dataframe(data[path_athena].arrays(library="ak"))
data_acts = ak.to_dataframe(data[path_acts].arrays(library="ak"))

mean_athena, _, _ = scipy.stats.binned_statistic(
    data_athena["NClustersCreated"],
    data_athena["TIME_execute"],
    bins=bin_edges,
    statistic=robust_mean,
)
mean_acts, _, _ = scipy.stats.binned_statistic(
    data_acts["NClustersCreated"],
    data_acts["TIME_execute"],
    bins=bin_edges,
    statistic=robust_mean,
)

std_athena, _, _ = scipy.stats.binned_statistic(
    data_athena["NClustersCreated"],
    data_athena["TIME_execute"],
    bins=bin_edges,
    statistic=robust_std,
)
std_acts, _, _ = scipy.stats.binned_statistic(
    data_acts["NClustersCreated"],
    data_acts["TIME_execute"],
    bins=bin_edges,
    statistic=robust_std,
)

ymin = mean_athena.min()
mean_athena /= ymin
mean_acts /= ymin
std_athena /= ymin
std_acts /= ymin

atlasify.monkeypatch_axis_labels()

fig, axs = plt.subplots(
    2,
    1,
    figsize=(6, 4),
    sharex=True,
    gridspec_kw={"height_ratios": [10, 4], "hspace": 0.02},
    layout="constrained",
)

# axs[0].set_xlabel(xlabel)
axs[0].set_ylabel("Average Execution Time [A.U.]")

axs[1].set_xlabel(xlabel)
axs[1].set_ylabel("ACTS / Non-ACTS")

axs[0].errorbar(
    x=bin_mid,
    y=mean_athena,
    xerr=bin_size,
    yerr=std_athena,
    label="Non-ACTS\nMean $\\pm$ RMS",
    linestyle="",
    color=colors[0],
    marker=markers[0],
)
axs[0].errorbar(
    x=bin_mid,
    y=mean_acts,
    xerr=bin_size,
    yerr=std_acts,
    label="ACTS-based\nMean $\\pm$ RMS",
    linestyle="",
    color=colors[1],
    marker=markers[1],
)

axs[0].legend()

subtext = r"""
$\sqrt{s} = 14$ TeV, HL-LHC
$t\bar{t}$, $\langle \mu \rangle$ = 200
ITk Layout: 03-00-00
ACTS v43.0.1, Athena 25.0.40
""".strip()

atlasify.atlasify(
    axes=axs[0],
    brand="ATLAS",
    atlas="Simulation Preliminary",
    subtext=subtext,
    enlarge=1.8,
)

ylim = axs[0].get_ylim()
axs[0].set_ylim(0, ylim[1])

# axs[1].hlines(
#     1,
#     xmin=bin_edges[0],
#     xmax=bin_edges[-1],
#     linestyle="--",
#     color=colors[0],
# )
axs[1].errorbar(
    bin_mid,
    mean_acts / mean_athena,
    yerr=ratio_std(
        mean_acts,
        mean_athena,
        std_acts,
        std_athena,
    ),
    xerr=bin_size,
    linestyle="",
    color=colors[1],
    marker=markers[1],
)

atlasify.atlasify(
    axes=axs[1],
    brand=None,
    atlas=None,
    subtext=None,
)
axs[1].xaxis.get_offset_text().set_x(1.07)
axs[1].xaxis.get_offset_text().set_va("bottom")

plt.ticklabel_format(style="sci", axis="x", scilimits=(-5, 5), useMathText=True)

if args.output is not None:
    fig.savefig(args.output)

if args.output is None or args.show:
    plt.show()
