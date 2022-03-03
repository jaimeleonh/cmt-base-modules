#include "Base/Modules/interface/prefiringWeightInterface.h"


// Constructor
prefiringWeightInterface::prefiringWeightInterface (std::string jetroot, std::string jetmapname,
  std::string photonroot, std::string photonmapname, bool useEMpt): useEMpt_(useEMpt)
{
  TFile* photon_file  = TFile::Open(photonroot.c_str());
  photon_map = (TH2F*) photon_file->Get(photonmapname.c_str());

  TFile* jet_file  = TFile::Open(jetroot.c_str());
  jet_map = (TH2F*) jet_file->Get(jetmapname.c_str());
}

// Destructor
prefiringWeightInterface::~prefiringWeightInterface() {}

std::vector<float> prefiringWeightInterface::get_weights(
  fRVec Jet_pt, fRVec Jet_eta, fRVec Jet_chEmEF, fRVec Jet_neEmEF,
  iRVec Photon_jetIdx, fRVec Photon_pt, fRVec Photon_eta, iRVec Photon_electronIdx,
  fRVec Electron_pt, fRVec Electron_eta, iRVec Electron_jetIdx, iRVec Electron_photonIdx
) 
{
  std::vector <float> weights;
  for (int variation = -1; variation < 2; variation++) {
    float prefw = 1.;
    for (size_t ijet = 0; ijet < Jet_pt.size(); ijet++) {
      auto jet_pt = Jet_pt[ijet];
      if (useEMpt_)
        jet_pt *= (Jet_chEmEF[ijet] + Jet_neEmEF[ijet]);
      float jetpf = 1.;
      if (jet_pt >= JetMinPt && fabs(Jet_eta[ijet]) <= JetMaxEta
          && fabs(Jet_eta[ijet]) >= JetMinEta) {
        jetpf *= 1 - getPrefireProbability(jet_map, Jet_eta[ijet], jet_pt, JetMaxPt, variation);
      }

      auto phopf = EGvalue(ijet, Photon_jetIdx, Photon_pt, Photon_eta, Photon_electronIdx,
        Electron_pt, Electron_eta, Electron_jetIdx, Electron_photonIdx, variation);
      prefw *= std::min(jetpf, phopf);
    }
    prefw *= EGvalue(-1, Photon_jetIdx, Photon_pt, Photon_eta, Photon_electronIdx,
      Electron_pt, Electron_eta, Electron_jetIdx, Electron_photonIdx, variation);
    weights.push_back(prefw);
  }
  return weights;
}

float prefiringWeightInterface::getPrefireProbability(
  TH2F* histo, float eta, float pt, float max_pt, int variation
)
{
  auto bin = histo->FindBin(eta, std::min(pt, (float) (max_pt - 0.01)));
  auto pref_prob = histo->GetBinContent(bin);
  auto stat = histo->GetBinError(bin);  // bin statistical uncertainty
  auto syst = 0.2 * pref_prob;  // 20% of prefire rate

  if (variation == 1)
    pref_prob = std::min(pref_prob + sqrt(stat * stat + syst * syst), 1.0);
  else if (variation == -1)
    pref_prob = std::max(pref_prob - sqrt(stat * stat + syst * syst), 0.0);
  return pref_prob;
}

float prefiringWeightInterface::EGvalue(
  int jet_index, iRVec Photon_jetIdx, fRVec Photon_pt, fRVec Photon_eta, iRVec Photon_electronIdx,
  fRVec Electron_pt, fRVec Electron_eta, iRVec Electron_jetIdx, iRVec Electron_photonIdx,
  int variation
)
{
  float photon_pf = 1.;
  std::vector<int> photon_in_jet;

  for (size_t ipho = 0; ipho < Photon_pt.size(); ipho++) {
    if (Photon_jetIdx[ipho] != jet_index)
      continue;
    if (Photon_pt[ipho] >= PhotonMinPt && fabs(Photon_eta[ipho]) <= PhotonMaxEta
        && fabs(Photon_eta[ipho]) >= PhotonMinEta) {
      auto photon_pf_temp = 1 - getPrefireProbability(
        photon_map, Photon_eta[ipho], Photon_pt[ipho], PhotonMaxPt, variation);
      if (Photon_electronIdx[ipho] > -1) {
        float ele_pf_temp = 1.0;
        if (Electron_pt[Photon_electronIdx[ipho]] >= PhotonMinPt
            && fabs(Electron_eta[Photon_electronIdx[ipho]]) <= PhotonMaxEta
            && fabs(Electron_eta[Photon_electronIdx[ipho]]) >= PhotonMinEta) {
          ele_pf_temp = 1 - getPrefireProbability(
            photon_map, Electron_eta[Photon_electronIdx[ipho]],
            Electron_pt[Photon_electronIdx[ipho]], PhotonMaxPt, variation);
        }
        photon_pf *= std::min(photon_pf_temp, ele_pf_temp);
      }
      photon_in_jet.push_back((int) ipho);
    }
  }
  std::vector<int>::iterator it;
  for (size_t iele = 0; iele < Electron_pt.size(); iele++) {
    it = std::find(photon_in_jet.begin(), photon_in_jet.end(), Electron_photonIdx[iele]);
    if (Electron_jetIdx[iele] == jet_index && it == photon_in_jet.end()) {
      if (Electron_pt[iele] >= PhotonMinPt
          && fabs(Electron_eta[iele]) <= PhotonMaxEta
          && fabs(Electron_eta[iele]) >= PhotonMinEta) {
        photon_pf *= (1 - getPrefireProbability(
          photon_map, Electron_eta[iele], Electron_pt[iele], PhotonMaxPt, variation));
      }
    }
  }
  return photon_pf;

}