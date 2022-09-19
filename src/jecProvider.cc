#include "Base/Modules/interface/jecProvider.h"


// Constructors
jecProvider::jecProvider (std::string jerInputFileName, std::vector<std::string> jec_sources)
{
  for (const auto& source: jec_sources) {
    JetCorrectorParameters source_parameters_reduced(jerInputFileName, source);
    std::unique_ptr<JetCorrectionUncertainty> source_uncertainty_reduced(
      new JetCorrectionUncertainty(source_parameters_reduced));
    jecSourceUncRegroupedProviders_.emplace(source, std::move(source_uncertainty_reduced));
  }
  jec_sources_regrouped_ = jec_sources;
}

// Destructor
jecProvider::~jecProvider() {}

std::vector<std::vector<ROOT::VecOps::RVec<float>>> jecProvider::get_jec_uncertainties(
    size_t nJet,
    ROOT::VecOps::RVec<float> Jet_pt,
    ROOT::VecOps::RVec<float> Jet_eta
)
{
  std::vector <ROOT::VecOps::RVec<float>> jec_uncertainties_up;
  std::vector <ROOT::VecOps::RVec<float>> jec_uncertainties_down;

  for (auto source: jec_sources_regrouped_) {
    ROOT::VecOps::RVec<float> unc_up;
    ROOT::VecOps::RVec<float> unc_down;

    for (size_t ijet = 0; ijet < nJet; ijet++) {
      jecSourceUncRegroupedProviders_[source]->setJetEta(Jet_eta[ijet]);
      jecSourceUncRegroupedProviders_[source]->setJetPt(Jet_pt[ijet]);
      unc_up.push_back(1 + jecSourceUncRegroupedProviders_[source]->getUncertainty(true));

      jecSourceUncRegroupedProviders_[source]->setJetEta(Jet_eta[ijet]);
      jecSourceUncRegroupedProviders_[source]->setJetPt(Jet_pt[ijet]);
      unc_down.push_back(1 - jecSourceUncRegroupedProviders_[source]->getUncertainty(false));
    }

    jec_uncertainties_up.push_back(unc_up);
    jec_uncertainties_down.push_back(unc_down);
  }
  return {jec_uncertainties_up, jec_uncertainties_down};
};