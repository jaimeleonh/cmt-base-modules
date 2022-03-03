import os
from analysis_tools.utils import import_root

from PhysicsTools.NanoAODTools.postprocessing.modules.common.PrefireCorr import PrefCorr

from Base.Modules.baseModules import JetLepMetSyst, DummyModule

ROOT = import_root()


def prefiringWeight(**kwargs):
    isMC = kwargs.pop("isMC")
    if not isMC:
        return lambda: DummyModule(**kwargs)
    return lambda: PrefCorr(**kwargs)


class prefiringWeightRDFProducer(JetLepMetSyst):
    def __init__(self, *args, **kwargs):
        super(prefiringWeightRDFProducer, self).__init__(*args, **kwargs)
        self.isMC = kwargs.pop("isMC")
        if self.isMC:
            if "/libBaseModules.so" not in ROOT.gSystem.GetLibraries():
                ROOT.gSystem.Load("libBaseModules.so")
            base = "{}/{}/src/Base/Modules".format(
                os.getenv("CMT_CMSSW_BASE"), os.getenv("CMT_CMSSW_VERSION"))
            ROOT.gROOT.ProcessLine(".L {}/interface/prefiringWeightInterface.h".format(base))

            base_folder = (os.getenv('CMSSW_BASE')
                + "/src/PhysicsTools/NanoAODTools/data/prefire_maps/")
            jet_file = base_folder + "L1prefiring_jetpt_2017BtoF.root"
            jetmapname = "L1prefiring_jetpt_2017BtoF"
            photon_file = base_folder + "L1prefiring_photonpt_2017BtoF.root"
            photonmapname = "L1prefiring_photonpt_2017BtoF"

            ROOT.gInterpreter.Declare(
                'auto prefiring_weight = prefiringWeightInterface("%s", "%s", "%s", "%s", %s);' % (
                    jet_file, jetmapname, photon_file, photonmapname,
                    ("true" if ("jetempt" in jet_file) else "false"))
            )

    def run(self, df):
        if not self.isMC:
            return df, []
        branch_names = ["PrefireWeight_Down", "PrefireWeight", "PrefireWeight_Up"]
        df = df.Define("pref_weights", "prefiring_weight.get_weights(Jet_pt{0}, Jet_eta, "
            "Jet_chEmEF, Jet_neEmEF, Photon_jetIdx, Photon_pt{1}, Photon_eta, Photon_electronIdx, "
            "Electron_pt{2}, Electron_eta, Electron_jetIdx, Electron_photonIdx)".format(
                self.jet_syst, self.electron_syst, self.photon_syst))
        for ib, branch in enumerate(branch_names):
            df = df.Define(branch, "pref_weights[%s]" % ib)

        return df, branch_names


def prefiringWeightRDF(**kwargs):
    return lambda: prefiringWeightRDFProducer(**kwargs)
