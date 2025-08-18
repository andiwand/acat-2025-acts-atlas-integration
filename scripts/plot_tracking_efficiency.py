#!/usr/bin/env python3

import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import ROOT
import atlasify

from common import TH1


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

fig, ax = plt.subplots(1, 1, figsize=(6, 4))

ax.set_xlim(-4, 4)

ax.set_xlabel("$\\eta$")
ax.set_ylabel(ylabel)

eff_athena_slow.errorbar(
    ax, label="Current Athena", marker="^", linestyle="", color="C0"
)
if eff_acts_slow is not None:
    eff_acts_slow.errorbar(
        ax, label="ACTS in Athena", marker="s", linestyle="", color="C1"
    )
if eff_acts_fast is not None:
    eff_acts_fast.errorbar(
        ax, label="ACTS in Athena, Fast", marker="o", linestyle="", color="C2"
    )
if eff_acts_slow_analog is not None:
    eff_acts_slow_analog.errorbar(
        ax,
        label="ACTS in Athena, Analog",
        marker="D",
        linestyle="",
        color="C3",
    )

ax.legend()

subtext = r"""
$\sqrt{s} = 14$ TeV, HL-LHC
$t\bar{t}$, $\langle \mu \rangle$ = 200, Truth $p_T > 1$ GeV
ITk Layout: 03-00-00
ACTS v43.0.1, Athena 25.0.40
""".strip()

atlasify.atlasify(
    axes=ax,
    brand="ATLAS",
    atlas="Simulation Internal",
    subtext=subtext,
    enlarge=1.6,
)

fig.tight_layout()

if args.output is not None:
    fig.savefig(args.output)

if args.output is None or args.show:
    plt.show()
