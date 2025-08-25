#!/usr/bin/env python3

import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import ROOT
import atlasify

from common import markers, colors, TH1, ratio_std


base_dir = Path(__file__).parent.parent.parent

parser = argparse.ArgumentParser()
parser.add_argument("input_athena_slow", type=Path)
parser.add_argument("--input-acts-fast", type=Path)
parser.add_argument("--input-acts-slow", type=Path)
parser.add_argument("--input-acts-slow-analog", type=Path)
parser.add_argument("mode", choices=["physics", "technical"])
parser.add_argument(
    "--output",
    type=Path,
    help="Path to output file",
)
parser.add_argument("--show", action="store_true", help="Show plot")
args = parser.parse_args()

input_athena_slow = ROOT.TFile.Open(args.input_athena_slow.as_posix())
data_acts_fast = (
    ROOT.TFile.Open(args.input_acts_fast.as_posix()) if args.input_acts_fast else None
)
data_acts_slow = (
    ROOT.TFile.Open(args.input_acts_slow.as_posix()) if args.input_acts_slow else None
)
data_acts_slow_analog = (
    ROOT.TFile.Open(args.input_acts_slow_analog.as_posix())
    if args.input_acts_slow_analog
    else None
)

if args.mode == "physics":
    idtpm_path = "InDetTrackPerfMonPlots/TrkAnaEF_EFsel/Offline/Tracks/Efficiencies/eff_vs_truth_eta"
    ylabel = "Physics Efficiency"
elif args.mode == "technical":
    idtpm_path = "InDetTrackPerfMonPlots/TrkAnaEF_EFsel/Offline/Tracks/Efficiencies/Technical/eff_vs_truth_eta"
    ylabel = "Technical Efficiency"
else:
    raise ValueError("Invalid mode specified. Choose 'physics' or 'technical'.")

eff_athena_slow = TH1(input_athena_slow.Get(idtpm_path), xrange=(-4, 4))
eff_acts_fast = (
    TH1(data_acts_fast.Get(idtpm_path), xrange=(-4, 4)) if data_acts_fast else None
)
eff_acts_slow = (
    TH1(data_acts_slow.Get(idtpm_path), xrange=(-4, 4)) if data_acts_slow else None
)
eff_acts_slow_analog = (
    TH1(data_acts_slow_analog.Get(idtpm_path), xrange=(-4, 4))
    if data_acts_slow_analog
    else None
)

atlasify.monkeypatch_axis_labels()

fig, axs = plt.subplots(
    2,
    1,
    figsize=(6, 4),
    sharex=True,
    gridspec_kw={"height_ratios": [10, 4], "hspace": 0.02},
    layout="constrained",
)

axs[0].set_xlim(-4, 4)

# axs[0].set_xlabel("$\\eta$")
axs[0].set_ylabel(ylabel)

axs[1].set_xlabel("$\\eta$")
axs[1].set_ylabel("ACTS / Non-ACTS")

eff_athena_slow.errorbar(
    axs[0], label="Non-ACTS", linestyle="", marker=markers[0], color=colors[0]
)
if eff_acts_slow is not None:
    eff_acts_slow.errorbar(
        axs[0], label="ACTS-based", linestyle="", marker=markers[1], color=colors[1]
    )
if eff_acts_fast is not None:
    eff_acts_fast.errorbar(
        axs[0],
        label="ACTS-based, Fast",
        linestyle="",
        marker=markers[2],
        color=colors[2],
    )
if eff_acts_slow_analog is not None:
    eff_acts_slow_analog.errorbar(
        axs[0],
        label="ACTS-based, Analog",
        linestyle="",
        marker=markers[3],
        color=colors[3],
    )

axs[0].legend()

subtext = r"""
$\sqrt{s} = 14$ TeV, HL-LHC
$t\bar{t}$, $\langle \mu \rangle$ = 200, Truth $p_T > 1$ GeV
ITk Layout: 03-00-00
ACTS v43.0.1, Athena 25.0.40
""".strip()

atlasify.atlasify(
    axes=axs[0],
    brand="ATLAS",
    atlas="Simulation Preliminary",
    subtext=subtext,
    enlarge=2.0,
)

axs[1].hlines(
    1,
    xmin=eff_athena_slow.x[0],
    xmax=eff_athena_slow.x[-1],
    color=colors[0],
    linestyle="--",
)
if eff_acts_slow is not None:
    axs[1].errorbar(
        eff_acts_slow.x,
        eff_acts_slow.y / eff_athena_slow.y,
        yerr=ratio_std(
            eff_acts_slow.y,
            eff_athena_slow.y,
            0.5 * (eff_acts_slow.y_err_hi - eff_acts_slow.y_err_lo),
            0.5 * (eff_athena_slow.y_err_hi - eff_athena_slow.y_err_lo),
        ),
        xerr=(eff_acts_slow.x_err_lo, eff_acts_slow.x_err_hi),
        linestyle="",
        marker=markers[1],
        color=colors[1],
    )
if eff_acts_fast is not None:
    axs[1].errorbar(
        eff_acts_fast.x,
        eff_acts_fast.y / eff_athena_slow.y,
        yerr=ratio_std(
            eff_acts_fast.y,
            eff_athena_slow.y,
            0.5 * (eff_acts_fast.y_err_hi - eff_acts_fast.y_err_lo),
            0.5 * (eff_athena_slow.y_err_hi - eff_athena_slow.y_err_lo),
        ),
        xerr=(eff_acts_fast.x_err_lo, eff_acts_fast.x_err_hi),
        linestyle="",
        marker=markers[2],
        color=colors[2],
    )
if eff_acts_slow_analog is not None:
    axs[1].errorbar(
        eff_acts_slow_analog.x,
        eff_acts_slow_analog.y / eff_athena_slow.y,
        yerr=ratio_std(
            eff_acts_slow_analog.y,
            eff_athena_slow.y,
            0.5 * (eff_acts_slow_analog.y_err_hi - eff_acts_slow_analog.y_err_lo),
            0.5 * (eff_athena_slow.y_err_hi - eff_athena_slow.y_err_lo),
        ),
        xerr=(eff_acts_slow_analog.x_err_lo, eff_acts_slow_analog.x_err_hi),
        linestyle="",
        marker=markers[3],
        color=colors[3],
    )

atlasify.atlasify(
    axes=axs[1],
    brand=None,
    atlas=None,
    subtext=None,
)

if args.output is not None:
    fig.savefig(args.output)

if args.output is None or args.show:
    plt.show()
