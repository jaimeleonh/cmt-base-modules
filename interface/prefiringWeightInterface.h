#ifndef prefiringWeightInterface_h
#define prefiringWeightInterface_h

// Standard libraries
#include <vector>
#include <string>
#include <cmath>
#include <math.h> 

// ROOT libraries
#include <ROOT/RVec.hxx>
#include <TH2.h>
#include <TFile.h>

typedef ROOT::VecOps::RVec<float> fRVec;
typedef ROOT::VecOps::RVec<bool> bRVec;
typedef ROOT::VecOps::RVec<int> iRVec;

// prefiringWeightInterface class
class prefiringWeightInterface {
  public:
    prefiringWeightInterface (std::string jetroot, std::string jetmapname,
      std::string photonroot, std::string photonmapname, bool useEMpT);
    ~prefiringWeightInterface ();

    std::vector<float> get_weights(
      fRVec Jet_pt, fRVec Jet_eta, fRVec Jet_chEmEF, fRVec Jet_neEmEF,
      iRVec Photon_jetIdx, fRVec Photon_pt, fRVec Photon_eta, iRVec Photon_electronIdx,
      fRVec Electron_pt, fRVec Electron_eta, iRVec Electron_jetIdx, iRVec Electron_photonIdx
    );

  private:
    TH2F* photon_map;
    TH2F* jet_map;
    bool useEMpt_;

    const float JetMinPt = 20;  // Min/Max Values may need to be fixed for new maps
    const float JetMaxPt = 500;
    const float JetMinEta = 2.0;
    const float JetMaxEta = 3.0;
    const float PhotonMinPt = 20;
    const float PhotonMaxPt = 500;
    const float PhotonMinEta = 2.0;
    const float PhotonMaxEta = 3.0;

    float getPrefireProbability(TH2F* histo, float eta, float pt, float max_pt, int variation);

    float EGvalue(
      int jet_index, iRVec Photon_jetIdx, fRVec Photon_pt, fRVec Photon_eta, iRVec Photon_electronIdx,
      fRVec Electron_pt, fRVec Electron_eta, iRVec Electron_jetIdx, iRVec Electron_photonIdx,
      int variation
    );

};

#endif // prefiringWeightInterface_h