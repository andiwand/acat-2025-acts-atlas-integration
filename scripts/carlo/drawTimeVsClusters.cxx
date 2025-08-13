#include <iostream>
#include <vector>
#include <string>
#include <string_view>

#include <TFile.h>
#include <TTree.h>
#include <TGraph.h>
#include <TH1.h>
#include <TH2.h>
#include <TProfile.h>
#include <TCanvas.h>
#include <TApplication.h>
#include <TStyle.h>
#include <TAxis.h>
#include <TLegend.h>
#include <TLatex.h>

#include "atlasstyle-00-03-05/AtlasStyle.C"
#include "atlasstyle-00-03-05/AtlasUtils.C"
#include "atlasstyle-00-03-05/AtlasLabels.C"

using data_format_t = TProfile;
//using data_format_t = TGraph;


enum class Mode {
    PIXELALG,
    PIXELTOOL,
    STRIPALG,
    STRIPTOOL
};

Mode parseMode(std::string_view input) {
    static const std::unordered_map<std::string_view, Mode> modeMap {
        {"PIXELALG", Mode::PIXELALG},
        {"PIXELTOOL", Mode::PIXELTOOL},
        {"STRIPALG", Mode::STRIPALG},
        {"STRIPTOOL", Mode::STRIPTOOL}
    };

    if (auto it = modeMap.find(input); it != modeMap.end()) {
        return it->second;
    }
    throw std::invalid_argument("Invalid mode: " + std::string(input));
}

template <typename T>
T makeData([[maybe_unused]] const std::string& name,
           [[maybe_unused]] const Mode mode) {
  int nBins = 30;
  float min = 80 * 1e3;
  float max = 420 * 1e3;
  if (mode == Mode::STRIPALG) {
    min = 100 * 1e3;
    max = 380 * 1e3;
  } else if (mode == Mode::PIXELTOOL or mode == Mode::STRIPTOOL) {
    min = 0;
    max = 1000;
  }

  return T(name.c_str(), name.c_str(),
           nBins,
           min, max);
}

template <std::same_as<TGraph> T>
T makeData([[maybe_unused]] const std::string& name,
           [[maybe_unused]] const Mode mode) { return T(); }

template <typename T>
void fillData(T& data, auto valA, auto valB) {
  data.Fill(valA, valB);
}

template <std::same_as<TGraph> T>
void fillData(T& data, auto valA, auto valB) {
  data.SetPoint(data.GetN(), valA, valB);
}

template <typename U,
          typename ... T>
void drawData(TCanvas& canvas,
              U& firstData,
              T& ... data) {
  firstData.Draw();
  (data.Draw("SAME"), ... );
}

template <std::same_as<TGraph> U,
          typename ... T>
void drawData(TCanvas& canvas,
              U& firstData,
              T& ... data) {
  firstData.Draw("AP");
  (data.Draw("P SAME"), ... );
}

data_format_t retrieveTimings(TTree& tree,
                              const std::string& name,
                              const Mode mode);
void setStyle(data_format_t& gr,
              int color);
void setLabels(data_format_t& data,
               const std::string& xAxisLabel,
               const std::string& yAxisLabel) {
  data.GetXaxis()->SetTitle(xAxisLabel.c_str());
  data.GetYaxis()->SetTitle(yAxisLabel.c_str());
}

