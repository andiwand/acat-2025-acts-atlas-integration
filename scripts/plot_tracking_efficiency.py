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
parser.add_argument("input_acts_fast", type=Path)
parser.add_argument("mode", choices=["physics", "technical"])
parser.add_argument(
    "--output",
    type=Path,
    help="Path to output file",
)
parser.add_argument("--show", action="store_true", help="Show plot")
args = parser.parse_args()

input_athena_slow = ROOT.TFile.Open(args.input_athena_slow.as_posix())
data_acts_fast = ROOT.TFile.Open(args.input_acts_fast.as_posix())

if args.mode == "physics":
    idtpm_path = "InDetTrackPerfMonPlots/TrkAnaEF_EFsel/Offline/Tracks/Efficiencies/eff_vs_truth_eta"
    ylabel = "Physics Efficiency"
elif args.mode == "technical":
    idtpm_path = "InDetTrackPerfMonPlots/TrkAnaEF_EFsel/Offline/Tracks/Efficiencies/Technical/eff_vs_truth_eta"
    ylabel = "Technical Efficiency"
else:
    raise ValueError("Invalid mode specified. Choose 'physics' or 'technical'.")

eff_athena = TH1(input_athena_slow.Get(idtpm_path), xrange=(-4, 4))
eff_acts = TH1(data_acts_fast.Get(idtpm_path), xrange=(-4, 4))

fig, ax = plt.subplots(1, 1, figsize=(6, 4))

ax.set_xlim(-4, 4)

ax.set_xlabel("$\\eta$")
ax.set_ylabel(ylabel)

eff_acts.errorbar(
    ax, label="ACTS in Athena, Fast", marker="o", linestyle="", color="C0"
)
eff_athena.errorbar(
    ax, label="Current Athena, Default", marker="^", linestyle="", color="C1"
)

ax.legend()

subtext = """
$\\sqrt{s} = 14$ TeV, HL-LHC, ITk Layout: 03-00-00
$t\\bar{t}$, <$\\mu$> = 200
ACTS v43.0.1
Athena 25.0.40
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
