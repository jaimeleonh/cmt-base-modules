#ifndef jecProvider_h
#define jecProvider_h

// -------------------------------------------------------------------------------------------------------------- //
//                                                                                                                //
//   class jecProvider                                                                                            //
//                                                                                                                //
//   Class to compute JEC values.                                                                                 //
//                                                                                                                //
//   Author: Jaime Leon Holgado (jaime.leon.holgado@cern.ch)                                                      //
//   Date  : Sep 2022                                                                                             //
//   Based on https://github.com/LLRCMS/KLUBAnalysis/blob/VBF_UL/interface/JECKLUBinterface.h                     //
//                                                                                                                //
// -------------------------------------------------------------------------------------------------------------- //

// Standard libraries

//CMSSW libraries
#include "CondFormats/JetMETObjects/interface/JetCorrectorParameters.h"
#include "CondFormats/JetMETObjects/interface/JetCorrectionUncertainty.h"

#include <TLorentzVector.h>
#include <TMath.h>
#include <ROOT/RVec.hxx>

typedef std::map<std::string, std::unique_ptr<JetCorrectionUncertainty>> myJECMap;

// jecProvider class
class jecProvider {
  public:
    jecProvider(std::string jerInputFileName, std::vector<std::string> jec_sources);
    ~jecProvider();
    std::vector<std::vector<ROOT::VecOps::RVec<float>>> get_jec_uncertainties(
      size_t nJet,
      ROOT::VecOps::RVec<float> Jet_pt,
      ROOT::VecOps::RVec<float> Jet_eta
    );

  private:
    std::vector<std::string> jec_sources_regrouped_;
    myJECMap jecSourceUncRegroupedProviders_;
};

#endif // jecProvider_h
