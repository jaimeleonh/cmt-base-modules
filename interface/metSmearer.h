#ifndef metSmearer_h
#define metSmearer_h

// Standard libraries

#include <TLorentzVector.h>
#include <TMath.h>
#include <ROOT/RVec.hxx>

// metSmearer class
class metSmearer {
  public:
    metSmearer ();
    ~metSmearer ();
    std::vector<double> get_smeared_met(
      ROOT::VecOps::RVec<float> Jet_pt,
      ROOT::VecOps::RVec<float> Jet_eta,
      ROOT::VecOps::RVec<float> Jet_phi,
      ROOT::VecOps::RVec<float> Jet_mass,
      float Met_pt,
      float Met_phi,
      ROOT::VecOps::RVec<float> smear_factor
    );

};

#endif // metSmearer_h
