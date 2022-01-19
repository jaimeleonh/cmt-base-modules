#include "Base/Modules/interface/puWeightinterface.h"


// Constructors


puWeightinterface::puWeightinterface (
      std::string filename, std::string target_filename,
      std::string histoname, std::string target_histoname,
      bool norm, bool verbose
    )
{
  TFile* file = TFile::Open(filename.c_str());
  histo = (TH1F*) file->Get(histoname.c_str());

  TFile* target_file = TFile::Open(target_filename.c_str());
  target_histo = (TH1F*) target_file->Get(target_histoname.c_str());
  
  worker = WeightCalculatorFromHistogram(histo, target_histo, norm, true, verbose);
}

// Destructor
puWeightinterface::~puWeightinterface() {}

float puWeightinterface::get_weight(float nvtx) {
  if (nvtx > histo->GetNbinsX()) return 1;
  else return worker.getWeight(nvtx);  
}