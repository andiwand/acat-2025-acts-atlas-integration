#!/usr/bin/env python3

import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import ROOT
import atlasify

from common import TH1, ratio_std


base_dir = Path(__file__).parent.parent.parent

parser = argparse.ArgumentParser()
parser.add_argument("input_athena_slow", type=Path)
parser.add_argument("input_acts_fast", type=Path)
parser.add_argument("mode", choices=["d0", "z0", "ptqopt"])
parser.add_argument(
    "--output",
    type=Path,
    help="Path to output file",
)
parser.add_argument("--show", action="store_true", help="Show plot")
args = parser.parse_args()

input_athena_slow = ROOT.TFile.Open(args.input_athena_slow.as_posix())
data_acts_fast = ROOT.TFile.Open(args.input_acts_fast.as_posix())

if args.mode == "d0":
    idtpm_path = "InDetTrackPerfMonPlots/TrkAnaEF_EFsel/Offline/Tracks/Resolutions/resolution_d0_vs_truth_eta"
    ylabel = "$\\sigma(d_0)$ [μm]"
elif args.mode == "z0":
    idtpm_path = "InDetTrackPerfMonPlots/TrkAnaEF_EFsel/Offline/Tracks/Resolutions/resolution_z0_vs_truth_eta"
    ylabel = "$\\sigma(z_0)$ [μm]"
elif args.mode == "ptqopt":
    idtpm_path = "InDetTrackPerfMonPlots/TrkAnaEF_EFsel/Offline/Tracks/Resolutions/resolution_ptqopt_vs_truth_eta"
    ylabel = "$p_T \\cdot \\sigma(q/p_T)$"
else:
    raise ValueError("Invalid mode specified. Choose 'd0', 'z0', or 'ptqopt'.")

eff_athena = TH1(input_athena_slow.Get(idtpm_path), xrange=(-4, 4))
eff_acts = TH1(data_acts_fast.Get(idtpm_path), xrange=(-4, 4))

fig, axs = plt.subplots(2, 1, figsize=(6, 4), sharex=True, gridspec_kw={"height_ratios": [10, 3]})

#axs[0].set_xlabel("$\\eta$")
axs[0].set_ylabel(ylabel)

axs[1].set_xlabel("$\\eta$")
axs[1].set_ylabel("Ratio")

eff_acts.errorbar(
    axs[0], label="ACTS in Athena, Fast", marker="o", linestyle="", color="C0"
)
eff_athena.errorbar(
    axs[0], label="Current Athena, Default", marker="^", linestyle="", color="C1"
)

axs[0].legend()

subtext="""
$\\sqrt{s} = 14$ TeV, HL-LHC, ITk Layout: 03-00-00
$t\\bar{t}$, <$\\mu$> = 200
ACTS v43.0.1
Athena 25.0.40
""".strip()

atlasify.atlasify(
    axes=axs[0],
    brand="ATLAS",
    atlas="Simulation Internal",
    subtext=subtext,
    enlarge=2.0,
)

# axs[1].errorbar(
#     eff_athena.x,
#     np.ones(len(eff_athena.x)),
#     xerr=(eff_athena.x_err_lo, eff_athena.x_err_hi),
#     marker="^",
#     linestyle="",
#     color="C1",
#     alpha=0.5,
# )
axs[1].hlines(
    1,
    xmin=eff_athena.x[0],
    xmax=eff_athena.x[-1],
    color="C1",
    linestyle="--",
)
axs[1].errorbar(
    eff_acts.x,
    eff_acts.y / eff_athena.y,
    yerr=ratio_std(eff_acts.y, eff_athena.y, 0.5 * (eff_acts.y_err_hi - eff_acts.y_err_lo), 0.5 * (eff_athena.y_err_hi - eff_athena.y_err_lo)),
    xerr=(eff_acts.x_err_lo, eff_acts.x_err_hi),
    marker="o",
    linestyle="",
    color="C0",
    alpha=0.5,
)

atlasify.atlasify(
    axes=axs[1],
    brand=None,
    atlas=None,
    subtext=None,
)

fig.tight_layout()

if args.output is not None:
    fig.savefig(args.output)

if args.output is None or args.show:
    plt.show()