int main(int argc, char* argv[]) {
  gStyle->SetOptTitle(0);
  gStyle->SetOptStat(0);

  if (argc != 2) {
    std::cerr << "Usage: " << argv[0] << " [PIXELALG|PIXELTOOL|STRIPALG|STRIPTOOL]\n";
    return 1;
  }

  Mode mode = parseMode(argv[1]);
  
  switch (mode) {
  case Mode::PIXELALG:
    std::cout << "Running Pixel Algorithm...\n";
    break;
  case Mode::PIXELTOOL:
    std::cout << "Running Pixel Tool...\n";
    break;
  case Mode::STRIPALG:
    std::cout << "Running Strip Algorithm...\n";
    break;
  case Mode::STRIPTOOL:
    std::cout << "Running Strip Tool...\n";
    break;
  default:
    std::cerr << "Mode not recognized" << std::endl;
    return 1;
  }


  const std::string fileName = "acts-expert-monitoring.root";
  TFile inFile(fileName.c_str(), "READ");

  std::string pathActs = "";
  std::string pathAthena = "";
  switch (mode) {
    case Mode::PIXELALG:
      {
        pathActs = "ActsPixelClusterizationAlg/TimeVsClusters";
        pathAthena = "ITkPixelClusterization/TimeVsClusters";
      }
      break;
  case Mode::PIXELTOOL:
    {
      pathActs = "ActsPixelClusterizationAlg/ActsPixelClusteringTool/TimeVsClusters";
      pathAthena = "ITkPixelClusterization/ITkMergedPixelsTool/TimeVsClusters";
    }
    break;
  case Mode::STRIPALG:
    {
      pathActs = "ActsStripClusterizationAlg/TimeVsClusters";
      pathAthena = "ITkStripClusterization/TimeVsClusters";
    }
    break;
  case Mode::STRIPTOOL:
    {
      pathActs = "ActsStripClusterizationAlg/ActsStripClusteringTool/TimeVsClusters";
      pathAthena = "ITkStripClusterization/ITkStripClusteringTool/TimeVsClusters";
    }
    break;
  }
  
  TTree *treeActs = static_cast<TTree*>( inFile.Get(pathActs.c_str()) );
  TTree *treeAthena = static_cast<TTree*>( inFile.Get(pathAthena.c_str()) );

  if (not treeActs) {
    std::cerr << "Problem retrieving ACTS tree with path: " << pathActs << std::endl;
    return 1;
  }

  if (not treeAthena) {
    std::cerr << "Problem retrieving Athena tree with path: " << pathAthena	<< std::endl;
    return 1;
  }

  data_format_t grActs = retrieveTimings(*treeActs, "Acts", mode);
  data_format_t grAthena = retrieveTimings(*treeAthena, "Athena", mode);

  switch (mode) {
  case Mode::PIXELALG:  
    setLabels(grAthena, "Number of Pixel Clusters", "Average Execution Time [A.U.]");
    break;
  case Mode::STRIPALG:
    setLabels(grAthena, "Number of Strip Clusters", "Average Execution Time [A.U.]");
    break;
  default:
    setLabels(grAthena, "Number of Cells", "Average Execution Time [A.U.]");
    break;
  }
  
  setStyle(grActs, 2);
  setStyle(grAthena, 4);

  if (mode == Mode::PIXELALG) {
    grAthena.GetYaxis()->SetRangeUser(0., 4.5);
  } else if (mode == Mode::STRIPALG) {
    grAthena.GetYaxis()->SetRangeUser(0., 3.8);
  }

  TLegend legend(0.6, 0.15, 0.85, 0.25);
  legend.SetFillColor(0);
  legend.SetLineColor(0);
  legend.AddEntry(&grAthena, "Current Athena", "lp");
  legend.AddEntry(&grActs, "ACTS in Athena", "lp");

  TApplication runner("gui", 0, NULL);
  TCanvas canvas;
  drawData(canvas, grAthena, grActs);
  legend.Draw("SAME");
  canvas.Draw();

  ATLASLabel(0.15, 0.8, "Simulation Internal");
  myText(0.15, 0.75, 1, "#bf{#sqrt{s} = 14 TeV, HL-LHC, ITk Layout: 03-00-00}");
  myText(0.15, 0.70, 1, "#bf{t#bar{t}, #LT#mu#GT = 200}");
  myText(0.15, 0.65, 1, "#bf{ACTS v43.0.1}");
  myText(0.15, 0.60, 1, "#bf{Athena 25.0.40}");

  canvas.Update();

  runner.Run(true);
  
  inFile.Close();
}

// ************************************************* //

data_format_t retrieveTimings(TTree& tree,
                              const std::string& name,
                              const Mode mode) {
  data_format_t data = makeData<data_format_t>(name, mode);

  int v_time {0};
  int v_nClusters {0};

  tree.SetBranchAddress( "TIME_execute", &v_time );
  tree.SetBranchAddress( "NClustersCreated", &v_nClusters );

  std::cout << "Procedding tree with " << tree.GetEntries() << " entries" << std::endl;
  for (std::size_t i(0); i<tree.GetEntries(); ++i) {
    tree.GetEntry(i);
    fillData<data_format_t>(data, v_nClusters, v_time / 100.);
  }
  
  return data;
}

void setStyle(data_format_t& data,
              int color) {
  data.SetMarkerStyle(20);
  data.SetMarkerColor(color);
  data.SetLineColor(color);
  data.SetMarkerSize(0.4);
}

