import os
import tarfile
import tempfile

from analysis_tools.utils import import_root

ROOT = import_root()


class jetSmearerRDFProducer():
    def __init__(self, isMC, 
            jerInputFileName="Spring16_25nsV10_MC_PtResolution_AK4PFchs.txt",
            jerUncertaintyInputFileName="Spring16_25nsV10_MC_SF_AK4PFchs.txt",
            *args, **kwargs):

        self.isMC = isMC

        if self.isMC:
            self.jerInputArchivePath = os.environ['CMSSW_BASE'] + \
                "/src/PhysicsTools/NanoAODTools/data/jme/"
            self.jerTag = jerInputFileName[:jerInputFileName.find('_MC_') + len('_MC')]
            self.jerArchive = tarfile.open(
                self.jerInputArchivePath + self.jerTag + ".tgz", "r:gz")
            self.jerInputFilePath = tempfile.mkdtemp()
            self.jerArchive.extractall(self.jerInputFilePath)
            self.jerInputFileName = jerInputFileName
            self.jerUncertaintyInputFileName = jerUncertaintyInputFileName

            if "/libBaseModules.so" not in ROOT.gSystem.GetLibraries():
                ROOT.gSystem.Load("libBaseModules.so")
            base = "{}/{}/src/Base/Modules".format(
                os.getenv("CMT_CMSSW_BASE"), os.getenv("CMT_CMSSW_VERSION"))
            ROOT.gROOT.ProcessLine(".L {}/interface/jetSmearer.h".format(base))

            ROOT.gInterpreter.Declare(
                'auto jet_smearer = jetSmearer("%s", "%s", "%s");' % (
                    self.jerInputFilePath, self.jerInputFileName, self.jerUncertaintyInputFileName)
            )

    def run(self, df):
        if not self.isMC:
            return df, []
        branches = ["jet_smear_factor", "jet_smear_factor_down", "jet_smear_factor_up"]
        df = df.Define("smear_factors", "jet_smearer.get_smear_vals("
            "run, luminosityBlock, event, Jet_pt, Jet_eta, Jet_phi, Jet_mass, "
            "GenJet_pt, GenJet_eta, GenJet_phi, GenJet_mass, fixedGridRhoFastjetAll)")
        for ib, branch in enumerate(branches):
            df = df.Define(branch, "smear_factors[%s]" % ib)
        return df, branches


def jetSmearerRDF(**kwargs):
    isMC = kwargs.pop("isMC")
    year = str(kwargs.pop("year"))
    jetType = kwargs.pop("jetType", "AK4PFchs")
    jerTag = kwargs.pop("jerTag", "")

    jerTagsMC = {
        '2016': 'Summer16_25nsV1_MC',
        '2017': 'Fall17_V3_MC',
        '2018': 'Autumn18_V7b_MC',
        'UL2016_preVFP': 'Summer20UL16APV_JRV3_MC',
        'UL2016': 'Summer20UL16_JRV3_MC',
        'UL2017': 'Summer19UL17_JRV2_MC',
        'UL2018': 'Summer19UL18_JRV2_MC',
    }

    jerInputFileName = ""
    jerUncertaintyInputFileName = ""
    if jerTag != "":
        jerTag = jerTagsMC[year]
        jerInputFileName = jerTag + "_PtResolution_" + jetType + ".txt"
        jerUncertaintyInputFileName = jerTag + "_SF_" + jetType + ".txt"
    else:
        if year == "2016":
            jerInputFileName = "Summer16_25nsV1_MC_PtResolution_" + jetType + ".txt"
            jerUncertaintyInputFileName = "Summer16_25nsV1_MC_SF_" + jetType + ".txt"
        elif year == "2017" or year == "2018":  # use 2017 JER for 2018 for the time being
            jerInputFileName = "Fall17_V3_MC_PtResolution_" + jetType + ".txt"
            jerUncertaintyInputFileName = "Fall17_V3_MC_SF_" + jetType + ".txt"
        elif year == "2018" and False:  # jetSmearer not working with 2018 JERs yet
            jerInputFileName = "Autumn18_V7_MC_PtResolution_" + jetType + ".txt"
            jerUncertaintyInputFileName = "Autumn18_V7_MC_SF_" + jetType + ".txt"

    return lambda: jetSmearerRDFProducer(
        isMC=isMC,
        jerInputFileName=jerInputFileName,
        jerUncertaintyInputFileName=jerUncertaintyInputFileName,
        **kwargs)


class jetVarRDFProducer():
    def __init__(self, *args, **kwargs):
        self.isMC = kwargs.pop("isMC")
    
    def run(self, df):
        if not self.isMC:
            return df, []
        df = df.Define("Jet_pt_nom", "Jet_pt * jet_smear_factor")
        df = df.Define("Jet_mass_nom", "Jet_mass * jet_smear_factor")
        return df, ["Jet_pt_nom", "Jet_mass_nom"]


def jetVarRDF(**kwargs):
    return lambda: jetVarRDFProducer(**kwargs)


class metSmearerRDFProducer():
    def __init__(self, isMC):
        self.isMC = isMC
        if self.isMC:
            if "/libBaseModules.so" not in ROOT.gSystem.GetLibraries():
                ROOT.gSystem.Load("libBaseModules.so")
            base = "{}/{}/src/Base/Modules".format(
                os.getenv("CMT_CMSSW_BASE"), os.getenv("CMT_CMSSW_VERSION"))
            ROOT.gROOT.ProcessLine(".L {}/interface/metSmearer.h".format(base))
            ROOT.gInterpreter.Declare('auto met_smearer = metSmearer();')

    def run(self, df):
        if not self.isMC:
            return df, []
        branches = ["MET_smeared_pt", "MET_smeared_phi"]
        df = df.Define("smeared_met", "met_smearer.get_smeared_met("
            "Jet_pt, Jet_eta, Jet_phi, Jet_mass, MET_pt, MET_phi, jet_smear_factor)")
        for ib, branch in enumerate(branches):
            df = df.Define(branch, "smeared_met[%s]" % ib)
        return df, branches


def metSmearerRDF(**kwargs):
    isMC = kwargs.pop("isMC")
    return lambda: metSmearerRDFProducer(isMC, **kwargs);

    