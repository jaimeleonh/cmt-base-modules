#ifndef puWeightinterface_h
#define puWeightinterface_h

// Standard libraries
#include <vector>
#include <string>
#include <cmath>

#include <TH1.h>
#include <TFile.h>

#include "PhysicsTools/NanoAODTools/interface/WeightCalculatorFromHistogram.h"

// puWeightinterface class
class puWeightinterface {
  public:
  puWeightinterface ();
    puWeightinterface (
      std::string filename, std::string target_filename,
      std::string histoname, std::string target_histoname,
      bool norm, bool verbose
    );
    ~puWeightinterface ();
    float get_weight(float nvtx);

  private:
    WeightCalculatorFromHistogram worker;
    TH1F* histo;
    TH1F* target_histo;

};

#endif // puWeightinterface_h