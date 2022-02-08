#include "Base/Modules/interface/jetsmearer.h"


// Constructors


jetSmearer::jetSmearer (
  std::string jerInputFilePath,
  std::string jerInputFileName,
  std::string jerUncertaintyInputFileName
)
{
  jerSF_and_Uncertainty = PyJetResolutionScaleFactorWrapper(jerInputFilePath
    + "/" + jerUncertaintyInputFileName);
  jer = PyJetResolutionWrapper(jerInputFilePath + "/" + jerInputFileName);
}

// Destructor
jetSmearer::~jetSmearer() {}

// std::vector<std::vector<float>> jetSmearer::get_smear_vals(
std::vector<std::vector<float>> jetSmearer::get_smear_vals(
    int run,
    int luminosityBlock,
    int event,
    ROOT::VecOps::RVec<float> Jet_pt,
    ROOT::VecOps::RVec<float> Jet_eta,
    ROOT::VecOps::RVec<float> Jet_phi,
    ROOT::VecOps::RVec<float> Jet_mass,
    ROOT::VecOps::RVec<float> GenJet_pt,
    ROOT::VecOps::RVec<float> GenJet_eta,
    ROOT::VecOps::RVec<float> GenJet_phi,
    ROOT::VecOps::RVec<float> GenJet_mass,
    float rho
) {

  std::vector<float> jet_smeared_pt, jet_smeared_pt_down, jet_smeared_pt_up;//jet_smeared_mass;

  // set seed
  int runnum = run << 20;
  int luminum = luminosityBlock << 10;
  int evtnum = event;
  int jet0eta = 0;
  if (Jet_eta.size() > 1) {
    jet0eta = int(Jet_eta[0] / 0.01);
  }
  rnd.SetSeed(1 + runnum + evtnum + luminum + jet0eta);

  // Loop over jets
  auto jet_tlv = TLorentzVector();
  double jet_pt_resolution = -1;
  for (size_t ijet = 0; ijet < Jet_pt.size(); ijet++) {
    jet_tlv.SetPtEtaPhiM(Jet_pt[ijet], Jet_eta[ijet], Jet_phi[ijet], Jet_mass[ijet]);\
    params_resolution.setJetPt(jet_tlv.Perp());
    params_resolution.setJetEta(jet_tlv.Eta());
    params_resolution.setRho(rho);
    jet_pt_resolution = jer.getResolution(params_resolution);
    
    int genjet_index = -1;
    auto genjet_tlv = TLorentzVector();
    for (size_t igenjet = 0; igenjet < GenJet_pt.size(); igenjet++) {
      genjet_tlv.SetPtEtaPhiM(
        GenJet_pt[igenjet], GenJet_eta[igenjet], GenJet_phi[igenjet], GenJet_mass[igenjet]);
      if (jet_tlv.DeltaR(genjet_tlv) < 0.2 && (
          fabs(jet_tlv.Pt() - genjet_tlv.Pt()) < 3 * jet_pt_resolution * jet_tlv.Pt())) {
        genjet_index = igenjet;
        break;
      }
    }

    params_sf_and_uncertainty.setJetEta(jet_tlv.Eta());
    params_sf_and_uncertainty.setJetPt(jet_tlv.Pt());

    std::vector <Variation> variations = {Variation::NOMINAL, Variation::DOWN, Variation::UP};

    std::vector<float> jet_pt_sf_and_uncertainty;
    for (size_t central_or_shift = 0; central_or_shift < variations.size(); central_or_shift++) {
      jet_pt_sf_and_uncertainty.push_back(
        jerSF_and_Uncertainty.getScaleFactor(
          params_sf_and_uncertainty, variations[central_or_shift]));
    }

    std::vector<float> smear_vals;
    if (genjet_index != -1) {
      auto dPt = jet_tlv.Perp() - genjet_tlv.Perp();
      for (size_t central_or_shift = 0; central_or_shift < jet_pt_sf_and_uncertainty.size();
          central_or_shift++) {
        smear_vals.push_back(1. + (
          jet_pt_sf_and_uncertainty[central_or_shift] - 1.) * dPt / jet_tlv.Perp());
      }
    } else {
      auto rand = rnd.Gaus(0, jet_pt_resolution);
      for (size_t central_or_shift = 0; central_or_shift < jet_pt_sf_and_uncertainty.size();
          central_or_shift++) {
        if (jet_pt_sf_and_uncertainty[central_or_shift] > 1.) {
          smear_vals.push_back(
            1. + rand * sqrt(std::pow(jet_pt_sf_and_uncertainty[central_or_shift], 2) - 1.));
        } else {
          smear_vals.push_back(1.);
        }
      }

      // check that smeared jet energy remains positive,
      // as the direction of the jet would change ("flip")
      // otherwise - and this is not what we want
      
      for (size_t central_or_shift = 0; central_or_shift < jet_pt_sf_and_uncertainty.size();
          central_or_shift++) {
        if (smear_vals[central_or_shift] * jet_tlv.E() < 1E-2)
          smear_vals[central_or_shift] = 1E-2 / jet_tlv.E();

      }
    }
    for (size_t central_or_shift = 0; central_or_shift < jet_pt_sf_and_uncertainty.size();
        central_or_shift++) {
      smear_vals[central_or_shift] = jet_tlv.Pt() * smear_vals[central_or_shift];
    }
    jet_smeared_pt.push_back(smear_vals[0]);
    jet_smeared_pt_down.push_back(smear_vals[1]);
    jet_smeared_pt_up.push_back(smear_vals[2]);
  }
  return {jet_smeared_pt, jet_smeared_pt_down, jet_smeared_pt_up};
  
};