#include "Base/Modules/interface/metSmearer.h"


// Constructors
metSmearer::metSmearer () {}

// Destructor
metSmearer::~metSmearer() {}

std::vector<double> metSmearer::get_smeared_met(
    ROOT::VecOps::RVec<float> Jet_pt,
    ROOT::VecOps::RVec<float> Jet_eta,
    ROOT::VecOps::RVec<float> Jet_phi,
    ROOT::VecOps::RVec<float> Jet_mass,
    float Met_pt,
    float Met_phi,
    ROOT::VecOps::RVec<float> smear_factor
  )
{
  auto met_tlv = TLorentzVector();
  met_tlv.SetPxPyPzE(Met_pt * cos(Met_phi), Met_pt * sin(Met_phi), 0, Met_pt);
  for (size_t iJet = 0; iJet < Jet_pt.size(); iJet++) {
    auto jet_tlv = TLorentzVector();
    jet_tlv.SetPtEtaPhiM(Jet_pt[iJet], Jet_eta[iJet], Jet_phi[iJet], Jet_mass[iJet]);
    auto jet_smeared_tlv = jet_tlv * smear_factor[iJet];
    met_tlv += jet_tlv;
    met_tlv -= jet_smeared_tlv;
  }
  return {met_tlv.Pt(), met_tlv.Phi()};
};