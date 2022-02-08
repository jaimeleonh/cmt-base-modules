#ifndef jetSmearer_h
#define jetSmearer_h

// Standard libraries

#include "PhysicsTools/NanoAODTools/interface/PyJetResolutionScaleFactorWrapper.h"
#include "PhysicsTools/NanoAODTools/interface/PyJetParametersWrapper.h"
#include "PhysicsTools/NanoAODTools/interface/PyJetResolutionWrapper.h"
#include "CondFormats/JetMETObjects/interface/JetResolutionObject.h"

#include <TRandom3.h>
#include <TLorentzVector.h>
#include <TMath.h>
#include <ROOT/RVec.hxx>

// jetSmearer class
class jetSmearer {
  public:
    jetSmearer (
      std::string jerInputFilePath,
      std::string jerInputFileName,
      std::string jerUncertaintyInputFileName
    );
    ~jetSmearer ();
    std::vector<std::vector<float>> get_smear_vals(
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
    );

  private:
    PyJetResolutionScaleFactorWrapper jerSF_and_Uncertainty;
    PyJetParametersWrapper params_sf_and_uncertainty = PyJetParametersWrapper();
    PyJetResolutionWrapper jer;
    PyJetParametersWrapper params_resolution = PyJetParametersWrapper();
    TRandom3 rnd = TRandom3(12345);
};

#endif // jetSmearer_h
