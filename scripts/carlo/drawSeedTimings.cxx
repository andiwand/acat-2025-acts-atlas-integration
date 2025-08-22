#include <iostream>
#include <string>
#include <vector>
#include <filesystem>

#include <TApplication.h>
#include <TCanvas.h>
#include <TFile.h>
#include <TTree.h>
#include <TProfile.h>
#include <TAxis.h>
#include <TStyle.h>

const std::size_t target = 2ul;

std::vector<std::string> getRootFiles(const std::string& folderPath);
std::pair<TProfile, TProfile> getData(const std::string& name,
                                      const std::vector<std::string>& files,
                                      const std::string& pathActs,
                                      const std::string& pathAthena);
void processFile(TFile& file,
                 const std::string& path,
                 TProfile& profile);
void setStyle(TProfile& gr,
              int color);

int main() {
  gStyle->SetOptStat(0);
  gStyle->SetOptTitle(0);
  
  //  const std::string pathRelease36 = "/Users/cvarni/Desktop/ACAT/Seeding/data/user.ncalace.seedingOutput.25.0.36_EXT0";
  //  const std::string pathRelease40 = "/Users/cvarni/Desktop/ACAT/Seeding/data/user.ncalace.seedingOutput.25.0.40_EXT0";
  const std::string pathRelease36 = "./Release36";
  const std::string pathRelease40 = "./Release40";

  const std::vector<std::string> filesRelease36 = getRootFiles(pathRelease36);
  const std::vector<std::string> filesRelease40 = getRootFiles(pathRelease40);

  std::cout << "Located " << filesRelease36.size() << " files for release 36" << std::endl;
  std::cout << "Located " << filesRelease40.size() << " files for release 40" << std::endl;
  
  if (filesRelease36.empty()) {
    std::cerr << "Could not locate any file for release 36" << std::endl;
    return 1;
  }
  
  if (filesRelease40.empty()) {
    std::cerr << "Could not locate any file for release 40" << std::endl;
    return 1;
  }

  const std::string pathActs = "run_242020/ActsITkSiSpacePointSeedMaker/ntuples/seedInformation";
  const std::string pathAthena = "run_242020/ITkSiSpacePointSeedMaker/ntuples/seedInformation";

  auto [actsRelease36, athenaRelease36] = getData("36",
                                                  filesRelease36,
                                                  pathActs,
                                                  pathAthena);
  auto [actsRelease40, athenaRelease40] = getData("40",
                                                  filesRelease40,
                                                  pathActs,
                                                  pathAthena);

  setStyle(athenaRelease36, 1);
  setStyle(athenaRelease40, 8);
  setStyle(actsRelease36, 2);
  setStyle(actsRelease40, 4);
  
  actsRelease36.GetYaxis()->SetRangeUser(0, 2.5);
  actsRelease36.GetXaxis()->SetTitle("Number of Seeds");
  actsRelease36.GetYaxis()->SetTitle("Initialisation + Production Time [A.U.]");
    
  TApplication Runner("gui", 0, NULL);
  TCanvas canvas;
  actsRelease36.Draw();
  actsRelease40.Draw("SAME");
  athenaRelease36.Draw("SAME");
  athenaRelease40.Draw("SAME");
  canvas.Draw();
  canvas.Update();
  Runner.Run(true);
}

std::vector<std::string> getRootFiles(const std::string& folderPath) {
  std::vector<std::string> rootFiles {};
  
  // Iterate through the directory entries
  for (const auto& entry : std::filesystem::directory_iterator(folderPath)) {
    if (not entry.is_regular_file()) continue;
    auto path = entry.path();
    if (path.extension() != ".root") continue;
    rootFiles.push_back(path.string());
  }
  
  return rootFiles;
}

std::pair<TProfile, TProfile> getData(const std::string& name,
                                      const std::vector<std::string>& files,
                                      const std::string& pathActs,
                                      const std::string& pathAthena)
{
  int nBins = 30;
  float min = 0;
  float max = 40 * 1e3;

  TProfile profileActs(Form("acts_%s", name.c_str()),
                       Form("acts_%s", name.c_str()),
                       nBins, min, max);
  TProfile profileAthena(Form("athena_%s", name.c_str()),
                         Form("athena_%s", name.c_str()),
                         nBins, min, max);

  std::size_t counter = 0ul;
  for (const std::string& fileName : files) {
    std::cout << "Processing of file: " << fileName << std::endl;
    TFile file(fileName.c_str(), "READ");
    // Read Acts
    processFile(file, pathActs, profileActs);
    // Read Athena
    processFile(file, pathAthena, profileAthena);
    file.Close();
  }
  
  return std::make_pair(profileActs, profileAthena);
}


void processFile(TFile& file,
                 const std::string& path,
                 TProfile& profile)
{
  std::cout << "- Extracting tree: " << path << std::endl;
  TTree *tree = static_cast<TTree*>( file.Get(path.c_str()) );
  if (not tree) {
    throw std::runtime_error("Incable of retrieving tree");
  }

  int v_nSeeds {0};
  float v_time_init {0};
  float v_time_reco {0};

  tree->SetBranchAddress("numberPixelSeeds", &v_nSeeds);
  tree->SetBranchAddress("pixelSeedInitialisationTime", &v_time_init);
  tree->SetBranchAddress("pixelSeedProductionTime", &v_time_reco);

  for (std::size_t i(0); i<tree->GetEntries(); ++i) {
    tree->GetEntry(i);
    profile.Fill(v_nSeeds, (v_time_init + v_time_reco) / 1000.);
    //    profile.Fill(v_nSeeds, (v_time_reco) / 1000.);
  }
  
}

void setStyle(TProfile& data,
              int color) {
  data.SetMarkerStyle(20);
  data.SetMarkerColor(color);
  data.SetLineColor(color);
  data.SetMarkerSize(0.4);
}

